from __future__ import annotations

import csv
import io
import logging
import pickle
import shutil
from collections.abc import Iterator
from pathlib import Path

import polars as pl

from TSUMUGI import (
    annotator,
    filterer,
    formatter,
    io_handler,
    network_constructor,
    report_generator,
    similarity_calculator,
    web_deployer,
)
from TSUMUGI.config import IMPC_RELEASE, TEMPDIR

# Logging Config
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

############################################################
# Preparation
############################################################

sub_dirs: list[Path] = [
    Path("preprocessed"),
    Path("phenotype_similarity"),
    Path("network", "phenotype"),
    Path("network", "genesymbol"),
    Path("webapp"),
    Path("download"),
]

io_handler.make_directories(TEMPDIR, sub_dirs)

###########################################################
# Download data
###########################################################

logging.info("Downloading data...")

path_output = Path(TEMPDIR, "download", "impc_phenodigm.csv")
if not path_output.exists():
    url_phenodigm = "https://github.com/whri-phenogenomics/disease_models/raw/main/disease_models_app/data/phenodigm_matches_dr20.1.txt"

    error_message = "Please manually download impc phenodigm data (impc_phenodigm.csv) from https://diseasemodels.research.its.qmul.ac.uk/."

    phenodigm_tsv = io_handler.download_file(url_phenodigm, error_message)
    reader = csv.reader(io.StringIO(phenodigm_tsv), delimiter="\t")
    phenodigm_csv = (row for row in reader)
    io_handler.save_csv(phenodigm_csv, path_output)

path_output = Path(TEMPDIR, "download", "mp.obo")
if not path_output.exists():
    url_mp_obo = "https://purl.obolibrary.org/obo/mp.obo"

    error_message = "Please manually download mp.obo data from https://purl.obolibrary.org/obo/mp.obo."

    mp_obo = io_handler.download_file(url_mp_obo, error_message)
    path_output.write_text(mp_obo)

path_output = Path(TEMPDIR, f"statistical_all_{IMPC_RELEASE}.csv")
if not path_output.exists():
    url_impc = f"https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-{IMPC_RELEASE}/results/statistical-results-ALL.csv.gz"

    error_message = "Please manually download impc statistical data (statistical_results_ALL.csv) from https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-23.0/results/."

    statistical_all = io_handler.download_file(url_impc, error_message)
    reader = csv.reader(io.StringIO(statistical_all), delimiter=",")
    statistical_all_rows = (row for row in reader)
    io_handler.save_csv(statistical_all_rows, path_output)


records = io_handler.load_csv_as_dicts(path_output)
ontology_terms = io_handler.parse_obo_file(Path(TEMPDIR / "mp.obo"))

with open(Path(TEMPDIR, "download", "impc_phenodigm.csv")) as f:
    reader = csv.DictReader(f)
    disease_annotations = [record for record in reader if len(record["description"].split(" ")) == 3]

###########################################################
# Preprocess data
###########################################################

# --------------------------------------------------------
# Select columns, maintained mp term, and significant genes
# --------------------------------------------------------

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

# --------------------------------------------------------
# Extract significant phenotypes (p_value < 1e-4)
# --------------------------------------------------------
records_significants: list[dict[str, str | float]] = filterer.extract_significant_phenotypes(
    records_subset, threshold=1e-4
)  # 1 min

# --------------------------------------------------------
# Convert string to float and take absolute value of effect size
# --------------------------------------------------------
float_columns = [
    "p_value",
    "effect_size",
    "female_ko_effect_p_value",  # sex differences
    "male_ko_effect_p_value",  # sex differences
    "female_ko_parameter_estimate",  # sex differences
    "male_ko_parameter_estimate",  # sex differences
]

records_significants = formatter.format_statistics_float(records_significants, float_columns)

# --------------------------------------------------------
# Keep only records with mp_term_id in the ontology file (= not obsolete)
# --------------------------------------------------------
records_significants = [record for record in records_significants if record["mp_term_id"] in ontology_terms]

