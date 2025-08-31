from __future__ import annotations

import csv
import io
from pathlib import Path

from directory_manager import make_directories
from io_handler import download_file, load_csv_as_dicts, save_csv

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


# =========================================
# Filter significant genes
# significant genesはmp_term_nameが存在する列であることを利用
# =========================================

columns = [
    "marker_symbol",
    "marker_accession_id",
    "mp_term_name",
    "mp_term_id",
    "p_value",
    "effect_size",
    "female_ko_effect_p_value",
    "male_ko_effect_p_value",
    "female_ko_parameter_estimate",
    "sex_effect_p_value",
    "male_ko_parameter_estimate",  # sex differences
    "genotype_effect_p_value",
    "genotype_effect_parameter_estimate",
    "zygosity",  # zygosity
    "pipeline_name",
    "procedure_name",  # life-stage
    "allele_symbol",  # map to Phendigm
]

records = load_csv_as_dicts(Path(TEMPDIR, f"statistical_all_{IMPC_RELEASE}.csv"))

records_filtered = (record for record in records if "mp_term_name" in record)

# =========================================
# Subset columns
# =========================================
records_subset = (
    {col: record.get(col, "") for col in columns}
    for record in records_filtered
    if record.get("mp_term_name") not in (None, "")
)

output_path = Path(TEMPDIR, f"statistical_filtered_{IMPC_RELEASE}.csv")

with open(output_path, "w", newline="", encoding="utf-8") as f:
    first = next(records_subset)  # 1件目を取り出してヘッダー確定
    writer = csv.DictWriter(f, fieldnames=first.keys())
    writer.writeheader()
    writer.writerow(first)
    for row in records_subset:
        _ = writer.writerow(row)
