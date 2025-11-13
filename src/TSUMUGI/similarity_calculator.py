from __future__ import annotations

import math
from collections import defaultdict
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
# calculate_all_pairwise_similarities (with multiprocessing)
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


def _precompute_information_content(
    ontology_terms: dict[str, dict], child_term_map: dict[str, set[str]]
) -> dict[str, float]:
    """Precompute information content (IC) for all ontology terms."""
    total_term_count = len(ontology_terms)
    ic_map: dict[str, float] = {}

    for term_id in ontology_terms:
        descendants = find_all_descendant_terms(term_id, child_term_map)
        term_count = len(descendants) + 1
        probability = term_count / total_term_count
        ic_map[term_id] = -math.log(probability)

    return ic_map


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


def _compute_pair_worker(term_pair: tuple[str, str]) -> tuple[frozenset[str], dict[str | None, float]]:
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

    return frozenset((term1_id, term2_id)), {msca: sim}


def _compute_pair_singleprocess(
    term1_id: str, term2_id: str, parent_term_map: dict[str, set[str]], ic_map: dict[str, float]
) -> tuple[frozenset[str], dict[str | None, float]]:
    """Single-process version (used when threads=1)."""
    msca, sim = _compute_pair_mica_and_resnik(term1_id, term2_id, parent_term_map, ic_map)
    return frozenset((term1_id, term2_id)), {msca: sim}


def calculate_all_pairwise_similarities(
    ontology_terms: dict[str, dict],
    all_term_ids: set[str],
    threads: int | None = None,
) -> dict[frozenset[str], dict[str | None, float]]:
    """Calculate pairwise Resnik similarities for all term IDs."""
    parent_term_map, child_term_map = build_term_hierarchy(ontology_terms)
    ic_map = _precompute_information_content(ontology_terms, child_term_map)

    term_list = sorted(all_term_ids)
    pairs: list[tuple[str, str]] = list(combinations_with_replacement(term_list, 2))
    total_pairs = len(pairs)

    term_pair_similarity_map: dict[frozenset[str], dict[str | None, float]] = {}

    if threads == 1:
        for term1_id, term2_id in tqdm(pairs, total=total_pairs):
            key, val = _compute_pair_singleprocess(term1_id, term2_id, parent_term_map, ic_map)
            term_pair_similarity_map[key] = val
        return term_pair_similarity_map

    with ProcessPoolExecutor(
        max_workers=threads,
        initializer=_init_worker,
        initargs=(parent_term_map, child_term_map, ic_map),
    ) as executor:
        for key, val in tqdm(executor.map(_compute_pair_worker, pairs), total=total_pairs):
            term_pair_similarity_map[key] = val

    return term_pair_similarity_map


###########################################################
# Common ancestor annotation (with optional parallelization)
###########################################################


def _calculate_information_content(term_id: str, child_term_map: dict[str, set[str]], total_term_count: int) -> float:
    """Calculate information content for a term based on its descendants."""
    descendant_terms = find_all_descendant_terms(term_id, child_term_map)
    term_count = len(descendant_terms) + 1
    probability = term_count / total_term_count
    return -math.log(probability)


def _delete_parent_terms_from_ancestors(
    candidate_ancestors: dict[str, dict[str, str]],
    child_term_map: dict[str, set[str]],
) -> dict[str, dict[str, str]]:
    """
    Remove parent terms from the common ancestors.
    Keep only the most specific terms among candidates with identical metadata.
    """
    to_delete: set[str] = set()
    items_snapshot = list(candidate_ancestors.items())

    for (term1_id, term1_meta), (term2_id, term2_meta) in combinations(items_snapshot, 2):
        if term1_id == term2_id or term1_meta != term2_meta:
            continue

        if term2_id in child_term_map.get(term1_id, set()):
            to_delete.add(term1_id)

        if term1_id in child_term_map.get(term2_id, set()):
            to_delete.add(term2_id)

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

    for term_id in ontology_terms.keys():
        ic = _calculate_information_content(term_id, child_term_map, total_term_count)
        map_term_to_ic[term_id] = ic

    ic_values = list(map_term_to_ic.values())
    ic_min_values = np.percentile(ic_values, ic_threshold)
    return {term for term, ic in map_term_to_ic.items() if ic < ic_min_values}


# =========================================================
# Single-process implementation (core per-pair logic)
# =========================================================


