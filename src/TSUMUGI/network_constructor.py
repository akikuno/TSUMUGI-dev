from __future__ import annotations

import gzip
import hashlib
import io
import json
import math
import random
import tempfile
import zlib
from collections import defaultdict
from collections.abc import Iterable
from contextlib import ExitStack
from itertools import combinations
from pathlib import Path
from typing import Any

from tqdm import tqdm

random.seed(0)


ZYGOSITY_MAP = {
    "homozygote": "Homo",
    "heterozygote": "Hetero",
    "hemizygote": "Hemi",
    "hom": "Homo",
    "het": "Hetero",
    "hem": "Hemi",
}


MAX_GENE_COUNT = 150
GENE_COUNT_LOWER_BOUND = 100
GENE_COUNT_UPPER_BOUND = 150
GENE_ASSET_SCHEMA_VERSION = 2
DIRECT_EDGE_BUCKET_COUNT = 256

###############################################################################
# Compose datasets
###############################################################################


def _create_annotation_string(*parts: str) -> str:
    """Join non-empty parts with commas."""
    return ", ".join(part for part in parts if part)


def _normalize_sexual_dimorphism(sexual_dimorphism) -> str:
    """Normalize missing sexual dimorphism values used in phenotype labels."""
    if sexual_dimorphism in (None, "None"):
        return ""
    return sexual_dimorphism


def _create_phenotype_annotation_string(
    mp_term_name,
    zygosity,
    life_stage="",
    sexual_dimorphism="",
) -> str:
    """Create the display label used for phenotype annotations."""
    annotation_str = _create_annotation_string(
        zygosity,
        life_stage,
        _normalize_sexual_dimorphism(sexual_dimorphism),
    )
    return f"{mp_term_name} ({annotation_str})"


def _build_target_phenotype_annotations(
    records,
    mp_term_name,
) -> set[str]:
    """Build exact phenotype labels required for phenotype network edges."""
    return {
        _create_phenotype_annotation_string(
            record["mp_term_name"],
            record["zygosity"],
            record.get("life_stage", ""),
            record.get("sexual_dimorphism", ""),
        )
        for record in records
        if record["mp_term_name"] == mp_term_name
    }


def _has_required_shared_annotation(
    pair_annotations,
    required_shared_annotations=None,
) -> bool:
    """Return whether a pair has a required shared phenotype annotation."""
    if not required_shared_annotations:
        return True
    return bool(required_shared_annotations.intersection(pair_annotations["phenotype_shared_annotations"]))


# ----------------------------------------------------------
# Compose genewise_phenotype_significants
# ----------------------------------------------------------
def _compose_genewise_phenotype_significants(
    genewise_phenotype_significants: list[dict[str, str | float]],
) -> dict[str, list[dict[str, str | float]]]:
    """Compose genewise_phenotype_significants into gene_records_map for Nodes."""

    gene_records_map = defaultdict(list)
    for record in genewise_phenotype_significants:
        mp_term_name_with_metadata = _create_phenotype_annotation_string(
            record["mp_term_name"],
            record["zygosity"],
            record.get("life_stage", ""),
            record.get("sexual_dimorphism", ""),
        )

        effect_size = record["effect_size"]

        gene_records_map[record["marker_symbol"]].append(
            {
                "mp_term_name": record["mp_term_name"],
                "effect_size": effect_size,
                "mp_term_name_with_metadata": mp_term_name_with_metadata,
            }
        )

    return dict(gene_records_map)


# ----------------------------------------------------------
# Compose biological annotations
# ----------------------------------------------------------


