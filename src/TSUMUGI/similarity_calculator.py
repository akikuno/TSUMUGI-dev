from __future__ import annotations

import math
import multiprocessing as mp
import threading
from collections import defaultdict
from collections.abc import Iterable, Iterator
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations, combinations_with_replacement
from multiprocessing.context import BaseContext

import numpy as np
from tqdm import tqdm

from TSUMUGI.ontology_handler import (
    build_term_hierarchy,
    find_all_ancestor_terms,
    find_all_descendant_terms,
    find_common_ancestors,
)

###########################################################
# Pairwise term similarity (with multiprocessing)
###########################################################


def _get_inferred_attributes(term_id: str, parent_term_map: dict[str, set[str]]) -> set[str]:
    """Return the term itself and all ontology ancestors used by OWLSim-style simJ."""
    inferred_attributes = find_all_ancestor_terms(term_id, parent_term_map)
    inferred_attributes.add(term_id)
    return inferred_attributes


def _calculate_inferred_attribute_map(term_ids: set[str], parent_term_map: dict[str, set[str]]) -> dict[str, set[str]]:
    """Precompute inferred attribute sets for the terms being compared."""
    return {term_id: _get_inferred_attributes(term_id, parent_term_map) for term_id in term_ids}


def _calculate_term_descendant_count_map(
    term_ids: Iterable[str], child_term_map: dict[str, set[str]]
) -> dict[str, int]:
    """Precompute the number of unique transitive descendants for each ontology term."""
    return {term_id: len(find_all_descendant_terms(term_id, child_term_map)) for term_id in term_ids}


def _calculate_term_ic_map(
    ontology_terms: dict[str, dict],
    parent_term_map: dict[str, set[str]],
    genewise_phenotype_significants: list[dict[str, str | float]],
) -> dict[str, float]:
    """
    Calculate PhenoDigm-style information content from annotation frequency.

    Each direct annotation is propagated to the annotated MP term and all of its ancestors.
    """
    annotation_counts: dict[str, int] = defaultdict(int)
    total_annotation_count = 0

    for record in genewise_phenotype_significants:
        term_id = record["mp_term_id"]
        if term_id not in ontology_terms:
            continue

        total_annotation_count += 1
        for inferred_term_id in _get_inferred_attributes(term_id, parent_term_map):
            if inferred_term_id in ontology_terms:
                annotation_counts[inferred_term_id] += 1

    if total_annotation_count == 0:
        return dict.fromkeys(ontology_terms, 0.0)

    term_ic_map: dict[str, float] = {}
    for term_id in ontology_terms:
        annotation_count = annotation_counts.get(term_id, 0)
        if annotation_count == 0:
            term_ic_map[term_id] = 0.0
            continue

        probability = annotation_count / total_annotation_count
        term_ic_map[term_id] = -math.log2(probability)

    return term_ic_map


_worker_parent_term_map: dict[str, set[str]] | None = None
_worker_inferred_attribute_map: dict[str, set[str]] | None = None
_worker_term_ic_map: dict[str, float] | None = None
_worker_term_descendant_count_map: dict[str, int] | None = None


def _get_process_pool_context() -> BaseContext:
    """Return a process context that avoids forking from a multithreaded process."""
    if threading.active_count() <= 1:
        return mp.get_context()

    for start_method in ("spawn", "forkserver"):
        if start_method in mp.get_all_start_methods():
            return mp.get_context(start_method)
    return mp.get_context()


def _init_worker(
    parent_term_map: dict[str, set[str]],
    inferred_attribute_map: dict[str, set[str]],
    term_ic_map: dict[str, float],
    term_descendant_count_map: dict[str, int],
) -> None:
    """Initializer for worker processes to avoid repeatedly pickling large objects."""
    global _worker_parent_term_map, _worker_inferred_attribute_map, _worker_term_ic_map
    global _worker_term_descendant_count_map
    _worker_parent_term_map = parent_term_map
    _worker_inferred_attribute_map = inferred_attribute_map
    _worker_term_ic_map = term_ic_map
    _worker_term_descendant_count_map = term_descendant_count_map