def _annotate_gene_pair_singleprocess(
    gene1_symbol: str,
    gene2_symbol: str,
    gene_records_map: dict[str, list[dict[str, str | float]]],
    term_pair_similarity_map: dict[frozenset[str], dict[str | float]],
    child_term_map: dict[str, set[str]],
    terms_with_low_ic: set[str],
    annotations: set[str],
) -> tuple[frozenset[str], dict[str, dict[str, str]]]:
    """Annotate phenotype ancestors for a single gene pair (single-process version)."""
    gene1_records = gene_records_map[gene1_symbol]
    gene2_records = gene_records_map[gene2_symbol]

    candidate_ancestors: dict[str, dict[str, str]] = {}
    added_keys: set[tuple[str, tuple[tuple[str, str], ...]]] = set()

    for gene1_record in gene1_records:
        for gene2_record in gene2_records:
            gene1_mp_term_id = gene1_record["mp_term_id"]
            gene2_mp_term_id = gene2_record["mp_term_id"]
            key = frozenset([gene1_mp_term_id, gene2_mp_term_id])

            # term_pair_similarity_map: {frozenset({t1,t2}): {common_ancestor: similarity}}
            mapping = term_pair_similarity_map.get(key)
            if not mapping:
                continue

            # Take first (only) item
            common_ancestor, similarity = next(iter(mapping.items()))

            if not common_ancestor or similarity == 0.0:
                continue

            if common_ancestor in terms_with_low_ic:
                continue

            gene1_metadata = {k: v for k, v in gene1_record.items() if k in annotations}
            gene2_metadata = {k: v for k, v in gene2_record.items() if k in annotations}

            if gene1_metadata != gene2_metadata:
                continue

            meta = gene1_metadata
            meta_key = tuple(sorted(meta.items()))
            current_key = (common_ancestor, meta_key)

            if current_key in added_keys:
                continue

            candidate_ancestors[common_ancestor] = meta
            added_keys.add(current_key)

    # Remove parent terms from candidate ancestors
    candidate_ancestors = _delete_parent_terms_from_ancestors(candidate_ancestors, child_term_map)

    gene_pair_key = frozenset([gene1_symbol, gene2_symbol])
    return gene_pair_key, (dict(candidate_ancestors) if candidate_ancestors else {})


# =========================================================
# Parallel implementation (worker globals)
# =========================================================

_worker_gene_records_map: dict[str, list[dict[str, str | float]]] | None = None
_worker_term_pair_similarity_map: dict[frozenset[str], dict[str | float]] | None = None
_worker_child_term_map: dict[str, set[str]] | None = None
_worker_terms_with_low_ic: set[str] | None = None
_worker_annotations: set[str] | None = None


def _init_annotate_worker(
    gene_records_map: dict[str, list[dict[str, str | float]]],
    term_pair_similarity_map: dict[frozenset[str], dict[str | float]],
    child_term_map: dict[str, set[str]],
    terms_with_low_ic: set[str],
    annotations: set[str],
) -> None:
    """Initializer for annotate workers to set shared read-only data."""
    global _worker_gene_records_map, _worker_term_pair_similarity_map
    global _worker_child_term_map, _worker_terms_with_low_ic, _worker_annotations

    _worker_gene_records_map = gene_records_map
    _worker_term_pair_similarity_map = term_pair_similarity_map
    _worker_child_term_map = child_term_map
    _worker_terms_with_low_ic = terms_with_low_ic
    _worker_annotations = annotations


def _annotate_gene_pair_worker(gene_pair: tuple[str, str]) -> tuple[frozenset[str], dict[str, dict[str, str]]]:
    """Worker-side function: annotate phenotype ancestors for a single gene pair."""
    gene1_symbol, gene2_symbol = gene_pair

    if (
        _worker_gene_records_map is None
        or _worker_term_pair_similarity_map is None
        or _worker_child_term_map is None
        or _worker_terms_with_low_ic is None
        or _worker_annotations is None
    ):
        raise RuntimeError("Annotate worker globals are not initialized.")

    return _annotate_gene_pair_singleprocess(
        gene1_symbol=gene1_symbol,
        gene2_symbol=gene2_symbol,
        gene_records_map=_worker_gene_records_map,
        term_pair_similarity_map=_worker_term_pair_similarity_map,
        child_term_map=_worker_child_term_map,
        terms_with_low_ic=_worker_terms_with_low_ic,
        annotations=_worker_annotations,
    )