def _compose_pairwise_similarity_annotations(
    pairwise_similarity_annotations: list[dict[str, list[dict[str, str]] | int]],
) -> dict[tuple[str], dict[str, list[str] | int]]:
    """Compose pair similarity annotations (Edges) into strings."""
    pairwise_similarity_annotations_composed = {}
    for record in pairwise_similarity_annotations:
        pair_annotations_composed = set()
        for annotation in record["phenotype_shared_annotations"]:
            pair_annotations_composed.add(
                _create_phenotype_annotation_string(
                    annotation["mp_term_name"],
                    annotation["zygosity"],
                    annotation.get("life_stage", ""),
                    annotation.get("sexual_dimorphism", ""),
                )
            )

        gene_pair = tuple(sorted([record["gene1_symbol"], record["gene2_symbol"]]))

        pairwise_similarity_annotations_composed[gene_pair] = {
            "phenotype_shared_annotations": sorted(pair_annotations_composed),
            "phenotype_similarity_score": record["phenotype_similarity_score"],
        }
    return pairwise_similarity_annotations_composed


# ----------------------------------------------------------
# Compose disease_annotations_by_allele
# ----------------------------------------------------------
def _compose_disease_annotations_by_allele(
    disease_annotations_by_allele: dict[str, list[dict[str, str]]],
) -> dict[str, set[str]]:
    disease_annotations_composed = defaultdict(set)
    for marker_symbol, records in disease_annotations_by_allele.items():
        for record in records:
            disorder_name = record["disorder_name"]
            zygosity = record["zygosity"]
            life_stage = record["life_stage"]

            annotation = []
            annotation.append(zygosity)
            annotation.append(life_stage)
            annotation = ", ".join(annotation)

            disease_annotations_composed[marker_symbol].add(f"{disorder_name} ({annotation})")

    return dict(disease_annotations_composed)


def _compose_dataset(genewise_phenotype_significants, pairwise_similarity_annotations, disease_annotations_by_allele):
    gene_records_map = _compose_genewise_phenotype_significants(genewise_phenotype_significants)
    pairwise_similarity_annotations_composed = _compose_pairwise_similarity_annotations(
        pairwise_similarity_annotations
    )
    disease_annotations_composed = _compose_disease_annotations_by_allele(disease_annotations_by_allele)
    return gene_records_map, pairwise_similarity_annotations_composed, disease_annotations_composed


###############################################################################
# Build network JSON
###############################################################################


def _scale_to_1_100(x: int, min_val: int, max_val: int) -> int:
    if max_val == min_val:
        return 100
    if x <= min_val:
        return 1
    if x >= max_val:
        return 100

    scale = 99 / (max_val - min_val)
    shifted = x - min_val
    scaled_score = 1 + shifted * scale

    return int(scaled_score)


def _finite_float_or_default(value, default: float) -> float:
    try:
        value_float = float(value)
    except (TypeError, ValueError):
        return default
    return value_float if math.isfinite(value_float) else default


def _target_effect_size_is_missing(records, mp_term_name) -> bool:
    target_effect_sizes = [
        _finite_float_or_default(record.get("effect_size"), float("nan"))
        for record in records
        if record["mp_term_name"] == mp_term_name
    ]
    return bool(target_effect_sizes) and not any(math.isfinite(value) for value in target_effect_sizes)


def _scale_phenotype_similarity_scores(pairwise_similarity_annotations_filtered, target_gene: str | None = None):
    if target_gene:
        scores = [
            v["phenotype_similarity_score"]
            for pair, v in pairwise_similarity_annotations_filtered.items()
            if target_gene in pair
        ]
    else:
        scores = [v["phenotype_similarity_score"] for v in pairwise_similarity_annotations_filtered.values()]

    min_val = min(scores)
    max_val = max(scores)

    scaled_annotations = {}

    for pair, annotation in pairwise_similarity_annotations_filtered.items():
        scaled_annotation = annotation.copy()
        scaled_annotation["phenotype_similarity_score"] = _scale_to_1_100(
            annotation["phenotype_similarity_score"],
            min_val,
            max_val,
        )
        scaled_annotations[pair] = scaled_annotation

    return scaled_annotations


