from __future__ import annotations

from collections.abc import Iterator

INF = float("inf")


def subset_columns(records: Iterator[dict[str, str]], columns: list[str]) -> Iterator[dict[str, str]]:
    """Yield dicts keeping only the requested columns; missing keys become empty strings."""
    for record in records:
        yield {col: record.get(col, "") for col in columns}


def _to_float_or_inf(x) -> float:
    """Convert a string to float; empty/None becomes +Inf."""
    return float(x) if x not in (None, "") else INF


def _normalized_record(record: dict[str, str]) -> dict[str, float | str]:
    """Return a shallow-copied record with numeric fields coerced to float/Inf."""
    out = dict(record)  # avoid mutating the input iterator's backing data
    out["p_value"] = _to_float_or_inf(record.get("p_value"))
    out["female_ko_effect_p_value"] = _to_float_or_inf(record.get("female_ko_effect_p_value"))
    out["male_ko_effect_p_value"] = _to_float_or_inf(record.get("male_ko_effect_p_value"))
    out["effect_size"] = _to_float_or_inf(record.get("effect_size"))
    return out


def _is_significant(rec: dict[str, float | str], threshold: float) -> bool:
    """Significance rule:
    - If p_value is Inf and effect_size is finite -> keep.
    - OR any of the three p-values is below threshold -> keep."""
    if rec["p_value"] == INF and rec["effect_size"] != INF:
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
