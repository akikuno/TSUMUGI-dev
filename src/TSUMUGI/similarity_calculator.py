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


def _calculate_term_ic_map(
    ontology_terms: dict[str, dict], child_term_map: dict[str, set[str]], ic_threshold: int = 5
) -> dict[str, float]:
    """
    Calculate information content (IC) for all ontology terms.
    Annotate 0 for terms below the given IC threshold percentile (default: 5th percentile).
    """
    total_term_count = len(ontology_terms)
    term_ic_map: dict[str, float] = {}

    for term_id in ontology_terms:
        descendants = find_all_descendant_terms(term_id, child_term_map)
        term_count = len(descendants) + 1
        probability = term_count / total_term_count
        term_ic_map[term_id] = -math.log(probability)

    ic_values = list(term_ic_map.values())
    ic_min_values = np.percentile(ic_values, ic_threshold)
    for term_id, ic in term_ic_map.items():
        if ic < ic_min_values:
            term_ic_map[term_id] = 0.0

    return term_ic_map


_worker_parent_term_map: dict[str, set[str]] | None = None
_worker_child_term_map: dict[str, set[str]] | None = None
_worker_term_ic_map: dict[str, float] | None = None


def _init_worker(
    parent_term_map: dict[str, set[str]], child_term_map: dict[str, set[str]], term_ic_map: dict[str, float]
) -> None:
    """Initializer for worker processes to avoid repeatedly pickling large objects."""
    global _worker_parent_term_map, _worker_child_term_map, _worker_term_ic_map
    _worker_parent_term_map = parent_term_map
    _worker_child_term_map = child_term_map
    _worker_term_ic_map = term_ic_map


def _calculate_pair_mica_and_resnik(
    term1_id: str, term2_id: str, parent_term_map: dict[str, set[str]], term_ic_map: dict[str, float]
) -> tuple[str | None, float]:
    """Calculate MSCA (by IC) and Resnik similarity using precalculated IC."""
    if term1_id == term2_id:
        return term1_id, term_ic_map.get(term1_id, 0.0)
    common_ancestors = find_common_ancestors(term1_id, term2_id, parent_term_map)
    if not common_ancestors:
        return None, 0.0

    msca = max(common_ancestors, key=lambda t: term_ic_map.get(t, 0.0))
    similarity = term_ic_map.get(msca, 0.0)
    return msca, similarity


def _calculate_pair_jaccard(
    term1_id: str, term2_id: str, parent_term_map: dict[str, set[str]], term_ic_map: dict[str, float]
) -> float:
    """Calculate Jaccard index for parent ancestors."""
    if term1_id == term2_id:
        return 1.0
    ancestors1 = parent_term_map.get(term1_id, set())
    ancestors2 = parent_term_map.get(term2_id, set())

    intersection = ancestors1.intersection(ancestors2)
    union = ancestors1.union(ancestors2)

    if not union:
        return 0.0

    jaccard_index = len(intersection) / len(union)
    return jaccard_index


def _calculate_pair_worker(term_pair: tuple[str, str]) -> tuple[tuple[str], dict[str | None, float]]:
    """Worker-side calculation using globals set by _init_worker."""
    term1_id, term2_id = term_pair

    parent_term_map = _worker_parent_term_map
    term_ic_map = _worker_term_ic_map

    if parent_term_map is None or term_ic_map is None:
        raise RuntimeError("Worker maps are not initialized.")

    if term1_id == term2_id:
        msca = term1_id
        sim = term_ic_map.get(term1_id, 0.0)
    else:
        msca, sim = _calculate_pair_mica_and_resnik(term1_id, term2_id, parent_term_map, term_ic_map)

    term_pairs = tuple(sorted((term1_id, term2_id)))
    return term_pairs, {msca: sim}