def _scale_effect_sizes(gene_records_map_filtered, mp_term_name):
    target_records = []
    for records in gene_records_map_filtered.values():
        for record in records:
            if record["mp_term_name"] == mp_term_name:
                target_records.append(record)

    effect_sizes = [_finite_float_or_default(record.get("effect_size"), float("nan")) for record in target_records]
    effect_sizes = [effect_size for effect_size in effect_sizes if math.isfinite(effect_size)]

    if not effect_sizes:
        for record in target_records:
            record["effect_size"] = 1
        return gene_records_map_filtered

    # For binary effect sizes (0 or 1), set 1 to 100 directly
    if all(es == 1 for es in effect_sizes):
        for record in target_records:
            effect_size = _finite_float_or_default(record.get("effect_size"), float("nan"))
            record["effect_size"] = 100 if effect_size == 1 else 1
        return gene_records_map_filtered

    effect_sizes_log1p = [math.log1p(es) for es in effect_sizes]
    min_val = min(effect_sizes_log1p)
    max_val = max(effect_sizes_log1p)
    for record in target_records:
        effect_size = _finite_float_or_default(record.get("effect_size"), float("nan"))
        if not math.isfinite(effect_size):
            record["effect_size"] = 1
            continue
        effect_size_scaled = _scale_to_1_100(math.log1p(effect_size), min_val, max_val)
        record["effect_size"] = effect_size_scaled
    return gene_records_map_filtered


def _normalize_gene_pair(gene1: str, gene2: str) -> tuple[str, str]:
    return tuple(sorted([gene1, gene2]))


def _build_pairwise_adjacency_index(
    pairwise_similarity_annotations_composed: dict[tuple[str, str], dict[str, list[str] | int]],
) -> dict[str, list[tuple[str, str]]]:
    adjacency_index = defaultdict(list)
    for gene1, gene2 in pairwise_similarity_annotations_composed.keys():
        pair = _normalize_gene_pair(gene1, gene2)
        pair_key = pair if pair in pairwise_similarity_annotations_composed else (gene1, gene2)
        adjacency_index[pair[0]].append(pair_key)
        adjacency_index[pair[1]].append(pair_key)
    return {gene: sorted(set(pairs)) for gene, pairs in adjacency_index.items()}


def _iter_existing_gene_pairs(
    related_genes: set[str],
    pairwise_similarity_annotations_composed: dict[tuple[str, str], dict[str, list[str] | int]],
    candidate_pairs: list[tuple[str, str]] | None = None,
):
    if candidate_pairs is None:
        for gene1, gene2 in combinations(sorted(related_genes), 2):
            gene_pair = _normalize_gene_pair(gene1, gene2)
            if gene_pair in pairwise_similarity_annotations_composed:
                yield gene_pair
        return

    seen_pairs = set()
    for gene1, gene2 in candidate_pairs:
        if gene1 not in related_genes or gene2 not in related_genes:
            continue
        gene_pair = _normalize_gene_pair(gene1, gene2)
        if (
            gene_pair not in pairwise_similarity_annotations_composed
            and (
                gene1,
                gene2,
            )
            in pairwise_similarity_annotations_composed
        ):
            gene_pair = (gene1, gene2)
        elif (
            gene_pair not in pairwise_similarity_annotations_composed
            and (
                gene2,
                gene1,
            )
            in pairwise_similarity_annotations_composed
        ):
            gene_pair = (gene2, gene1)
        if gene_pair in seen_pairs or gene_pair not in pairwise_similarity_annotations_composed:
            continue
        seen_pairs.add(gene_pair)
        yield gene_pair


def _collect_induced_gene_pairs(
    related_genes: set[str],
    pairwise_adjacency_index: dict[str, list[tuple[str, str]]],
) -> list[tuple[str, str]]:
    related_pairs = set()
    for gene in related_genes:
        for gene_pair in pairwise_adjacency_index.get(gene, []):
            gene1, gene2 = gene_pair
            if gene1 in related_genes and gene2 in related_genes:
                related_pairs.add(gene_pair)
    return sorted(related_pairs)


