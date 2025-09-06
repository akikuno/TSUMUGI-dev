from __future__ import annotations

from collections.abc import Iterator

from TSUMUGI.formatter import floatinize_columns


def subset_columns(records: Iterator[dict[str, str]], columns: list[str]) -> Iterator[dict[str, str]]:
    """Yield dicts keeping only the requested columns; missing keys become empty strings."""
    for record in records:
        yield {col: record.get(col, "") for col in columns}


def _is_significant(rec: dict[str, float | str], threshold: float) -> bool:
    """Significance rule:
    - If p_value is NaN and effect_size is finite -> keep.
        * preweaning lethal phenotypes may have significance without no p_value but an effect_size
    - OR any of the three p-values is below threshold -> keep.
    """
    if rec["p_value"] == float("nan") and rec["effect_size"] != float("nan"):
        return True
    return (
        rec["p_value"] < threshold
        or rec["female_ko_effect_p_value"] < threshold
        or rec["male_ko_effect_p_value"] < threshold
    )


def extract_significant_phenotypes(
    records: Iterator[dict[str, str]], threshold: float = 1e-4
) -> list[dict[str, float | str]]:
    """
    Filter significant phenotype records and drop exact duplicates (key+value match).
    """
    significants: list[dict[str, float | str]] = []

    float_columns = [
        "p_value",
        "effect_size",
        "female_ko_effect_p_value",
        "male_ko_effect_p_value",
        "female_ko_parameter_estimate",
        "male_ko_parameter_estimate",
    ]

    for record in records:
        # Skip when 'mp_term_name' is empty
        if not record.get("mp_term_name"):
            continue

        # Normalize numeric fields and evaluate significance
        record = floatinize_columns(record, float_columns)
        if _is_significant(record, threshold):
            significants.append(record)

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
