import pytest
from TSUMUGI.subcommands import genes_filterer
from TSUMUGI.subcommands.genes_filterer import (
    _filter_annotations_by_gene_pairs,
    _filter_annotations_by_genes,
    filter_annotations_by_gene_pairs,
)


@pytest.fixture
def base_input():
    return [
        {
            "gene1_symbol": "GeneA",
            "gene2_symbol": "GeneB",
            "phenotype_shared_annotations": [
                {"mp_term_name": "dummy", "zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "None"}
            ],
            "phenotype_similarity_score": 70,
        },
        {
            "gene1_symbol": "GeneC",
            "gene2_symbol": "GeneD",
            "phenotype_shared_annotations": [
                {"mp_term_name": "dummy", "zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "None"}
            ],
            "phenotype_similarity_score": 60,
        },
        {
            "gene1_symbol": "GeneE",
            "gene2_symbol": "GeneF",
            "phenotype_shared_annotations": [
                {"mp_term_name": "dummy", "zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "None"}
            ],
            "phenotype_similarity_score": 50,
        },
    ]


def select_expected(records, indices):
    return [records[i] for i in indices]


@pytest.mark.parametrize(
    "genes,keep,drop,expected_idx",
    [
        # --- keep only: yield if either gene is in genes ---
        ({"GeneA"}, True, False, [0]),  # match on gene1
        ({"GeneD"}, True, False, [1]),  # match on gene2
        ({"GeneX"}, True, False, []),  # no match
        # --- drop only: yield if both genes are NOT in genes ---
        ({"GeneA"}, False, True, [1, 2]),  # exclude record 0 from output
        ({"GeneC", "GeneD"}, False, True, [0, 2]),
        ({"GeneA", "GeneB", "GeneC", "GeneD", "GeneE", "GeneF"}, False, True, []),
        # --- empty genes set edge cases ---
        (set(), True, False, []),  # keep nothing
        (set(), False, True, [0, 1, 2]),  # drop all (both not in empty set)
    ],
)
def test_filter_annotations_by_genes_parametrized(base_input, genes, keep, drop, expected_idx):
    out = list(
        _filter_annotations_by_genes(
            pairwise_similarity_annotations=base_input,
            gene_list=genes,
            keep=keep,
            drop=drop,
        )
    )
    assert out == select_expected(base_input, expected_idx)


def test_empty_input_yields_nothing():
    out = list(
        _filter_annotations_by_genes(
            pairwise_similarity_annotations=[],
            gene_list={"GeneA"},
            keep=True,
            drop=False,
        )
    )
    assert out == []


@pytest.mark.parametrize(
    "gene_pairs,keep,drop,expected_idx",
    [
        ({frozenset({"GeneA", "GeneB"})}, True, False, [0]),
        ({frozenset({"GeneA", "GeneB"})}, False, True, [1, 2]),
        ({frozenset({"GeneX", "GeneY"})}, True, False, []),
        (set(), False, True, [0, 1, 2]),
    ],
)
def test_filter_annotations_by_gene_pairs_parametrized(base_input, gene_pairs, keep, drop, expected_idx):
    out = list(
        _filter_annotations_by_gene_pairs(
            pairwise_similarity_annotations=base_input,
            gene_pairs=gene_pairs,
            keep=keep,
            drop=drop,
        )
    )
    assert out == select_expected(base_input, expected_idx)


def test_filter_annotations_by_gene_pairs_reads_and_writes(monkeypatch, base_input):
    dumped = []

    monkeypatch.setattr(genes_filterer.io_handler, "read_jsonl", lambda path: base_input)
    monkeypatch.setattr(genes_filterer.io_handler, "write_jsonl_to_stdout", lambda record: dumped.append(record))

    filter_annotations_by_gene_pairs(
        path_pairwise_similarity_annotations="pairwise-path",
        gene_pairs={frozenset({"GeneC", "GeneD"})},
        keep=True,
    )

    assert dumped == [base_input[1]]
