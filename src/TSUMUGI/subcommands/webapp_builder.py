from __future__ import annotations

import gzip
import json
import shutil
from collections import defaultdict
from collections.abc import Iterator
from pathlib import Path

from TSUMUGI import io_handler

MAX_NODE_COUNT = 150

from importlib.resources import as_file, files

WEB_DIR = files("TSUMUGI") / "web"
WEB_APP_DIR = WEB_DIR / "app"
LAUNCHER_FILES = [
    "open_webapp_linux.sh",
    "open_webapp_mac.command",
    "open_webapp_windows.bat",
    "serve_index.py",
]


def _create_annotation_string(*parts):
    """Join non-empty parts with commas."""
    return ", ".join([p for p in parts if p])


###############################################################################
# Node building
###############################################################################


def build_nodes(gene_to_records, all_genes, hide_severity: bool = False):
    """
    Embed the following formatted text into data.annotation:
        Phenotypes of {GENE} KO mice
        - {mp_term_name} (zygosity, life_stage, sexual_dimorphism)
        ...
        Associated Human Diseases
        - {disease_name} (zygosity, life_stage, sexual_dimorphism)
        ...
    """
    nodes = []

    for gene in sorted(all_genes):
        records = gene_to_records.get(gene, [])

        phenotype_lines: list[str] = []
        disease_lines: list[str] = []

        for record in records:
            mp_term_name = record["mp_term_name"]
            zygosity = record["zygosity"]
            life_stage = record["life_stage"]
            sexual_dimorphism = record["sexual_dimorphism"]
            if sexual_dimorphism == "None":
                sexual_dimorphism = ""

            annotations = _create_annotation_string(zygosity, life_stage, sexual_dimorphism)

            phenotype_lines.append(f"{mp_term_name} ({annotations})")

            # Associated Human Diseases (list[str] only)
            for disease in record["disease_annotation"]:
                disease_lines.append(f"{disease} ({annotations})")

        phenotype_lines = list(set(phenotype_lines))
        disease_lines = list(set(disease_lines))

        # Formatted annotation text for display
        lines = [f"Phenotypes of {gene} KO mice"]
        lines += [f"- {p}" for p in phenotype_lines]
        if disease_lines:
            lines.append("Associated Human Diseases")
            lines += [f"- {d}" for d in disease_lines]

        node = {
            "data": {
                "id": gene,
                "label": gene,
                "phenotype": phenotype_lines,
                "disease": disease_lines if disease_lines else "",
                "node_color": 1,
            }
        }
        if hide_severity:
            node["data"]["hide_severity"] = True

        nodes.append(node)

    return nodes


###############################################################################
# Edge building
###############################################################################


def _build_edges(pairwise_similarity_annotations: Iterator[dict[str, str | int | list[dict[str, str]]]]) -> list[dict]:
    """Return list of Cytoscape.js edges."""
    edges = []

    for records in pairwise_similarity_annotations:
        g1 = records["gene1_symbol"]
        g2 = records["gene2_symbol"]

        shared_annotations: list[dict[str, str]] = records["phenotype_shared_annotations"]
        phenotype_lines = []

        for shared_annotation in shared_annotations:
            mp_term_name = shared_annotation["mp_term_name"]
            zygosity = shared_annotation["zygosity"]
            life_stage = shared_annotation["life_stage"]
            sexual_dimorphism = shared_annotation["sexual_dimorphism"]
            if sexual_dimorphism == "None":
                sexual_dimorphism = ""

            annotations = _create_annotation_string(zygosity, life_stage, sexual_dimorphism)

            phenotype_lines.append(f"{mp_term_name} ({annotations})")

        edge_size = records["phenotype_similarity_score"]

        edges.append(
            {
                "data": {
                    "source": g1,
                    "target": g2,
                    "phenotype": phenotype_lines,
                    "edge_size": edge_size,
                }
            }
        )

    return edges


###############################################################################
# Main builder
###############################################################################


def _build_symbol_to_id_map(gene_to_records: dict[str, list[dict]]) -> dict[str, str]:
    symbol_to_id: dict[str, str] = {}
    for symbol, recs in gene_to_records.items():
        for r in recs:
            acc = r.get("marker_accession_id")
            if isinstance(acc, str) and acc and symbol not in symbol_to_id:
                symbol_to_id[symbol] = acc
                break
    return symbol_to_id


