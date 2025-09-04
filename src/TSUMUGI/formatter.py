from __future__ import annotations

INF = float("inf")


def to_float(x) -> float:
    """Convert a string to float; empty/None becomes +Inf."""
    return float(x) if x not in (None, "") else INF


def floatinize_columns(record: dict[str, str], columns: list[str]) -> dict[str, float | str]:
    """Return a shallow-copied record with numeric fields coerced to float/Inf."""
    for col in columns:
        record[col] = to_float(record.get(col))
    return record
