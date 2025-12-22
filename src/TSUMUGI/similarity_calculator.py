from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterator
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations, combinations_with_replacement

import numpy as np
from tqdm import tqdm

from TSUMUGI.ontology_handler import (
    build_term_hierarchy,
    find_all_descendant_terms,
    find_common_ancestors,
)

###########################################################
# Pairwise term similarity (with multiprocessing)
###########################################################

_worker_parent_term_map: dict[str, set[str]] | None = None
_worker_child_term_map: dict[str, set[str]] | None = None
_worker_ic_map: dict[str, float] | None = None


def _init_worker(
    parent_term_map: dict[str, set[str]], child_term_map: dict[str, set[str]], ic_map: dict[str, float]
) -> None:
    """Initializer for worker processes to avoid repeatedly pickling large objects."""
    global _worker_parent_term_map, _worker_child_term_map, _worker_ic_map
    _worker_parent_term_map = parent_term_map
    _worker_child_term_map = child_term_map
    _worker_ic_map = ic_map


def _precompute_term_ic_map(ontology_terms: dict[str, dict], child_term_map: dict[str, set[str]]) -> dict[str, float]:
    """Precompute information content (IC) for all ontology terms."""
    total_term_count = len(ontology_terms)
    term_ic_map: dict[str, float] = {}

    for term_id in ontology_terms:
        descendants = find_all_descendant_terms(term_id, child_term_map)
        term_count = len(descendants) + 1
        probability = term_count / total_term_count
        term_ic_map[term_id] = -math.log(probability)

    return term_ic_map


def _compute_pair_mica_and_resnik(
    term1_id: str, term2_id: str, parent_term_map: dict[str, set[str]], ic_map: dict[str, float]
) -> tuple[str | None, float]:
    """Compute MSCA (by IC) and Resnik similarity using precomputed IC."""
    if term1_id == term2_id:
        return term1_id, ic_map.get(term1_id, 0.0)

    common_ancestors = find_common_ancestors(term1_id, term2_id, parent_term_map)
    if not common_ancestors:
        return None, 0.0

    msca = max(common_ancestors, key=lambda t: ic_map.get(t, 0.0))
    similarity = ic_map.get(msca, 0.0)
    return msca, similarity


def _compute_pair_worker(term_pair: tuple[str, str]) -> tuple[tuple[str], dict[str | None, float]]:
    """Worker-side computation using globals set by _init_worker."""
    term1_id, term2_id = term_pair

    parent_term_map = _worker_parent_term_map
    ic_map = _worker_ic_map

    if parent_term_map is None or ic_map is None:
        raise RuntimeError("Worker maps are not initialized.")

    if term1_id == term2_id:
        msca = term1_id
        sim = ic_map.get(term1_id, 0.0)
    else:
        common_ancestors = find_common_ancestors(term1_id, term2_id, parent_term_map)
        if not common_ancestors:
            return frozenset((term1_id, term2_id)), {None: 0.0}
        msca = max(common_ancestors, key=lambda t: ic_map.get(t, 0.0))
        sim = ic_map.get(msca, 0.0)

    term_pairs = tuple(sorted((term1_id, term2_id)))
    return term_pairs, {msca: sim}


def _compute_pair_singleprocess(
    term1_id: str, term2_id: str, parent_term_map: dict[str, set[str]], ic_map: dict[str, float]
) -> tuple[tuple[str], dict[str | None, float]]:
    """Single-process version (used when threads=1)."""
    msca, sim = _compute_pair_mica_and_resnik(term1_id, term2_id, parent_term_map, ic_map)
    term_pairs = tuple(sorted((term1_id, term2_id)))
    return term_pairs, {msca: sim}


def calculate_all_pairwise_similarities(
    ontology_terms: dict[str, dict],
    all_term_ids: set[str],
    threads: int | None = None,
) -> tuple[dict[tuple[str], dict[str | None, float]], dict[str, float]]:
    """Calculate pairwise Resnik similarities for all term IDs."""
    parent_term_map, child_term_map = build_term_hierarchy(ontology_terms)
    term_ic_map = _precompute_term_ic_map(ontology_terms, child_term_map)

    term_list = sorted(all_term_ids)
    total_pairs = len(term_list) * (len(term_list) + 1) // 2

    term_pair_similarity_map: dict[tuple[str], dict[str | None, float]] = {}

    if threads == 1:
        for term1_id, term2_id in tqdm(combinations_with_replacement(term_list, 2), total=total_pairs):
            term_pairs, ancester_ic = _compute_pair_singleprocess(term1_id, term2_id, parent_term_map, term_ic_map)
            term_pair_similarity_map[term_pairs] = ancester_ic
        return term_pair_similarity_map

    with ProcessPoolExecutor(
        max_workers=threads,
        initializer=_init_worker,
        initargs=(parent_term_map, child_term_map, term_ic_map),
    ) as executor:
        for term_pairs, ancester_ic in tqdm(
            executor.map(_compute_pair_worker, combinations_with_replacement(term_list, 2)), total=total_pairs
        ):
            term_pair_similarity_map[term_pairs] = ancester_ic

    return term_pair_similarity_map, term_ic_map


