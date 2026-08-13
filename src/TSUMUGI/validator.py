from __future__ import annotations

import csv
from pathlib import Path

from TSUMUGI import io_handler


def validate_statistical_results(file_path: str, *, require_strain: bool = False) -> None:
    # Implementation for validating statistical results file
    columns = {
        "marker_symbol",
        "marker_accession_id",
        "mp_term_name",
        "mp_term_id",
        "p_value",
        "effect_size",
        "female_ko_effect_p_value",  # sex differences
        "female_ko_parameter_estimate",  # sex-specific effect size
        "male_ko_effect_p_value",  # sex differences
        "male_ko_parameter_estimate",  # sex-specific effect size
        "zygosity",  # zygosity
        "pipeline_name",  # life-stage
        "procedure_name",  # life-stage
        "allele_symbol",  # map to Phendigm
        "intermediate_mp_term_id",  # measured phenotype mapping
    }
    if require_strain:
        columns.add("strain_name")
    records = io_handler.load_csv_as_dicts(file_path)
    record_columns = next(records).keys()
    missing_columns = columns - record_columns
    if missing_columns:
        raise ValueError(f"Invalid file: Missing columns {missing_columns} in {file_path}")


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


def validate_mp_term_id(term_id: str, mp_obo_path: str) -> None:
    # Implementation for validating MP term ID
    ontology_terms = io_handler.parse_obo_file(mp_obo_path)
    if term_id not in ontology_terms:
        raise ValueError(f"MP term ID '{term_id}' not found in OBO file '{mp_obo_path}'.")


def validate_phenodigm_file(file_path: str) -> None:
    # Implementation for validating Phenodigm file
    columns = {"Disorder name", "Mouse model description"}
    record_columns = next(io_handler.load_csv_as_dicts(file_path)).keys()
    missing_columns = columns - record_columns
    if missing_columns:
        raise ValueError(f"Invalid file: Missing {missing_columns} in {file_path}")


def _first_non_comment_tsv_row(path: str | Path) -> list[str]:
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        for line in handle:
            if line.startswith("#"):
                continue
            row = next(csv.reader([line], delimiter="\t"))
            if row:
                return row
    raise ValueError(f"Invalid file: No data rows in {path}")


def validate_mgi_reports(
    gene_pheno_path: str | Path,
    phenotypic_allele_path: str | Path,
    pheno_sex_path: str | Path,
) -> None:
    """Validate the three MGI reports used by the integration mode."""
    paths = [Path(gene_pheno_path), Path(phenotypic_allele_path), Path(pheno_sex_path)]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Required MGI input files are missing: {missing}")

    gene_pheno_row = _first_non_comment_tsv_row(gene_pheno_path)
    if len(gene_pheno_row) != 8:
        raise ValueError(f"Invalid MGI_GenePheno.rpt: expected 8 columns, found {len(gene_pheno_row)}")

    allele_row = _first_non_comment_tsv_row(phenotypic_allele_path)
    if len(allele_row) != 13:
        raise ValueError(f"Invalid MGI_PhenotypicAllele.rpt: expected 13 columns, found {len(allele_row)}")

    with Path(pheno_sex_path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {
            "Genotype ID",
            "Sex",
            "MP ID",
            "MP Term",
            "Allelic Composition",
            "Background Strain",
            "Sex-specific Normal Y/N",
            "Citation (PubMed/MGI)",
        }
        columns = set(reader.fieldnames or [])
        if columns != required:
            raise ValueError(f"Invalid MGI_Pheno_Sex.rpt columns: {reader.fieldnames}")