def _find_optimal_scores(
    sorted_scores,
    related_genes,
    pairwise_similarity_annotations_composed,
    required_shared_annotations: set[str] | None = None,
    low_threshold=GENE_COUNT_LOWER_BOUND,
    high_threshold=GENE_COUNT_UPPER_BOUND,
    candidate_pairs: list[tuple[str, str]] | None = None,
):
    low = 0
    high = len(sorted_scores) - 1
    while low <= high:
        mid = (low + high) // 2

        count_genes = set()
        for gene_pair in _iter_existing_gene_pairs(
            related_genes,
            pairwise_similarity_annotations_composed,
            candidate_pairs=candidate_pairs,
        ):
            gene1, gene2 = gene_pair
            pair_annotations = pairwise_similarity_annotations_composed[gene_pair]
            if not _has_required_shared_annotation(pair_annotations, required_shared_annotations):
                continue
            if pair_annotations["phenotype_similarity_score"] >= sorted_scores[mid]:
                count_genes.add(gene1)
                count_genes.add(gene2)

        n = len(count_genes)

        if low_threshold <= n <= high_threshold:
            return sorted_scores[mid]
        elif n < low_threshold:
            high = mid - 1
        else:
            low = mid + 1
    return -1


def _filter_related_genes(
    records: list[dict[str, str | float]],
    related_genes: set[str],
    pairwise_similarity_annotations_composed: dict[tuple[str, str], dict[str, list[str] | int]],
    is_gene_network: bool = False,
    required_shared_annotations: set[str] | None = None,
    candidate_pairs: list[tuple[str, str]] | None = None,
) -> set[str]:
    """
    Strategy:
      1) If possible, select by a threshold on phenotype similarity score found via _find_optimal_scores().
      2) Otherwise, rank by:
         - effect size (desc),
         - then number of shared phenotypes (desc),
         - then phenotype similarity score (desc),
         - then gene symbol (asc, for stability),
         and take the top MAX_GENE_COUNT.
    Notes:
      - NaN effect sizes are treated as 0 for ranking.
      - For speed, pair stats are computed in a single pass over unique gene pairs.
    """

    # --- Compute maximum values per gene ---
    phenotype_similarity_scores = []
    gene_max_score = defaultdict(float)
    gene_max_shared_phenotype = defaultdict(int)
    matching_pairs = []

    for gene_pair in _iter_existing_gene_pairs(
        related_genes,
        pairwise_similarity_annotations_composed,
        candidate_pairs=candidate_pairs,
    ):
        gene1, gene2 = gene_pair
        pair_annotations = pairwise_similarity_annotations_composed[gene_pair]
        if not _has_required_shared_annotation(pair_annotations, required_shared_annotations):
            continue
        matching_pairs.append(gene_pair)
        score = pair_annotations["phenotype_similarity_score"]
        num_shared_phenotypes = len(pair_annotations["phenotype_shared_annotations"])

        phenotype_similarity_scores.append(score)

        # Update maximum similarity score for each gene
        gene_max_score[gene1] = max(gene_max_score[gene1], score)
        gene_max_score[gene2] = max(gene_max_score[gene2], score)

        # Update maximum number of shared phenotypes for each gene
        gene_max_shared_phenotype[gene1] = max(gene_max_shared_phenotype[gene1], num_shared_phenotypes)
        gene_max_shared_phenotype[gene2] = max(gene_max_shared_phenotype[gene2], num_shared_phenotypes)

    # 1. Filter genes by phenotype similarity score
    unique_phenotype_similarity_scores = sorted(set(phenotype_similarity_scores))
    candidate_related_genes = set(gene_max_score.keys()) if required_shared_annotations else related_genes

    optimal_score = -1
    if unique_phenotype_similarity_scores:
        optimal_score = _find_optimal_scores(
            unique_phenotype_similarity_scores,
            related_genes,
            pairwise_similarity_annotations_composed,
            required_shared_annotations=None,
            low_threshold=GENE_COUNT_LOWER_BOUND,
            high_threshold=GENE_COUNT_UPPER_BOUND,
            candidate_pairs=matching_pairs,
        )
    if optimal_score > -1:
        return {gene for gene, max_score in gene_max_score.items() if max_score >= optimal_score}

    if is_gene_network is False:
        # For gene networks, effect size is only 0 or 1, so skip effect size filtering

        # Compute maximum effect size per gene
        gene_max_effect_sizes = defaultdict(float)
        for record in records:
            gene = record["marker_symbol"]
            if gene in candidate_related_genes:
                effect_size = _finite_float_or_default(record.get("effect_size"), 0.0)
                gene_max_effect_sizes[gene] = max(gene_max_effect_sizes[gene], effect_size)

        # 2. Filter genes by effect size
        filtered_effect_sizes = {g: s for g, s in gene_max_effect_sizes.items() if g in candidate_related_genes}
        gene_max_effect_sizes_sorted = sorted(filtered_effect_sizes.items(), key=lambda x: x[1], reverse=True)

        # If the top MAX_GENE_COUNT entries have different effect sizes, return them
        if len({score for _, score in gene_max_effect_sizes_sorted[:MAX_GENE_COUNT]}) > 1:
            return {gene for gene, _ in gene_max_effect_sizes_sorted[:MAX_GENE_COUNT]}

    # 3. Filter genes by number of shared phenotypes
    filtered_shared_phenotypes = {g: s for g, s in gene_max_shared_phenotype.items() if g in candidate_related_genes}
    gene_max_shared_phenotype_sorted = sorted(filtered_shared_phenotypes.items(), key=lambda x: x[1], reverse=True)
    return {gene for gene, _ in gene_max_shared_phenotype_sorted[:MAX_GENE_COUNT]}


