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
TEMPLATE_HTML_DIR = WEB_DIR / "template" / "template-app-html"
TEMPLATE_JS_DIR = WEB_DIR / "template" / "template-app-js"
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


def _format_suffix(zygosity: str, life_stage: str, sexual_dimorphism: str) -> str:
    """Return a suffix like '(Homo, Early, Male)'; omit 'None'."""
    parts = [zygosity, life_stage]
    if sexual_dimorphism and sexual_dimorphism != "None":
        parts.append(sexual_dimorphism)
    return f"({', '.join(parts)})"


def build_nodes(gene_to_records, all_genes):
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
        recs = gene_to_records.get(gene, [])

        phenotype_lines: list[str] = []
        disease_lines: list[str] = []

        for r in recs:
            mp = r.get("mp_term_name", "")
            zyg = r.get("zygosity", "")
            ls = r.get("life_stage", "")
            sd = r.get("sexual_dimorphism", "None")
            suffix = _format_suffix(zygosity=zyg, life_stage=ls, sexual_dimorphism=sd)

            # Phenotypes of {gene} KO mice
            if mp:
                phenotype_lines.append(f"{mp} {suffix}")

            # Associated Human Diseases (list[str] only)
            for dis in r.get("disease_annotation", []) or []:
                disease_lines.append(f"{dis} {suffix}")

        phenotype_lines = list(set(phenotype_lines))
        disease_lines = list(set(disease_lines))

        # Formatted annotation text for display
        lines = [f"Phenotypes of {gene} KO mice"]
        lines += [f"- {p}" for p in phenotype_lines]
        if disease_lines:
            lines.append("Associated Human Diseases")
            lines += [f"- {d}" for d in disease_lines]

        nodes.append(
            {
                "data": {
                    "id": gene,
                    "label": gene,
                    "phenotype": phenotype_lines,
                    "disease": disease_lines if disease_lines else "",
                    "node_color": 1,
                }
            }
        )

    return nodes


###############################################################################
# Edge building
###############################################################################