def _calculate_pair_mica_and_resnik(
    term1_id: str,
    term2_id: str,
    parent_term_map: dict[str, set[str]],
    term_ic_map: dict[str, float],
    term_descendant_count_map: dict[str, int],
    inferred_attribute_map: dict[str, set[str]] | None = None,
) -> tuple[str | None, float]:
    """Calculate MICA and Resnik similarity with deterministic ontology-breadth tie-breaking."""
    if term1_id == term2_id:
        return term1_id, term_ic_map.get(term1_id, 0.0)

    if inferred_attribute_map is None:
        common_ancestors = find_common_ancestors(term1_id, term2_id, parent_term_map)
    else:
        common_ancestors = inferred_attribute_map.get(term1_id, set()).intersection(
            inferred_attribute_map.get(term2_id, set())
        )

    if not common_ancestors:
        return None, 0.0

    mica = min(
        common_ancestors,
        key=lambda term_id: (
            -term_ic_map.get(term_id, 0.0),
            term_descendant_count_map[term_id],
            term_id,
        ),
    )
    similarity = term_ic_map.get(mica, 0.0)
    return mica, similarity


def _calculate_pair_jaccard(
    term1_id: str,
    term2_id: str,
    parent_term_map: dict[str, set[str]],
    inferred_attribute_map: dict[str, set[str]] | None = None,
) -> float:
    """Calculate OWLSim-style Jaccard index over self plus all ancestors."""
    if term1_id == term2_id:
        return 1.0
    if inferred_attribute_map is None:
        ancestors1 = _get_inferred_attributes(term1_id, parent_term_map)
        ancestors2 = _get_inferred_attributes(term2_id, parent_term_map)
    else:
        ancestors1 = inferred_attribute_map.get(term1_id, {term1_id})
        ancestors2 = inferred_attribute_map.get(term2_id, {term2_id})

    intersection = ancestors1.intersection(ancestors2)
    union = ancestors1.union(ancestors2)

    if not union:
        return 0.0

    jaccard_index = len(intersection) / len(union)
    return jaccard_index


def _calculate_pair_msca_score_map(
    term1_id: str,
    term2_id: str,
    parent_term_map: dict[str, set[str]],
    term_ic_map: dict[str, float],
    term_descendant_count_map: dict[str, int],
    inferred_attribute_map: dict[str, set[str]] | None = None,
) -> tuple[tuple[str, str], dict[str | None, float]]:
    """Calculate pairwise term similarity.
    Pairwise term similarity: sqrt(Resnik similarity * Jaccard index).
    msca: Most Specific Common Ancestor
    """
    term_pairs = tuple(sorted((term1_id, term2_id)))

    if term1_id == term2_id:
        msca = term1_id
        resnik = term_ic_map.get(term1_id, 0.0)
        jaccard = 1.0
    else:
        msca, resnik = _calculate_pair_mica_and_resnik(
            term1_id,
            term2_id,
            parent_term_map,
            term_ic_map,
            term_descendant_count_map,
            inferred_attribute_map,
        )
        jaccard = _calculate_pair_jaccard(term1_id, term2_id, parent_term_map, inferred_attribute_map)

    score = math.sqrt(resnik * jaccard)

    return term_pairs, {msca: score}


def _calculate_pair_worker(term_pair: tuple[str, str]) -> tuple[tuple[str], dict[str | None, float]]:
    """Worker-side calculation using globals set by _init_worker."""
    term1_id, term2_id = term_pair

    parent_term_map = _worker_parent_term_map
    inferred_attribute_map = _worker_inferred_attribute_map
    term_ic_map = _worker_term_ic_map
    term_descendant_count_map = _worker_term_descendant_count_map
    if (
        parent_term_map is None
        or inferred_attribute_map is None
        or term_ic_map is None
        or term_descendant_count_map is None
    ):
        raise RuntimeError("Worker maps are not initialized.")

    return _calculate_pair_msca_score_map(
        term1_id,
        term2_id,
        parent_term_map,
        term_ic_map,
        term_descendant_count_map,
        inferred_attribute_map,
    )