def _calculate_pair_similarity_score(
    term1_id: str, term2_id: str, parent_term_map: dict[str, set[str]], term_ic_map: dict[str, float]
) -> tuple[tuple[str], dict[str | None, float]]:
    """Calculate pairwise similarity (Phenodigm score).
    msca: Most Specific Common Ancestor
    Phenodigm score: sqrt(Resnik similarity * Jaccard index)
    """
    msca, resnik = _calculate_pair_mica_and_resnik(term1_id, term2_id, parent_term_map, term_ic_map)
    jaccard = _calculate_pair_jaccard(term1_id, term2_id, parent_term_map, term_ic_map)

    term_pairs = tuple(sorted((term1_id, term2_id)))
    score = math.sqrt(resnik * jaccard)
    return term_pairs, {msca: score}


def calculate_all_pairwise_similarities(
    ontology_terms: dict[str, dict],
    all_term_ids: set[str],
    ic_threshold: int = 5,
    threads: int | None = None,
) -> tuple[dict[tuple[str], dict[str | None, float]], dict[str, float]]:
    """Calculate pairwise Resnik similarities for all term IDs."""
    parent_term_map, child_term_map = build_term_hierarchy(ontology_terms)
    term_ic_map = _calculate_term_ic_map(ontology_terms, child_term_map, ic_threshold=ic_threshold)
    term_list = sorted(all_term_ids)

    terms_similarity_map: dict[tuple[str], dict[str | None, float]] = {}

    if threads == 1:
        for term1_id, term2_id in combinations_with_replacement(term_list, 2):
            term_pairs, ancestor_ic_map = _calculate_pair_similarity_score(
                term1_id, term2_id, parent_term_map, term_ic_map
            )
            terms_similarity_map[term_pairs] = ancestor_ic_map
        return terms_similarity_map

    with ProcessPoolExecutor(
        max_workers=threads,
        initializer=_init_worker,
        initargs=(parent_term_map, child_term_map, term_ic_map),
    ) as executor:
        for term_pairs, ancestor_ic_map in executor.map(
            _calculate_pair_worker, combinations_with_replacement(term_list, 2)
        ):
            terms_similarity_map[term_pairs] = ancestor_ic_map

    return terms_similarity_map, term_ic_map


###########################################################
# Phenotype ancestor annotation
###########################################################


def _delete_parent_terms_from_ancestors(
    candidate_ancestors: list[dict[str, str]],
    child_term_map: dict[str, set[str]],
) -> list[dict[str, str]]:
    """
    Remove parent terms from the common ancestors.
    Keep only the most specific terms among candidates with identical metadata.
    """
    to_delete: set[int] = set()
    phenotype_to_meta = defaultdict(list)

    for ancestor in candidate_ancestors:
        phenotype_to_meta[ancestor["phenotype"]].append({k: v for k, v in ancestor.items() if k != "phenotype"})

    for idx, ancestor in enumerate(candidate_ancestors):
        term_id = ancestor["phenotype"]
        term_meta = {k: v for k, v in ancestor.items() if k != "phenotype"}

        if idx in to_delete:
            continue

        stack = list(child_term_map.get(term_id, ()))
        while stack:
            child_id = stack.pop()
            child_metas = phenotype_to_meta.get(child_id, [])
            if any(child_meta == term_meta for child_meta in child_metas):
                to_delete.add(idx)
                break
            stack.extend(child_term_map.get(child_id, ()))

    return [ancestor for i, ancestor in enumerate(candidate_ancestors) if i not in to_delete]


# ---------------------------------------------------------
# Helper functions for building gene metadata maps
# ---------------------------------------------------------


def _build_gene_metadata_maps(
    gene_records_map: dict[str, list[dict[str, str | float]]],
    annotations: set[str],
) -> tuple[dict[str, dict[tuple[str, str, str], list[str]]], dict[tuple[str, str, str], dict[str, str]]]:
    """
    Group gene records by metadata signature for faster matching.
    Returns:
        gene_metadata_map: example: {"GeneA": {("Homo", "Embryo", "None"): ["MP:0001", "MP:0002"]}}
        meta_dict_cache: example: {("Homo", "Embryo", "None"): {"zygosity": "Homo", "life_stage": "Embryo", "sexual_dimorphism": "None"}}
    """
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