###########################################################
# Phenotype ancestor annotation
###########################################################


def _delete_parent_terms_from_ancestors(
    candidate_ancestors: dict[str, dict[str, str]],
    child_term_map: dict[str, set[str]],
) -> dict[str, dict[str, str]]:
    """
    Remove parent terms from the common ancestors.
    Keep only the most specific terms among candidates with identical metadata.
    Uses descendant traversal to avoid O(n^2) pair comparisons.
    """
    to_delete: set[str] = set()

    for term_id, term_meta in candidate_ancestors.items():
        if term_id in to_delete:
            continue

        stack = list(child_term_map.get(term_id, ()))
        while stack:
            child_id = stack.pop()
            child_meta = candidate_ancestors.get(child_id)
            if child_meta is not None and child_meta == term_meta:
                to_delete.add(term_id)
                break
            stack.extend(child_term_map.get(child_id, ()))

    for t in to_delete:
        candidate_ancestors.pop(t, None)

    return candidate_ancestors


def _get_terms_with_low_ic(
    ontology_terms: dict[str, dict[str, str]],
    child_term_map: dict[str, set[str]],
    ic_threshold,
) -> set[str]:
    """Return terms whose IC is below the given percentile threshold."""
    total_term_count = len(ontology_terms)
    map_term_to_ic: dict[str, float] = {}
    descendant_cache: dict[str, set[str]] = {}

    def _get_descendants(term_id: str) -> set[str]:
        if term_id in descendant_cache:
            return descendant_cache[term_id]
        descendants = find_all_descendant_terms(term_id, child_term_map)
        descendant_cache[term_id] = descendants
        return descendants

    for term_id in ontology_terms.keys():
        descendant_terms = _get_descendants(term_id)
        term_count = len(descendant_terms) + 1
        probability = term_count / total_term_count
        ic = -math.log(probability)
        map_term_to_ic[term_id] = ic

    ic_values = list(map_term_to_ic.values())
    ic_min_values = np.percentile(ic_values, ic_threshold)
    return {term for term, ic in map_term_to_ic.items() if ic < ic_min_values}


# =========================================================
# Single-process implementation (core per-pair logic)
# =========================================================


def _annotate_ancestors(
    gene1_symbol: str,
    gene2_symbol: str,
    gene_metadata_map: dict[str, dict[tuple[str, str, str], list[str]]],
    meta_dict_cache: dict[tuple[str, str, str], dict[str, str]],
    term_pair_similarity_map: dict[tuple[str, str], dict[str | None, float]],
    child_term_map: dict[str, set[str]],
    terms_with_low_ic: set[str],
) -> tuple[tuple[str], dict[str, dict[str, str]]]:
    """Annotate phenotype ancestors for a single gene pair (single-process version)."""
    gene1_meta_map = gene_metadata_map[gene1_symbol]
    gene2_meta_map = gene_metadata_map[gene2_symbol]

    candidate_ancestors: dict[str, dict[str, str]] = {}
    added_keys: set[tuple[str, tuple[str, str, str]]] = set()

    shared_meta_signatures = set(gene1_meta_map.keys()) & set(gene2_meta_map.keys())

    for meta_signature in shared_meta_signatures:
        gene1_terms = gene1_meta_map[meta_signature]
        gene2_terms = gene2_meta_map[meta_signature]
        meta_dict = meta_dict_cache[meta_signature]

        for gene1_mp_term_id in gene1_terms:
            for gene2_mp_term_id in gene2_terms:
                pair_key = tuple(sorted([gene1_mp_term_id, gene2_mp_term_id]))
                mapping = term_pair_similarity_map.get(pair_key)
                if not mapping:
                    continue

                common_ancestor, similarity = next(iter(mapping.items()))

                if not common_ancestor or similarity == 0.0:
                    continue

                if common_ancestor in terms_with_low_ic:
                    continue

                current_key = (common_ancestor, meta_signature)

                if current_key in added_keys:
                    continue

                candidate_ancestors[common_ancestor] = meta_dict
                added_keys.add(current_key)

    # Remove parent terms from candidate ancestors
    candidate_ancestors = _delete_parent_terms_from_ancestors(candidate_ancestors, child_term_map)

    gene_pair = tuple(sorted([gene1_symbol, gene2_symbol]))
    return gene_pair, (dict(candidate_ancestors) if candidate_ancestors else {})


