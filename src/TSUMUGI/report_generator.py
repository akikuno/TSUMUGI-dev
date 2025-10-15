from __future__ import annotations

import gzip
import json
from collections import defaultdict
from pathlib import Path


# available mp terms
def write_available_mp_terms_txt(TEMPDIR: Path, output_file: Path) -> None:
    with open(output_file, "w") as f:
        for path_phenotype in Path(TEMPDIR, "network", "phenotype").glob("*.json.gz"):
            mp_term_name = path_phenotype.name.replace(".json.gz", "").replace("_", " ")
            f.write(f"{mp_term_name}\n")


def write_available_mp_terms_json(TEMPDIR: Path, output_file: Path) -> None:
    mp_term_name_json = {}
    for path_phenotype in Path(TEMPDIR, "network", "phenotype").glob("*.json.gz"):
        mp_term_name_underscore = path_phenotype.name.replace(".json.gz", "")
        mp_term_name = mp_term_name_underscore.replace("_", " ")
        mp_term_name_json[mp_term_name] = mp_term_name_underscore
    # Save as a JSON file
    with open(output_file, "w") as f:
        json.dump(mp_term_name_json, f, ensure_ascii=False, indent=2)


# binary phenotypes
def write_binary_phenotypes_txt(records_significants, TEMPDIR: Path, output_file: Path) -> None:
    paths_available_mp_terms = Path(TEMPDIR, "network", "phenotype").glob("*.json.gz")
    available_mp_terms = {p.name.replace(".json.gz", "").replace("_", " ") for p in paths_available_mp_terms}

    mp_term_names_effect_size = defaultdict(set)
    for record in records_significants:
        mp_term_name = record["mp_term_name"]
        if mp_term_name not in available_mp_terms:
            continue
        effect_size = record["effect_size"]
        mp_term_names_effect_size[mp_term_name].add(effect_size)

    binary_phenotypes = set()
    for mp_term_name, effect_sizes in mp_term_names_effect_size.items():
        if all(True if es in {0, 1} else False for es in effect_sizes):
            binary_phenotypes.add(mp_term_name)

    with open(output_file, "w") as f:
        for bp in binary_phenotypes:
            f.write(f"{bp}\n")


# available gene symbols
def write_available_gene_symbols_txt(TEMPDIR: Path, output_file: Path) -> None:
    with open(output_file, "w") as f:
        for path_genesymbol in Path(TEMPDIR, "network", "genesymbol").glob("*.json.gz"):
            gene_symbol = path_genesymbol.name.replace(".json.gz", "")
            f.write(f"{gene_symbol}\n")


def write_marker_symbol_accession_id_json(records_significants, TEMPDIR: Path, output_file: Path) -> None:
    marker_symbol_accession_id = {}
    paths_genesymbol = Path(TEMPDIR, "network", "genesymbol").glob("*.json.gz")
    available_gene_symbols = {p.name.replace(".json.gz", "") for p in paths_genesymbol}
    for record in records_significants:
        if record["marker_symbol"] not in available_gene_symbols:
            continue
        marker_symbol_accession_id[record["marker_symbol"]] = record.get("marker_accession_id")
    # Save as a JSON file
    with open(output_file, "w") as f:
        json.dump(marker_symbol_accession_id, f, ensure_ascii=False, indent=2)


def write_records_significants_jsonl_gz(records_significants, output_file: Path) -> None:
    with gzip.open(output_file, "wt", encoding="utf-8") as f:
        for record in records_significants:
            f.write(json.dumps(record) + "\n")


def write_pair_similarity_annotations(pair_similarity_annotations, output_file: Path) -> None:
    with gzip.open(output_file, "wt", encoding="utf-8") as f:
        for gene_pair, annotation in pair_similarity_annotations.items():
            gene1_symbol, gene2_symbol = sorted(gene_pair)
            if not annotation["phenotype_shared_annotations"]:
                continue
            phenotype_similarity_score = annotation["phenotype_similarity_score"]
            f.write(
                json.dumps(
                    {
                        "gene1_symbol": gene1_symbol,
                        "gene2_symbol": gene2_symbol,
                        "phenotype_shared_annotations": annotation["phenotype_shared_annotations"],
                        "phenotype_similarity_score": phenotype_similarity_score,
                    }
                )
                + "\n"
            )