def calculate_all_pairwise_similarities(
    ontology_terms: dict[str, dict],
    all_term_ids: set[str],
    genewise_phenotype_significants: list[dict[str, str | float]] | None = None,
    threads: int = 1,
    annotation_records: list[dict[str, str | float]] | None = None,
) -> tuple[dict[tuple[str], dict[str | None, float]], dict[str, float]]:
    """Calculate pairwise term similarities for all term IDs."""
    if genewise_phenotype_significants is None:
        if annotation_records is None:
            raise ValueError("genewise_phenotype_significants is required for annotation-frequency IC.")
        genewise_phenotype_significants = annotation_records

    parent_term_map, child_term_map = build_term_hierarchy(ontology_terms)
    term_ic_map = _calculate_term_ic_map(ontology_terms, parent_term_map, genewise_phenotype_significants)
    term_descendant_count_map = _calculate_term_descendant_count_map(ontology_terms, child_term_map)
    term_list = sorted(all_term_ids)
    inferred_attribute_map = _calculate_inferred_attribute_map(set(term_list), parent_term_map)

    terms_similarity_map: dict[tuple[str, str], dict[str | None, float]] = {}

    if threads == 1:
        for term1_id, term2_id in combinations_with_replacement(term_list, 2):
            term_pairs, msca_score_map = _calculate_pair_msca_score_map(
                term1_id,
                term2_id,
                parent_term_map,
                term_ic_map,
                term_descendant_count_map,
                inferred_attribute_map,
            )
            terms_similarity_map[term_pairs] = msca_score_map
        return terms_similarity_map, term_ic_map

    with ProcessPoolExecutor(
        max_workers=threads,
        mp_context=_get_process_pool_context(),
        initializer=_init_worker,
        initargs=(parent_term_map, inferred_attribute_map, term_ic_map, term_descendant_count_map),
    ) as executor:
        term_pairs_iterable = combinations_with_replacement(term_list, 2)
        chunksize = max(1, len(term_list) * (len(term_list) + 1) // (threads * 16))
        for term_pairs, msca_score_map in executor.map(
            _calculate_pair_worker,
            term_pairs_iterable,
            chunksize=chunksize,
        ):
            terms_similarity_map[term_pairs] = msca_score_map

    return terms_similarity_map, term_ic_map


###########################################################
# Phenotype ancestor annotation
###########################################################


def _delete_parent_terms_from_ancestors(
    candidate_ancestors: list[dict[str, str]],
    term_ancestor_map: dict[str, set[str]],
) -> list[dict[str, str]]:
    """
    Remove parent terms from the common ancestors.
    Keep only the most specific terms among candidates with identical metadata.
    """
    to_delete: set[int] = set()
    grouped_candidates: dict[tuple[str, str, str], list[tuple[int, str]]] = defaultdict(list)

    for idx, ancestor in enumerate(candidate_ancestors):
        meta_signature = (
            ancestor["zygosity"],
            ancestor["life_stage"],
            ancestor["sexual_dimorphism"],
        )
        grouped_candidates[meta_signature].append((idx, ancestor["mp_term_name"]))

    for candidates in grouped_candidates.values():
        index_by_term = {term_id: idx for idx, term_id in candidates}
        candidate_terms = set(index_by_term)
        for _, term_id in candidates:
            for parent_term_id in term_ancestor_map.get(term_id, set()).intersection(candidate_terms):
                to_delete.add(index_by_term[parent_term_id])

    return [ancestor for i, ancestor in enumerate(candidate_ancestors) if i not in to_delete]


def _calculate_term_ancestor_map(term_ids: Iterable[str], parent_term_map: dict[str, set[str]]) -> dict[str, set[str]]:
    """Precompute ancestor sets used to prune parent phenotype annotations."""
    return {term_id: find_all_ancestor_terms(term_id, parent_term_map) for term_id in term_ids}


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


def _meta_signature_to_dict(meta_signature: tuple[str, str, str]) -> dict[str, str]:
    """Convert the compact metadata signature into the pairwise annotation schema."""
    zygosity, life_stage, sexual_dimorphism = meta_signature
    return {
        "zygosity": zygosity,
        "life_stage": life_stage,
        "sexual_dimorphism": sexual_dimorphism,
    }


def _annotate_ancestors(
    gene1_meta_map: dict,
    gene2_meta_map: dict,
    terms_similarity_map: dict[tuple[str, str], dict[str, float]],
    term_ancestor_map: dict[str, set[str]],
) -> list[dict[str, str]]:
    """Annotate phenotype ancestors for a single gene pair."""

    candidate_ancestors: list[dict[str, str]] = []
    added_keys: set[tuple[str, tuple[str, str, str]]] = set()

    shared_meta_signatures = set(gene1_meta_map.keys()) & set(gene2_meta_map.keys())
    for meta_signature in shared_meta_signatures:
        gene1_terms = gene1_meta_map[meta_signature]
        gene2_terms = gene2_meta_map[meta_signature]
        meta_dict = _meta_signature_to_dict(meta_signature)

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

                candidate_ancestors.append({"mp_term_name": common_ancestor, **meta_dict})
                added_keys.add(current_key)

    # Remove parent terms from candidate ancestors
    ancestors = _delete_parent_terms_from_ancestors(candidate_ancestors, term_ancestor_map)

    return ancestors


def annotate_phenotype_ancestors(
    genewise_phenotype_significants: list[dict[str, str | float]],
    terms_similarity_map: dict[tuple[str, str], dict[str, float]],
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
    parent_term_map, _ = build_term_hierarchy(ontology_terms)
    term_ancestor_map = _calculate_term_ancestor_map(ontology_terms, parent_term_map)
    annotations: set[str] = {"zygosity", "life_stage", "sexual_dimorphism"}
    gene_metadata_map, _ = _build_gene_metadata_maps(gene_records_map, annotations)

    for (gene1_symbol, gene1_meta_map), (gene2_symbol, gene2_meta_map) in combinations(gene_metadata_map.items(), 2):
        ancestors = _annotate_ancestors(
            gene1_meta_map=gene1_meta_map,
            gene2_meta_map=gene2_meta_map,
            terms_similarity_map=terms_similarity_map,
            term_ancestor_map=term_ancestor_map,
        )
        yield {
            "gene1_symbol": gene1_symbol,
            "gene2_symbol": gene2_symbol,
            "phenotype_shared_annotations": ancestors,
        }


###########################################################
# Phenodigm score calculation
###########################################################


def _calculate_similarity_matrix(
    gene1_record: dict[str, np.ndarray],
    gene2_record: dict[str, np.ndarray],
    terms_similarity_map: dict[tuple[str, str], dict[str, float]],
) -> np.ndarray:
    """Calculate the PhenoDigm term similarity matrix between two genes."""
    gene1_terms = gene1_record["terms"]
    gene2_terms = gene2_record["terms"]

    similarity_matrix = np.zeros((len(gene1_terms), len(gene2_terms)), dtype=float)
    for i, term1 in enumerate(gene1_terms):
        row = similarity_matrix[i]
        for j, term2 in enumerate(gene2_terms):
            _, similarity = next(iter(terms_similarity_map.get(tuple(sorted([term1, term2])), {None: 0.0}).items()))
            row[j] = similarity

    return similarity_matrix


def _apply_phenodigm_scaling(
    similarity_matrix: np.ndarray,
    gene1_record: dict[str, np.ndarray],
    gene2_record: dict[str, np.ndarray],
) -> float:
    """Apply PhenoDigm max/average percentage scaling to similarity scores."""
    # Calculate max and average scores from the observed gene pair.
    max_row_similarities = similarity_matrix.max(axis=1)
    max_column_similarities = similarity_matrix.max(axis=0)

    max_score_real_model = np.max([np.max(max_row_similarities), np.max(max_column_similarities)])
    average_score_real_model = np.mean(np.concatenate([max_row_similarities, max_column_similarities]))

    # Calculate max and average scores from the symmetric TSUMUGI optimal match.
    max_score_best_model = max(gene1_record["similarity_max"], gene2_record["similarity_max"])
    combined_similarity_scores = np.concatenate([gene1_record["similarity_scores"], gene2_record["similarity_scores"]])
    average_score_best_model = float(np.mean(combined_similarity_scores))

    # Normalize scores and compute final Phenodigm score
    normalized_max_score = max_score_real_model / max_score_best_model if max_score_best_model > 0 else 0.0
    normalized_average_score = (
        average_score_real_model / average_score_best_model if average_score_best_model > 0 else 0.0
    )

    phenodigm_score = 100 * (normalized_max_score + normalized_average_score) / 2

    return float(phenodigm_score)


def _calculate_phenodigm(
    gene1_record: dict[str, np.ndarray],
    gene2_record: dict[str, np.ndarray],
    terms_similarity_map: dict[tuple[str, str], dict[str, float]],
) -> float:
    """Calculate the Phenodigm score for a single gene pair."""
    similarity_matrix = _calculate_similarity_matrix(
        gene1_record,
        gene2_record,
        terms_similarity_map,
    )

    if np.max(similarity_matrix) == 0:
        return 0.0

    score = _apply_phenodigm_scaling(
        similarity_matrix,
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
        # Self similarity is sqrt(IC * 1.0) because simJ is 1.0 for identical terms.
        similarity_scores = np.sqrt(np.array([term_ic_map.get(term, 0.0) for term in terms], dtype=float))

        gene_data_map[gene_symbol] = {
            "terms": terms,
            "similarity_scores": similarity_scores,
            "similarity_max": float(similarity_scores.max()) if similarity_scores.size else 0.0,
        }

    return gene_data_map


def calculate_phenodigm_score(
    genewise_phenotype_significants: list[dict[str, str | float]],
    terms_similarity_map: dict[tuple[str, str], dict[str, float]],
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
        score_int = int(round(score))
        yield {"gene1_symbol": gene1_symbol, "gene2_symbol": gene2_symbol, "phenotype_similarity_score": score_int}


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

    for phenotype_ancestor, phenodigm_score in tqdm(
        zip(phenotype_ancestors, phenodigm_scores, strict=True), total=total_pairs
    ):
        gene1_symbol = phenotype_ancestor["gene1_symbol"]
        gene2_symbol = phenotype_ancestor["gene2_symbol"]

        ancestors: list[dict[str, str]] = phenotype_ancestor["phenotype_shared_annotations"]

        ancestors_renamed = []
        for ancestor in ancestors:
            renamed_ancestor = {}
            for k, v in ancestor.items():
                if k == "mp_term_name" and v in id_name_map:
                    renamed_ancestor["mp_term_name"] = id_name_map[v]
                else:
                    renamed_ancestor[k] = v
            ancestors_renamed.append(renamed_ancestor)

        phenodigm_score = phenodigm_score["phenotype_similarity_score"] if ancestors_renamed else 0

        annotations = {
            "gene1_symbol": gene1_symbol,
            "gene2_symbol": gene2_symbol,
            "phenotype_shared_annotations": sorted(
                ancestors_renamed,
                key=lambda x: [x["mp_term_name"], x["zygosity"], x["life_stage"], x["sexual_dimorphism"]],
            ),
            "phenotype_similarity_score": phenodigm_score,
        }

        yield annotations
