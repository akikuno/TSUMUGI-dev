from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from collections.abc import Iterator
from itertools import groupby
from pathlib import Path

from tqdm import tqdm

from TSUMUGI import io_handler, similarity_calculator
from TSUMUGI.formatter import convert_jsonl_gz_to_pair_map, floatinize_columns


def subset_columns(records: Iterator[dict[str, str]], columns: list[str]) -> Iterator[dict[str, str]]:
    """Yield dicts keeping only the requested columns; missing keys become empty strings."""
    for record in records:
        yield {col: record.get(col, "") for col in columns}


def _is_significant(rec: dict[str, float | str], threshold: float) -> bool:
    """Significance rule:
    - If p_value is NaN and effect_size is finite -> keep.
        * some phenotypes may have significance without no p_value but an effect_size
        (e.g. Exoc6: https://www.mousephenotype.org/data/genes/MGI:1351611)
    - OR any of the three p-values is below threshold -> keep.
    """
    if math.isnan(rec["p_value"]) and not math.isnan(rec["effect_size"]):
        return True
    return (
        rec["p_value"] < threshold
        or rec["female_ko_effect_p_value"] < threshold
        or rec["male_ko_effect_p_value"] < threshold
    )


def extract_significant_phenotypes(
    records: Iterator[dict[str, str]], float_columns: list[str], threshold: float = 1e-4
) -> list[dict[str, float | str]]:
    """
    Filter significant phenotype records and drop exact duplicates (key+value match).
    """
    significants: list[dict[str, float | str]] = []

    for record in tqdm(records, desc="Filtering significant phenotypes"):
        # Skip when 'mp_term_name' is empty
        if not record.get("mp_term_name"):
            continue

        # Normalize numeric fields and evaluate significance
        record = floatinize_columns(record, float_columns)
        if _is_significant(record, threshold):
            significants.append(record)

    # Deduplicate by full key-value equality; ordering does not matter
    # Use a sorted tuple of items as a stable, hashable fingerprint.
    seen = set()
    unique_records = []
    for record in significants:
        fingerprint = tuple(sorted(record.items()))
        if fingerprint not in seen:
            seen.add(fingerprint)
            unique_records.append(record)

    return unique_records


###########################################################
# Exclude gene pairs with target_mp_term_id and its descendants
###########################################################


def _extract_term_parameters_map(path_statistical_all: str | Path) -> dict[str, set[str]]:
    records: Iterator[dict[str, str]] = io_handler.load_csv_as_dicts(Path(path_statistical_all))
    term_parameters_map = defaultdict(set)
    for record in tqdm(records):
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
    for gene, group in records_grouped:
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
    path_path_statistical_all: str | Path,
    path_mp_obo: str | Path,
    mp_term_id: set[str],
) -> None:
    ontology_terms = io_handler.parse_obo_file(path_mp_obo)
    term_parameters_map = _extract_term_parameters_map(path_path_statistical_all)
    related_parameter_ids = _get_related_parameter_ids(mp_term_id, term_parameters_map, ontology_terms)
    genes_without_specific_phenotype = _extract_genes_without_specific_phenotype(
        path_path_statistical_all, related_parameter_ids
    )

    pair_similarity_annotations = convert_jsonl_gz_to_pair_map(path_phenotype_similarity_per_gene_pair)
    for gene_pair, annotation in pair_similarity_annotations.items():
        if gene_pair.isdisjoint(genes_without_specific_phenotype):
            continue
        # output to stdout as JSON
        gene1, gene2 = sorted(gene_pair)
        record = {"gene1_symbol": gene1, "gene2_symbol": gene2, **annotation}
        json.dump(record, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")


def include_specific_phenotype(
    path_phenotype_similarity_per_gene_pair: str | Path, path_mp_obo: str | Path, term_id: str
) -> None:
    ontology_terms = io_handler.parse_obo_file(path_mp_obo)
    _, child_term_map = similarity_calculator._build_term_hierarchy(ontology_terms)
    descendants_of_term_id: set[str] = similarity_calculator._find_all_descendant_terms(term_id, child_term_map)
    descendants_of_term_name = {
        data["name"] for term_id, data in ontology_terms.items() if term_id in descendants_of_term_id
    }

    pair_similarity_annotations = convert_jsonl_gz_to_pair_map(path_phenotype_similarity_per_gene_pair)
    for gene_pair, annotation in pair_similarity_annotations.items():
        if not set(annotation["phenotype_shared_annotations"].keys()).intersection(descendants_of_term_name):
            continue
        # output to stdout as JSON
        gene1, gene2 = sorted(gene_pair)
        record = {"gene1_symbol": gene1, "gene2_symbol": gene2, **annotation}
        json.dump(record, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
