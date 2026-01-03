import copy

from TSUMUGI import network_constructor


def test_scale_phenotype_similarity_scores_does_not_mutate_input():
    input_data = {
        ("GeneA", "GeneB"): {
            "phenotype_shared_annotations": {"P1"},
            "phenotype_similarity_score": 10,
        },
        ("GeneC", "GeneD"): {
            "phenotype_shared_annotations": {"P2", "P3"},
            "phenotype_similarity_score": 30,
        },
    }
    original = copy.deepcopy(input_data)

    scaled = network_constructor._scale_phenotype_similarity_scores(input_data)

    assert input_data == original
    assert scaled is not input_data
    assert scaled[("GeneA", "GeneB")] is not input_data[("GeneA", "GeneB")]
    assert scaled[("GeneA", "GeneB")]["phenotype_similarity_score"] == 1
    assert scaled[("GeneC", "GeneD")]["phenotype_similarity_score"] == 100


def test_scale_phenotype_similarity_scores_all_same_value():
    input_data = {
        ("GeneA", "GeneB"): {
            "phenotype_shared_annotations": {"P1"},
            "phenotype_similarity_score": 42,
        },
        ("GeneC", "GeneD"): {
            "phenotype_shared_annotations": {"P2"},
            "phenotype_similarity_score": 42,
        },
    }

    scaled = network_constructor._scale_phenotype_similarity_scores(input_data)

    assert scaled[("GeneA", "GeneB")]["phenotype_similarity_score"] == 100
    assert scaled[("GeneC", "GeneD")]["phenotype_similarity_score"] == 100


def test_scale_phenotype_similarity_scores_target_gene_only():
    input_data = {
        ("GeneA", "GeneB"): {
            "phenotype_shared_annotations": {"P1"},
            "phenotype_similarity_score": 30,
        },
        ("GeneA", "GeneC"): {
            "phenotype_shared_annotations": {"P2"},
            "phenotype_similarity_score": 40,
        },
        ("GeneB", "GeneC"): {
            "phenotype_shared_annotations": {"P3"},
            "phenotype_similarity_score": 10,
        },
    }

    scaled = network_constructor._scale_phenotype_similarity_scores(input_data, target_gene="GeneA")

    assert scaled[("GeneA", "GeneB")]["phenotype_similarity_score"] == 1
    assert scaled[("GeneA", "GeneC")]["phenotype_similarity_score"] == 100