# --------------------------------------------------------
# Cache results
# --------------------------------------------------------
pl.DataFrame(records_significants).write_csv(
    Path(TEMPDIR, "preprocessed", f"statistical_significants_{IMPC_RELEASE}.csv"),
)
pl.DataFrame(records_significants).write_parquet(
    Path(TEMPDIR, "preprocessed", f"statistical_significants_{IMPC_RELEASE}.parquet"),
)

# --------------------------------------------------------
# Annotate life stage, sexual dimorphisms, human disease, and IMPC URLs
# --------------------------------------------------------

logging.info("Annotating life stage, sexual dimorphisms, human disease, and IMPC URLs...")

embryo_assays = {
    "E9.5",
    "E10.5",
    "E12.5",
    "Embryo LacZ",  # E12.5
    "E14.5",
    "E14.5-E15.5",
    "E18.5",
}

records_significants = annotator.annotate_life_stage(records_significants, embryo_assays)
records_significants = annotator.annotate_sexual_dimorphism(records_significants, threshold=1e-4)
records_significants = annotator.annotate_human_disease(records_significants, disease_annotations)
records_significants = annotator.annotate_impc_urls(records_significants)

# --------------------------------------------------------
# Select distinct records with max effect size
# --------------------------------------------------------

unique_keys = [
    "marker_symbol",
    "mp_term_id",
    "zygosity",
    "life_stage",
    "sexual_dimorphism",
]

records_significants = formatter.get_distinct_records_with_max_effect(records_significants, unique_keys)

# --------------------------------------------------------
# Cache results
# --------------------------------------------------------

pl.DataFrame(records_significants).write_csv(
    Path(TEMPDIR, "preprocessed", f"statistical_significants_annotated_{IMPC_RELEASE}.csv"),
)
pl.DataFrame(records_significants).write_parquet(
    Path(TEMPDIR, "preprocessed", f"statistical_significants_annotated_{IMPC_RELEASE}.parquet"),
)
pickle.dump(
    records_significants,
    open(Path(TEMPDIR / "preprocessed" / f"statistical_significants_annotated_{IMPC_RELEASE}.pkl"), "wb"),
)

###########################################################
# Calculate phenotype similarity
###########################################################

all_term_ids = {r["mp_term_id"] for r in records_significants}

logging.info(f"Calculating pairwise similarity for {len(all_term_ids)} terms...")

term_pair_similarity_map: dict[frozenset[str], dict[str, float]] = (
    similarity_calculator.calculate_all_pairwise_similarities(ontology_terms, all_term_ids)
)
# 30 min

# --------------------------------------------------------
# Cache results
# --------------------------------------------------------
with open(Path(TEMPDIR / "phenotype_similarity", "term_pair_similarity_map.pkl"), "wb") as f:
    pickle.dump(term_pair_similarity_map, f)

# ----------------------------------------
# Calculate phenotype similarity for genes
# ----------------------------------------

logging.info(f"Annotate phenotype ancestors for {len(records_significants)} records...")
phenotype_ancestors: dict[frozenset, dict[str, dict[str, str]]] = similarity_calculator.annotate_phenotype_ancestors(
    records_significants, term_pair_similarity_map, ontology_terms
)
# 20 min

logging.info(f"Calculating phenodigm similarity for {len(records_significants)} records...")
phenodigm_scores: dict[frozenset[str], int] = similarity_calculator.calculate_phenodigm_score(
    records_significants, term_pair_similarity_map
)
# 30 min

num_shared_phenotypes = similarity_calculator.calculate_num_shared_phenotypes(records_significants)
jaccard_indices = similarity_calculator.calculate_jaccard_indices(records_significants)

# --------------------------------------------------------
# Cache results
# --------------------------------------------------------
with open(Path(TEMPDIR / "phenotype_similarity", "phenotype_ancestors.pkl"), "wb") as f:
    pickle.dump(phenotype_ancestors, f)

with open(Path(TEMPDIR / "phenotype_similarity", "phenodigm_scores.pkl"), "wb") as f:
    pickle.dump(phenodigm_scores, f)