def _build_edges(pairwise_similarity_annotations: Iterator[dict]):
    """Return list of Cytoscape.js edges."""
    edges = []

    for r in pairwise_similarity_annotations:
        g1 = r["gene1_symbol"]
        g2 = r["gene2_symbol"]

        shared = r.get("phenotype_shared_annotations", {}) or {}
        phen_list = []

        for mp, ann in shared.items():
            zyg = ann.get("zygosity", "")
            ls = ann.get("life_stage", "")
            sd = ann.get("sexual_dimorphism", "")
            if sd == "None":
                sd = ""

            ann_str = _create_annotation_string(zyg, ls, sd)

            if mp:
                if ann_str:
                    phen_list.append(f"{mp} ({ann_str})")
                else:
                    phen_list.append(mp)

        edge_size = r.get("phenotype_similarity_score", 0)

        edges.append(
            {
                "data": {
                    "source": g1,
                    "target": g2,
                    "phenotype": phen_list,
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


def build_webapp_network(genewise_path, pairwise_path):
    """Return (nodes, edges)."""
    # Read pairwise annotations and collect all genes
    pairwise_similarity_annotations: list[dict] = list(io_handler.read_jsonl(pairwise_path))

    all_genes = set()
    for record in pairwise_similarity_annotations:
        all_genes.add(record["gene1_symbol"])
        all_genes.add(record["gene2_symbol"])

    # Read genewise annotations and map by marker_symbol
    genewise_phenotype_annotations: Iterator[dict] = io_handler.read_jsonl(genewise_path)
    gene_to_records = defaultdict(list)
    for rec in genewise_phenotype_annotations:
        gene_to_records[rec["marker_symbol"]].append(rec)
    gene_to_records = dict(gene_to_records)

    nodes = build_nodes(gene_to_records, all_genes)

    if len(nodes) > MAX_NODE_COUNT:
        raise ValueError(
            f"Number of nodes ({len(nodes)}) exceeds the maximum allowed ({MAX_NODE_COUNT}). "
            "For large networks, please generate a GraphML file using the `tsumugi build-graphml` "
            "command and visualize it with Cytoscape or another network visualization tool."
        )

    edges = _build_edges(pairwise_similarity_annotations)

    symbol_to_id = _build_symbol_to_id_map(gene_to_records)

    return nodes, edges, symbol_to_id


def build_and_save_webapp_network(genewise_path, pairwise_path, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "network.json.gz"
    network_label = "Gene List"

    nodes, edges, symbol_to_id = build_webapp_network(genewise_path, pairwise_path)
    elements = nodes + edges
    with gzip.open(json_path, "wt", encoding="utf-8") as f:
        json.dump(elements, f, indent=4)

    symmap_path = output_dir / "marker_symbol_accession_id.json"
    with open(symmap_path, "w", encoding="utf-8") as fh:
        json.dump(symbol_to_id, fh, ensure_ascii=False, indent=2)

    _create_webapp_bundle(
        output_dir=output_dir,
        data_filename=json_path.name,
        network_label=network_label,
    )


###############################################################################
# Helpers for HTML/JS generation
###############################################################################


def _safe_filename(name: str) -> str:
    if not name:
        return "gene_list"
    safe = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in name)
    return safe or "gene_list"


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

    _copy_asset_tree(WEB_APP_DIR / "css", output_dir / "css")
    _copy_asset_tree(WEB_APP_DIR / "js", output_dir / "js")
    _copy_asset_tree(WEB_DIR / "image", output_dir / "image")
    _copy_launchers(output_dir)

    safe_entry_name = _safe_filename(network_label)
    _generate_genelist_entry_script(
        output_dir=output_dir,
        entry_js_name=safe_entry_name,
        data_filename=data_filename,
        export_label=safe_entry_name,
    )
    _generate_index_html(
        output_dir=output_dir,
        entry_js_name=safe_entry_name,
        network_label=network_label,
    )


def _read_template(path: Path) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _generate_genelist_entry_script(
    output_dir: Path,
    entry_js_name: str,
    data_filename: str,
    export_label: str,
) -> None:
    template_lines = _read_template(TEMPLATE_JS_DIR / "template_app.js").splitlines()
    filtered_lines = [
        line
        for line in template_lines
        if "XXX_NODE_COLOR_INITIALIZATION" not in line and "XXX_NODE_COLOR_UPDATE" not in line
    ]
    template = "\n".join(filtered_lines)
    template = template.replace(
        'const isGeneSymbolPage = "XXX_ELEMENTS".includes("genesymbol");',
        "const isGeneSymbolPage = false;",
    )

    filter_js = _read_template(TEMPLATE_JS_DIR / "filterByNodeColorAndEdgeSize_genelist.js")

    final_js = (
        template.replace("XXX_FILTER_BY_NODE_COLOR_AND_EDGE_SIZE", filter_js)
        .replace("XXX_NODE_MIN_MAX", "")
        .replace(
            "XXX_EDGE_MIN_MAX",
            "const edgeMin = Math.min(...edgeSizes); const edgeMax = Math.max(...edgeSizes);",
        )
        .replace("XXX_ELEMENTS", f"loadJSONGz('./{data_filename}')")
        .replace("XXX_PHENOTYPE", "")
        .replace("XXX_NAME", export_label)
    )
    final_js = final_js.replace(
        'const map_symbol_to_id = loadJSON("../../data/marker_symbol_accession_id.json");',
        'const map_symbol_to_id = loadJSON("./marker_symbol_accession_id.json");',
    )

    js_path = output_dir / "js" / f"{entry_js_name}.js"
    with open(js_path, "w", encoding="utf-8") as fh:
        fh.write(final_js)


def _generate_index_html(
    output_dir: Path,
    entry_js_name: str,
    network_label: str,
) -> None:
    body_html = _read_template(TEMPLATE_HTML_DIR / "body-container.html").replace("XXX_PHENOTYPE_SEVERITY", "")
    cy_html = _read_template(TEMPLATE_HTML_DIR / "cy-container.html").replace("XXX_PHENOTYPE_SEVERITY", "")

    page_title = network_label or "Gene List"

    head_html = (
        _read_template(TEMPLATE_HTML_DIR / "head.html")
        .replace("XXX_TITLE", page_title)
        .replace('src="./XXX_JS_FILE_NAME.js"', f'src="./js/{entry_js_name}.js"')
        .replace("XXX_JS_FILE_NAME", entry_js_name)
    )
    head_html = head_html.replace("../js/", "./js/").replace("../css/", "./css/").replace("../../image", "./image")

    if network_label and network_label.lower() != "gene list":
        header_insert = f"Gene List: {network_label}"
    else:
        header_insert = "Gene List"
    header_html = _read_template(TEMPLATE_HTML_DIR / "header.html").replace("XXX_TITLE", header_insert)

    template_html = _read_template(TEMPLATE_HTML_DIR / "template_app.html")
    final_html = (
        template_html.replace("XXX_HEAD", head_html)
        .replace("XXX_H1", header_html)
        .replace("XXX_BODY_CONTAINER", body_html)
        .replace("XXX_CY_CONTAINER", cy_html)
    )

    index_path = output_dir / "index.html"
    with open(index_path, "w", encoding="utf-8") as fh:
        fh.write(final_html)
