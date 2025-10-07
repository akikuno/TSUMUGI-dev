from __future__ import annotations

import re

from TSUMUGI.formatter import format_disease_annotations

###########################################################
# annotate_life_stage
###########################################################


def _annotate_life_stage(procedure_name: str, pipeline_name: str, embryo_pattern: re.Pattern) -> str:
    if bool(embryo_pattern.search(procedure_name)):
        return "embryo"
    if "Interval" in pipeline_name or "interval" in pipeline_name:
        return "interval"
    elif "Late" in pipeline_name or "late" in pipeline_name:
        return "late"
    else:
        return "early"


def annotate_life_stage(records_significants, embryo_assays: set[str]) -> list[dict]:
    embryo_pattern = re.compile("|".join(map(re.escape, embryo_assays)))
    for record in records_significants:
        record["life_stage"] = _annotate_life_stage(record["procedure_name"], record["pipeline_name"], embryo_pattern)
    return records_significants


###########################################################
# annotate_sexual_dimorphism
###########################################################


def _annotate_sexual_dimorphism(
    female_ko_effect_p_value: float, male_ko_effect_p_value: float, threshold: float = 1e-4
) -> str:
    if female_ko_effect_p_value <= threshold and male_ko_effect_p_value > threshold:
        return "female"
    elif male_ko_effect_p_value <= threshold and female_ko_effect_p_value > threshold:
        return "male"
    else:
        return ""


def annotate_sexual_dimorphism(records_significants, threshold: float = 1e-4) -> list[dict]:
    for record in records_significants:
        record["sexual_dimorphism"] = _annotate_sexual_dimorphism(
            record["female_ko_effect_p_value"], record["male_ko_effect_p_value"], threshold
        )
    return records_significants


###########################################################
# annotate_human_disease
###########################################################


def _annotate_human_disease(
    allele_symbol: str, zygosity: str, life_stage: str, allele_phenodigm: dict[str, dict[str | str | float]]
) -> dict[str | str | float] | dict:
    """Annotate human disease information from Phenodigm records."""
    record_phenodigm = allele_phenodigm.get(allele_symbol, {})

    if not record_phenodigm:
        return {}
    zygosity_phenodigm = record_phenodigm["zygosity"]
    life_stage_phenodigm = record_phenodigm["life_stage"]

    if zygosity == zygosity_phenodigm and life_stage == life_stage_phenodigm:
        return record_phenodigm
    else:
        return {}


def annotate_human_disease(
    records_significants, disease_annotations: dict[str, dict[str | str | float]]
) -> list[dict]:
    """Annotate human disease information from Phenodigm records."""
    allele_phenodigm = format_disease_annotations(disease_annotations)
    for record in records_significants:
        record |= _annotate_human_disease(
            record["allele_symbol"], record["zygosity"], record["life_stage"], allele_phenodigm
        )


###########################################################
# annotate_impc_urls
###########################################################


def annotate_impc_urls(records_significants) -> list[dict]:
    for record in records_significants:
        gene_symbol = record["gene_symbol"]
        allele_symbol = record["allele_symbol"]
        record["impc_gene_url"] = f"https://www.mousephenotype.org/data/genes/{gene_symbol}"
        record["impc_allele_url"] = f"https://www.mousephenotype.org/data/alleles/{allele_symbol}"
    return records_significants