def _annotate_ancestors(
    gene1_meta_map: dict,
    gene2_meta_map: dict,
    meta_dict_cache: dict,
    terms_similarity_map: dict[tuple[str, str], dict[str | None, float]],
    child_term_map: dict[str, set[str]],
) -> list[dict[str, str]]:
    """Annotate phenotype ancestors for a single gene pair."""

    candidate_ancestors: list[dict[str, str]] = []
    added_keys: set[tuple[str, tuple[str, str, str]]] = set()

    shared_meta_signatures = set(gene1_meta_map.keys()) & set(gene2_meta_map.keys())

    for meta_signature in shared_meta_signatures:
        gene1_terms = gene1_meta_map[meta_signature]
        gene2_terms = gene2_meta_map[meta_signature]
        meta_dict = meta_dict_cache[meta_signature]

        for gene1_mp_term_id in gene1_terms:
            for gene2_mp_term_id in gene2_terms:
                pair_key = tuple(sorted([gene1_mp_term_id, gene2_mp_term_id]))
                mapping = terms_similarity_map.get(pair_key)
                if not mapping:
                    continue

                common_ancestor, similarity = next(iter(mapping.items()))

                if not common_ancestor or similarity == 0.0:
                    continue

                current_key = (common_ancestor, meta_signature)

                if current_key in added_keys:
                    continue

                candidate_ancestors.append({"phenotype": common_ancestor, **meta_dict})
                added_keys.add(current_key)

    # Remove parent terms from candidate ancestors
    ancestors = _delete_parent_terms_from_ancestors(candidate_ancestors, child_term_map)

    return ancestors


def annotate_phenotype_ancestors(
    genewise_phenotype_significants: list[dict[str, str | float]],
    terms_similarity_map: dict[tuple[str], dict[str, float]],
    ontology_terms: dict[str, dict[str, str]],
) -> Iterator[dict[str, str | list[dict[str, str]]]]:
    """
    Annotate phenotype ancestors for each gene pair.
    """
    # Build gene -> records map
    gene_records_map: dict[str, list[dict[str, str | float]]] = defaultdict(list)
    for record in genewise_phenotype_significants:
        gene_records_map[record["marker_symbol"]].append(record)

    # Build hierarchy and IC-based filters
    _, child_term_map = build_term_hierarchy(ontology_terms)
    annotations: set[str] = {"zygosity", "life_stage", "sexual_dimorphism"}
    gene_metadata_map, meta_dict_cache = _build_gene_metadata_maps(gene_records_map, annotations)

    for (gene1_symbol, gene1_meta_map), (gene2_symbol, gene2_meta_map) in combinations(gene_metadata_map.items(), 2):
        ancestors = _annotate_ancestors(
            gene1_meta_map=gene1_meta_map,
            gene2_meta_map=gene2_meta_map,
            meta_dict_cache=meta_dict_cache,
            terms_similarity_map=terms_similarity_map,
            child_term_map=child_term_map,
        )
        yield {
            "gene1_symbol": gene1_symbol,
            "gene2_symbol": gene2_symbol,
            "phenotype_shared_annotations": sorted(ancestors),
        }


###########################################################
# Phenodigm score calculation
###########################################################


def _calculate_weighted_similarity_matrix(
    gene1_record: dict[str, np.ndarray],
    gene2_record: dict[str, np.ndarray],
    terms_similarity_map: dict[tuple[str, str], dict[str | None, float]],
) -> np.ndarray:
    """Calculate weighted similarity matrix between two genes based on their phenotype records."""
    gene1_terms = gene1_record["terms"]
    gene2_terms = gene2_record["terms"]

    similarity_matrix = np.zeros((len(gene1_terms), len(gene2_terms)), dtype=float)
    for i, term1 in enumerate(gene1_terms):
        row = similarity_matrix[i]
        for j, term2 in enumerate(gene2_terms):
            _, similarity = next(iter(terms_similarity_map.get(tuple(sorted([term1, term2])), {None: 0.0}).items()))
            row[j] = similarity

    z_match = gene1_record["zygosity"][:, None] == gene2_record["zygosity"][None, :]
    l_match = gene1_record["life_stage"][:, None] == gene2_record["life_stage"][None, :]
    s_match = gene1_record["sexual_dimorphism"][:, None] == gene2_record["sexual_dimorphism"][None, :]
    match_counts = z_match.astype(int) + l_match.astype(int) + s_match.astype(int)

    weight_lookup = np.array([0.25, 0.5, 0.75, 1.0])
    weight_matrix = weight_lookup[match_counts]

    return similarity_matrix * weight_matrix


