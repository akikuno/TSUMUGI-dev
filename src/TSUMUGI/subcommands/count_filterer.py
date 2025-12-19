from __future__ import annotations

from collections import Counter
from pathlib import Path

from tqdm import tqdm

from TSUMUGI import io_handler


def filter_by_number_of_phenotypes_per_gene(
    path_pairwise_similarity_annotations: str | Path | None,
    path_genewise_phenotype_annotations: str | Path,
    min_phenotypes: int | None = None,
    max_phenotypes: int | None = None,
) -> None:
    genewise_phenotype_annotations = io_handler.read_jsonl(path_genewise_phenotype_annotations)

    cnt = Counter(rec["marker_symbol"] for rec in genewise_phenotype_annotations if rec["significant"])
    matched_genes = {
        marker
        for marker, c in cnt.items()
        if (min_phenotypes is None or c >= min_phenotypes) and (max_phenotypes is None or c <= max_phenotypes)
    }
    pairwise_similarity_annotations = io_handler.read_jsonl(path_pairwise_similarity_annotations)
    for record in tqdm(pairwise_similarity_annotations, desc="Filtering gene pairs"):
        # check both genes in the pair match the criteria
        if record["gene1_symbol"] in matched_genes and record["gene2_symbol"] in matched_genes:
            # output to stdout as JSON
            io_handler.write_jsonl_to_stdout(record)


def filter_by_number_of_phenotypes_per_pair(
    path_pairwise_similarity_annotations: str | Path | None,
    min_phenotypes: int | None = None,
    max_phenotypes: int | None = None,
) -> None:
    pairwise_similarity_annotations = io_handler.read_jsonl(path_pairwise_similarity_annotations)
    for record in pairwise_similarity_annotations:
        num_shared_phenotypes = len(record["phenotype_shared_annotations"])
        if min_phenotypes is not None and num_shared_phenotypes < min_phenotypes:
            continue
        if max_phenotypes is not None and num_shared_phenotypes > max_phenotypes:
            continue

        # output to stdout as JSON
        io_handler.write_jsonl_to_stdout(record)
