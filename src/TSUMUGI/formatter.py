from __future__ import annotations

from itertools import groupby

###########################################################
# String to Float
###########################################################


def to_float(x: str | None) -> float:
    """Convert a string to float; empty/None becomes NaN."""
    return float(x) if x not in (None, "") else float("nan")


def floatinize_columns(record: dict[str, str], columns: list[str]) -> dict[str, str | float]:
    """Return a record with numeric fields coerced to float/NaN."""
    for col in columns:
        record[col] = to_float(record.get(col))
    return record


def abs_effect_size(record: dict[str, float | str]) -> dict[str, str | float]:
    """Return a record with the absolute effect size."""
    record["effect_size"] = abs(record["effect_size"])
    return record


def format_statistics_float(records: list[dict[str, str | None]], columns: list[str]) -> list[dict[str, str | float]]:
    """Format statistics by converting string values to float."""
    for record in records:
        record = floatinize_columns(record, columns)
        record = abs_effect_size(record)
    return records


###########################################################
# Phenodigm
###########################################################


def format_phenodigm_record(records_phenodigm: list[dict[str, str | float]]) -> dict[str, dict[str, str | float]]:
    """Format the phenodigm records for output."""

    zygosity_converter = {"het": "heterozygote", "hom": "homozygote", "hem": "hemizygote"}
    life_stage_converter = {"middle": "interval"}
    for record in records_phenodigm:
        description = record["description"]
        description_split = description.split(" ")
        allele_symbol = "".join(description_split[:-2])
        zygosity = description_split[-2]
        life_stage = description_split[-1]
        # Apply converters
        zygosity = zygosity_converter.get(zygosity, zygosity)
        life_stage = life_stage_converter.get(life_stage, life_stage)
        # Update record with new values
        record["allele_symbol"] = allele_symbol
        record["zygosity"] = zygosity
        record["life_stage"] = life_stage
        # Delete used fields
        del record["description"]

    # Using allele_symbol as the key makes it easier to join with IMPC phenotype records later
    return {r["allele_symbol"]: r for r in records_phenodigm}


###########################################################
# Others
###########################################################
def distinct_records(records: list[dict[str, str | float]]) -> list[dict[str, str | float]]:
    """
    Return a list of distinct records with the maximum effect size.
    Note: effect size is already absolute.
    """

    def record_key(x: dict[str, str | float]) -> tuple[str, str, str, str]:
        return (x["marker_symbol"], x["mp_term_name"], x["zygosity"], x["life_stage"])

    records_distinct = []
    records_sorted = sorted(records, key=record_key)

    for _, group in groupby(records_sorted, key=record_key):
        max_effect_size = -1
        for record in group:
            if record["effect_size"] > max_effect_size:
                records_max = record
                max_effect_size = record["effect_size"]
        records_distinct.append(records_max)

    return records_distinct