def _apply_phenodigm_scaling(
    weighted_similarity_matrix: np.ndarray,
    gene1_record: dict[str, np.ndarray],
    gene2_record: dict[str, np.ndarray],
) -> int:
    """Apply Phenodigm scaling method to similarity scores (0-100)."""
    gene1_information_content_scores = gene1_record["ic_scores"]
    gene2_information_content_scores = gene2_record["ic_scores"]

    max_gene1_information_content = gene1_record["ic_max"]
    max_gene2_information_content = gene2_record["ic_max"]

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
    gene1_record: dict[str, np.ndarray],
    gene2_record: dict[str, np.ndarray],
    terms_similarity_map: dict[tuple[str, str], dict[str | None, float]],
) -> int:
    """Calculate the Phenodigm score for a single gene pair."""
    weighted_similarity_matrix = _calculate_weighted_similarity_matrix(
        gene1_record,
        gene2_record,
        terms_similarity_map,
    )

    score = _apply_phenodigm_scaling(
        weighted_similarity_matrix,
        gene1_record,
        gene2_record,
    )

    return score


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
    genewise_phenotype_significants: list[dict[str, str | float]],
    terms_similarity_map: dict[tuple[str], dict[str, float]],
    term_ic_map: dict[str, float],
) -> Iterator[dict[str, str | int]]:
    """
    Calculate Phenodigm score between gene pairs.
    """
    # Build gene -> records map
    gene_records_map: dict[str, list[dict[str, str | float]]] = defaultdict(list)
    for record in genewise_phenotype_significants:
        gene_records_map[record["marker_symbol"]].append(record)

    gene_data_map = _build_gene_data_map(gene_records_map, term_ic_map)

    for (gene1_symbol, gene1_record), (gene2_symbol, gene2_record) in combinations(gene_data_map.items(), 2):
        score = _calculate_phenodigm(
            gene1_record=gene1_record,
            gene2_record=gene2_record,
            terms_similarity_map=terms_similarity_map,
        )
        yield {"gene1_symbol": gene1_symbol, "gene2_symbol": gene2_symbol, "phenotype_similarity_score": score}


###########################################################
# Summarize the phenotype similarity results
###########################################################


def summarize_similarity_annotations(
    ontology_terms: dict[str, dict[str, str]],
    phenotype_ancestors: Iterator[dict[str, str | list[dict[str, str]]]],
    phenodigm_scores: Iterator[dict[str, str | int]],
    total_pairs: int,
) -> Iterator[dict[str, list[dict[str, str]] | int]]:
    """Summarize similarity annotations including common ancestors and Phenodigm scores."""

    id_name_map = {v["id"]: v["name"] for v in ontology_terms.values()}

    for phenotype_ancestor, phenodigm_score in tqdm(zip(phenotype_ancestors, phenodigm_scores), total=total_pairs):
        gene1_symbol = phenotype_ancestor["gene1_symbol"]
        gene2_symbol = phenotype_ancestor["gene2_symbol"]

        ancestors: list[dict[str, str]] = phenotype_ancestor["phenotype_shared_annotations"]

        ancestors_renamed = []
        for ancestor in ancestors:
            renamed_ancestor = {}
            for k, v in ancestor.items():
                if k == "phenotype" and v in id_name_map:
                    renamed_ancestor["phenotype"] = id_name_map[v]
                else:
                    renamed_ancestor[k] = v
            ancestors_renamed.append(renamed_ancestor)

        phenodigm_score = phenodigm_score["phenotype_similarity_score"]

        annotations = {
            "gene1_symbol": gene1_symbol,
            "gene2_symbol": gene2_symbol,
            "phenotype_shared_annotations": sorted(ancestors_renamed),
            "phenotype_similarity_score": phenodigm_score if ancestors_renamed else 0,
        }

        yield annotations
