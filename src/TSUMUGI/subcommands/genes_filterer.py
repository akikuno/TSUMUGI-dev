from collections.abc import Iterator
from pathlib import Path

from TSUMUGI import io_handler

###############################################################################
# filter_annotations_by_genes
###############################################################################


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
        # - gene1: A, gene2: B, gene_list: {A, C} -> Keep
        # - gene1: D, gene2: E, gene_list: {A, C} -> Drop
        if (gene1 in gene_list or gene2 in gene_list) and keep:
            yield pairwise_similarity_annotation

        # Drop only when both genes are not in the list
        # - gene1: A, gene2: B, gene_list: {A, C} -> Drop
        # - gene1: D, gene2: E, gene_list: {A, C} -> Keep
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


###############################################################################
# filter_annotations_by_gene_pairs
###############################################################################


def _filter_annotations_by_gene_pairs(
    pairwise_similarity_annotations: Iterator[dict[str, str | dict[str, dict] | dict[str | int]]],
    gene_pairs: set[frozenset[str]],
    keep: bool = False,
    drop: bool = False,
) -> Iterator[dict[str, str | dict[str, dict] | dict[str | int]]]:
    for pairwise_similarity_annotation in pairwise_similarity_annotations:
        gene1 = pairwise_similarity_annotation["gene1_symbol"]
        gene2 = pairwise_similarity_annotation["gene2_symbol"]
        gene_pair = frozenset({gene1, gene2})

        # Keep if either gene is in the list
        if gene_pair in gene_pairs and keep:
            yield pairwise_similarity_annotation
        # Drop only when both genes are not in the list
        if gene_pair not in gene_pairs and drop:
            yield pairwise_similarity_annotation


def filter_annotations_by_gene_pairs(
    path_pairwise_similarity_annotations: str | Path,
    gene_pairs: set[frozenset[str]],
    keep: bool = False,
    drop: bool = False,
):
    pairwise_similarity_annotations = io_handler.read_jsonl(path_pairwise_similarity_annotations)
    for record in _filter_annotations_by_gene_pairs(
        pairwise_similarity_annotations=pairwise_similarity_annotations,
        gene_pairs=gene_pairs,
        keep=keep,
        drop=drop,
    ):
        # output to stdout as JSONL
        io_handler.safe_jsonl_dump(record)
