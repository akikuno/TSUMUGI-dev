from __future__ import annotations

from collections.abc import Iterator
from formatter import floatinize_columns


def subset_columns(records: Iterator[dict[str, str]], columns: list[str]) -> Iterator[dict[str, str]]:
    """Yield dicts keeping only the requested columns; missing keys become empty strings."""
    for record in records:
        yield {col: record.get(col, "") for col in columns}


def _normalized_record(record: dict[str, str]) -> dict[str, float | str]:
    """Return a shallow-copied record with numeric fields coerced to float/Inf."""
    record = floatinize_columns(
        record, ["p_value", "female_ko_effect_p_value", "male_ko_effect_p_value", "effect_size"]
    )
    return record


def _is_significant(rec: dict[str, float | str], threshold: float) -> bool:
    """Significance rule:
    - If p_value is Inf and effect_size is finite -> keep.
    - OR any of the three p-values is below threshold -> keep."""
    if rec["p_value"] == float("inf") and rec["effect_size"] != float("inf"):
        return True
    return (
        rec["p_value"] < threshold
        or rec["female_ko_effect_p_value"] < threshold
        or rec["male_ko_effect_p_value"] < threshold
    )


def extract_significant_phenotypes(
    records: Iterator[dict[str, str]], threshold: float = 1e-4
) -> list[dict[str, float | str]]:
    """Filter significant phenotype records and drop exact duplicates (key+value match)."""
    significants: list[dict[str, float | str]] = []

    for record in records:
        # Skip when 'mp_term_name' is empty
        if not record.get("mp_term_name"):
            continue

        # Normalize numeric fields and evaluate significance
        rec = _normalized_record(record)
        if _is_significant(rec, threshold):
            significants.append(rec)

    # Deduplicate by full key-value equality; ordering does not matter
    # Use a sorted tuple of items as a stable, hashable fingerprint.
    seen: set[tuple[tuple[str, float | str], ...]] = set()
    unique: list[dict[str, float | str]] = []
    for rec in significants:
        fingerprint = tuple(sorted(rec.items()))
        if fingerprint not in seen:
            seen.add(fingerprint)
            unique.append(rec)

    return unique