def annotate_phenotype_ancestors(
    records_significants: list[dict[str, str | float]],
    term_pair_similarity_map: dict[frozenset[str], dict[str, float]],
    ontology_terms: dict[str, dict[str, str]],
    ic_threshold,
    threads: int | None = None,
) -> dict[frozenset[str], dict[str, dict[str, str]]]:
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

    # Prepare gene pairs
    gene_pairs: list[tuple[str, str]] = list(combinations(all_gene_symbols, 2))
    total_pairs = len(gene_pairs)

    phenotype_ancestors: dict[frozenset[str], dict[str, dict[str, str]]] = {}

    # Single-process mode
    if threads == 1:
        for gene1_symbol, gene2_symbol in tqdm(
            gene_pairs,
            total=total_pairs,
        ):
            key, ancestors = _annotate_gene_pair_singleprocess(
                gene1_symbol=gene1_symbol,
                gene2_symbol=gene2_symbol,
                gene_records_map=gene_records_map,
                term_pair_similarity_map=term_pair_similarity_map,
                child_term_map=child_term_map,
                terms_with_low_ic=terms_with_low_ic,
                annotations=annotations,
            )
            phenotype_ancestors[key] = ancestors
        return phenotype_ancestors

    # Parallel mode
    with ProcessPoolExecutor(
        max_workers=threads,
        initializer=_init_annotate_worker,
        initargs=(gene_records_map, term_pair_similarity_map, child_term_map, terms_with_low_ic, annotations),
    ) as executor:
        for key, ancestors in tqdm(
            executor.map(_annotate_gene_pair_worker, gene_pairs),
            total=total_pairs,
        ):
            phenotype_ancestors[key] = ancestors

    return phenotype_ancestors


###########################################################
# Phenodigm score calculation
###########################################################


