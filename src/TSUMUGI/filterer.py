from __future__ import annotations

from collections.abc import Generator, Iterable, Iterator
from itertools import groupby
from operator import itemgetter


def subset_columns(records: Iterator[dict[str, str]], columns: set[str]) -> Generator[dict[str, str]]:
    """Return list[dict] keeping only the requested columns; missing keys become empty strings."""
    return ({col: record.get(col, "") for col in columns} for record in records)


###########################################################
# Others
###########################################################


def distinct_records_with_max_effect(
    records: Iterable[dict[str, str | float]], unique_keys: list[str]
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
        # Find the record with the maximum effect_size within the group.
        # Use .get() to safely handle cases where the 'effect_size' key might be missing.
        record_with_max_effect = max(group, key=lambda r: r.get("effect_size", -1))
        yield record_with_max_effect
