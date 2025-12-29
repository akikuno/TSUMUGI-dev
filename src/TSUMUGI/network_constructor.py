from __future__ import annotations

import gzip
import json
import math
import random
from collections import defaultdict
from itertools import combinations
from pathlib import Path

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

###############################################################################
# Compose datasets
###############################################################################


def _create_annotation_string(*parts: str) -> str:
    """Join non-empty parts with commas."""
    return ", ".join(part for part in parts if part)


# ----------------------------------------------------------
# Compose genewise_phenotype_significants
# ----------------------------------------------------------
def _compose_genewise_phenotype_significants(
    genewise_phenotype_significants: list[dict[str, str | float]],
) -> dict[str, list[dict[str, str | float]]]:
    """Compose genewise_phenotype_significants into gene_records_map for Nodes."""

    gene_records_map = defaultdict(list)
    for record in genewise_phenotype_significants:
        zygosity = record["zygosity"]
        life_stage = record.get("life_stage", "")
        sexual_dimorphism = record.get("sexual_dimorphism", "")
        sexual_dimorphism = "" if sexual_dimorphism == "None" else sexual_dimorphism

        annotation_str = _create_annotation_string(zygosity, life_stage, sexual_dimorphism)
        phenotype_composed = f"{record['mp_term_name']} ({annotation_str})"

        effect_size = record["effect_size"]

        gene_records_map[record["marker_symbol"]].append(
            {
                "mp_term_name": record["mp_term_name"],
                "effect_size": effect_size,
                "phenotype": phenotype_composed,
            }
        )

    return dict(gene_records_map)


# ----------------------------------------------------------
# Compose biological annotations
# ----------------------------------------------------------


def _compose_pair_similarity_annotations(
    pair_similarity_annotations: list[dict[str, dict[str, str] | int]],
) -> dict[tuple[str], dict[str, set[str] | int]]:
    """Compose pair similarity annotations (Edges) into strings."""
    pair_similarity_annotations_composed = {}
    for record in pair_similarity_annotations:
        pair_annotations_composed = set()
        for mp_term_name, annotation in record["phenotype_shared_annotations"].items():
            zygosity = annotation["zygosity"]
            life_stage = annotation.get("life_stage", "")
            sexual_dimorphism = annotation.get("sexual_dimorphism", "")
            sexual_dimorphism = "" if sexual_dimorphism == "None" else sexual_dimorphism

            annotation_str = _create_annotation_string(zygosity, life_stage, sexual_dimorphism)
            pair_annotations_composed.add(f"{mp_term_name} ({annotation_str})")

        gene_pair = (record["gene1_symbol"], record["gene2_symbol"])

        pair_similarity_annotations_composed[gene_pair] = {
            "phenotype_shared_annotations": pair_annotations_composed,
            "phenotype_similarity_score": record["phenotype_similarity_score"],
        }
    return pair_similarity_annotations_composed


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


def _compose_dataset(genewise_phenotype_significants, pair_similarity_annotations, disease_annotations_by_allele):
    gene_records_map = _compose_genewise_phenotype_significants(genewise_phenotype_significants)
    pair_similarity_annotations_composed = _compose_pair_similarity_annotations(pair_similarity_annotations)
    disease_annotations_composed = _compose_disease_annotations_by_allele(disease_annotations_by_allele)
    return gene_records_map, pair_similarity_annotations_composed, disease_annotations_composed


###############################################################################
# Build network JSON
###############################################################################


def _scale_to_1_100(x, min_val, max_val) -> int:
    if max_val == min_val:
        return 100
    return int(1 + (x - min_val) * (99 / (max_val - min_val)))


def _scale_phenotype_similarity_scores(pair_similarity_annotations_filtered):
    min_val = min(v["phenotype_similarity_score"] for v in pair_similarity_annotations_filtered.values())
    max_val = max(v["phenotype_similarity_score"] for v in pair_similarity_annotations_filtered.values())
    for v in pair_similarity_annotations_filtered.values():
        v["phenotype_similarity_score"] = _scale_to_1_100(v["phenotype_similarity_score"], min_val, max_val)
    return pair_similarity_annotations_filtered


