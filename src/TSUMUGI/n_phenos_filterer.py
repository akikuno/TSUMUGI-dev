from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from tqdm import tqdm

from TSUMUGI import io_handler


def filter_by_number_of_phenotypes_per_gene(
    path_phenotype_similarity_per_gene_pair: str | Path | None,
    path_significant_phenotypes_per_gene: str | Path,
    min_phenotypes: int | None = None,
    max_phenotypes: int | None = None,
) -> list[dict[str, str]]:
    records_significants = io_handler.parse_jsonl_gz_to_records_significants(path_significant_phenotypes_per_gene)

    cnt = Counter(rec["marker_symbol"] for rec in records_significants)
    matched_genes = {
        marker
        for marker, c in cnt.items()
        if (min_phenotypes is None or c >= min_phenotypes) and (max_phenotypes is None or c <= max_phenotypes)
    }

    pair_similarity_annotations = io_handler.parse_jsonl_gz_to_pair_map(path_phenotype_similarity_per_gene_pair)
    for gene_pair, annotation in tqdm(pair_similarity_annotations.items(), desc="Filtering gene pairs"):
        if not gene_pair.issubset(matched_genes):
            continue

        # output to stdout as JSON
        gene1, gene2 = sorted(gene_pair)
        record = {"gene1_symbol": gene1, "gene2_symbol": gene2, **annotation}
        json.dump(record, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")


def filter_by_number_of_phenotypes_per_pair(
    path_phenotype_similarity_per_gene_pair: str | Path | None,
    min_phenotypes: int | None = None,
    max_phenotypes: int | None = None,
) -> list[dict[str, str]]:
    pair_similarity_annotations = io_handler.parse_jsonl_gz_to_pair_map(path_phenotype_similarity_per_gene_pair)
    for gene_pair, annotation in tqdm(pair_similarity_annotations.items(), desc="Filtering gene pairs"):
        num_shared_phenotypes = len(annotation["phenotype_shared_annotations"])
        if min_phenotypes is not None and num_shared_phenotypes < min_phenotypes:
            continue
        if max_phenotypes is not None and num_shared_phenotypes > max_phenotypes:
            continue
        # output to stdout as JSON
        gene1, gene2 = sorted(gene_pair)
        record = {"gene1_symbol": gene1, "gene2_symbol": gene2, **annotation}
        json.dump(record, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