def _build_gene_metadata_maps(
    gene_records_map: dict[str, list[dict[str, str | float]]],
    annotations: set[str],
) -> tuple[dict[str, dict[tuple[str, str, str], list[str]]], dict[tuple[str, str, str], dict[str, str]]]:
    """Group gene records by metadata signature for faster matching."""
    gene_metadata_map: dict[str, dict[tuple[str, str, str], list[str]]] = {}
    meta_dict_cache: dict[tuple[str, str, str], dict[str, str]] = {}

    for gene_symbol, records in gene_records_map.items():
        per_gene_map: dict[tuple[str, str, str], list[str]] = defaultdict(list)
        for record in records:
            meta_signature = (
                record["zygosity"],
                record["life_stage"],
                record.get("sexual_dimorphism", "None"),
            )
            per_gene_map[meta_signature].append(record["mp_term_id"])
            if meta_signature not in meta_dict_cache:
                meta_dict_cache[meta_signature] = {k: v for k, v in record.items() if k in annotations}
        gene_metadata_map[gene_symbol] = dict(per_gene_map)

    return gene_metadata_map, meta_dict_cache


def annotate_phenotype_ancestors(
    records_significants: list[dict[str, str | float]],
    term_pair_similarity_map: dict[tuple[str], dict[str, float]],
    ontology_terms: dict[str, dict[str, str]],
    ic_threshold,
) -> dict[tuple[str], dict[str, dict[str, str]]]:
    """
    Annotate phenotype ancestors for each gene pair.
    """
    # Build gene -> records map
    gene_records_map: dict[str, list[dict[str, str | float]]] = defaultdict(list)
    for record in records_significants:
        gene_records_map[record["marker_symbol"]].append(record)

    all_gene_symbols = list(gene_records_map.keys())

    # Build hierarchy and IC-based filters
    _, child_term_map = build_term_hierarchy(ontology_terms)
    annotations: set[str] = {"zygosity", "life_stage", "sexual_dimorphism"}
    terms_with_low_ic: set[str] = _get_terms_with_low_ic(ontology_terms, child_term_map, ic_threshold=ic_threshold)
    gene_metadata_map, meta_dict_cache = _build_gene_metadata_maps(gene_records_map, annotations)

    total_pairs = len(all_gene_symbols) * (len(all_gene_symbols) - 1) // 2

    phenotype_ancestors: dict[tuple[str], dict[str, dict[str, str]]] = {}

    for gene1_symbol, gene2_symbol in tqdm(
        combinations(all_gene_symbols, 2),
        total=total_pairs,
    ):
        key, ancestors = _annotate_ancestors(
            gene1_symbol=gene1_symbol,
            gene2_symbol=gene2_symbol,
            gene_metadata_map=gene_metadata_map,
            meta_dict_cache=meta_dict_cache,
            term_pair_similarity_map=term_pair_similarity_map,
            child_term_map=child_term_map,
            terms_with_low_ic=terms_with_low_ic,
        )
        phenotype_ancestors[key] = ancestors

    return phenotype_ancestors


###########################################################
# Phenodigm score calculation
###########################################################


def _calculate_weighted_similarity_matrix(
    gene1_data: dict[str, np.ndarray],
    gene2_data: dict[str, np.ndarray],
    term_pair_similarity_map: dict[tuple[str, str], dict[str | None, float]],
) -> np.ndarray:
    """Calculate weighted similarity matrix between two genes based on their phenotype records."""
    gene1_terms = gene1_data["terms"]
    gene2_terms = gene2_data["terms"]

    similarity_matrix = np.zeros((len(gene1_terms), len(gene2_terms)), dtype=float)
    for i, term1 in enumerate(gene1_terms):
        row = similarity_matrix[i]
        for j, term2 in enumerate(gene2_terms):
            _, similarity = next(
                iter(term_pair_similarity_map.get(tuple(sorted([term1, term2])), {None: 0.0}).items())
            )
            row[j] = similarity

    z_match = gene1_data["zygosity"][:, None] == gene2_data["zygosity"][None, :]
    l_match = gene1_data["life_stage"][:, None] == gene2_data["life_stage"][None, :]
    s_match = gene1_data["sexual_dimorphism"][:, None] == gene2_data["sexual_dimorphism"][None, :]
    match_counts = z_match.astype(int) + l_match.astype(int) + s_match.astype(int)

    weight_lookup = np.array([0.25, 0.5, 0.75, 1.0])
    weight_matrix = weight_lookup[match_counts]

    return similarity_matrix * weight_matrix


