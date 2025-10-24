from __future__ import annotations

import math
from collections.abc import Iterator
from itertools import groupby
from operator import itemgetter

from tqdm import tqdm

from TSUMUGI.formatter import floatinize_columns


def subset_columns(records: Iterator[dict[str, str]], columns: set[str]) -> list[dict[str, str]]:
    """Return list[dict] keeping only the requested columns; missing keys become empty strings."""
    return [{col: record.get(col, "") for col in columns} for record in records]


def _is_significant(rec: dict[str, float | str], threshold: float) -> bool:
    """Significance rule:
    - If p_value is NaN and effect_size is finite -> keep.
        * some phenotypes may have significance without no p_value but an effect_size
        (e.g. Exoc6: https://www.mousephenotype.org/data/genes/MGI:1351611)
    - OR any of the three p-values is below threshold -> keep.
    """
    if math.isnan(rec["p_value"]) and not math.isnan(rec["effect_size"]):
        return True
    return (
        rec["p_value"] < threshold
        or rec["female_ko_effect_p_value"] < threshold
        or rec["male_ko_effect_p_value"] < threshold
    )


def extract_significant_phenotypes(
    records: Iterator[dict[str, str]], float_columns: list[str], threshold: float = 1e-4
) -> list[dict[str, float | str]]:
    """
    Filter significant phenotype records and drop exact duplicates (key+value match).
    """
    significants: list[dict[str, float | str]] = []

    for record in tqdm(records, desc="Filtering significant phenotypes"):
        # Skip when 'mp_term_name' is empty
        if not record.get("mp_term_name"):
            continue

        # Normalize numeric fields and evaluate significance
        record = floatinize_columns(record, float_columns)
        if _is_significant(record, threshold):
            significants.append(record)

    # Deduplicate by full key-value equality; ordering does not matter
    # Use a sorted tuple of items as a stable, hashable fingerprint.
    seen = set()
    unique_records = []
    for record in significants:
        fingerprint = tuple(sorted(record.items()))
        if fingerprint not in seen:
            seen.add(fingerprint)
            unique_records.append(record)

    return unique_records


###########################################################
# Others
###########################################################


def distinct_records_with_max_effect(
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
