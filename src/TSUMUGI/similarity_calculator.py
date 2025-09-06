from __future__ import annotations

import math
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np
from tqdm import tqdm


def parse_obo_file(file_path: str | Path) -> dict[str, dict]:
    """Parse OBO file and extract term information.
    {id, name, is_a (parent terms), is_obsolete}
    """
    terms = {}
    current_term = None
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line == "[Term]":
                current_term = {}
                continue

            if line.startswith("[") and line.endswith("]") and line != "[Term]":
                current_term = None
                continue

            if current_term is None:
                continue

            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                if key == "id":
                    current_term["id"] = value
                elif key == "name":
                    current_term["name"] = value
                elif key == "is_a":
                    if "is_a" not in current_term:
                        current_term["is_a"] = []
                    parent_id = value.split("!")[0].strip()
                    current_term["is_a"].append(parent_id)
                elif key == "is_obsolete":
                    current_term["is_obsolete"] = value.lower() == "true"

            if line == "" and current_term and "id" in current_term:
                if not current_term.get("is_obsolete", False):
                    terms[current_term["id"]] = current_term
                current_term = None

    return terms


def build_parent_child_relations(
    ontology_terms: dict[str, dict],
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Build parent-child relationships from terms."""
    parents = defaultdict(list)  # term_id -> [parent_ids]
    children = defaultdict(list)  # term_id -> [child_ids]

    for term_id, term_data in ontology_terms.items():
        if "is_a" in term_data:
            for parent_id in term_data["is_a"]:
                parents[term_id].append(parent_id)
                children[parent_id].append(term_id)

    return dict(parents), dict(children)


def get_all_ancestors(term_id: str, parents: dict[str, list[str]]) -> set[str]:
    """Get all ancestor terms for a given term."""
    ancestors = set()
    queue = [term_id]

    while queue:
        current = queue.pop(0)
        if current in parents:
            for parent in parents[current]:
                if parent not in ancestors:
                    ancestors.add(parent)
                    queue.append(parent)

    return ancestors


def find_common_ancestors(term1_id: str, term2_id: str, parents: dict[str, list[str]]) -> set[str]:
    """Find common ancestors of two terms."""
    ancestors1 = get_all_ancestors(term1_id, parents)
    ancestors1.add(term1_id)  # Include the term itself

    ancestors2 = get_all_ancestors(term2_id, parents)
    ancestors2.add(term2_id)  # Include the term itself

    return ancestors1.intersection(ancestors2)


def get_all_descendants(term_id: str, children: dict[str, list[str]]) -> set[str]:
    """Get all descendant terms for a given term."""
    descendants = set()
    queue = [term_id]

    while queue:
        current = queue.pop(0)
        if current in children:
            for child in children[current]:
                if child not in descendants:
                    descendants.add(child)
                    queue.append(child)

    return descendants


def calculate_information_content(term_id: str, children: dict[str, list[str]], total_terms: int) -> float:
    """Calculate information content for a term based on its descendants."""
    descendants = get_all_descendants(term_id, children)
    # Include the term itself in the count
    term_count = len(descendants) + 1
    probability = term_count / total_terms
    return -math.log(probability)


def resnik_similarity(
    term1_id: str,
    term2_id: str,
    parents: dict[str, list[str]],
    children: dict[str, list[str]],
    total_terms: int,
) -> float:
    """Calculate Resnik similarity between two terms."""
    if term1_id == term2_id:
        return calculate_information_content(term1_id, children, total_terms)

    common_ancestors = find_common_ancestors(term1_id, term2_id, parents)

    if not common_ancestors:
        return 0.0

    # Find the most informative common ancestor (MICA)
    max_ic = 0.0
    for ancestor in common_ancestors:
        ic = calculate_information_content(ancestor, children, total_terms)
        max_ic = max(max_ic, ic)

    return max_ic


def calculate_all_pairwise_similarities(
    path_obo: str | Path,
    all_mp_term_ids: set[str],
) -> dict[frozenset[str], float]:
    """Calculate pairwise Resnik similarities for a list of terms."""
    mp_terms = parse_obo_file(path_obo)
    total_mp_terms = len(mp_terms)
    parents, children = build_parent_child_relations(mp_terms)

    similarity_of_mp_term_id_pairs = {}
    for term1_id, term2_id in tqdm(
        combinations(all_mp_term_ids, 2), total=(len(all_mp_term_ids) * (len(all_mp_term_ids) - 1)) // 2
    ):
        key = frozenset([term1_id, term2_id])
        similarity_of_mp_term_id_pairs[key] = resnik_similarity(term1_id, term2_id, parents, children, total_mp_terms)

    return similarity_of_mp_term_id_pairs


###########################################################
# Phenodigm scaling
###########################################################


def calculate_ic_by_term(
    term_ids: set[str],
    children: dict[str, list[str]],
) -> dict[str, float]:
    """Calculate information content for each term ID."""

    total_terms = len(term_ids)
    ic_by_term = {}
    for term_id in term_ids:
        ic_by_term[term_id] = calculate_information_content(term_id, children, total_terms)

    return ic_by_term


def get_similarity_of_terms(
    term_id_1: str, term_id_2: str, ic_by_term: dict[str, float], pairs_sim: dict[frozenset[str], float]
) -> float:
    """Get similarity score between two terms based on their IC values."""
    if term_id_1 == term_id_2:
        return ic_by_term.get(term_id_1, 0.0)
    else:
        return pairs_sim.get(frozenset([term_id_1, term_id_2]), 0.0)


def adjust_score_by_annotations(
    sim: float,
    gene1_zygosity: str,
    gene2_zygosity: str,
    gene1_life_stage: str,
    gene2_life_stage: str,
    gene1_sexual_dimorphism: str,
    gene2_sexual_dimorphism: str,
) -> float:
    """Adjust similarity score based on gene annotations."""
    matches = sum(
        [
            gene1_zygosity == gene2_zygosity,
            gene1_life_stage == gene2_life_stage,
            gene1_sexual_dimorphism == gene2_sexual_dimorphism,
        ]
    )
    if matches == 3:
        weight = 1.0
    elif matches == 2:
        weight = 0.75
    elif matches == 1:
        weight = 0.5
    else:
        weight = 0.25
    return sim * weight


def calculate_weighted_similarity_matrix(
    gene1_records: list[dict[str, str | float]],
    gene2_records: list[dict[str, str | float]],
    ic_by_term: dict[str, float],
    similarity_of_mp_term_id_pairs: dict[frozenset[str], float],
) -> np.ndarray:
    """Calculate weighted similarity between two genes based on their phenotype records."""
    weighted_similarity_matrix = []
    for gene1_record in gene1_records:
        row = []
        for gene2_record in gene2_records:
            gene1_id = gene1_record["mp_term_id"]
            gene2_id = gene2_record["mp_term_id"]
            sim = get_similarity_of_terms(gene1_id, gene2_id, ic_by_term, similarity_of_mp_term_id_pairs)

            # Adjust score by zygosity, life stage, sexual dimorphism
            gene1_zygosity = gene1_record["zygosity"]
            gene2_zygosity = gene2_record["zygosity"]
            gene1_life_stage = gene1_record["life_stage"]
            gene2_life_stage = gene2_record["life_stage"]
            gene1_sexual_dimorphism = gene1_record.get("sexual_dimorphism", "")
            gene2_sexual_dimorphism = gene2_record.get("sexual_dimorphism", "")

            adjusted_sim = adjust_score_by_annotations(
                sim,
                gene1_zygosity,
                gene2_zygosity,
                gene1_life_stage,
                gene2_life_stage,
                gene1_sexual_dimorphism,
                gene2_sexual_dimorphism,
            )
            row.append(adjusted_sim)

        weighted_similarity_matrix.append(row)

    return np.array(weighted_similarity_matrix)


def scale_sim_by_phenodigm(
    weighted_similarity_matrix: np.ndarray,
    term1_ids: set[str],
    term2_ids: set[str],
    ic_by_term: dict[str, float],
) -> tuple[float, float, float]:
    """Scale similarity scores based on Phenodigm method."""

    rows_max = weighted_similarity_matrix.max(axis=1)
    cols_max = weighted_similarity_matrix.max(axis=0)

    max_score_real_model = np.max([np.max(rows_max), np.max(cols_max)])
    ave_score_real_model = (rows_max.sum() + cols_max.sum()) / (len(rows_max) + len(cols_max))

    term1_ic_scores = [ic_by_term[term1_id] for term1_id in term1_ids]
    term2_ic_scores = [ic_by_term[term2_id] for term2_id in term2_ids]

    term1_ic_scores_max = max(term1_ic_scores) if term1_ic_scores else 0.0
    term2_ic_scores_max = max(term2_ic_scores) if term2_ic_scores else 0.0

    max_score_best_model = max(term1_ic_scores_max, term2_ic_scores_max)
    ave_score_best_model_term1 = sum(term1_ic_scores) / len(term1_ic_scores) if term1_ic_scores else 0.0
    ave_score_best_model_term2 = sum(term2_ic_scores) / len(term2_ic_scores) if term2_ic_scores else 0.0

    max_score = max_score_real_model / max_score_best_model
    ave_score_term1 = ave_score_real_model / ave_score_best_model_term1
    ave_score_term2 = ave_score_real_model / ave_score_best_model_term2

    score_term1 = 100 * (max_score + ave_score_term1) / 2
    score_term2 = 100 * (max_score + ave_score_term2) / 2
    score_total = (score_term1 + score_term2) / 2

    return score_total, score_term1, score_term2
