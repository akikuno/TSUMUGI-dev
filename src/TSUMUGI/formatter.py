from __future__ import annotations

from itertools import groupby
from operator import itemgetter

import polars as pl

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
# IMPC human disease_annotations
###########################################################


def format_disease_annotations(disease_annotations: list[dict[str, str | float]]) -> dict[str, dict[str, str | float]]:
    """Format the IMPC human disease_annotations for output."""

    zygosity_converter = {"het": "heterozygote", "hom": "homozygote", "hem": "hemizygote"}
    life_stage_converter = {"middle": "interval"}
    for record in disease_annotations:
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
    return {r["allele_symbol"]: r for r in disease_annotations}


###########################################################
# Others
###########################################################


def get_distinct_records_with_max_effect(
    records: list[dict[str, str | float]], unique_keys: list[str]
) -> list[dict[str, str | float]]:
    """
    Groups records by the specified keys and returns the record with the maximum
    effect_size from each group.
    Note: effect_size is already an absolute value.
    """
    # Dynamically define the key function based on unique_keys.
    record_key_getter = itemgetter(*unique_keys)

    # Pre-sort by the same key for groupby to function correctly.
    records_sorted = sorted(records, key=record_key_getter)

    distinct_records = []
    for _, group in groupby(records_sorted, key=record_key_getter):
        # Find the record with the maximum effect_size within the group.
        # Use .get() to safely handle cases where the 'effect_size' key might be missing.
        record_with_max_effect = max(group, key=lambda r: r.get("effect_size", -1))
        distinct_records.append(record_with_max_effect)

    return distinct_records


def fill_nulls_to_nan_str(df_polars: pl.DataFrame) -> pl.DataFrame:
    """Fill nulls in Float64 columns with NaN and in Utf8 columns with an empty string."""
    exprs = []
    for name, dtype in df_polars.schema.items():
        if dtype == pl.Float64:
            exprs.append(pl.col(name).fill_null(float("nan")))
        elif dtype == pl.Utf8:
            exprs.append(pl.col(name).fill_null(""))
        else:
            exprs.append(pl.col(name))  # No change
    return df_polars.with_columns(exprs)