def _scale_effect_sizes(gene_records_map_filtered, mp_term_name):
    effect_sizes = []
    for records in gene_records_map_filtered.values():
        for record in records:
            if record["mp_term_name"] == mp_term_name:
                effect_sizes.append(record["effect_size"])

    # For binary effect sizes (0 or 1), set 1 to 100 directly
    if all(es == 1 for es in effect_sizes):
        for records in gene_records_map_filtered.values():
            for record in records:
                if record["mp_term_name"] == mp_term_name:
                    record["effect_size"] = 100
        return gene_records_map_filtered

    effect_sizes_log1p = [math.log1p(es) for es in effect_sizes]
    min_val = min(effect_sizes_log1p)
    max_val = max(effect_sizes_log1p)
    for records in gene_records_map_filtered.values():
        for record in records:
            if record["mp_term_name"] == mp_term_name:
                effect_size_scaled = _scale_to_1_100(math.log1p(record["effect_size"]), min_val, max_val)
                record["effect_size"] = effect_size_scaled
    return gene_records_map_filtered


def _find_optimal_scores(
    sorted_scores,
    related_genes,
    pair_similarity_annotations_composed,
    low_threshold=GENE_COUNT_LOWER_BOUND,
    high_threshold=GENE_COUNT_UPPER_BOUND,
):
    low = 0
    high = len(sorted_scores) - 1
    while low <= high:
        mid = (low + high) // 2

        count_genes = set()
        for gene1, gene2 in combinations(sorted(related_genes), 2):
            gene_pair = tuple(sorted([gene1, gene2]))
            if gene_pair not in pair_similarity_annotations_composed:
                continue
            pair_annotations = pair_similarity_annotations_composed[gene_pair]
            if pair_annotations["phenotype_similarity_score"] >= sorted_scores[mid]:
                count_genes.add(gene1)
                count_genes.add(gene2)

        n = len(count_genes)

        if low_threshold <= n <= high_threshold:
            return sorted_scores[mid]
        elif n < low_threshold:
            low = mid + 1
        else:
            high = mid - 1
    return -1


