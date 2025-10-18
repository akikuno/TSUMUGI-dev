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
    records_significants = io_handler.read_jsonl(path_significant_phenotypes_per_gene)

    cnt = Counter(rec["marker_symbol"] for rec in records_significants)
    matched_genes = {
        marker
        for marker, c in cnt.items()
        if (min_phenotypes is None or c >= min_phenotypes) and (max_phenotypes is None or c <= max_phenotypes)
    }
    records = io_handler.read_jsonl(path_phenotype_similarity_per_gene_pair)
    for record in tqdm(records, desc="Filtering gene pairs"):
        # check both genes in the pair match the criteria
        if record["gene1_symbol"] in matched_genes and record["gene2_symbol"] in matched_genes:
            # output to stdout as JSON
            json.dump(record, sys.stdout, ensure_ascii=False)
            sys.stdout.write("\n")


def filter_by_number_of_phenotypes_per_pair(
    path_phenotype_similarity_per_gene_pair: str | Path | None,
    min_phenotypes: int | None = None,
    max_phenotypes: int | None = None,
) -> list[dict[str, str]]:
    records = io_handler.read_jsonl(path_phenotype_similarity_per_gene_pair)
    for record in tqdm(records, desc="Filtering gene pairs"):
        num_shared_phenotypes = len(record["phenotype_shared_annotations"])
        if min_phenotypes is not None and num_shared_phenotypes < min_phenotypes:
            continue
        if max_phenotypes is not None and num_shared_phenotypes > max_phenotypes:
            continue

        # output to stdout as JSON
        json.dump(record, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
