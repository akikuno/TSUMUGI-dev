from __future__ import annotations

import re


def annotate_life_stage(procedure_name: str, pipeline_name: str, embryo_pattern: re.Pattern) -> str:
    if bool(embryo_pattern.search(procedure_name)):
        return "embryo"
    if "Interval" in pipeline_name or "interval" in pipeline_name:
        return "interval"
    elif "Late" in pipeline_name or "late" in pipeline_name:
        return "late"
    else:
        return "early"


def annotate_sexual_dimorphism(
    female_ko_effect_p_value: float, male_ko_effect_p_value: float, threshold: float = 1e-4
) -> str:
    if female_ko_effect_p_value <= threshold and male_ko_effect_p_value > threshold:
        return "female"
    elif male_ko_effect_p_value <= threshold and female_ko_effect_p_value > threshold:
        return "male"
    else:
        return ""
