from __future__ import annotations

import json
import pickle
import sys
from collections import defaultdict
from collections.abc import Iterator
from itertools import groupby
from pathlib import Path

from tqdm import tqdm

from TSUMUGI import io_handler, similarity_calculator

###########################################################
# Exclude gene pairs with target_mp_term_id and its descendants
###########################################################


def _extract_term_parameters_map(path_statistical_all: str | Path) -> dict[str, set[str]]:
    records: Iterator[dict[str, str]] = io_handler.load_csv_as_dicts(Path(path_statistical_all))
    term_parameters_map = defaultdict(set)
    for record in tqdm(records, desc="Extracting term-parameter map"):
        if record["mp_term_id"]:
            term_parameters_map[record["mp_term_id"]].add(record["parameter_stable_id"])

    return dict(term_parameters_map)


def _get_related_parameter_ids(
    mp_term_id: str, term_parameters_map, ontology_terms: dict[str, dict[str, str]]
) -> set[str]:
    _, child_term_map = similarity_calculator._build_term_hierarchy(ontology_terms)
    descendants_of_term_id = similarity_calculator._find_all_descendant_terms(mp_term_id, child_term_map)

    related_parameter_ids = set()
    for term_id in descendants_of_term_id:
        if term_id in term_parameters_map:
            related_parameter_ids |= term_parameters_map[term_id]

    return related_parameter_ids


def _extract_genes_without_specific_phenotype(
    path_statistical_all: str | Path, related_parameter_ids: set[str]
) -> set[str]:
    """Rather than simply genes with no recorded phenotype (where it is unclear whether the phenotype was measured or not),
    extract the group of genes for which measurements were definitely conducted but no phenotype was observed."""
    records: Iterator[dict[str, str]] = io_handler.load_csv_as_dicts(Path(path_statistical_all))
    records_grouped = groupby(sorted(records, key=lambda r: r["marker_symbol"]), key=lambda r: r["marker_symbol"])

    genes_without_specific_phenotype = set()
    for gene, group in tqdm(records_grouped, desc="Extracting genes without specific phenotype"):
        with_mp_term = False
        is_assayed = False

        for record in group:
            if record["parameter_stable_id"] in related_parameter_ids:
                is_assayed = True
                if record["mp_term_id"]:
                    with_mp_term = True

        if gene and is_assayed and with_mp_term is False:
            genes_without_specific_phenotype.add(gene)

    return genes_without_specific_phenotype


def exclude_specific_phenotype(
    path_phenotype_similarity_per_gene_pair: str | Path,
    path_statistical_all: str | Path,
    path_obo: str | Path,
    mp_term_id: set[str],
) -> None:
    cache_dir = Path(path_obo).parent / ".tsumugi_cache"
    if not cache_dir.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
    if not (cache_dir / "term_parameters_map.pkl").exists():
        term_parameters_map = _extract_term_parameters_map(path_statistical_all)
        pickle.dump(term_parameters_map, open(cache_dir / "term_parameters_map.pkl", "wb"))
    else:
        term_parameters_map = pickle.load(open(cache_dir / "term_parameters_map.pkl", "rb"))

    ontology_terms = io_handler.parse_obo_file(path_obo)
    related_parameter_ids = _get_related_parameter_ids(mp_term_id, term_parameters_map, ontology_terms)
    genes_without_specific_phenotype = _extract_genes_without_specific_phenotype(
        path_statistical_all, related_parameter_ids
    )

    pair_similarity_annotations = io_handler.parse_jsonl_gz_to_pair_map(path_phenotype_similarity_per_gene_pair)
    for gene_pair, annotation in tqdm(pair_similarity_annotations.items(), desc="Filtering gene pairs"):
        if gene_pair.isdisjoint(genes_without_specific_phenotype):
            continue
        # output to stdout as JSON
        gene1, gene2 = sorted(gene_pair)
        record = {"gene1_symbol": gene1, "gene2_symbol": gene2, **annotation}
        json.dump(record, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")


def include_specific_phenotype(
    path_phenotype_similarity_per_gene_pair: str | Path, path_obo: str | Path, term_id: str
) -> None:
    cache_dir = Path(path_obo).parent / ".tsumugi_cache"
    if not cache_dir.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
    if not (cache_dir / "descendants_of_term_name.pkl").exists():
        ontology_terms = io_handler.parse_obo_file(path_obo)
        _, child_term_map = similarity_calculator._build_term_hierarchy(ontology_terms)
        descendants_of_term_id: set[str] = similarity_calculator._find_all_descendant_terms(term_id, child_term_map)
        descendants_of_term_name = {
            data["name"] for term_id, data in ontology_terms.items() if term_id in descendants_of_term_id
        }
        pickle.dump(descendants_of_term_name, open(cache_dir / "descendants_of_term_name.pkl", "wb"))
    else:
        descendants_of_term_name = pickle.load(open(cache_dir / "descendants_of_term_name.pkl", "rb"))

    pair_similarity_annotations = io_handler.parse_jsonl_gz_to_pair_map(path_phenotype_similarity_per_gene_pair)
    for gene_pair, annotation in tqdm(pair_similarity_annotations.items(), desc="Filtering gene pairs"):
        if not set(annotation["phenotype_shared_annotations"].keys()).intersection(descendants_of_term_name):
            continue
        # output to stdout as JSON
        gene1, gene2 = sorted(gene_pair)
        record = {"gene1_symbol": gene1, "gene2_symbol": gene2, **annotation}
        json.dump(record, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