###############################################################################
# build_phenotype_network_json
###############################################################################


def _convert_to_nodes_json(
    related_genes: set[str],
    mp_term_name: str,
    gene_records_map: dict[str, list[dict[str, str | float]]],
    disease_annotations_composed: dict[str, set[str]],
    hide_effect_size: bool = False,
) -> list[dict[str, dict[str, str | list[str] | int]]]:
    nodes_json = []
    gene_records_map_filtered = {gene: gene_records_map[gene] for gene in related_genes}
    missing_effect_size_by_gene = {
        gene: _target_effect_size_is_missing(records, mp_term_name)
        for gene, records in gene_records_map_filtered.items()
    }

    # Scale effect sizes to 1-100
    gene_records_map_filtered = _scale_effect_sizes(gene_records_map_filtered, mp_term_name)

    for gene, records in gene_records_map_filtered.items():
        phenotypes: list[str] = [r["mp_term_name_with_metadata"] for r in records]
        diseases: set[str] = disease_annotations_composed.get(gene, set())
        target_node_colors = [
            _finite_float_or_default(r.get("effect_size"), 1) for r in records if r["mp_term_name"] == mp_term_name
        ]
        node_color = max(target_node_colors, default=1)

        node = {
            "data": {
                "id": gene,
                "label": gene,
                "phenotype": sorted(phenotypes),
                "disease": sorted(diseases) if diseases else "",
                "node_color": node_color,
            }
        }
        if missing_effect_size_by_gene.get(gene, False):
            node["data"]["effect_size_missing"] = True
        if hide_effect_size:
            node["data"]["hide_effect_size"] = True
        nodes_json.append(node)

    # Sort nodes for stability
    nodes_json.sort(key=lambda x: x["data"]["id"])
    return nodes_json


