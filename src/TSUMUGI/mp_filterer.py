from __future__ import annotations

from pathlib import Path

from TSUMUGI import io_handler, ontology_handler

###########################################################
# Exclude gene pairs with target_mp_term_id and its descendants
###########################################################


def exclude_specific_phenotype(
    path_pairwise_similarity_annotations: str | Path,
    path_genewise_phenotype_annotations: str | Path,
    path_obo: str | Path,
    mp_term_id: set[str],
    life_stage: str | None = None,
    sex: str | None = None,
    zygosity: str | None = None,
) -> None:
    ontology_terms = io_handler.parse_obo_file(path_obo)
    parent_term_map, child_term_map = ontology_handler.build_term_hierarchy(ontology_terms)
    descendants_of_term_id = ontology_handler.find_all_descendant_terms(mp_term_id, child_term_map)
    ancesters_of_term_id = ontology_handler.find_all_ancestor_terms(mp_term_id, parent_term_map)

    # If a gene exhibits a significant abnormal phenotype annotated to
    # the target mp_term_id or any of its descendant terms,
    # the gene is classified as “having a phenotype.”
    genewise_phenotype_annotations = io_handler.read_jsonl(Path(path_genewise_phenotype_annotations))
    genes_with_phenotype = set()
    for record in genewise_phenotype_annotations:
        condition1 = record["mp_term_id"] == mp_term_id
        condition2 = record["mp_term_id"] in descendants_of_term_id
        if (condition1 or condition2) and record["significant"] is True:
            if life_stage is not None and record["life_stage"] != life_stage:
                continue
            if sex is not None and record["sexual_dimorphism"] != sex:
                continue
            if zygosity is not None and record["zygosity"] != zygosity:
                continue
            genes_with_phenotype.add(record["marker_symbol"])

    # For genes whose phenotype status remains undetermined in (1),
    # if a non-significant phenotype annotation exists for the target mp_term_id or any of
    # its ancestor terms, the gene is classified as “confirmed as having no phenotype.”
    genewise_phenotype_annotations = io_handler.read_jsonl(Path(path_genewise_phenotype_annotations))
    genes_without_phenotype = set()
    for record in genewise_phenotype_annotations:
        if record["marker_symbol"] in genes_with_phenotype:
            continue

        condition1 = record["mp_term_id"] == mp_term_id
        condition2 = record["mp_term_id"] in ancesters_of_term_id
        if (condition1 or condition2) and record["significant"] is False:
            if life_stage is not None and record["life_stage"] != life_stage:
                continue
            if sex is not None and record["sexual_dimorphism"] != sex:
                continue
            if zygosity is not None and record["zygosity"] != zygosity:
                continue
            genes_without_phenotype.add(record["marker_symbol"])

    # Now filter gene pairs based on genes_without_phenotype
    pairwise_similarity_annotations = io_handler.read_jsonl(path_pairwise_similarity_annotations)
    for record in pairwise_similarity_annotations:
        if record["gene1_symbol"] in genes_without_phenotype and record["gene2_symbol"] in genes_without_phenotype:
            # output to stdout as JSONL
            io_handler.safe_jsonl_dump(record)


def include_specific_phenotype(
    path_pairwise_similarity_annotations: str | Path,
    path_obo: str | Path,
    mp_term_id: str,
    life_stage: str | None = None,
    sex: str | None = None,
    zygosity: str | None = None,
) -> None:
    ontology_terms = io_handler.parse_obo_file(path_obo)
    _, child_term_map = ontology_handler.build_term_hierarchy(ontology_terms)
    descendants_of_term_id = ontology_handler.find_all_descendant_terms(mp_term_id, child_term_map)
    descendants_of_term_name = {
        data["name"] for term_id, data in ontology_terms.items() if term_id in descendants_of_term_id
    }

    pairwise_similarity_annotations = io_handler.read_jsonl(path_pairwise_similarity_annotations)
    for record in pairwise_similarity_annotations:
        target_term_names = set(record["phenotype_shared_annotations"].keys()).intersection(descendants_of_term_name)

        # If none of the target terms are present, skip
        if not target_term_names:
            continue

        # Check if any of the target terms have the specified phenotype
        has_phenotype = False
        for term_name in target_term_names:
            annotation = record["phenotype_shared_annotations"][term_name]
            if life_stage is not None and annotation["life_stage"] != life_stage:
                continue
            if sex is not None and annotation["sexual_dimorphism"] != sex:
                continue
            if zygosity is not None and annotation["zygosity"] != zygosity:
                continue
            has_phenotype = True

        if has_phenotype:
            # output to stdout as JSONL
            io_handler.safe_jsonl_dump(record)