def _adjust_similarity_by_metadata(
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


def _calculate_weighted_similarity_matrix(
    gene1_records: list[dict[str, str | float]],
    gene2_records: list[dict[str, str | float]],
    term_pair_similarity_map: dict[frozenset[str], dict[str, float]],
) -> np.ndarray:
    """Calculate weighted similarity matrix between two genes based on their phenotype records."""
    weighted_similarity_matrix = []
    for gene1_record in gene1_records:
        similarity_row = []
        for gene2_record in gene2_records:
            gene1_term_id = gene1_record["mp_term_id"]
            gene2_term_id = gene2_record["mp_term_id"]
            similarity = next(iter(term_pair_similarity_map[frozenset([gene1_term_id, gene2_term_id])].values()), 0.0)
            if similarity == 0.0:
                similarity_row.append(0.0)
                continue

            # Adjust score by zygosity, life stage, sexual dimorphism
            gene1_zygosity = gene1_record["zygosity"]
            gene2_zygosity = gene2_record["zygosity"]
            gene1_life_stage = gene1_record["life_stage"]
            gene2_life_stage = gene2_record["life_stage"]
            gene1_sexual_dimorphism = gene1_record.get("sexual_dimorphism", "None")
            gene2_sexual_dimorphism = gene2_record.get("sexual_dimorphism", "None")

            adjusted_similarity = _adjust_similarity_by_metadata(
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


def _apply_phenodigm_scaling(
    weighted_similarity_matrix: np.ndarray,
    gene1_mp_term_ids: set[str],
    gene2_mp_term_ids: set[str],
    term_pair_similarity_map: dict[frozenset[str], dict[str, float]],
) -> int:
    """Apply Phenodigm scaling method to similarity scores."""
    gene1_information_content_scores = [
        next(iter(term_pair_similarity_map[frozenset([term_id])].values()), 0.0) for term_id in gene1_mp_term_ids
    ]
    gene2_information_content_scores = [
        next(iter(term_pair_similarity_map[frozenset([term_id])].values()), 0.0) for term_id in gene2_mp_term_ids
    ]

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

    return int(phenodigm_score)


###########################################################
# Per-pair helper (single-process core)
###########################################################


def _calculate_phenodigm_for_pair_singleprocess(
    gene1_symbol: str,
    gene2_symbol: str,
    gene_records_map: dict[str, list[dict[str, str | float]]],
    term_pair_similarity_map: dict[frozenset[str], dict[str, float]],
) -> tuple[frozenset[str], int]:
    gene1_records = gene_records_map[gene1_symbol]
    gene2_records = gene_records_map[gene2_symbol]

    gene1_mp_term_ids = {record["mp_term_id"] for record in gene1_records}
    gene2_mp_term_ids = {record["mp_term_id"] for record in gene2_records}

    weighted_similarity_matrix = _calculate_weighted_similarity_matrix(
        gene1_records,
        gene2_records,
        term_pair_similarity_map,
    )

    score = _apply_phenodigm_scaling(
        weighted_similarity_matrix,
        gene1_mp_term_ids,
        gene2_mp_term_ids,
        term_pair_similarity_map,
    )

    return frozenset([gene1_symbol, gene2_symbol]), score


###########################################################
# Parallel worker setup
###########################################################

_worker_gene_records_map: dict[str, list[dict[str, str | float]]] | None = None
_worker_term_pair_similarity_map: dict[frozenset[str], dict[str, float]] | None = None


def _init_phenodigm_worker(
    gene_records_map: dict[str, list[dict[str, str | float]]],
    term_pair_similarity_map: dict[frozenset[str], dict[str, float]],
) -> None:
    """Initializer for Phenodigm workers to set shared read-only data."""
    global _worker_gene_records_map, _worker_term_pair_similarity_map
    _worker_gene_records_map = gene_records_map
    _worker_term_pair_similarity_map = term_pair_similarity_map


def _calculate_phenodigm_for_pair_worker(
    gene_pair: tuple[str, str],
) -> tuple[frozenset[str], int]:
    """Worker-side computation for a single gene pair."""
    if _worker_gene_records_map is None or _worker_term_pair_similarity_map is None:
        raise RuntimeError("Phenodigm worker globals are not initialized.")

    gene1_symbol, gene2_symbol = gene_pair

    return _calculate_phenodigm_for_pair_singleprocess(
        gene1_symbol=gene1_symbol,
        gene2_symbol=gene2_symbol,
        gene_records_map=_worker_gene_records_map,
        term_pair_similarity_map=_worker_term_pair_similarity_map,
    )


###########################################################
# Public API
###########################################################


def calculate_phenodigm_score(
    records_significants: list[dict[str, str | float]],
    term_pair_similarity_map: dict[frozenset[str], dict[str, float]],
    threads: int | None = None,
) -> dict[frozenset[str], int]:
    """
    Calculate Phenodigm score between gene pairs.
    """
    # Build gene -> records map
    gene_records_map: dict[str, list[dict[str, str | float]]] = defaultdict(list)
    for record in records_significants:
        gene_records_map[record["marker_symbol"]].append(record)

    all_gene_symbols = list(gene_records_map.keys())
    gene_pairs: list[tuple[str, str]] = list(combinations(all_gene_symbols, 2))
    total_pairs = len(gene_pairs)

    phenodigm_scores: dict[frozenset[str], int] = {}

    # Single-process mode
    if threads == 1:
        for gene1_symbol, gene2_symbol in tqdm(
            gene_pairs,
            total=total_pairs,
        ):
            key, score = _calculate_phenodigm_for_pair_singleprocess(
                gene1_symbol=gene1_symbol,
                gene2_symbol=gene2_symbol,
                gene_records_map=gene_records_map,
                term_pair_similarity_map=term_pair_similarity_map,
            )
            phenodigm_scores[key] = score
        return phenodigm_scores

    # Parallel mode
    with ProcessPoolExecutor(
        max_workers=threads,
        initializer=_init_phenodigm_worker,
        initargs=(gene_records_map, term_pair_similarity_map),
    ) as executor:
        for key, score in tqdm(
            executor.map(_calculate_phenodigm_for_pair_worker, gene_pairs),
            total=total_pairs,
        ):
            phenodigm_scores[key] = score

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

        num_shared_phenotypes[frozenset([gene1, gene2])] = len(phenotypes_gene1.intersection(phenotypes_gene2))

    return num_shared_phenotypes


def calculate_jaccard_indices(records_significants: list[dict[str, str | float]]) -> dict[frozenset, int]:
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
        jaccard_indices[frozenset([gene1, gene2])] = int(len(intersection) / len(union) * 100 if union else 0)

    return jaccard_indices


###########################################################
# Summarize the phenotype similarity results
###########################################################


def summarize_similarity_annotations(
    ontology_terms: dict[str, dict[str, str]],
    phenotype_ancestors: dict[frozenset[str], dict[str, dict[str, str]]],
    phenodigm_scores: dict[frozenset[str], int],
) -> dict[frozenset[str], dict[str, dict[str, str] | int]]:
    """Summarize similarity annotations including common ancestors and Phenodigm scores."""

    id_name_map = {v["id"]: v["name"] for v in ontology_terms.values()}

    pair_similarity_annotations = defaultdict(list)

    for gene1_symbol, gene2_symbol in tqdm(phenotype_ancestors.keys(), total=len(phenotype_ancestors)):
        phenotype_ancestor = phenotype_ancestors[frozenset([gene1_symbol, gene2_symbol])]
        phenotype_ancestor_name = {id_name_map[k]: v for k, v in phenotype_ancestor.items()}
        phenodigm_score = phenodigm_scores[frozenset([gene1_symbol, gene2_symbol])]

        pair_similarity_annotations[frozenset([gene1_symbol, gene2_symbol])] = {
            "phenotype_shared_annotations": phenotype_ancestor_name,
            "phenotype_similarity_score": phenodigm_score if phenotype_ancestor_name else 0,
        }

    return dict(pair_similarity_annotations)