def _convert_to_edges_json(
    related_genes: set[str],
    pairwise_similarity_annotations_composed: dict[tuple[str], dict[str, list[str] | int]],
    required_shared_annotations: set[str] | None = None,
) -> list[dict[str, dict[str, str | list[str] | float]]]:
    edges_json = []
    pairwise_similarity_annotations_filtered = {}
    for gene1, gene2 in combinations(sorted(related_genes), 2):
        gene_pairs = tuple(sorted([gene1, gene2]))
        if gene_pairs not in pairwise_similarity_annotations_composed:
            continue
        pair_annotations = pairwise_similarity_annotations_composed[gene_pairs]
        if not _has_required_shared_annotation(pair_annotations, required_shared_annotations):
            continue
        pairwise_similarity_annotations_filtered[gene_pairs] = pair_annotations

    if not pairwise_similarity_annotations_filtered:
        return []

    # Scale phenotype similarity scores to 1-100
    pairwise_similarity_annotations_filtered = _scale_phenotype_similarity_scores(
        pairwise_similarity_annotations_filtered, target_gene=None
    )

    for pair_genes, pair_annotations in pairwise_similarity_annotations_filtered.items():
        gene1, gene2 = sorted(pair_genes)
        edges_json.append(
            {
                "data": {
                    "source": gene1,
                    "target": gene2,
                    "phenotype": sorted(pair_annotations["phenotype_shared_annotations"]),
                    "edge_size": pair_annotations["phenotype_similarity_score"],
                }
            }
        )
    # Sort edges for stability
    edges_json.sort(key=lambda e: (e["data"]["source"], e["data"]["target"]))
    return edges_json


def _write_network_json_gz(network_json, output_json: Path) -> None:
    with gzip.open(output_json, "wt", encoding="utf-8") as f:
        json.dump(network_json, f, indent=4)


def build_phenotype_network_json(
    genewise_phenotype_significants: list[dict[str, str | float]],
    pairwise_similarity_annotations: dict[tuple[str], dict[str, dict[str, dict[str, str] | int]]],
    disease_annotations_by_gene: dict[str, dict[str, str]],
    output_dir,
    binary_phenotypes: set[str] | None = None,
    hide_effect_size: bool = False,
) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for existing_network in output_dir.glob("*.json.gz"):
        existing_network.unlink()

    gene_records_map, pairwise_similarity_annotations_composed, disease_annotations_composed = _compose_dataset(
        genewise_phenotype_significants, pairwise_similarity_annotations, disease_annotations_by_gene
    )

    phenotype_records_map: dict[str, list[dict[str, str | float]]] = defaultdict(list)
    for record in genewise_phenotype_significants:
        phenotype_records_map[record["mp_term_name"]].append(record)
    phenotype_records_map = dict(phenotype_records_map)

    gene_lists = set()
    for pair in pairwise_similarity_annotations_composed.keys():
        for gene in pair:
            gene_lists.add(gene)

    for mp_term_name in tqdm(phenotype_records_map.keys(), total=len(phenotype_records_map)):
        records = phenotype_records_map[mp_term_name]
        related_genes = {r["marker_symbol"] for r in records if r["marker_symbol"] in gene_lists}
        target_phenotype_annotations = _build_target_phenotype_annotations(records, mp_term_name)
        mp_term_name_underscore = mp_term_name.replace(" ", "_").replace("/", "_")
        output_json = Path(output_dir / f"{mp_term_name_underscore}.json.gz")

        if len(related_genes) < 2:
            continue

        if len(related_genes) > MAX_GENE_COUNT:
            related_genes = _filter_related_genes(
                records,
                related_genes,
                pairwise_similarity_annotations_composed,
                required_shared_annotations=target_phenotype_annotations,
            )

        is_binary = False
        if binary_phenotypes:
            is_binary = mp_term_name in binary_phenotypes

        edges_json = _convert_to_edges_json(
            related_genes,
            pairwise_similarity_annotations_composed,
            required_shared_annotations=target_phenotype_annotations,
        )

        if not edges_json:
            continue

        # Remove unconnected nodes
        connected_node_ids = set()
        for edge in edges_json:
            connected_node_ids.add(edge["data"]["source"])
            connected_node_ids.add(edge["data"]["target"])

        if not connected_node_ids:
            continue

        nodes_json = _convert_to_nodes_json(
            connected_node_ids,
            mp_term_name,
            gene_records_map,
            disease_annotations_composed,
            hide_effect_size=hide_effect_size or is_binary,
        )

        network_json = nodes_json + edges_json

        _write_network_json_gz(network_json, output_json)


