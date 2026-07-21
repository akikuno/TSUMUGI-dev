from __future__ import annotations

import csv
import gzip
import json
from collections import Counter, defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from tqdm import tqdm

MP_ONTOLOGY_ROOT_ID = "MP:0000001"
EDGE_KEY_SEPARATOR = "||"


def _edge_key(source: str, target: str) -> str:
    return EDGE_KEY_SEPARATOR.join(sorted([source, target]))


def _build_top_level_module_index(
    ontology_terms: dict[str, dict[str, Any]],
    root_id: str = MP_ONTOLOGY_ROOT_ID,
) -> tuple[dict[str, dict[str, str]], dict[str, list[dict[str, str]]]]:
    top_level_ids = {
        term_id for term_id, term_data in ontology_terms.items() if root_id in set(term_data.get("is_a", []))
    }
    modules_by_id = {
        term_id: {"id": term_id, "name": ontology_terms[term_id]["name"], "label": ontology_terms[term_id]["name"]}
        for term_id in top_level_ids
        if "name" in ontology_terms[term_id]
    }
    cache: dict[str, list[dict[str, str]]] = {}

    def resolve_modules(term_id: str) -> list[dict[str, str]]:
        if term_id in cache:
            return cache[term_id]
        if term_id in modules_by_id:
            cache[term_id] = [modules_by_id[term_id]]
            return cache[term_id]

        modules: dict[str, dict[str, str]] = {}
        for parent_id in ontology_terms.get(term_id, {}).get("is_a", []):
            for module in resolve_modules(parent_id):
                modules[module["id"]] = module

        cache[term_id] = sorted(modules.values(), key=lambda module: (module["name"], module["id"]))
        return cache[term_id]

    modules_by_term_name: dict[str, list[dict[str, str]]] = {}
    for term_id, term_data in ontology_terms.items():
        term_name = term_data.get("name")
        if not term_name:
            continue
        modules = resolve_modules(term_id)
        if modules:
            modules_by_term_name[term_name] = modules

    return modules_by_id, modules_by_term_name


def _get_annotation_term_name(annotation: dict[str, Any] | str) -> str:
    if isinstance(annotation, dict):
        return str(annotation.get("mp_term_name", ""))
    text = str(annotation)
    suffix_index = text.rfind(" (")
    if suffix_index >= 0:
        return text[:suffix_index]
    return text


def _build_edge_module_memberships(
    pairwise_similarity_annotations: Iterable[dict[str, Any]],
    modules_by_term_name: dict[str, list[dict[str, str]]],
    modules_by_id: dict[str, dict[str, str]],
) -> tuple[dict[str, dict[str, Any]], Counter[str]]:
    edge_modules: dict[str, dict[str, Any]] = {}
    missing_terms: Counter[str] = Counter()

    for record in pairwise_similarity_annotations:
        source = str(record["gene1_symbol"])
        target = str(record["gene2_symbol"])
        module_counts: Counter[str] = Counter()

        for annotation in record.get("phenotype_shared_annotations", []):
            term_name = _get_annotation_term_name(annotation)
            modules = modules_by_term_name.get(term_name, [])
            if not modules:
                if term_name:
                    missing_terms[term_name] += 1
                continue
            for module in modules:
                module_counts[module["id"]] += 1

        total_count = sum(module_counts.values())
        if total_count == 0:
            continue

        modules_json = []
        for module_id, count in module_counts.items():
            module = modules_by_id[module_id]
            modules_json.append(
                {
                    "id": module_id,
                    "name": module["name"],
                    "label": module["label"],
                    "count": count,
                    "support_count": count,
                    "weight": round(count / total_count, 6),
                }
            )
        modules_json.sort(key=lambda module: (-module["weight"], -module["count"], module["name"]))

        edge_modules[_edge_key(source, target)] = {
            "source": source,
            "target": target,
            "modules": modules_json,
        }

    return edge_modules, missing_terms


def _load_gene_network(path_json_gz: Path) -> list[dict[str, dict[str, Any]]]:
    with gzip.open(path_json_gz, "rt", encoding="utf-8") as f:
        return json.load(f)