with open(Path(TEMPDIR / "phenotype_similarity", "num_shared_phenotypes.pkl"), "wb") as f:
    pickle.dump(num_shared_phenotypes, f)

with open(Path(TEMPDIR / "phenotype_similarity", "jaccard_indices.pkl"), "wb") as f:
    pickle.dump(jaccard_indices, f)


# ----------------------------------------
# Summarize the phenotype similarity results
# ----------------------------------------

pair_similarity_annotations: dict[frozenset, dict[str, dict[str, str] | int]] = (
    similarity_calculator.summarize_similarity_annotations(ontology_terms, phenotype_ancestors, phenodigm_scores)
)

# output_file = f"data/TSUMUGI_v{TSUMUGI_VERSION}_phenotype_similarity.jsonl.gz"
# with gzip.open(output_file, "wt", encoding="utf-8") as f:
#     for genes, annotations in pair_similarity_annotations.items():
#         gene1, gene2 = sorted(genes)
#         record = {"gene1": gene1, "gene2": gene2, **annotations}
#         f.write(json.dumps(record, ensure_ascii=False) + "\n")

# --------------------------------------------------------
# Cache results
# --------------------------------------------------------
with open(Path(TEMPDIR / "phenotype_similarity", "pair_similarity_annotations.pkl"), "wb") as f:
    pickle.dump(pair_similarity_annotations, f)

# 1 min

###########################################################
# Generate network
###########################################################
MIN_NUM_PHENOTYPES = 3

pair_similarity_annotations_with_shared_phenotype = {
    k: v
    for k, v in pair_similarity_annotations.items()
    if len(v["phenotype_shared_annotations"]) >= MIN_NUM_PHENOTYPES
}


logging.info("Building phenotype network JSON files...")

output_dir = Path(TEMPDIR / "network" / "phenotype")
output_dir.mkdir(parents=True, exist_ok=True)
network_constructor.build_phenotype_network_json(
    records_significants, pair_similarity_annotations_with_shared_phenotype, disease_annotations, output_dir
)

logging.info("Building gene network JSON files...")
output_dir = Path(TEMPDIR / "network" / "genesymbol")
output_dir.mkdir(parents=True, exist_ok=True)

network_constructor.build_gene_network_json(
    records_significants, pair_similarity_annotations_with_shared_phenotype, disease_annotations, output_dir
)

###########################################################
# Output data for web application
###########################################################


output_dir = Path(TEMPDIR / "webapp")  # data for webapp
output_dir.mkdir(parents=True, exist_ok=True)

# available mp terms
report_generator.write_available_mp_terms_txt(Path(output_dir / "available_mp_terms.txt"))
report_generator.write_available_mp_terms_json(Path(output_dir / "available_mp_terms.json"))

# binary phenotypes
report_generator.write_binary_phenotypes_txt(records_significants, Path(output_dir / "binary_phenotypes.txt"))

# available gene symbols
report_generator.write_available_gene_symbols_txt(Path(output_dir / "available_gene_symbols.txt"))

# marker symbol to accession id
report_generator.write_marker_symbol_accession_id_json(
    records_significants, Path(output_dir / "marker_symbol_accession_id.json")
)


###########################################################
# Deploy to web application
###########################################################

logging.info("Building gene network JSON files...")
is_test = True

output_dir = Path(TEMPDIR, "test-tsumugi") if is_test else Path(TEMPDIR, "TSUMUGI-webapp")
shutil.rmtree(output_dir)
output_dir.mkdir(parents=True, exist_ok=True)

targetted_phenotypes = web_deployer.select_targetted_phenotypes(is_test=is_test)
targetted_genes = web_deployer.select_targetted_genes(is_test=is_test)

web_deployer.prepare_files(targetted_phenotypes, targetted_genes, output_dir)

web_deployer.generate_phenotype_pages(records_significants, targetted_phenotypes, output_dir)
web_deployer.generate_gene_pages(records_significants, targetted_genes, output_dir)
web_deployer.generate_genelist_page(output_dir)

# def execute():
#     pass


# if __name__ == "__main__":
#     execute()
