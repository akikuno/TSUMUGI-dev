from __future__ import annotations

import math
from collections import defaultdict
from itertools import combinations, combinations_with_replacement
from pathlib import Path

import numpy as np
from tqdm import tqdm


def parse_obo_file(file_path: str | Path) -> dict[str, dict]:
    """Parse ontology file (OBO format) and extract term information.
    Returns dict with keys: id, name, is_a (parent terms), is_obsolete
    """
    ontology_terms = {}
    current_term_data = None
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line == "[Term]":
                current_term_data = {}
                continue

            if line.startswith("[") and line.endswith("]") and line != "[Term]":
                current_term_data = None
                continue

            if current_term_data is None:
                continue

            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                if key == "id":
                    current_term_data["id"] = value
                elif key == "name":
                    current_term_data["name"] = value
                elif key == "is_a":
                    if "is_a" not in current_term_data:
                        current_term_data["is_a"] = []
                    parent_id = value.split("!")[0].strip()
                    current_term_data["is_a"].append(parent_id)
                elif key == "is_obsolete":
                    current_term_data["is_obsolete"] = value.lower() == "true"

            if line == "" and current_term_data and "id" in current_term_data:
                if not current_term_data.get("is_obsolete", False):
                    ontology_terms[current_term_data["id"]] = current_term_data
                current_term_data = None

    return ontology_terms


