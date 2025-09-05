from __future__ import annotations

from itertools import groupby


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


def distinct_records(records: list[dict[str, str | float]]) -> list[dict[str, str | float]]:
    """Return a list of distinct records with the maximum absolute effect size."""
    records_distinct = []
    records_sorted = sorted(records, key=lambda x: (x["marker_symbol"], x["mp_term_name"]))
    for _, group in groupby(records_sorted, key=lambda x: (x["marker_symbol"], x["mp_term_name"])):
        max_abs_effect_size = -1
        for record in group:
            if max_abs_effect_size < abs(record["effect_size"]):
                records_max = record
                max_abs_effect_size = abs(record["effect_size"])
        records_distinct.append(records_max)
    return records_distinct