def _apply_phenodigm_scaling(
    weighted_similarity_matrix: np.ndarray,
    gene1_data: dict[str, np.ndarray],
    gene2_data: dict[str, np.ndarray],
) -> int:
    """Apply Phenodigm scaling method to similarity scores."""
    gene1_information_content_scores = gene1_data["ic_scores"]
    gene2_information_content_scores = gene2_data["ic_scores"]

    max_gene1_information_content = gene1_data["ic_max"]
    max_gene2_information_content = gene2_data["ic_max"]

    row_max_similarities = weighted_similarity_matrix.max(axis=1)
    column_max_similarities = weighted_similarity_matrix.max(axis=0)

    max_score_actual = np.max([np.max(row_max_similarities), np.max(column_max_similarities)])
    average_score_actual = (
        np.mean(np.concatenate([row_max_similarities, column_max_similarities]))
        if (len(row_max_similarities) > 0 or len(column_max_similarities) > 0)
        else 0.0
    )

    max_score_theoretical = max(max_gene1_information_content, max_gene2_information_content)

    combined_ic_scores = np.concatenate([gene1_information_content_scores, gene2_information_content_scores])
    average_score_theoretical = float(np.mean(combined_ic_scores)) if combined_ic_scores.size else 0.0

    normalized_max_score = max_score_actual / max_score_theoretical if max_score_theoretical > 0 else 0.0
    normalized_average_score = (
        average_score_actual / average_score_theoretical if average_score_theoretical > 0 else 0.0
    )

    phenodigm_score = 100 * (normalized_max_score + normalized_average_score) / 2

    return int(phenodigm_score)


def _calculate_phenodigm(
    gene1_symbol: str,
    gene2_symbol: str,
    gene_data_map: dict[str, dict[str, np.ndarray]],
    term_pair_similarity_map: dict[tuple[str, str], dict[str | None, float]],
) -> tuple[tuple[str], int]:
    gene1_data = gene_data_map[gene1_symbol]
    gene2_data = gene_data_map[gene2_symbol]

    weighted_similarity_matrix = _calculate_weighted_similarity_matrix(
        gene1_data,
        gene2_data,
        term_pair_similarity_map,
    )

    score = _apply_phenodigm_scaling(
        weighted_similarity_matrix,
        gene1_data,
        gene2_data,
    )

    gene_pair = tuple(sorted([gene1_symbol, gene2_symbol]))
    return gene_pair, score


def _build_gene_data_map(
    gene_records_map: dict[str, list[dict[str, str | float]]],
    term_ic_map: dict[str, float],
) -> dict[str, dict[str, np.ndarray]]:
    """Convert raw gene records into array-based representation for faster scoring."""
    gene_data_map: dict[str, dict[str, np.ndarray]] = {}
    for gene_symbol, records in gene_records_map.items():
        terms = np.array([r["mp_term_id"] for r in records], dtype=object)
        zygosity = np.array([r["zygosity"] for r in records], dtype=object)
        life_stage = np.array([r["life_stage"] for r in records], dtype=object)
        sexual_dimorphism = np.array([r.get("sexual_dimorphism", "None") for r in records], dtype=object)
        ic_scores = np.array([term_ic_map.get(term, 0.0) for term in terms], dtype=float)

        gene_data_map[gene_symbol] = {
            "terms": terms,
            "zygosity": zygosity,
            "life_stage": life_stage,
            "sexual_dimorphism": sexual_dimorphism,
            "ic_scores": ic_scores,
            "ic_max": float(ic_scores.max()) if ic_scores.size else 0.0,
        }

    return gene_data_map


