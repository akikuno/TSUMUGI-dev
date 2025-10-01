from __future__ import annotations

import csv
import gzip
import io
import json
import logging
import pickle
import re
from collections import defaultdict
from collections.abc import Iterator
from pathlib import Path

import polars as pl

from TSUMUGI import annotator, directory_manager, filterer, formatter, io_handler, similarity_calculator

TSUMUGI_VERSION = "1.0.0"
IMPC_RELEASE = 23.0

###########################################################
# Preparation
###########################################################

ROOT_DIR = Path("TSUMUGI-dev")
sub_dirs: list[str] = ["data/.temp"]

directory_manager.make_directories(ROOT_DIR, sub_dirs)

TEMPDIR = ROOT_DIR / Path("data/.temp")


# Logging Config
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

###########################################################
# Download data
###########################################################

logging.info("Downloading data...")

if not Path(TEMPDIR, "impc_phenodigm.csv").exists():
    url_phenodigm = "https://github.com/whri-phenogenomics/disease_models/raw/main/disease_models_app/data/phenodigm_matches_dr20.1.txt"

    error_message = "Please manually download impc phenodigm data (impc_phenodigm.csv) from https://diseasemodels.research.its.qmul.ac.uk/."

    phenodigm_tsv = io_handler.download_file(url_phenodigm, error_message)
    reader = csv.reader(io.StringIO(phenodigm_tsv), delimiter="\t")
    phenodigm_csv = (row for row in reader)
    io_handler.save_csv(phenodigm_csv, Path(TEMPDIR, "impc_phenodigm.csv"))


if not Path(TEMPDIR, "mp.obo").exists():
    url_mp_obo = "https://purl.obolibrary.org/obo/mp.obo"

    error_message = "Please manually download mp.obo data from https://purl.obolibrary.org/obo/mp.obo."

    mp_obo = io_handler.download_file(url_mp_obo, error_message)
    Path(TEMPDIR, "mp.obo").write_text(mp_obo)


if not Path(TEMPDIR, f"statistical_all_{IMPC_RELEASE}.csv").exists():
    url_impc = f"https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-{IMPC_RELEASE}/results/statistical-results-ALL.csv.gz"

    error_message = "Please manually download impc statistical data (statistical_results_ALL.csv) from https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-23.0/results/."

    statistical_all = io_handler.download_file(url_impc, error_message)
    reader = csv.reader(io.StringIO(statistical_all), delimiter=",")
    statistical_all_rows = (row for row in reader)
    io_handler.save_csv(statistical_all_rows, Path(TEMPDIR, f"statistical_all_{IMPC_RELEASE}.csv"))


records = io_handler.load_csv_as_dicts(Path(TEMPDIR, f"statistical_all_{IMPC_RELEASE}.csv"))
ontology_terms = io_handler.parse_obo_file(Path(TEMPDIR / "mp.obo"))

# =========================================
# Select colums, maintained mp term, and significant genes
# =========================================
logging.info("Selecting columns and significant genes...")

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

records_subset: Iterator[dict[str, str]] = filterer.subset_columns(records, columns)

# Extract significant phenotypes (p_value < 1e-4)
records_significants: list[dict[str, str | float]] = filterer.extract_significant_phenotypes(
    records_subset, threshold=1e-4
)  # 1 min

# Convert string to float and take absolute value of effect size
float_columns = [
    "p_value",
    "effect_size",
    "female_ko_effect_p_value",  # sex differences
    "male_ko_effect_p_value",  # sex differences
    "female_ko_parameter_estimate",  # sex differences
    "male_ko_parameter_estimate",  # sex differences
]

records_significants = formatter.format_statistics_float(records_significants, float_columns)

# Keep only records with mp_term_id in the ontology file (= not obsolete)
records_significants = [record for record in records_significants if record["mp_term_id"] in ontology_terms]

# Cache results
pl.DataFrame(records_significants).write_csv(
    Path(TEMPDIR, f"statistical_significants_{IMPC_RELEASE}.csv"),
)
pl.DataFrame(records_significants).write_parquet(
    Path(TEMPDIR, f"statistical_significants_{IMPC_RELEASE}.parquet"),
)

# =========================================
# Annotate life stage, sexual dimorphisms, and human disease
# =========================================
logging.info("Annotating life stage, sexual dimorphisms, and human disease...")

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
    record["life_stage"] = annotator.annotate_life_stage(
        record["procedure_name"], record["pipeline_name"], embryo_pattern
    )

for record in records_significants:
    record["sexual_dimorphism"] = annotator.annotate_sexual_dimorphism(
        record["female_ko_effect_p_value"], record["male_ko_effect_p_value"], threshold=1e-4
    )

records_phenodigm: list[dict[str | str | float]] = pl.read_csv(Path(TEMPDIR, "impc_phenodigm.csv")).to_dicts()

allele_phenodigm = formatter.format_phenodigm_record(records_phenodigm)

