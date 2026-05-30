from TSUMUGI.core import _filter_pairwise_similarity_annotations_for_web


def test_filter_pairwise_similarity_annotations_for_web_uses_count_and_score():
    records = [
        {
            "gene1_symbol": "GeneA",
            "gene2_symbol": "GeneB",
            "phenotype_shared_annotations": [{}, {}, {}],
            "phenotype_similarity_score": 39,
        },
        {
            "gene1_symbol": "GeneC",
            "gene2_symbol": "GeneD",
            "phenotype_shared_annotations": [{}, {}],
            "phenotype_similarity_score": 80,
        },
        {
            "gene1_symbol": "GeneE",
            "gene2_symbol": "GeneF",
            "phenotype_shared_annotations": [{}, {}, {}],
            "phenotype_similarity_score": 40,
        },
    ]

    filtered = _filter_pairwise_similarity_annotations_for_web(
        iter(records),
        min_shared_annotations=3,
        min_phenotype_similarity_score=40,
    )

    assert filtered == [records[2]]