def build_term_hierarchy(
    ontology_terms: dict[str, dict],
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Build parent-child hierarchy relationships from ontology terms."""
    parent_term_map = defaultdict(list)  # term_id -> [parent_ids]
    child_term_map = defaultdict(list)  # term_id -> [child_ids]

    for term_id, term_data in ontology_terms.items():
        if "is_a" in term_data:
            for parent_id in term_data["is_a"]:
                parent_term_map[term_id].append(parent_id)
                child_term_map[parent_id].append(term_id)

    return dict(parent_term_map), dict(child_term_map)


def find_all_ancestor_terms(term_id: str, parent_term_map: dict[str, list[str]]) -> set[str]:
    """Find all ancestor terms for a given term."""
    ancestor_terms = set()
    terms_to_process = [term_id]

    while terms_to_process:
        current_term = terms_to_process.pop(0)
        if current_term in parent_term_map:
            for parent_term in parent_term_map[current_term]:
                if parent_term not in ancestor_terms:
                    ancestor_terms.add(parent_term)
                    terms_to_process.append(parent_term)

    return ancestor_terms


def find_common_ancestors(term1_id: str, term2_id: str, parent_term_map: dict[str, list[str]]) -> set[str]:
    """Find common ancestors of two terms."""
    term1_ancestors = find_all_ancestor_terms(term1_id, parent_term_map)
    term1_ancestors.add(term1_id)  # Include the term itself

    term2_ancestors = find_all_ancestor_terms(term2_id, parent_term_map)
    term2_ancestors.add(term2_id)  # Include the term itself

    return term1_ancestors.intersection(term2_ancestors)


def find_all_descendant_terms(term_id: str, child_term_map: dict[str, list[str]]) -> set[str]:
    """Find all descendant terms for a given term."""
    descendant_terms = set()
    terms_to_process = [term_id]

    while terms_to_process:
        current_term = terms_to_process.pop(0)
        if current_term in child_term_map:
            for child_term in child_term_map[current_term]:
                if child_term not in descendant_terms:
                    descendant_terms.add(child_term)
                    terms_to_process.append(child_term)

    return descendant_terms


def calculate_information_content(term_id: str, child_term_map: dict[str, list[str]], total_term_count: int) -> float:
    """Calculate information content for a term based on its descendants."""
    descendant_terms = find_all_descendant_terms(term_id, child_term_map)
    # Include the term itself in the count
    term_count = len(descendant_terms) + 1
    probability = term_count / total_term_count
    return -math.log(probability)


def calculate_resnik_similarity(
    term1_id: str,
    term2_id: str,
    parent_term_map: dict[str, list[str]],
    child_term_map: dict[str, list[str]],
    total_term_count: int,
) -> float:
    """Calculate Resnik similarity between two terms."""
    if term1_id == term2_id:
        return calculate_information_content(term1_id, child_term_map, total_term_count)

    common_ancestors = find_common_ancestors(term1_id, term2_id, parent_term_map)

    if not common_ancestors:
        return 0.0

    # Find the most informative common ancestor (MICA)
    max_information_content = 0.0
    for ancestor_term in common_ancestors:
        information_content = calculate_information_content(ancestor_term, child_term_map, total_term_count)
        max_information_content = max(max_information_content, information_content)

    return max_information_content


def calculate_all_pairwise_similarities(
    ontology_file_path: str | Path,
    all_term_ids: set[str],
) -> dict[frozenset[str], float]:
    """Calculate pairwise Resnik similarities for a list of terms."""
    ontology_terms = parse_obo_file(ontology_file_path)
    total_term_count = len(ontology_terms)
    parent_term_map, child_term_map = build_term_hierarchy(ontology_terms)

    term_pair_similarity_map = {}
    for term1_id, term2_id in tqdm(
        combinations_with_replacement(all_term_ids, 2), total=(len(all_term_ids) * (len(all_term_ids) - 1)) // 2
    ):
        term_pair_key = frozenset([term1_id, term2_id])
        term_pair_similarity_map[term_pair_key] = calculate_resnik_similarity(
            term1_id, term2_id, parent_term_map, child_term_map, total_term_count
        )

    return term_pair_similarity_map


###########################################################
# Phenodigm scaling
###########################################################


def adjust_similarity_by_metadata(
    similarity_score: float,
    gene1_zygosity: str,
    gene2_zygosity: str,
    gene1_life_stage: str,
    gene2_life_stage: str,
    gene1_sexual_dimorphism: str,
    gene2_sexual_dimorphism: str,
) -> float:
    """Adjust similarity score based on gene metadata (zygosity, life stage, sexual dimorphism)."""
    matching_metadata_count = sum(
        [
            gene1_zygosity == gene2_zygosity,
            gene1_life_stage == gene2_life_stage,
            gene1_sexual_dimorphism == gene2_sexual_dimorphism,
        ]
    )
    if matching_metadata_count == 3:
        adjustment_weight = 1.0
    elif matching_metadata_count == 2:
        adjustment_weight = 0.75
    elif matching_metadata_count == 1:
        adjustment_weight = 0.5
    else:
        adjustment_weight = 0.25
    return similarity_score * adjustment_weight


def calculate_weighted_similarity_matrix(
    gene1_records: list[dict[str, str | float]],
    gene2_records: list[dict[str, str | float]],
    term_pair_similarity_map: dict[frozenset[str], float],
) -> np.ndarray:
    """Calculate weighted similarity matrix between two genes based on their phenotype records."""
    weighted_similarity_matrix = []
    for gene1_record in gene1_records:
        similarity_row = []
        for gene2_record in gene2_records:
            gene1_term_id = gene1_record["mp_term_id"]
            gene2_term_id = gene2_record["mp_term_id"]
            similarity = term_pair_similarity_map.get(frozenset([gene1_term_id, gene2_term_id]), 0.0)

            # Adjust score by zygosity, life stage, sexual dimorphism
            gene1_zygosity = gene1_record["zygosity"]
            gene2_zygosity = gene2_record["zygosity"]
            gene1_life_stage = gene1_record["life_stage"]
            gene2_life_stage = gene2_record["life_stage"]
            gene1_sexual_dimorphism = gene1_record.get("sexual_dimorphism", "")
            gene2_sexual_dimorphism = gene2_record.get("sexual_dimorphism", "")

            adjusted_similarity = adjust_similarity_by_metadata(
                similarity,
                gene1_zygosity,
                gene2_zygosity,
                gene1_life_stage,
                gene2_life_stage,
                gene1_sexual_dimorphism,
                gene2_sexual_dimorphism,
            )
            similarity_row.append(adjusted_similarity)

        weighted_similarity_matrix.append(similarity_row)

    return np.array(weighted_similarity_matrix)


def apply_phenodigm_scaling(
    weighted_similarity_matrix: np.ndarray,
    gene1_mp_term_ids: set[str],
    gene2_mp_term_ids: set[str],
    term_pair_similarity_map: dict[frozenset[str], float],
) -> dict[str, float]:
    """Apply Phenodigm scaling method to similarity scores."""

    gene1_information_content_scores = [term_pair_similarity_map[frozenset([term_id])] for term_id in gene1_mp_term_ids]
    gene2_information_content_scores = [term_pair_similarity_map[frozenset([term_id])] for term_id in gene2_mp_term_ids]

    max_gene1_information_content = max(gene1_information_content_scores) if gene1_information_content_scores else 0.0
    max_gene2_information_content = max(gene2_information_content_scores) if gene2_information_content_scores else 0.0

    row_max_similarities = weighted_similarity_matrix.max(axis=1)
    column_max_similarities = weighted_similarity_matrix.max(axis=0)

    max_score_actual = np.max([np.max(row_max_similarities), np.max(column_max_similarities)])
    average_score_actual = (
        np.mean(np.concatenate([row_max_similarities, column_max_similarities]))
        if (len(row_max_similarities) > 0 or len(column_max_similarities) > 0)
        else 0.0
    )

    max_score_theoretical = max(max_gene1_information_content, max_gene2_information_content)

    average_score_theoretical = float(
        np.mean(gene1_information_content_scores + gene2_information_content_scores)
        if (gene1_information_content_scores or gene2_information_content_scores)
        else 0.0
    )

    normalized_max_score = max_score_actual / max_score_theoretical if max_score_theoretical > 0 else 0.0
    normalized_average_score = (
        average_score_actual / average_score_theoretical if average_score_theoretical > 0 else 0.0
    )

    phenodigm_score = 100 * (normalized_max_score + normalized_average_score) / 2

    return float(phenodigm_score)


def calculate_phenodigm_score(
    records_significants: list[dict[str, str | float]],
    term_pair_similarity_map: dict[frozenset[str], float],
) -> dict[frozenset, float]:
    """Wrapper function to calculate Phenodigm score between two genes."""
    gene_records_map: dict[str, list[dict[str, str | float]]] = defaultdict(list)
    for record in records_significants:
        gene_records_map[record["marker_symbol"]].append(record)

    all_gene_symbols = gene_records_map.keys()
    phenodigm_scores = {}
    for gene1_symbol, gene2_symbol in tqdm(
        combinations(all_gene_symbols, 2), total=(len(all_gene_symbols) * (len(all_gene_symbols) - 1)) // 2
    ):
        gene1_records = gene_records_map[gene1_symbol]
        gene2_records = gene_records_map[gene2_symbol]
        gene1_mp_term_ids = {record["mp_term_id"] for record in gene1_records}
        gene2_mp_term_ids = {record["mp_term_id"] for record in gene2_records}

        weighted_similarity_matrix = calculate_weighted_similarity_matrix(
            gene1_records, gene2_records, term_pair_similarity_map
        )

        phenodigm_scores[frozenset([gene1_symbol, gene2_symbol])] = apply_phenodigm_scaling(
            weighted_similarity_matrix, gene1_mp_term_ids, gene2_mp_term_ids, term_pair_similarity_map
        )

    return phenodigm_scores


def calculate_num_shared_phenotypes(records_significants: list[dict[str, str | float]]) -> dict[frozenset, float]:
    """Calculate the number of shared phenotypes between two genes."""
    gene_phenotypes_map = defaultdict(set)
    for record in records_significants:
        gene_phenotypes_map[record["marker_symbol"]].add(
            frozenset(
                [record["mp_term_id"], record["zygosity"], record["life_stage"], record.get("sexual_dimorphism", "")]
            )
        )
    num_shared_phenotypes = {}
    for gene1, gene2 in tqdm(combinations(gene_phenotypes_map.keys(), 2), total=math.comb(len(gene_phenotypes_map), 2)):
        phenotypes_gene1 = gene_phenotypes_map[gene1]
        phenotypes_gene2 = gene_phenotypes_map[gene2]

        num_shared_phenotypes[frozenset([gene1, gene2])] = len(phenotypes_gene1.intersection(phenotypes_gene2))

    return num_shared_phenotypes


def calculate_jaccard_indices(records_significants: list[dict[str, str | float]]) -> dict[frozenset, float]:
    """Calculate the number of shared phenotypes between two genes."""
    gene_phenotypes_map = defaultdict(set)
    for record in records_significants:
        gene_phenotypes_map[record["marker_symbol"]].add(
            frozenset(
                [record["mp_term_id"], record["zygosity"], record["life_stage"], record.get("sexual_dimorphism", "")]
            )
        )

    jaccard_indices = {}
    for gene1, gene2 in tqdm(combinations(gene_phenotypes_map.keys(), 2), total=math.comb(len(gene_phenotypes_map), 2)):
        phenotypes_gene1 = gene_phenotypes_map[gene1]
        phenotypes_gene2 = gene_phenotypes_map[gene2]

        intersection = phenotypes_gene1.intersection(phenotypes_gene2)
        union = phenotypes_gene1.union(phenotypes_gene2)
        jaccard_indices[frozenset([gene1, gene2])] = len(intersection) / len(union) if union else 0

    return jaccard_indices
