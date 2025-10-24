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


def _build_term_parameters_map(path_statistical_all: str | Path) -> dict[str, set[str]]:
    records: Iterator[dict[str, str]] = io_handler.load_csv_as_dicts(Path(path_statistical_all))
    term_parameters_map = defaultdict(set)
    for record in tqdm(records, desc="Extracting term-parameter map"):
        if record["mp_term_id"]:
            term_parameters_map[record["mp_term_id"]].add(record["parameter_stable_id"])

    return dict(term_parameters_map)


def _build_parameter_genes_without_phenotype_map(
    path_statistical_all: str | Path,
) -> dict[str, set[str]]:
    records: Iterator[dict[str, str]] = io_handler.load_csv_as_dicts(Path(path_statistical_all))
    records_sorted = sorted(records, key=lambda r: r["marker_symbol"])

    records_grouped = groupby(records_sorted, key=lambda r: r["marker_symbol"])
    parameter_genes_without_phenotype_map = defaultdict(set)
    for gene, group in tqdm(records_grouped, desc="Extracting genes without specific phenotype"):
        if not gene:
            continue

        is_assayed = set()
        is_not_significant = defaultdict(lambda: True)
        for record in group:
            parameter_id = record["parameter_stable_id"]
            term_id = record["mp_term_id"]
            if term_id:
                is_not_significant[parameter_id] = False
            if parameter_id not in is_assayed and not term_id:
                is_not_significant[parameter_id] = True
            is_assayed.add(parameter_id)

        for parameter_id in is_assayed:
            if is_not_significant[parameter_id]:
                parameter_genes_without_phenotype_map[parameter_id].add(gene)

    return dict(parameter_genes_without_phenotype_map)


def _build_term_genes_without_significant(
    term_parameters_map: dict[str, set[str]], parameter_genes_without_phenotype_map: dict[str, set[str]]
) -> dict[str, set[str]]:
    term_genes_without_significant = defaultdict(set)

    for term_id, parameter_ids in term_parameters_map.items():
        # intersect genes without significant phenotype across all related parameters
        genes_without_significant = None
        for parameter_id in parameter_ids:
            if parameter_id not in parameter_genes_without_phenotype_map:
                continue
            if genes_without_significant is None:
                genes_without_significant = set(parameter_genes_without_phenotype_map[parameter_id])
            else:
                genes_without_significant &= parameter_genes_without_phenotype_map[parameter_id]
        genes_without_significant = genes_without_significant or set()

        term_genes_without_significant[term_id] = genes_without_significant
    return dict(term_genes_without_significant)


# def _get_related_parameter_ids(
#     mp_term_id: str, term_parameters_map, ontology_terms: dict[str, dict[str, str]]
# ) -> set[str]:
#     _, child_term_map = similarity_calculator._build_term_hierarchy(ontology_terms)
#     descendants_of_term_id = similarity_calculator._find_all_descendant_terms(mp_term_id, child_term_map)

#     related_parameter_ids = set()
#     for term_id in descendants_of_term_id:
#         if term_id in term_parameters_map:
#             related_parameter_ids |= term_parameters_map[term_id]

#     return related_parameter_ids


def _extract_genes_without_specific_phenotype(
    term_genes_without_significant: dict[str, set[str]], descendants_of_term_id: set[str]
) -> set[str]:
    """Rather than simply genes with no recorded phenotype (where it is unclear whether the phenotype was measured or not),
    extract the group of genes for which measurements were definitely conducted but no phenotype was observed."""
    pass
    # records: Iterator[dict[str, str]] = io_handler.load_csv_as_dicts(Path(path_statistical_all))
    # records_grouped = groupby(sorted(records, key=lambda r: r["marker_symbol"]), key=lambda r: r["marker_symbol"])

    # genes_without_specific_phenotype = set()
    # for gene, group in tqdm(records_grouped, desc="Extracting genes without specific phenotype"):
    #     with_mp_term = False
    #     is_assayed = False

    #     for record in group:
    #         if record["parameter_stable_id"] in related_parameter_ids:
    #             is_assayed = True
    #             if record["mp_term_id"]:
    #                 with_mp_term = True

    #     if gene and is_assayed and with_mp_term is False:
    #         genes_without_specific_phenotype.add(gene)

    # return genes_without_specific_phenotype


def exclude_specific_phenotype(
    path_phenotype_similarity_per_gene_pair: str | Path,
    path_statistical_all: str | Path,
    path_obo: str | Path,
    mp_term_id: set[str],
) -> None:
    cache_dir = Path(path_statistical_all).parent / ".tsumugi_cache"
    if not (cache_dir / "term_genes_without_significant.pkl").exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        term_parameters_map = _build_term_parameters_map(path_statistical_all)
        parameter_genes_without_phenotype_map = _build_parameter_genes_without_phenotype_map(path_statistical_all)
        term_genes_without_significant = _build_term_genes_without_significant(
            term_parameters_map, parameter_genes_without_phenotype_map
        )
        pickle.dump(term_genes_without_significant, open(cache_dir / "term_genes_without_significant.pkl", "wb"))
    else:
        term_genes_without_significant = pickle.load(open(cache_dir / "term_genes_without_significant.pkl", "rb"))

    ontology_terms = io_handler.parse_obo_file(path_obo)
    _, child_term_map = similarity_calculator._build_term_hierarchy(ontology_terms)
    descendants_of_term_id = similarity_calculator._find_all_descendant_terms(mp_term_id, child_term_map)
    # related_parameter_ids = _get_related_parameter_ids(mp_term_id, term_parameters_map, ontology_terms)
    genes_without_specific_phenotype = _extract_genes_without_specific_phenotype(
        term_genes_without_significant, descendants_of_term_id
    )

    pair_similarity_annotations = io_handler.read_jsonl(path_phenotype_similarity_per_gene_pair)
    for record in tqdm(pair_similarity_annotations, desc="Filtering gene pairs"):
        if (
            record["gene1_symbol"] in genes_without_specific_phenotype
            and record["gene2_symbol"] in genes_without_specific_phenotype
        ):
            # output to stdout as JSON
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

    pair_similarity_annotations = io_handler.read_jsonl(path_phenotype_similarity_per_gene_pair)
    for record in tqdm(pair_similarity_annotations, desc="Filtering gene pairs"):
        if not set(record["phenotype_shared_annotations"].keys()).intersection(descendants_of_term_name):
            continue
        # output to stdout as JSON
        json.dump(record, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
