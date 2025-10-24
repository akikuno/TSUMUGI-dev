from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable

###########################################################
# String to Float
###########################################################


def _to_float(x: str | None) -> float:
    """Convert a string to float; empty/None becomes NaN."""
    return float(x) if x not in (None, "") else float("nan")


def floatinize_columns(record: dict[str, str], columns: list[str]) -> dict[str, str | float]:
    """Return a record with numeric fields coerced to float/NaN."""
    for col in columns:
        record[col] = _to_float(record.get(col))
    return record


def abs_effect_size(record: dict[str, str | float], effect_size_columns: list[str]) -> dict[str, str | float]:
    """Return a record with the absolute effect size and NaN replaced with 0."""
    for col in effect_size_columns:
        if math.isnan(record[col]):
            record[col] = 0.0
        record[col] = abs(record[col])
    return record


###########################################################
# Zygosity Formatting
###########################################################


def format_zygosity(records: Iterable[dict], zygosity_converter: dict[str, str]) -> Iterable[dict]:
    """Format zygosity values to a consistent style."""
    for record in records:
        record["zygosity"] = zygosity_converter.get(record["zygosity"], record["zygosity"])
    return records


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