def _filter_related_genes(
    records: list[dict[str, str | float]],
    related_genes: set[str],
    pair_similarity_annotations_composed: dict[tuple[str], dict[str, set[str] | int]],
    is_gene_network: bool = False,
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
      - NaN effect sizes are treated as 1.
      - For speed, pair stats are computed in a single pass over unique gene pairs.
    """

    # --- Compute maximum values per gene ---
    phenotype_similarity_scores = []
    gene_max_score = defaultdict(float)
    gene_max_shared_phenotype = defaultdict(int)

    for gene1, gene2 in combinations(sorted(related_genes), 2):
        gene_pair = tuple(sorted([gene1, gene2]))
        if gene_pair not in pair_similarity_annotations_composed:
            continue

        pair_annotations = pair_similarity_annotations_composed[gene_pair]
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

    optimal_score = _find_optimal_scores(
        unique_phenotype_similarity_scores,
        related_genes,
        pair_similarity_annotations_composed,
        low_threshold=GENE_COUNT_LOWER_BOUND,
        high_threshold=GENE_COUNT_UPPER_BOUND,
    )
    if optimal_score > -1:
        return {gene for gene, max_score in gene_max_score.items() if max_score >= optimal_score}

    if is_gene_network is False:
        # For gene networks, effect size is only 0 or 1, so skip effect size filtering

        # Compute maximum effect size per gene
        gene_max_effect_sizes = defaultdict(float)
        for record in records:
            gene = record["marker_symbol"]
            if gene in related_genes:
                effect_size = record["effect_size"] if not math.isnan(record["effect_size"]) else 0.0
                gene_max_effect_sizes[gene] = max(gene_max_effect_sizes[gene], effect_size)

        # 2. Filter genes by effect size
        filtered_effect_sizes = {g: s for g, s in gene_max_effect_sizes.items() if g in related_genes}
        gene_max_effect_sizes_sorted = sorted(filtered_effect_sizes.items(), key=lambda x: x[1], reverse=True)

        # If the top MAX_GENE_COUNT entries have different effect sizes, return them
        if len({score for _, score in gene_max_effect_sizes_sorted[:MAX_GENE_COUNT]}) > 1:
            return {gene for gene, _ in gene_max_effect_sizes_sorted[:MAX_GENE_COUNT]}

    # 3. Filter genes by number of shared phenotypes
    filtered_shared_phenotypes = {g: s for g, s in gene_max_shared_phenotype.items() if g in related_genes}
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
    hide_severity: bool = False,
) -> list[dict[str, dict[str, str | list[str] | int]]]:
    nodes_json = []
    gene_records_map_filtered = {gene: gene_records_map[gene] for gene in related_genes}

    # Scale effect sizes to 1-100
    gene_records_map_filtered = _scale_effect_sizes(gene_records_map_filtered, mp_term_name)

    for gene, records in gene_records_map_filtered.items():
        phenotypes: list[str] = [r["phenotype"] for r in records]
        diseases: set[str] = disease_annotations_composed.get(gene, set())
        node_color: int = next((r["effect_size"] for r in records if r["mp_term_name"] == mp_term_name), 1)

        node = {
            "data": {
                "id": gene,
                "label": gene,
                "phenotype": sorted(phenotypes),
                "disease": sorted(diseases) if diseases else "",
                "node_color": node_color,
            }
        }
        if hide_severity:
            node["data"]["hide_severity"] = True
        nodes_json.append(node)

    return nodes_json


def _convert_to_edges_json(
    related_genes: set[str],
    pair_similarity_annotations_composed: dict[tuple[str], dict[str, set[str] | int]],
) -> list[dict[str, dict[str, str | list[str] | float]]]:
    edges_json = []
    pair_similarity_annotations_filtered = {}
    for gene1, gene2 in combinations(sorted(related_genes), 2):
        gene_pairs = tuple(sorted([gene1, gene2]))
        if gene_pairs not in pair_similarity_annotations_composed:
            continue
        pair_similarity_annotations_filtered[gene_pairs] = pair_similarity_annotations_composed[gene_pairs]

    if not pair_similarity_annotations_filtered:
        return []

    # Scale phenotype similarity scores to 1-100
    pair_similarity_annotations_filtered = _scale_phenotype_similarity_scores(pair_similarity_annotations_filtered)

    for pair_genes, pair_annotations in pair_similarity_annotations_filtered.items():
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
    return edges_json


def build_phenotype_network_json(
    genewise_phenotype_significants: list[dict[str, str | float]],
    pair_similarity_annotations: dict[tuple[str], dict[str, dict[str, dict[str, str] | int]]],
    disease_annotations_by_gene: dict[str, dict[str, str]],
    output_dir,
    binary_phenotypes: set[str] | None = None,
    hide_severity: bool = False,
) -> None:
    gene_records_map, pair_similarity_annotations_composed, disease_annotations_composed = _compose_dataset(
        genewise_phenotype_significants, pair_similarity_annotations, disease_annotations_by_gene
    )

    phenotype_records_map: dict[str, list[dict[str, str | float]]] = defaultdict(list)
    for record in genewise_phenotype_significants:
        phenotype_records_map[record["mp_term_name"]].append(record)
    phenotype_records_map = dict(phenotype_records_map)

    gene_lists = set()
    for keys in pair_similarity_annotations_composed.keys():
        for gene in keys:
            gene_lists.add(gene)

    for mp_term_name in tqdm(phenotype_records_map.keys(), total=len(phenotype_records_map)):
        records = phenotype_records_map[mp_term_name]
        related_genes = {r["marker_symbol"] for r in records if r["marker_symbol"] in gene_lists}

        if len(related_genes) < 2:
            continue

        if len(related_genes) > MAX_GENE_COUNT:
            related_genes = _filter_related_genes(records, related_genes, pair_similarity_annotations_composed)

        is_binary = False
        if binary_phenotypes:
            is_binary = mp_term_name in binary_phenotypes

        nodes_json = _convert_to_nodes_json(
            related_genes,
            mp_term_name,
            gene_records_map,
            disease_annotations_composed,
            hide_severity=hide_severity or is_binary,
        )
        edges_json = _convert_to_edges_json(related_genes, pair_similarity_annotations_composed)

        if not edges_json:
            continue

        # Sort nodes for stability
        nodes_json = sorted(nodes_json, key=lambda n: n["data"]["id"])
        edges_json = sorted(edges_json, key=lambda e: (e["data"]["source"], e["data"]["target"]))

        network_json = nodes_json + edges_json

        mp_term_name_underscore = mp_term_name.replace(" ", "_").replace("/", "_")
        output_json = Path(output_dir / f"{mp_term_name_underscore}.json.gz")
        with gzip.open(output_json, "wt", encoding="utf-8") as f:
            json.dump(network_json, f, indent=4)


###############################################################################
# build_gene_network_json
###############################################################################


def _build_node_info(
    gene: str,
    gene_records_map: dict[str, list[dict[str, str | float]]],
    disease_annotations_composed: dict[str, set[str]],
    target_gene: str,
    hide_severity: bool = False,
) -> dict[str, dict[str, str | list[str] | float]]:
    phenotypes: list[str] = [r["phenotype"] for r in gene_records_map.get(gene, [])]
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
    if hide_severity:
        node["data"]["hide_severity"] = True
    return node


def build_gene_network_json(
    genewise_phenotype_significants: list[dict[str, str | float]],
    pair_similarity_annotations: dict[tuple[str], dict[str, dict[str, str] | int]],
    disease_annotations_by_gene: dict[str, dict[str, str]],
    output_dir,
    hide_severity: bool = True,
) -> None:
    gene_records_map, pair_similarity_annotations_composed, disease_annotations_composed = _compose_dataset(
        genewise_phenotype_significants, pair_similarity_annotations, disease_annotations_by_gene
    )

    gene_lists = set()
    for keys in pair_similarity_annotations_composed.keys():
        for gene in keys:
            gene_lists.add(gene)

    for target_gene in tqdm(gene_lists, total=len(gene_lists)):
        related_pairs_with_target_gene = []
        for keys in pair_similarity_annotations_composed.keys():
            if target_gene not in keys:
                continue
            related_pairs_with_target_gene.append(keys)

        related_genes = set()
        for genes in related_pairs_with_target_gene:
            gene1, gene2 = genes
            related_genes.add(gene1)
            related_genes.add(gene2)

        # Skip if less than 2 related genes
        if len(related_genes) < 2:
            continue

        related_pairs = []
        for gene1, gene2 in combinations(related_genes, 2):
            gene_pair = tuple(sorted([gene1, gene2]))
            if gene_pair not in pair_similarity_annotations_composed:
                continue
            related_pairs.append(gene_pair)

        # Filter genes if more than MAX_GENE_COUNT
        if len(related_genes) > MAX_GENE_COUNT:
            related_genes_filtered = _filter_related_genes(
                genewise_phenotype_significants, related_genes, pair_similarity_annotations_composed
            )
            related_genes_filtered.add(target_gene)
            related_pairs = [pairs for pairs in related_pairs if all(gene in related_genes_filtered for gene in pairs)]

        # ---------------------------------------
        # Nodes
        # ---------------------------------------
        nodes_json = []
        visited_genes = set()
        for pair in related_pairs:
            gene1, gene2 = pair
            if gene1 not in visited_genes:
                visited_genes.add(gene1)
                node_json = _build_node_info(
                    gene1, gene_records_map, disease_annotations_composed, target_gene, hide_severity=hide_severity
                )
                nodes_json.append(node_json)
            if gene2 not in visited_genes:
                visited_genes.add(gene2)
                node_json = _build_node_info(
                    gene2, gene_records_map, disease_annotations_composed, target_gene, hide_severity=hide_severity
                )
                nodes_json.append(node_json)

        # ---------------------------------------
        # Edges
        # ---------------------------------------
        pair_similarity_annotations_filtered = {
            pair: pair_similarity_annotations_composed[pair] for pair in related_pairs
        }

        if not pair_similarity_annotations_filtered:
            return []

        # Scale phenotype similarity scores to 1-100
        pair_similarity_annotations_scaled = _scale_phenotype_similarity_scores(pair_similarity_annotations_filtered)

        edges_json = []
        for pair in related_pairs:
            gene1, gene2 = sorted(pair)
            phenotypes = pair_similarity_annotations_scaled[pair]["phenotype_shared_annotations"]
            phenodigm_score = pair_similarity_annotations_scaled[pair]["phenotype_similarity_score"]
            edges_json.append(
                {
                    "data": {
                        "source": gene1,
                        "target": gene2,
                        "phenotype": sorted(phenotypes),
                        "edge_size": phenodigm_score,
                    }
                }
            )

        # Sort nodes for stability
        nodes_json = sorted(nodes_json, key=lambda n: n["data"]["id"])
        edges_json = sorted(edges_json, key=lambda e: (e["data"]["source"], e["data"]["target"]))

        network_json = nodes_json + edges_json

        output_json = Path(output_dir / f"{target_gene}.json.gz")
        with gzip.open(output_json, "wt", encoding="utf-8") as f:
            json.dump(network_json, f, indent=4)
