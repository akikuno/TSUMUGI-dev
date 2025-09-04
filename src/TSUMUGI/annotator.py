from __future__ import annotations

import re


def annotate_life_stage(procedure_name: str, pipeline_name: str, embryo_pattern: re.Pattern) -> str:
    if bool(embryo_pattern.search(procedure_name)):
        return "Embryo"
    if "Interval" in pipeline_name or "interval" in pipeline_name:
        return "Interval"
    elif "Late" in pipeline_name or "late" in pipeline_name:
        return "Late"
    else:
        return "Early"
