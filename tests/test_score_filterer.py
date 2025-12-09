import pytest

from TSUMUGI import argparser
from TSUMUGI.subcommands import score_filterer


def test_parse_args_accepts_score_min_max():
    args = argparser.parse_args(["score", "--min", "10", "--max", "50"])

    assert args.cmd == "score"
    assert args.min == 10
    assert args.max == 50


def test_parse_args_requires_min_or_max():
    with pytest.raises(SystemExit) as excinfo:
        argparser.parse_args(["score"])

    assert excinfo.value.code == 2


def test_filter_by_score_with_min_and_max(monkeypatch):
    pairwise_annotations = [
        {"gene1_symbol": "GeneA", "gene2_symbol": "GeneB", "phenotype_similarity_score": 30},
        {"gene1_symbol": "GeneC", "gene2_symbol": "GeneD", "phenotype_similarity_score": 60},
        {"gene1_symbol": "GeneE", "gene2_symbol": "GeneF", "phenotype_similarity_score": 90},
    ]
    dumped = []

    monkeypatch.setattr(score_filterer.io_handler, "read_jsonl", lambda path: pairwise_annotations)
    monkeypatch.setattr(score_filterer.io_handler, "safe_jsonl_dump", lambda record: dumped.append(record))

    score_filterer.filter_by_score_of_phenotypes_per_pair(
        path_pairwise_similarity_annotations="pairwise-path",
        min_phenotypes=50,
        max_phenotypes=80,
    )

    assert dumped == [pairwise_annotations[1]]


def test_filter_by_score_with_only_min(monkeypatch):
    pairwise_annotations = [
        {"gene1_symbol": "GeneA", "gene2_symbol": "GeneB", "phenotype_similarity_score": 30},
        {"gene1_symbol": "GeneC", "gene2_symbol": "GeneD", "phenotype_similarity_score": 60},
        {"gene1_symbol": "GeneE", "gene2_symbol": "GeneF", "phenotype_similarity_score": 90},
    ]
    dumped = []

    monkeypatch.setattr(score_filterer.io_handler, "read_jsonl", lambda path: pairwise_annotations)
    monkeypatch.setattr(score_filterer.io_handler, "safe_jsonl_dump", lambda record: dumped.append(record))

    score_filterer.filter_by_score_of_phenotypes_per_pair(
        path_pairwise_similarity_annotations="pairwise-path",
        min_phenotypes=60,
        max_phenotypes=None,
    )

    assert dumped == [pairwise_annotations[1], pairwise_annotations[2]]
