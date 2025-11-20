from collections.abc import Iterator
from pathlib import Path

from TSUMUGI import io_handler


def _filter_annotations_by_genes(
    pairwise_similarity_annotations: Iterator[dict[str, str | dict[str, dict] | dict[str | int]]],
    gene_list: set[str],
    keep: bool = False,
    drop: bool = False,
) -> Iterator[dict[str, str | dict[str, dict] | dict[str | int]]]:
    for pairwise_similarity_annotation in pairwise_similarity_annotations:
        gene1 = pairwise_similarity_annotation["gene1_symbol"]
        gene2 = pairwise_similarity_annotation["gene2_symbol"]

        # Keep if either gene is in the list
        if (gene1 in gene_list or gene2 in gene_list) and keep:
            yield pairwise_similarity_annotation
        # Drop only when both genes are not in the list
        if (gene1 not in gene_list and gene2 not in gene_list) and drop:
            yield pairwise_similarity_annotation


def filter_annotations_by_genes(
    path_pairwise_similarity_annotations: str | Path,
    gene_list: set[str],
    keep: bool = False,
    drop: bool = False,
) -> None:
    pairwise_similarity_annotations = io_handler.read_jsonl(path_pairwise_similarity_annotations)
    for record in _filter_annotations_by_genes(
        pairwise_similarity_annotations=pairwise_similarity_annotations,
        gene_list=gene_list,
        keep=keep,
        drop=drop,
    ):
        # output to stdout as JSONL
        io_handler.safe_jsonl_dump(record)
