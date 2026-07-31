from __future__ import annotations

import math
from collections.abc import Generator, Iterable, Iterator
from itertools import groupby
from operator import itemgetter


def subset_columns(records: Iterator[dict[str, str]], columns: set[str]) -> Generator[dict[str, str]]:
    """Return list[dict] keeping only the requested columns; missing keys become empty strings."""
    return ({col: record.get(col, "") for col in columns} for record in records)


###########################################################
# Others
###########################################################


def _effect_size_sort_key(record: dict[str, str | float]) -> float:
    value = record.get("effect_size")
    try:
        effect_size = float(value)
    except (TypeError, ValueError):
        return float("-inf")
    return effect_size if math.isfinite(effect_size) else float("-inf")


def distinct_records_with_max_effect(
    records: Iterable[dict[str, str | float]],
    unique_keys: list[str],
    prefer_significant: bool = False,
) -> Generator[dict[str, str | float]]:
    """
    Groups records by the specified keys and returns the record with the maximum
    effect_size from each group.
    Note: effect_size is already an absolute value.
    """
    # Dynamically define the key function based on unique_keys.
    record_key_getter = itemgetter(*unique_keys)

    # Pre-sort by the same key for groupby to function correctly.
    records_sorted = sorted(records, key=record_key_getter)

    for _, group in groupby(records_sorted, key=record_key_getter):
        if prefer_significant:
            record_with_max_effect = max(
                group,
                key=lambda record: (
                    bool(record.get("significant", False)),
                    _effect_size_sort_key(record),
                ),
            )
        else:
            record_with_max_effect = max(group, key=_effect_size_sort_key)
        yield record_with_max_effect