def _iter_network_edges(network_json: list[dict[str, dict[str, Any]]]) -> Iterable[dict[str, Any]]:
    for element in network_json:
        data = element.get("data", {})
        if "source" in data and "target" in data:
            yield data


def _iter_network_nodes(network_json: list[dict[str, dict[str, Any]]]) -> Iterable[dict[str, Any]]:
    for element in network_json:
        data = element.get("data", {})
        if "source" not in data and "id" in data:
            yield data


def _new_module_stat(module: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": module["id"],
        "name": module["name"],
        "label": module.get("label", module["name"]),
        "edge_count": 0,
        "target_edge_count": 0,
        "support": 0.0,
        "target_support": 0.0,
        "phenotype_count": 0,
        "node_ids": set(),
    }


def _build_node_memberships(
    node_module_support: dict[str, dict[str, dict[str, Any]]],
    target_supported_module_ids: set[str],
) -> dict[str, dict[str, Any]]:
    nodes_json: dict[str, dict[str, Any]] = {}
    for node_id, module_map in node_module_support.items():
        filtered_modules = {
            module_id: values
            for module_id, values in module_map.items()
            if module_id in target_supported_module_ids and values["weighted_support"] > 0
        }
        total_support = sum(values["weighted_support"] for values in filtered_modules.values())
        if total_support == 0:
            continue

        modules = []
        for module_id, values in filtered_modules.items():
            modules.append(
                {
                    "id": module_id,
                    "name": values["name"],
                    "label": values["label"],
                    "support_count": values["support_count"],
                    "weight": round(values["weighted_support"] / total_support, 6),
                }
            )
        modules.sort(key=lambda module: (-module["weight"], -module["support_count"], module["name"]))
        nodes_json[node_id] = {
            "modules": modules,
            "dominant_module": modules[0]["id"],
        }

    return nodes_json


def _build_gene_module_payload(
    target_gene: str,
    network_json: list[dict[str, dict[str, Any]]],
    edge_module_memberships: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    module_stats: dict[str, dict[str, Any]] = {}
    node_module_support: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    target_supported_module_ids: set[str] = set()
    edges_json: dict[str, dict[str, Any]] = {}
    node_ids = {str(node["id"]) for node in _iter_network_nodes(network_json)}
    network_edge_count = 0
    missing_edge_count = 0

    for edge in _iter_network_edges(network_json):
        network_edge_count += 1
        source = str(edge["source"])
        target = str(edge["target"])
        key = _edge_key(source, target)
        membership = edge_module_memberships.get(key)
        if not membership:
            missing_edge_count += 1
            continue

        edge_size = edge.get("edge_size", 1) or 1
        edge_weight = float(edge_size)
        edge_modules = []
        for module in membership["modules"]:
            module_id = module["id"]
            module_stats.setdefault(module_id, _new_module_stat(module))
            stat = module_stats[module_id]
            weighted_support = edge_weight * float(module["weight"])
            support_count = int(module.get("support_count", module.get("count", 0)) or 0)

            stat["edge_count"] += 1
            stat["support"] += weighted_support
            stat["phenotype_count"] += support_count
            stat["node_ids"].update([source, target])
            if target_gene in {source, target}:
                stat["target_edge_count"] += 1
                stat["target_support"] += weighted_support
                target_supported_module_ids.add(module_id)

            edge_modules.append(module)

            for node_id in [source, target]:
                node_module_support[node_id].setdefault(
                    module_id,
                    {
                        "id": module_id,
                        "name": module["name"],
                        "label": module.get("label", module["name"]),
                        "support_count": 0,
                        "weighted_support": 0.0,
                    },
                )
                node_values = node_module_support[node_id][module_id]
                node_values["support_count"] += support_count
                node_values["weighted_support"] += weighted_support

        if edge_modules:
            edges_json[key] = {
                "source": source,
                "target": target,
                "modules": edge_modules,
            }

    modules_json = []
    for module_id, stat in module_stats.items():
        if module_id not in target_supported_module_ids:
            continue
        modules_json.append(
            {
                "id": stat["id"],
                "name": stat["name"],
                "label": stat["label"],
                "edge_count": stat["edge_count"],
                "target_edge_count": stat["target_edge_count"],
                "support": round(stat["support"], 6),
                "target_support": round(stat["target_support"], 6),
                "phenotype_count": stat["phenotype_count"],
                "node_count": len(stat["node_ids"]),
            }
        )
    modules_json.sort(
        key=lambda module: (
            -module["target_support"],
            -module["target_edge_count"],
            -module["support"],
            module["name"],
        )
    )
    for rank, module in enumerate(modules_json, start=1):
        module["rank"] = rank

    target_supported_module_ids = {module["id"] for module in modules_json}
    filtered_edges_json = {}
    for key, edge in edges_json.items():
        modules = [module for module in edge["modules"] if module["id"] in target_supported_module_ids]
        if modules:
            filtered_edges_json[key] = {**edge, "modules": modules}

    payload = {
        "target": target_gene,
        "ontology_root": MP_ONTOLOGY_ROOT_ID,
        "edge_key_separator": EDGE_KEY_SEPARATOR,
        "modules": modules_json,
        "edges": filtered_edges_json,
        "nodes": _build_node_memberships(node_module_support, target_supported_module_ids),
    }
    summary = {
        "target": target_gene,
        "nodes": len(node_ids),
        "edges": network_edge_count,
        "module_count": len(modules_json),
        "module_edge_count": len(filtered_edges_json),
        "missing_edge_items": missing_edge_count,
    }
    return payload, summary


def _write_json_gz(path_json_gz: Path, payload: dict[str, Any]) -> None:
    path_json_gz.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path_json_gz, "wt", encoding="utf-8") as f:
        json.dump(payload, f, indent=4)


