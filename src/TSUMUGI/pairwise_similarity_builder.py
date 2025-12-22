from __future__ import annotations

import logging
from collections.abc import Iterator

from TSUMUGI import similarity_calculator


def build_pairwise_similarity(
    genewise_phenotype_significants: list[dict], ontology_terms: set, threads: int, debug: bool = False
) -> dict[tuple[str], dict[str, dict[str, str] | int]]:
    mp_term_ids = {r["mp_term_id"] for r in genewise_phenotype_significants}

    logging.info(f"Calculating pairwise similarity for {len(mp_term_ids)} terms...")

    terms_resnik_map, term_ic_map = similarity_calculator.calculate_all_pairwise_similarities(
        ontology_terms, mp_term_ids, threads=threads
    )

    # ----------------------------------------
    # Calculate phenotype similarity
    # ----------------------------------------

    total_sorted_gene_symbols = sorted({r["marker_symbol"] for r in genewise_phenotype_significants})
    total_pairs = len(total_sorted_gene_symbols) * (len(total_sorted_gene_symbols) - 1) // 2

    logging.info(f"Annotate phenotype ancestors for {total_pairs} pairs...")
    phenotype_ancestors: dict[tuple[str], dict[str, dict[str, str]]] = (
        similarity_calculator.annotate_phenotype_ancestors(
            genewise_phenotype_significants,
            terms_resnik_map,
            ontology_terms,
            ic_threshold=5,
        )
    )

    logging.info(f"Calculating phenodigm similarity for {len(total_pairs)} pairs...")
    phenodigm_scores: dict[tuple[str], int] = similarity_calculator.calculate_phenodigm_score(
        genewise_phenotype_significants, terms_resnik_map, term_ic_map
    )

    # ----------------------------------------
    # Summarize the phenotype similarity results
    # ----------------------------------------

    logging.info(
        f"Integrating phenotype annotations and similarity score for {len(genewise_phenotype_significants)} records..."
    )
    pairwise_similarity_annotations: Iterator[dict[str, dict[str, str] | int]] = (
        similarity_calculator.summarize_similarity_annotations(ontology_terms, phenotype_ancestors, phenodigm_scores)
    )

    return pairwise_similarity_annotations, terms_resnik_map, phenotype_ancestors, phenodigm_scores
