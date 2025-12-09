from __future__ import annotations

from pathlib import Path

from TSUMUGI import io_handler


def filter_by_score_of_phenotypes_per_pair(
    path_pairwise_similarity_annotations: str | Path | None,
    min_phenotypes: int | None = None,
    max_phenotypes: int | None = None,
) -> None:
    pairwise_similarity_annotations = io_handler.read_jsonl(path_pairwise_similarity_annotations)
    for record in pairwise_similarity_annotations:
        phenotype_similarity_score = record["phenotype_similarity_score"]
        if min_phenotypes is not None and phenotype_similarity_score < min_phenotypes:
            continue
        if max_phenotypes is not None and phenotype_similarity_score > max_phenotypes:
            continue

        # output to stdout as JSON
        io_handler.safe_jsonl_dump(record)
