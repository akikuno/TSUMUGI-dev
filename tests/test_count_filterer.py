import pytest

from TSUMUGI import argparser
from TSUMUGI.subcommands import count_filterer


def test_parse_args_accepts_count_pairwise():
    args = argparser.parse_args(["count", "-p", "--min", "3"])

    assert args.cmd == "count"
    assert args.pairwise is True
    assert args.genewise is False
    assert args.min == 3
    assert args.max is None


def test_parse_args_accepts_count_genewise():
    args = argparser.parse_args(["count", "-g", "--min", "1", "--max", "5", "-a", "genewise.jsonl"])

    assert args.cmd == "count"
    assert args.genewise is True
    assert args.pairwise is False
    assert args.path_genewise == "genewise.jsonl"
    assert args.min == 1
    assert args.max == 5


def test_filter_by_number_of_phenotypes_per_gene(monkeypatch):
    genewise_annotations = [
        {"marker_symbol": "GeneA", "significant": True},
        {"marker_symbol": "GeneA", "significant": True},
        {"marker_symbol": "GeneB", "significant": True},
        {"marker_symbol": "GeneB", "significant": True},
        {"marker_symbol": "GeneC", "significant": True},
    ]
    pairwise_annotations = [
        {"gene1_symbol": "GeneA", "gene2_symbol": "GeneB", "phenotype_shared_annotations": {"x": {}}},
        {"gene1_symbol": "GeneA", "gene2_symbol": "GeneC", "phenotype_shared_annotations": {"y": {}}},
        {"gene1_symbol": "GeneB", "gene2_symbol": "GeneC", "phenotype_shared_annotations": {"z": {}}},
    ]
    dumped = []

    def fake_read_jsonl(path):
        if path == "genewise-path":
            return genewise_annotations
        return pairwise_annotations

    monkeypatch.setattr(count_filterer.io_handler, "read_jsonl", fake_read_jsonl)
    monkeypatch.setattr(count_filterer.io_handler, "safe_jsonl_dump", lambda record: dumped.append(record))
    monkeypatch.setattr(count_filterer, "tqdm", lambda iterable, desc=None: iterable)

    count_filterer.filter_by_number_of_phenotypes_per_gene(
        path_pairwise_similarity_annotations="pairwise-path",
        path_genewise_phenotype_annotations="genewise-path",
        min_phenotypes=2,
        max_phenotypes=2,
    )

    assert dumped == [pairwise_annotations[0]]


def test_filter_by_number_of_phenotypes_per_pair(monkeypatch):
    pairwise_annotations = [
        {"gene1_symbol": "GeneA", "gene2_symbol": "GeneB", "phenotype_shared_annotations": {"a": {}, "b": {}}},
        {"gene1_symbol": "GeneC", "gene2_symbol": "GeneD", "phenotype_shared_annotations": {"c": {}}},
        {
            "gene1_symbol": "GeneE",
            "gene2_symbol": "GeneF",
            "phenotype_shared_annotations": {"x": {}, "y": {}, "z": {}},
        },
    ]
    dumped = []

    monkeypatch.setattr(count_filterer.io_handler, "read_jsonl", lambda path: pairwise_annotations)
    monkeypatch.setattr(count_filterer.io_handler, "safe_jsonl_dump", lambda record: dumped.append(record))

    count_filterer.filter_by_number_of_phenotypes_per_pair(
        path_pairwise_similarity_annotations="pairwise-path",
        min_phenotypes=2,
        max_phenotypes=2,
    )

    assert dumped == [pairwise_annotations[0]]
