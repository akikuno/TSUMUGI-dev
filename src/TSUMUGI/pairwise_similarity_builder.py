from __future__ import annotations

import logging
from collections.abc import Iterator

from TSUMUGI import similarity_calculator


def build_pairwise_similarity(
    genewise_phenotype_significants: list[dict], ontology_terms: set, args
) -> dict[tuple[str], dict[str, dict[str, str] | int]]:
    mp_term_ids = {r["mp_term_id"] for r in genewise_phenotype_significants}

    logging.info(f"Calculating pairwise similarity for {len(mp_term_ids)} terms...")

    terms_similarity_map, term_ic_map = similarity_calculator.calculate_all_pairwise_similarities(
        ontology_terms, mp_term_ids, ic_threshold=5, threads=args.threads
    )

    # ----------------------------------------
    # Calculate phenotype similarity
    # ----------------------------------------

    total_genes = {r["marker_symbol"] for r in genewise_phenotype_significants}
    num_pairs = len(total_genes) * (len(total_genes) - 1) // 2

    logging.info(f"Annotate phenotype ancestors for {num_pairs} pairs...")
    phenotype_ancestors = similarity_calculator.annotate_phenotype_ancestors(
        genewise_phenotype_significants,
        terms_similarity_map,
        ontology_terms,
    )

    logging.info(f"Calculating phenodigm similarity for {num_pairs} pairs...")
    phenodigm_scores = similarity_calculator.calculate_phenodigm_score(
        genewise_phenotype_significants, terms_similarity_map, term_ic_map
    )

    # if args.debug:
    #     logging.debug("Caching phenotype ancestors and phenodigm scores...")

    #     # --------------------------------------------------------
    #     # Cache results
    #     # --------------------------------------------------------

    #     output_dir = Path(args.output_dir, ".tempdir", "preprocessed")
    #     output_dir.mkdir(parents=True, exist_ok=True)

    #     io_handler.write_jsonl(phenotype_ancestors, output_dir / "phenotype_ancestors.jsonl.gz")
    #     io_handler.write_jsonl(phenodigm_scores, output_dir / "phenodigm_scores.jsonl.gz")

    #     phenotype_ancestors = io_handler.read_jsonl(output_dir / "phenotype_ancestors.jsonl.gz")
    #     phenodigm_scores = io_handler.read_jsonl(output_dir / "phenodigm_scores.jsonl.gz")

    # ----------------------------------------
    # Summarize the phenotype similarity results
    # ----------------------------------------

    logging.info(f"Integrating phenotype annotations and similarity score for {num_pairs} pairs...")

    pairwise_similarity_annotations: Iterator[dict[str, dict[str, str] | int]] = (
        similarity_calculator.summarize_similarity_annotations(
            ontology_terms, phenotype_ancestors, phenodigm_scores, num_pairs
        )
    )

    return pairwise_similarity_annotations