for record in records_significants:
    record |= annotator.annotate_human_disease(
        record["allele_symbol"], record["zygosity"], record["life_stage"], allele_phenodigm
    )


for record in records_significants:
    mp_term_id = record["mp_term_id"]
    marker_accession_id = record["marker_accession_id"]
    record["impc_url_gene"] = f"https://www.mousephenotype.org/data/genes/{marker_accession_id}"
    record["impc_url_phenotype"] = f"https://www.mousephenotype.org/data/phenotypes/{mp_term_id}"


unique_keys = [
    "marker_symbol",
    "mp_term_id",
    "zygosity",
    "life_stage",
    "sexual_dimorphism",
]

records_significants = formatter.get_distinct_records_with_max_effect(records_significants, unique_keys)

# Cache results

pl.DataFrame(records_significants).write_csv(
    Path(TEMPDIR, f"statistical_significants_annotated_{IMPC_RELEASE}.csv"),
)
pl.DataFrame(records_significants).write_parquet(
    Path(TEMPDIR, f"statistical_significants_annotated_{IMPC_RELEASE}.parquet"),
)
pickle.dump(records_significants, open(Path(TEMPDIR / f"statistical_significants_annotated_{IMPC_RELEASE}.pkl"), "wb"))

# =========================================
# Calculate phenotype similarity
# =========================================

all_term_ids = {r["mp_term_id"] for r in records_significants}

logging.info(f"Calculating pairwise similarity for {len(all_term_ids)} terms...")

term_pair_similarity_map: dict[frozenset[str], dict[str, float]] = (
    similarity_calculator.calculate_all_pairwise_similarities(ontology_terms, all_term_ids)
)
# 30 min

# Cache results
with open(Path(TEMPDIR / "term_pair_similarity_map.pkl"), "wb") as f:
    pickle.dump(term_pair_similarity_map, f)

# ----------------------------------------
# Calculate phenotype similarity for genes
# ----------------------------------------

logging.info(f"Annotate phenotype ancestors for {len(records_significants)} records...")
phenotype_ancestors: dict[frozenset[str], list[str]] = similarity_calculator.annotate_phenotype_ancestors(
    records_significants, term_pair_similarity_map
)
# 20 min

logging.info(f"Calculating phenodigm similarity for {len(records_significants)} records...")
phenodigm_scores: dict[frozenset[str], int] = similarity_calculator.calculate_phenodigm_score(
    records_significants, term_pair_similarity_map
)
# 30 min

num_shared_phenotypes = similarity_calculator.calculate_num_shared_phenotypes(records_significants)
jaccard_indices = similarity_calculator.calculate_jaccard_indices(records_significants)

# Cache results
with open(Path(TEMPDIR / "phenotype_ancestors.pkl"), "wb") as f:
    pickle.dump(phenotype_ancestors, f)

with open(Path(TEMPDIR / "phenodigm_scores.pkl"), "wb") as f:
    pickle.dump(phenodigm_scores, f)

with open(Path(TEMPDIR / "num_shared_phenotypes.pkl"), "wb") as f:
    pickle.dump(num_shared_phenotypes, f)

with open(Path(TEMPDIR / "jaccard_indices.pkl"), "wb") as f:
    pickle.dump(jaccard_indices, f)


# ----------------------------------------
# Summarize the phenotype similarity results
# ----------------------------------------

map_id_to_name = {v["id"]: v["name"] for v in ontology_terms.values()}

pair_similarity_annotations = defaultdict(list)

for gene1_symbol, gene2_symbol in phenotype_ancestors.keys():
    phenotype_ancestor = phenotype_ancestors[frozenset([gene1_symbol, gene2_symbol])]
    phenotype_ancestor_name = [{map_id_to_name[k]: v for k, v in ancestor.items()} for ancestor in phenotype_ancestor]
    phenodigm_score = phenodigm_scores[frozenset([gene1_symbol, gene2_symbol])]

    pair_similarity_annotations[frozenset([gene1_symbol, gene2_symbol])] = {
        "phenotype_shared_annotations": phenotype_ancestor_name,
        "phenotype_similarity_score": phenodigm_score,
    }

pair_similarity_annotations = dict(pair_similarity_annotations)

output_file = f"data/TSUMUGI_v{TSUMUGI_VERSION}_phenotype_similarity.jsonl.gz"
with gzip.open(output_file, "wt", encoding="utf-8") as f:
    for genes, annotations in pair_similarity_annotations.items():
        gene1, gene2 = sorted(genes)  # 並びを安定させる
        record = {"gene1": gene1, "gene2": gene2, **annotations}
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

# Cache results
with open(Path(TEMPDIR / "pair_similarity_annotations.pkl"), "wb") as f:
    pickle.dump(pair_similarity_annotations, f)

# 1 min


# def execute():
#     pass


# if __name__ == "__main__":
#     execute()