def _write_summary_csv(path_csv: Path, rows: list[dict[str, Any]], missing_terms: Counter[str]) -> None:
    path_csv.parent.mkdir(parents=True, exist_ok=True)
    with path_csv.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "target",
            "nodes",
            "edges",
            "module_count",
            "module_edge_count",
            "missing_edge_items",
            "missing_unique_terms",
            "missing_term_items",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    **row,
                    "missing_unique_terms": len(missing_terms),
                    "missing_term_items": sum(missing_terms.values()),
                }
            )


def write_mp_top_level_module_lookup_json(
    ontology_terms: dict[str, dict[str, Any]],
    output_path: str | Path,
) -> None:
    """Write phenotype term name to top-level MP module mappings for the web viewer."""
    output_path = Path(output_path)
    _, modules_by_term_name = _build_top_level_module_index(ontology_terms)
    lookup = {
        term_name: [{"id": module["id"], "label": module["label"]} for module in modules]
        for term_name, modules in sorted(modules_by_term_name.items())
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(lookup, f, ensure_ascii=False, indent=2)


def build_gene_phenotype_module_json(
    pairwise_similarity_annotations: Iterable[dict[str, Any]],
    ontology_terms: dict[str, dict[str, Any]],
    gene_network_dir: str | Path,
    output_dir: str | Path,
    summary_csv_path: str | Path,
) -> None:
    """Build ontology-guided soft phenotype module metadata for gene-symbol pages."""
    gene_network_dir = Path(gene_network_dir)
    output_dir = Path(output_dir)
    summary_csv_path = Path(summary_csv_path)

    modules_by_id, modules_by_term_name = _build_top_level_module_index(ontology_terms)
    edge_module_memberships, missing_terms = _build_edge_module_memberships(
        pairwise_similarity_annotations,
        modules_by_term_name,
        modules_by_id,
    )

    rows = []
    gene_network_files = sorted(gene_network_dir.glob("*.json.gz"))
    for gene_network_path in tqdm(gene_network_files, total=len(gene_network_files)):
        target_gene = gene_network_path.name.removesuffix(".json.gz")
        network_json = _load_gene_network(gene_network_path)
        payload, summary = _build_gene_module_payload(target_gene, network_json, edge_module_memberships)
        _write_json_gz(output_dir / gene_network_path.name, payload)
        rows.append(summary)

    _write_summary_csv(summary_csv_path, rows, missing_terms)