###############################################################################
# build_gene_network_json
###############################################################################


def _build_node_info(
    gene: str,
    gene_records_map: dict[str, list[dict[str, str | float]]],
    disease_annotations_composed: dict[str, set[str]],
    target_gene: str,
    hide_effect_size: bool = False,
) -> dict[str, dict[str, str | list[str] | float]]:
    phenotypes: list[str] = [r["mp_term_name_with_metadata"] for r in gene_records_map.get(gene, [])]
    diseases: set[str] = disease_annotations_composed.get(gene, set())
    node_color: int = 100 if target_gene == gene else 1

    node = {
        "data": {
            "id": gene,
            "label": gene,
            "phenotype": sorted(phenotypes),
            "disease": sorted(diseases) if diseases else "",
            "node_color": node_color,
        }
    }
    if hide_effect_size:
        node["data"]["hide_effect_size"] = True
    return node


def _build_direct_edge_info(
    record: dict[str, Any],
) -> dict[str, dict[str, str | list[str] | int]]:
    gene1, gene2 = sorted([str(record["gene1_symbol"]), str(record["gene2_symbol"])])
    shared_annotations = record.get("phenotype_shared_annotations", [])
    phenotypes = {
        _create_phenotype_annotation_string(
            annotation["mp_term_name"],
            annotation["zygosity"],
            annotation.get("life_stage", ""),
            annotation.get("sexual_dimorphism", ""),
        )
        for annotation in shared_annotations
    }
    return {
        "data": {
            "source": gene1,
            "target": gene2,
            "phenotype": sorted(phenotypes),
            "phenotype_similarity_score": int(record.get("phenotype_similarity_score", 0)),
            "shared_context_count": len(shared_annotations),
        }
    }


def _direct_edge_bucket_index(gene: str, bucket_count: int) -> int:
    return zlib.crc32(gene.encode("utf-8")) % bucket_count


