from __future__ import annotations

import re

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


def annotate_life_stage(records_annotated, embryo_assays: set[str]) -> list[dict]:
    embryo_pattern = re.compile("|".join(map(re.escape, embryo_assays)))
    for record in records_annotated:
        record["life_stage"] = _annotate_life_stage(record["procedure_name"], record["pipeline_name"], embryo_pattern)

    return records_annotated


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


def annotate_sexual_dimorphism(records_annotated, threshold: float = 1e-4) -> list[dict]:
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

    return records_annotated


###########################################################
# annotate_diseases
###########################################################


def annotate_diseases(records_annotated, disease_annotations_by_gene: dict) -> list[dict]:
    for record in records_annotated:
        if not record["significant"]:
            record["disease_annotation"] = []
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

    return records_annotated


def annotate_non_significant_terms(records_annotated: list[dict]) -> list[dict]:
    for record in records_annotated:
        if record["mp_term_id"]:
            record["significant"] = True
            continue
        record["effect_size"] = 0.0
        record["p_value"] = 1.0
        record["significant"] = False
        record["mp_term_id"] = record["intermediate_mp_term_id"].split(",")[-1]
        record["mp_term_name"] = record["intermediate_mp_term_name"].split(",")[-1]
    return records_annotated
