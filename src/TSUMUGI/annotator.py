from __future__ import annotations

import re
from collections.abc import Generator, Iterable, Iterator

from TSUMUGI import ontology_handler

ROOT_MP_TERM_ID = "MP:0000001"

###########################################################
# annotate_life_stage
###########################################################


def _annotate_life_stage(procedure_name: str, pipeline_name: str, embryo_pattern: re.Pattern) -> str:
    if bool(embryo_pattern.search(procedure_name)):
        return "Embryo"
    if "Interval" in pipeline_name or "interval" in pipeline_name:
        return "Interval"
    elif "Late" in pipeline_name or "late" in pipeline_name:
        return "Late"
    else:
        return "Early"


def annotate_life_stage(records_annotated, embryo_assays: set[str]) -> Iterator[dict]:
    embryo_pattern = re.compile("|".join(map(re.escape, embryo_assays)))
    for record in records_annotated:
        record["life_stage"] = _annotate_life_stage(record["procedure_name"], record["pipeline_name"], embryo_pattern)

        yield record


###########################################################
# annotate_sexual_dimorphism
###########################################################


def _annotate_sexual_dimorphism(
    female_ko_effect_p_value: float, male_ko_effect_p_value: float, threshold: float = 1e-4
) -> str:
    if female_ko_effect_p_value <= threshold and male_ko_effect_p_value > threshold:
        return "Female"
    elif male_ko_effect_p_value <= threshold and female_ko_effect_p_value > threshold:
        return "Male"
    else:
        return "None"


def annotate_sexual_dimorphism(records_annotated, threshold: float = 1e-4) -> Generator[dict]:
    for record in records_annotated:
        # Annotate sexual dimorphism
        record["sexual_dimorphism"] = _annotate_sexual_dimorphism(
            record["female_ko_effect_p_value"], record["male_ko_effect_p_value"], threshold
        )

        # Set effect_size based on sexual_dimorphism
        if record["sexual_dimorphism"] == "Female":
            record["effect_size"] = record["female_ko_parameter_estimate"]
        elif record["sexual_dimorphism"] == "Male":
            record["effect_size"] = record["male_ko_parameter_estimate"]

        yield record


###########################################################
# annotate_diseases
###########################################################


def annotate_diseases(records_annotated, disease_annotations_by_gene: dict) -> Generator[dict]:
    for record in records_annotated:
        if not record["significant"]:
            record["disease_annotation"] = []
            yield record
            continue

        record["disease_annotation"] = set()

        marker = record["marker_symbol"]
        record_zygosity = record["zygosity"]
        record_life_stage = record["life_stage"]
        if marker in disease_annotations_by_gene:
            for disease_annotation in disease_annotations_by_gene[marker]:
                if (
                    record_zygosity == disease_annotation["zygosity"]
                    and record_life_stage == disease_annotation["life_stage"]
                ):
                    record["disease_annotation"].add(disease_annotation["disorder_name"])

        record["disease_annotation"] = sorted(record["disease_annotation"])

        yield record


def annotate_significant(records_annotated: Iterable[dict], ontology_terms: dict[str, dict]) -> Generator[dict]:
    parent_term_map, _ = ontology_handler.build_term_hierarchy(ontology_terms)
    ancestor_cache: dict[str, set[str]] = {}
    selection_cache: dict[str, tuple[str, ...]] = {}

    def find_ancestors(term_id: str) -> set[str]:
        if term_id not in ancestor_cache:
            ancestor_cache[term_id] = ontology_handler.find_all_ancestor_terms(term_id, parent_term_map)
        return ancestor_cache[term_id]

    def select_most_specific_terms(intermediate_mp_term_id: str) -> tuple[str, ...]:
        if intermediate_mp_term_id in selection_cache:
            return selection_cache[intermediate_mp_term_id]

        candidates = {
            term_id.strip()
            for term_id in intermediate_mp_term_id.split(",")
            if term_id.strip() in ontology_terms and term_id.strip() != ROOT_MP_TERM_ID
        }
        selected = tuple(
            sorted(
                term_id
                for term_id in candidates
                if not any(term_id in find_ancestors(other_term_id) for other_term_id in candidates - {term_id})
            )
        )
        selection_cache[intermediate_mp_term_id] = selected
        return selected

    for record in records_annotated:
        if record["mp_term_id"]:
            record["significant"] = True
            record["mp_term_name"] = ontology_terms.get(record["mp_term_id"], {}).get(
                "name",
                record["mp_term_name"],
            )
            yield record
            continue

        selected_term_ids = select_most_specific_terms(record["intermediate_mp_term_id"])
        for term_id in selected_term_ids:
            non_significant_record = record.copy()
            non_significant_record["effect_size"] = 0.0
            non_significant_record["p_value"] = 1.0
            non_significant_record["significant"] = False
            non_significant_record["mp_term_id"] = term_id
            non_significant_record["mp_term_name"] = ontology_terms[term_id].get("name", "")

            yield non_significant_record