def calculate_phenodigm_score(
    records_significants: list[dict[str, str | float]],
    term_pair_similarity_map: dict[tuple[str], dict[str, float]],
    term_ic_map: dict[str, float],
) -> dict[tuple[str], int]:
    """
    Calculate Phenodigm score between gene pairs.
    """
    # Build gene -> records map
    gene_records_map: dict[str, list[dict[str, str | float]]] = defaultdict(list)
    for record in records_significants:
        gene_records_map[record["marker_symbol"]].append(record)

    gene_data_map = _build_gene_data_map(gene_records_map, term_ic_map)

    all_gene_symbols = list(gene_records_map.keys())
    total_pairs = len(all_gene_symbols) * (len(all_gene_symbols) - 1) // 2

    phenodigm_scores: dict[tuple[str], int] = {}

    for gene1_symbol, gene2_symbol in tqdm(
        combinations(all_gene_symbols, 2),
        total=total_pairs,
    ):
        gene_pair, score = _calculate_phenodigm(
            gene1_symbol=gene1_symbol,
            gene2_symbol=gene2_symbol,
            gene_data_map=gene_data_map,
            term_pair_similarity_map=term_pair_similarity_map,
        )
        phenodigm_scores[gene_pair] = score

    return phenodigm_scores


# -----------------------------------------------------------
# Additional similarity evaluation metrics
# -----------------------------------------------------------


def calculate_num_shared_phenotypes(records_significants: list[dict[str, str | float]]) -> dict[frozenset, int]:
    """Calculate the number of shared phenotypes between two genes."""
    gene_phenotypes_map = defaultdict(set)
    for record in records_significants:
        gene_phenotypes_map[record["marker_symbol"]].add(
            frozenset(
                [
                    record["mp_term_id"],
                    record["zygosity"],
                    record["life_stage"],
                    record.get("sexual_dimorphism", "None"),
                ]
            )
        )
    num_shared_phenotypes = {}
    for gene1, gene2 in tqdm(
        combinations(gene_phenotypes_map.keys(), 2), total=math.comb(len(gene_phenotypes_map), 2)
    ):
        phenotypes_gene1 = gene_phenotypes_map[gene1]
        phenotypes_gene2 = gene_phenotypes_map[gene2]

        num_shared_phenotypes[tuple(sorted([gene1, gene2]))] = len(phenotypes_gene1.intersection(phenotypes_gene2))
    return num_shared_phenotypes


def calculate_jaccard_indices(records_significants: list[dict[str, str | float]]) -> dict[tuple[str], int]:
    """Calculate the number of shared phenotypes between two genes."""
    gene_phenotypes_map = defaultdict(set)
    for record in records_significants:
        gene_phenotypes_map[record["marker_symbol"]].add(
            frozenset(
                [
                    record["mp_term_id"],
                    record["zygosity"],
                    record["life_stage"],
                    record.get("sexual_dimorphism", "None"),
                ]
            )
        )

    jaccard_indices = {}
    for gene1, gene2 in tqdm(
        combinations(gene_phenotypes_map.keys(), 2), total=math.comb(len(gene_phenotypes_map), 2)
    ):
        phenotypes_gene1 = gene_phenotypes_map[gene1]
        phenotypes_gene2 = gene_phenotypes_map[gene2]

        intersection = phenotypes_gene1.intersection(phenotypes_gene2)
        union = phenotypes_gene1.union(phenotypes_gene2)
        # 0-100 scale
        jaccard_indices[tuple(sorted([gene1, gene2]))] = int(len(intersection) / len(union) * 100 if union else 0)

    return jaccard_indices


###########################################################
# Summarize the phenotype similarity results
###########################################################


def summarize_similarity_annotations(
    ontology_terms: dict[str, dict[str, str]],
    phenotype_ancestors: dict[tuple[str], dict[str, dict[str, str]]],
    phenodigm_scores: dict[tuple[str], int],
) -> Iterator[dict[str, dict[str, str] | int]]:
    """Summarize similarity annotations including common ancestors and Phenodigm scores."""

    id_name_map = {v["id"]: v["name"] for v in ontology_terms.values()}

    for gene1_symbol, gene2_symbol in tqdm(phenotype_ancestors.keys(), total=len(phenotype_ancestors)):
        gene_pair = tuple(sorted([gene1_symbol, gene2_symbol]))
        phenotype_ancestor = phenotype_ancestors[gene_pair]
        phenotype_ancestor_name = {id_name_map[k]: v for k, v in phenotype_ancestor.items()}
        phenodigm_score = phenodigm_scores[gene_pair]

        annotations = {
            "gene1_symbol": gene_pair[0],
            "gene2_symbol": gene_pair[1],
            "phenotype_shared_annotations": phenotype_ancestor_name,
            "phenotype_similarity_score": phenodigm_score if phenotype_ancestor_name else 0,
        }

        yield annotations
