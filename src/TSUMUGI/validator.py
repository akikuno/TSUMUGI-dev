from __future__ import annotations

from matplotlib.pylab import record

from TSUMUGI import io_handler


def validate_statistical_results(file_path: str) -> None:
    # Implementation for validating statistical results file
    columns = {
        "marker_symbol",
        "marker_accession_id",
        "mp_term_name",
        "mp_term_id",
        "p_value",
        "effect_size",
        "female_ko_effect_p_value",  # sex differences
        "male_ko_effect_p_value",  # sex differences
        "zygosity",  # zygosity
        "pipeline_name",  # life-stage
        "procedure_name",  # life-stage
        "allele_symbol",  # map to Phendigm
    }
    records = io_handler.load_csv_as_dicts(file_path)
    record_columns = next(records).keys()
    missing_columns = columns - record_columns
    if missing_columns:
        raise ValueError(f"Invalid file: Missing columns in record {record}: {missing_columns} in {file_path}")


def validate_obo_file(file_path: str) -> None:
    # Implementation for validating OBO file

    has_format = False
    has_term = False

    with open(file_path, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("!"):
                continue
            if s.startswith("format-version:"):
                has_format = True
            elif s.startswith("[Term]"):
                has_term = True
                break  # enough for quick validation

    if not has_format:
        raise ValueError("Invalid OBO file: missing 'format-version:' in header.")
    if not has_term:
        raise ValueError("Invalid OBO file: missing '[Term]' stanza.")


def validate_phenodigm_file(file_path: str) -> None:
    # Implementation for validating Phenodigm file
    columns = {"Disorder name", "Mouse model description"}
    with open(file_path, encoding="utf-8") as f:
        record_columns = next(io_handler.load_csv_as_dicts(f)).keys()
        missing_columns = columns - record_columns
        if missing_columns:
            raise ValueError(f"Invalid file: Missing columns in record {record}: {missing_columns} in {file_path}")


def validate_mp_term_id(term_id: str, mp_obo_path: str) -> None:
    # Implementation for validating MP term ID
    ontology_terms = io_handler.parse_obo_file(mp_obo_path)
    if term_id not in ontology_terms:
        raise ValueError(f"MP term ID '{term_id}' not found in OBO file '{mp_obo_path}'.")
