from __future__ import annotations

import csv
import io
import re
from collections.abc import Iterator
from pathlib import Path

import polars as pl

from TSUMUGI.annotator import annotate_life_stage, annotate_sexual_dimorphism
from TSUMUGI.directory_manager import make_directories
from TSUMUGI.filterer import extract_significant_phenotypes, subset_columns
from TSUMUGI.formatter import format_statistics_float
from TSUMUGI.io_handler import download_file, load_csv_as_dicts, save_csv

IMPC_RELEASE = 23.0

###########################################################
# Preparation
###########################################################

ROOT_DIR = Path("TSUMUGI")
sub_dirs: list[str] = [".temp"]

make_directories(ROOT_DIR, sub_dirs)

TEMPDIR = ROOT_DIR / Path(".temp")

###########################################################
# Download data
###########################################################

if not Path(TEMPDIR, "impc_phenodigm.csv").exists():
    url_phenodigm = "https://github.com/whri-phenogenomics/disease_models/raw/main/disease_models_app/data/phenodigm_matches_dr20.1.txt"

    error_message = "Please manually download impc phenodigm data (impc_phenodigm.csv) from https://diseasemodels.research.its.qmul.ac.uk/."

    phenodigm_tsv = download_file(url_phenodigm, error_message)
    reader = csv.reader(io.StringIO(phenodigm_tsv), delimiter="\t")
    phenodigm_csv = (row for row in reader)
    save_csv(phenodigm_csv, Path(TEMPDIR, "impc_phenodigm.csv"))

    # x = load_csv_as_dicts(Path(TEMPDIR, "impc_phenodigm.csv"))
    # write_pickle_iter(load_csv_as_dicts(Path(TEMPDIR, "impc_phenodigm.csv")), Path(TEMPDIR, "impc_phenodigm.pkl"))

if not Path(TEMPDIR, f"statistical_all_{IMPC_RELEASE}.csv").exists():
    url_impc = f"https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-{IMPC_RELEASE}/results/statistical-results-ALL.csv.gz"

    error_message = "Please manually download impc statistical data (statistical_results_ALL.csv) from https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-23.0/results/."

    statistical_all = download_file(url_impc, error_message)
    reader = csv.reader(io.StringIO(statistical_all), delimiter=",")
    statistical_all_rows = (row for row in reader)
    save_csv(statistical_all_rows, Path(TEMPDIR, f"statistical_all_{IMPC_RELEASE}.csv"))
    # write_pickle_iter(
    #     load_csv_as_dicts(Path(TEMPDIR, f"statistical_all_{IMPC_RELEASE}.csv")),
    #     Path(TEMPDIR, f"statistical_all_{IMPC_RELEASE}.pkl"),
    # )


records = load_csv_as_dicts(Path(TEMPDIR, f"statistical_all_{IMPC_RELEASE}.csv"))

# =========================================
# Filter colums and significant genes
# =========================================

columns = [
    "marker_symbol",
    "marker_accession_id",
    "mp_term_name",
    "mp_term_id",
    "p_value",
    "effect_size",
    "female_ko_effect_p_value",  # sex differences
    "male_ko_effect_p_value",  # sex differences
    "female_ko_parameter_estimate",  # sex differences
    "male_ko_parameter_estimate",  # sex differences
    "zygosity",  # zygosity
    "pipeline_name",  # life-stage
    "procedure_name",  # life-stage
    "allele_symbol",  # map to Phendigm
]

records_subset: Iterator[dict[str, str]] = subset_columns(records, columns)

records_significants: list[dict[str, str | float]] = extract_significant_phenotypes(
    records_subset, threshold=1e-4
)  # 1 min

float_columns = [
    "p_value",
    "effect_size",
    "female_ko_effect_p_value",  # sex differences
    "male_ko_effect_p_value",  # sex differences
    "female_ko_parameter_estimate",  # sex differences
    "male_ko_parameter_estimate",  # sex differences
]

records_significants = format_statistics_float(records_significants, float_columns)

# Cache results
pl.DataFrame(records_significants).write_csv(
    Path(TEMPDIR, f"statistical_significants_{IMPC_RELEASE}.csv"),
)
pl.DataFrame(records_significants).write_parquet(
    Path(TEMPDIR, f"statistical_significants_{IMPC_RELEASE}.parquet"),
)

# =========================================
# Annotate life stage, genotype, and sexual dimorphisms
# =========================================
embryo_assays = {
    "E9.5",
    "E10.5",
    "E12.5",
    "Embryo LacZ",  # E12.5
    "E14.5",
    "E14.5-E15.5",
    "E18.5",
}

embryo_pattern = re.compile("|".join(map(re.escape, embryo_assays)))

for record in records_significants:
    record["life_stage"] = annotate_life_stage(record["procedure_name"], record["pipeline_name"], embryo_pattern)

for record in records_significants:
    record["sexual_dimorphism"] = annotate_sexual_dimorphism(
        record["female_ko_effect_p_value"], record["male_ko_effect_p_value"], threshold=1e-4
    )


def execute():
    pass


if __name__ == "__main__":
    execute()