def _write_direct_edge_buckets(
    pairwise_similarity_annotations: Iterable[dict[str, Any]],
    bucket_paths: list[Path],
    min_shared_annotations: int,
    min_phenotype_similarity_score: int,
) -> int:
    pair_count = 0
    with ExitStack() as stack:
        handles = [
            stack.enter_context(path.open("w", encoding="utf-8"))
            for path in bucket_paths
        ]
        for record in pairwise_similarity_annotations:
            shared_annotations = record.get("phenotype_shared_annotations", [])
            score = int(record.get("phenotype_similarity_score", 0))
            if len(shared_annotations) < min_shared_annotations or score < min_phenotype_similarity_score:
                continue
            pair_count += 1

            edge = _build_direct_edge_info(record)
            edge_json = json.dumps(edge, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
            source = str(edge["data"]["source"])
            target = str(edge["data"]["target"])
            for gene in (source, target):
                bucket_index = _direct_edge_bucket_index(gene, len(bucket_paths))
                handles[bucket_index].write(f"{gene}\t{edge_json}\n")
    return pair_count


def _write_deterministic_json_gz(path: Path, payload: Any) -> None:
    with path.open("wb") as raw_file:
        with gzip.GzipFile(fileobj=raw_file, mode="wb", compresslevel=9, mtime=0) as gzip_file:
            with io.TextIOWrapper(gzip_file, encoding="utf-8") as text_file:
                json.dump(
                    payload,
                    text_file,
                    ensure_ascii=False,
                    separators=(",", ":"),
                    sort_keys=True,
                )


def _write_gene_assets_from_bucket(
    bucket_path: Path,
    gene_records_map: dict[str, list[dict[str, str | float]]],
    disease_annotations_composed: dict[str, set[str]],
    output_dir: Path,
    hide_effect_size: bool,
) -> list[dict[str, str | int]]:
    edges_by_gene: dict[str, dict[tuple[str, str], dict[str, Any]]] = defaultdict(dict)
    with bucket_path.open(encoding="utf-8") as f:
        for line in f:
            gene, edge_json = line.rstrip("\n").split("\t", 1)
            edge = json.loads(edge_json)
            data = edge["data"]
            pair = (str(data["source"]), str(data["target"]))
            existing = edges_by_gene[gene].get(pair)
            if existing is not None and existing != edge:
                raise ValueError(f"Conflicting direct edge payload for {pair[0]} and {pair[1]}")
            edges_by_gene[gene][pair] = edge

    manifest_entries = []
    for gene in sorted(edges_by_gene):
        direct_edges = [
            edges_by_gene[gene][pair]
            for pair in sorted(edges_by_gene[gene])
        ]
        node = _build_node_info(
            gene,
            gene_records_map,
            disease_annotations_composed,
            gene,
            hide_effect_size=hide_effect_size,
        )
        asset = {
            "schema_version": GENE_ASSET_SCHEMA_VERSION,
            "gene": gene,
            "node": node,
            "direct_edges": direct_edges,
        }
        output_json = output_dir / f"{gene}.json.gz"
        _write_deterministic_json_gz(output_json, asset)
        manifest_entries.append(
            {
                "gene": gene,
                "bytes": output_json.stat().st_size,
                "sha256": hashlib.sha256(output_json.read_bytes()).hexdigest(),
            }
        )
    return manifest_entries


def build_gene_network_json(
    genewise_phenotype_significants: list[dict[str, str | float]],
    pairwise_similarity_annotations: Iterable[dict[str, Any]],
    disease_annotations_by_gene: dict[str, dict[str, str]],
    output_dir,
    hide_effect_size: bool = True,
    min_shared_annotations: int = 1,
    min_phenotype_similarity_score: int = 1,
) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for stale_path in output_dir.glob("*.json.gz"):
        stale_path.unlink()
    manifest_path = output_dir / "manifest.json"
    if manifest_path.exists():
        manifest_path.unlink()

    gene_records_map = _compose_genewise_phenotype_significants(genewise_phenotype_significants)
    disease_annotations_composed = _compose_disease_annotations_by_allele(disease_annotations_by_gene)

    with tempfile.TemporaryDirectory(prefix="tsumugi-gene-assets-", dir=output_dir.parent) as temp_dir:
        temp_path = Path(temp_dir)
        bucket_paths = [
            temp_path / f"direct-edges-{bucket_index:03d}.jsonl"
            for bucket_index in range(DIRECT_EDGE_BUCKET_COUNT)
        ]
        pair_count = _write_direct_edge_buckets(
            pairwise_similarity_annotations,
            bucket_paths,
            min_shared_annotations,
            min_phenotype_similarity_score,
        )
        manifest_entries = []
        for bucket_path in tqdm(bucket_paths, desc="Writing complete gene assets"):
            manifest_entries.extend(
                _write_gene_assets_from_bucket(
                    bucket_path,
                    gene_records_map,
                    disease_annotations_composed,
                    output_dir,
                    hide_effect_size,
                )
            )
        manifest = {
            "schema_version": GENE_ASSET_SCHEMA_VERSION,
            "min_shared_annotations": min_shared_annotations,
            "min_phenotype_similarity_score": min_phenotype_similarity_score,
            "gene_count": len(manifest_entries),
            "pair_count": pair_count,
            "edge_copy_count": pair_count * 2,
            "files": sorted(manifest_entries, key=lambda entry: str(entry["gene"])),
        }
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
