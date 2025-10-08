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


def annotate_life_stage(records_significants, embryo_assays: set[str]) -> list[dict]:
    embryo_pattern = re.compile("|".join(map(re.escape, embryo_assays)))
    for record in records_significants:
        record["life_stage"] = _annotate_life_stage(record["procedure_name"], record["pipeline_name"], embryo_pattern)
        del record["procedure_name"]
        del record["pipeline_name"]

    return records_significants


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
        return ""


def annotate_sexual_dimorphism(records_significants, threshold: float = 1e-4) -> list[dict]:
    for record in records_significants:
        record["sexual_dimorphism"] = _annotate_sexual_dimorphism(
            record["female_ko_effect_p_value"], record["male_ko_effect_p_value"], threshold
        )
        del record["female_ko_effect_p_value"]
        del record["male_ko_effect_p_value"]
    return records_significants
