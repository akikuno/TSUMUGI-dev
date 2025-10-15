from __future__ import annotations

import gzip
import json
import math
from collections import defaultdict
from itertools import groupby
from operator import itemgetter
from pathlib import Path

###########################################################
# Zygosity Formatting
###########################################################


def format_zygosity(records_significants) -> str:
    """Format zygosity values to a consistent style."""
    zygosity_converter = {"heterozygote": "Hetero", "homozygote": "Homo", "hemizygote": "Hemi"}
    for record in records_significants:
        record["zygosity"] = zygosity_converter.get(record["zygosity"], record["zygosity"])
    return records_significants


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


def abs_effect_size(record: dict[str, str | float]) -> dict[str, str | float]:
    """Return a record with the absolute effect size and NaN replaced with 0."""
    if math.isnan(record["effect_size"]):
        record["effect_size"] = 0
    record["effect_size"] = abs(record["effect_size"])
    return record


###########################################################
# IMPC human disease_annotations
###########################################################


def _select_fields_from_disease_annotations(disease_annotations: list[dict[str, str]]) -> list[dict[str, str]]:
    """Select disorder_name and description fields from IMPC human disease_annotations."""

    # Heuristic to identify the correct fields
    prev_disorder_name = None
    prev_description = None
    for record in disease_annotations:
        for key, value in record.items():
            if "Syndrome" in value:
                prev_disorder_name = key
            if "<em1(IMPC)Bay>" in value:
                prev_description = key
        if prev_disorder_name is not None and prev_description is not None:
            break

    if prev_disorder_name is None or prev_description is None:
        raise ValueError("Could not identify disorder_name or description fields in disease_annotations.")

    # Select the fields
    disease_annotations_selected = []
    for record in disease_annotations:
        disease_annotations_selected.append(
            {"disorder_name": record[prev_disorder_name], "description": record[prev_description]}
        )

    return disease_annotations_selected


def format_disease_annotations(disease_annotations: list[dict[str, str | float]]) -> dict[str, list[dict[str, str]]]:
    """Format the IMPC human disease_annotations for output."""

    # Select "description" and "disorder_name" fields
    disease_annotations = _select_fields_from_disease_annotations(disease_annotations)

    # Filter out records with unexpected description format: expected format is "<allele_symbol> <zygosity> <life_stage>"
    disease_annotations = [record for record in disease_annotations if len(record["description"].split(" ")) == 3]

    zygosity_converter = {"het": "Hetero", "hom": "Homo", "hem": "Hemi"}
    life_stage_converter = {"middle": "Interval", "late": "Late", "early": "Early", "embryo": "Embryo"}

    for record in disease_annotations:
        description = record["description"]
        description_split = description.split(" ")
        marker_symbol = description.split("<")[0].strip()
        zygosity = description_split[-2]
        life_stage = description_split[-1]
        # Apply converters
        zygosity = zygosity_converter.get(zygosity, zygosity)
        life_stage = life_stage_converter.get(life_stage, life_stage)
        # Update record with new values
        record["marker_symbol"] = marker_symbol
        record["zygosity"] = zygosity
        record["life_stage"] = life_stage
        # Delete used fields
        del record["description"]

    # Using marker_symbol as the key makes it easier to join with IMPC phenotype records later
    disease_annotations_by_gene = defaultdict(list)
    appended_records = set()
    for record in disease_annotations:
        if tuple(record.items()) not in appended_records:
            appended_records.add(tuple(record.items()))
            marker_symbol = record["marker_symbol"]
            del record["marker_symbol"]
            disease_annotations_by_gene[marker_symbol].append(record)

    return dict(disease_annotations_by_gene)


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


###########################################################
# Convert report (jsonl.gz) files to `pair_similarity_annotations`:
# dict[frozenset[str], dict[str, dict[str, str] | int]]
###########################################################


def convert_jsonl_gz_to_pair_map(path_jsonl_gz: str | Path) -> dict[frozenset[str], dict[str, dict[str, str] | int]]:
    pair_similarity_annotations = {}
    with gzip.open(path_jsonl_gz, "rt", encoding="utf-8") as f:
        for obj in map(json.loads, f):
            gene1 = obj["gene1_symbol"]
            gene2 = obj["gene2_symbol"]
            pair = frozenset([gene1, gene2])
            del obj["gene1_symbol"]
            del obj["gene2_symbol"]
            pair_similarity_annotations[pair] = obj

    return pair_similarity_annotations