def build_webapp_network(genewise_path, pairwise_path, hide_severity: bool = False):
    """Return (nodes, edges)."""
    # Read pairwise annotations and collect all genes

    all_genes = set()
    for record in io_handler.read_jsonl(pairwise_path):
        all_genes.add(record["gene1_symbol"])
        all_genes.add(record["gene2_symbol"])

    # Read genewise annotations and map by marker_symbol
    genewise_phenotype_annotations: Iterator[dict] = io_handler.read_jsonl(genewise_path)
    gene_to_records = defaultdict(list)
    for rec in genewise_phenotype_annotations:
        gene_to_records[rec["marker_symbol"]].append(rec)
    gene_to_records = dict(gene_to_records)

    nodes = build_nodes(gene_to_records, all_genes, hide_severity=hide_severity)

    if len(nodes) > MAX_NODE_COUNT:
        raise ValueError(
            f"Number of nodes ({len(nodes)}) exceeds the maximum allowed ({MAX_NODE_COUNT}). "
            "For large networks, please generate a GraphML file using the `tsumugi build-graphml` "
            "command and visualize it with Cytoscape or another network visualization tool."
        )

    edges = _build_edges(io_handler.read_jsonl(pairwise_path))

    symbol_to_id = _build_symbol_to_id_map(gene_to_records)

    return nodes, edges, symbol_to_id


def build_and_save_webapp_network(genewise_path, pairwise_path, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir = output_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    json_path = data_dir / "network.json.gz"
    network_label = "Gene List"

    # For gene/gene list views, we hide severity; caller (TSUMUGI main) can pass False for phenotype mode
    nodes, edges, symbol_to_id = build_webapp_network(genewise_path, pairwise_path, hide_severity=True)
    elements = nodes + edges
    with gzip.open(json_path, "wt", encoding="utf-8") as f:
        json.dump(elements, f, indent=4)

    symmap_path = data_dir / "marker_symbol_accession_id.json"
    with open(symmap_path, "w", encoding="utf-8") as fh:
        json.dump(symbol_to_id, fh, ensure_ascii=False, indent=2)

    _create_webapp_bundle(
        output_dir=output_dir,
        data_filename=str(json_path.relative_to(output_dir)),
        network_label=network_label,
    )


###############################################################################
# Helpers for HTML/JS generation
###############################################################################


def _copy_asset_tree(src: Path, dst: Path) -> None:
    with as_file(src) as src_on_fs:
        src = Path(src_on_fs)
        if src.exists():
            shutil.copytree(src, dst, dirs_exist_ok=True)


def _copy_launchers(output_dir: Path) -> None:
    for filename in LAUNCHER_FILES:
        src = WEB_DIR / filename
        if src.exists():
            with as_file(src) as src_on_fs:
                shutil.copy(src_on_fs, output_dir / filename)


def _create_webapp_bundle(
    output_dir: Path,
    data_filename: str,
    network_label: str,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    _copy_asset_tree(WEB_APP_DIR, output_dir / "app")
    _copy_asset_tree(WEB_DIR / "image", output_dir / "image")
    _copy_launchers(output_dir)

    _generate_index_html(
        output_dir=output_dir,
        data_filename=data_filename,
        network_label=network_label,
    )


def _generate_index_html(
    output_dir: Path,
    data_filename: str,
    network_label: str,
) -> None:
    label = network_label or "Gene List"
    data_path = data_filename.replace("\\", "/")
    label_json = json.dumps(label)
    data_json = json.dumps(data_path)
    target_json = json.dumps("./app/viewer.html")
    final_html = f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{label}</title>
    <link rel="icon" href="./image/tsumugi-favicon.ico" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pako/2.1.0/pako.min.js"></script>
</head>
<body>
    <noscript>This page requires JavaScript to load the network data.</noscript>
    <div id="status" style="font-family: Arial, sans-serif; padding: 16px;">Loading network data...</div>
    <script>
        const dataPath = {data_json};
        const networkLabel = {label_json};
        const viewerPath = {target_json};

        async function loadAndRedirect() {{
            const statusEl = document.getElementById("status");
            try {{
                const response = await fetch(dataPath, {{ cache: "no-cache" }});
                if (!(response.ok || response.status === 0)) {{
                    throw new Error(`Failed to load data: ${{response.status}}`);
                }}
                const buffer = await response.arrayBuffer();
                const decompressed = window.pako.ungzip(new Uint8Array(buffer), {{ to: "string" }});
                localStorage.setItem("elements", decompressed);
                const target = `${{viewerPath}}?mode=genelist&title=${{encodeURIComponent(networkLabel)}}`;
                window.location.replace(target);
            }} catch (error) {{
                console.error(error);
                if (statusEl) {{
                    statusEl.textContent = "Failed to load network data. Please check the console for details.";
                }}
            }}
        }}

        loadAndRedirect();
    </script>
</body>
</html>
"""
    index_path = output_dir / "index.html"
    with open(index_path, "w", encoding="utf-8") as fh:
        fh.write(final_html)
