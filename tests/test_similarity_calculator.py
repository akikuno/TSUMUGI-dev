import numpy as np
import pytest
from TSUMUGI.ontology_handler import build_term_hierarchy
from TSUMUGI.similarity_calculator import (
    _apply_phenodigm_scaling,
    _calculate_pair_mica_and_resnik,
    _calculate_term_ic_map,
    _calculate_weighted_similarity_matrix,
    _delete_parent_terms_from_ancestors,
    annotate_phenotype_ancestors,
    calculate_all_pairwise_similarities,
    calculate_phenodigm_score,
    summarize_similarity_annotations,
)


@pytest.fixture
def sample_ontology():
    r"""
    Fixture that supplies sample ontology data for testing.
    Hierarchy:
          A (root)
         / \
        B   C
       / \ /
      D   E
          |
          F
    """
    ontology_terms = {
        "A": {"id": "A", "name": "Root"},
        "B": {"id": "B", "name": "Term B", "is_a": ["A"]},
        "C": {"id": "C", "name": "Term C", "is_a": ["A"]},
        "D": {"id": "D", "name": "Term D", "is_a": ["B"]},
        "E": {"id": "E", "name": "Term E", "is_a": ["B", "C"]},
        "F": {"id": "F", "name": "Term F", "is_a": ["E"]},
    }
    parent_map, child_map = build_term_hierarchy(ontology_terms)
    return {
        "ontology_terms": ontology_terms,
        "parent_map": parent_map,
        "child_map": child_map,
        "total_term_count": len(ontology_terms),
    }


@pytest.mark.parametrize(
    "term1, term2, expected_mica",
    [
        ("D", "E", "B"),  # Common ancestors: {B, A} -> B has higher IC
        ("D", "F", "B"),  # Common ancestors: {B, A} -> B
        ("B", "C", "A"),  # Common ancestors: {A} -> A
        ("F", "F", "F"),  # Same term
    ],
)
def test_calculate_pair_mica_and_resnik(sample_ontology, term1, term2, expected_mica):
    ontology_terms = sample_ontology["ontology_terms"]
    parent_map = sample_ontology["parent_map"]
    child_map = sample_ontology["child_map"]

    ic_map = _calculate_term_ic_map(ontology_terms, child_map)

    mica, sim = _calculate_pair_mica_and_resnik(term1, term2, parent_map, ic_map)

    assert mica == expected_mica
    assert sim == pytest.approx(ic_map[expected_mica])


def test_apply_phenodigm_scaling_identical_phenotypes():
    """
    Case 1: When phenotype sets match exactly, score should be 100.
    """

    term_ic_map = {"MP:A": 2.0, "MP:B": 4.0}
    ic_scores = np.array([term_ic_map["MP:A"], term_ic_map["MP:B"]], dtype=float)
    gene1_data = {
        "terms": np.array(["MP:A", "MP:B"], dtype=object),
        "zygosity": np.array(["hom", "hom"], dtype=object),
        "life_stage": np.array(["A", "A"], dtype=object),
        "sexual_dimorphism": np.array(["None", "None"], dtype=object),
        "ic_scores": ic_scores,
        "ic_max": float(ic_scores.max()),
    }
    gene2_data = gene1_data

    weighted_similarity_matrix = np.array([[2.0, 1.0], [1.0, 4.0]])

    result = _apply_phenodigm_scaling(
        weighted_similarity_matrix,
        gene1_data,
        gene2_data,
    )

    assert result == 100


def test_apply_phenodigm_scaling_disjoint_phenotypes():
    """
    Case 2: Completely disjoint phenotype sets should produce score 0.
    """

    term_ic_map = {"MP:A": 2.0, "MP:B": 4.0, "MP:C": 3.0, "MP:D": 5.0}
    gene1_ic = np.array([term_ic_map["MP:A"], term_ic_map["MP:B"]], dtype=float)
    gene2_ic = np.array([term_ic_map["MP:C"], term_ic_map["MP:D"]], dtype=float)
    gene1_data = {
        "terms": np.array(["MP:A", "MP:B"], dtype=object),
        "zygosity": np.array(["hom", "hom"], dtype=object),
        "life_stage": np.array(["A", "A"], dtype=object),
        "sexual_dimorphism": np.array(["None", "None"], dtype=object),
        "ic_scores": gene1_ic,
        "ic_max": float(gene1_ic.max()),
    }
    gene2_data = {
        "terms": np.array(["MP:C", "MP:D"], dtype=object),
        "zygosity": np.array(["hom", "hom"], dtype=object),
        "life_stage": np.array(["A", "A"], dtype=object),
        "sexual_dimorphism": np.array(["None", "None"], dtype=object),
        "ic_scores": gene2_ic,
        "ic_max": float(gene2_ic.max()),
    }

    weighted_similarity_matrix = np.array([[0.0, 0.0], [0.0, 0.0]])

    result = _apply_phenodigm_scaling(
        weighted_similarity_matrix,
        gene1_data,
        gene2_data,
    )

    assert result == 0


def test_apply_phenodigm_scaling_average_score_50():
    """
    Case 3: Observed similarity is exactly half of theoretical maximum -> score 50.
    """

    term_ic_map = {"MP:A": 4.0, "MP:B": 4.0}

    gene1_ic = np.array([term_ic_map["MP:A"]], dtype=float)
    gene2_ic = np.array([term_ic_map["MP:B"]], dtype=float)
    gene1_data = {
        "terms": np.array(["MP:A"], dtype=object),
        "zygosity": np.array(["hom"], dtype=object),
        "life_stage": np.array(["A"], dtype=object),
        "sexual_dimorphism": np.array(["None"], dtype=object),
        "ic_scores": gene1_ic,
        "ic_max": float(gene1_ic.max()),
    }
    gene2_data = {
        "terms": np.array(["MP:B"], dtype=object),
        "zygosity": np.array(["hom"], dtype=object),
        "life_stage": np.array(["A"], dtype=object),
        "sexual_dimorphism": np.array(["None"], dtype=object),
        "ic_scores": gene2_ic,
        "ic_max": float(gene2_ic.max()),
    }

    weighted_similarity_matrix = np.array([[2.0]])

    result = _apply_phenodigm_scaling(
        weighted_similarity_matrix,
        gene1_data,
        gene2_data,
    )

    assert result == 50


def test_calculate_weighted_similarity_matrix_metadata_weights():
    gene1_data = {
        "terms": np.array(["T1", "T2"], dtype=object),
        "zygosity": np.array(["hom", "het"], dtype=object),
        "life_stage": np.array(["E", "A"], dtype=object),
        "sexual_dimorphism": np.array(["None", "None"], dtype=object),
    }
    gene2_data = {
        "terms": np.array(["T1", "T3"], dtype=object),
        "zygosity": np.array(["hom", "het"], dtype=object),
        "life_stage": np.array(["E", "E"], dtype=object),
        "sexual_dimorphism": np.array(["None", "None"], dtype=object),
    }
    term_pair_similarity_map = {
        ("T1", "T1"): {"T1": 4.0},
        ("T1", "T2"): {"T1": 3.0},
        ("T1", "T3"): {"T1": 1.0},
        ("T2", "T3"): {"T2": 2.0},
    }

    weighted = _calculate_weighted_similarity_matrix(gene1_data, gene2_data, term_pair_similarity_map)

    expected = np.array(
        [
            [4.0, 0.75],  # full match -> 1.0, two-of-three match -> 0.75
            [1.5, 1.5],  # one-of-three -> 0.5 * 3.0, two-of-three -> 0.75 * 2.0
        ]
    )
    np.testing.assert_allclose(weighted, expected)


def test_calculate_all_pairwise_similarities_single_thread(sample_ontology):
    ontology_terms = sample_ontology["ontology_terms"]
    child_map = sample_ontology["child_map"]
    term_ids = set(ontology_terms.keys())

    result = calculate_all_pairwise_similarities(ontology_terms, term_ids, threads=1)
    if isinstance(result, tuple):
        pair_map, ic_map = result
    else:
        pair_map = result
        ic_map = _calculate_term_ic_map(ontology_terms, child_map)

    assert ("B", "E") in pair_map
    assert pair_map[("D", "E")]  # similarity map exists for each pair
    assert len(ic_map) == len(term_ids)


def test_delete_parent_terms_from_ancestors_removes_parent_with_same_meta(sample_ontology):
    child_map = sample_ontology["child_map"]
    meta = {"zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "None"}
    candidate_ancestors = [
        {"mp_term_name": "B", **meta},
        {"mp_term_name": "D", **meta},
        {"mp_term_name": "E", "zygosity": "Homo", "life_stage": "Late", "sexual_dimorphism": "None"},
    ]

    result = _delete_parent_terms_from_ancestors(candidate_ancestors, child_map)

    expected = [
        {"mp_term_name": "D", **meta},
        {"mp_term_name": "E", "zygosity": "Homo", "life_stage": "Late", "sexual_dimorphism": "None"},
    ]
    assert sorted(result, key=lambda item: item["mp_term_name"]) == sorted(
        expected, key=lambda item: item["mp_term_name"]
    )


def test_delete_parent_terms_from_ancestors_keeps_parent_with_different_meta(sample_ontology):
    child_map = sample_ontology["child_map"]
    candidate_ancestors = [
        {"mp_term_name": "B", "zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "None"},
        {"mp_term_name": "D", "zygosity": "Hetero", "life_stage": "Early", "sexual_dimorphism": "None"},
    ]

    result = _delete_parent_terms_from_ancestors(candidate_ancestors, child_map)

    expected = [
        {"mp_term_name": "B", "zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "None"},
        {"mp_term_name": "D", "zygosity": "Hetero", "life_stage": "Early", "sexual_dimorphism": "None"},
    ]
    assert sorted(result, key=lambda item: item["mp_term_name"]) == sorted(
        expected, key=lambda item: item["mp_term_name"]
    )


def test_annotate_phenotype_ancestors_basic(sample_ontology):
    ontology_terms = sample_ontology["ontology_terms"]
    term_ids = set(ontology_terms.keys())

    result = calculate_all_pairwise_similarities(ontology_terms, term_ids, threads=1)
    term_pair_map = result[0] if isinstance(result, tuple) else result

    records = [
        {
            "marker_symbol": "Gene1",
            "mp_term_id": "D",
            "zygosity": "Homo",
            "life_stage": "Early",
            "sexual_dimorphism": "None",
        },
        {
            "marker_symbol": "Gene2",
            "mp_term_id": "E",
            "zygosity": "Homo",
            "life_stage": "Early",
            "sexual_dimorphism": "None",
        },
    ]

    ancestors = list(
        annotate_phenotype_ancestors(
            genewise_phenotype_significants=records,
            terms_similarity_map=term_pair_map,
            ontology_terms=ontology_terms,
        )
    )

    assert len(ancestors) == 1
    assert ancestors[0]["gene1_symbol"] == "Gene1"
    assert ancestors[0]["gene2_symbol"] == "Gene2"
    assert ancestors[0]["phenotype_shared_annotations"] == [
        {"mp_term_name": "B", "zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "None"}
    ]


def test_calculate_phenodigm_score_identical_gene_sets():
    records = [
        {
            "marker_symbol": "Gene1",
            "mp_term_id": "MP:1",
            "zygosity": "hom",
            "life_stage": "E",
            "sexual_dimorphism": "None",
        },
        {
            "marker_symbol": "Gene2",
            "mp_term_id": "MP:1",
            "zygosity": "hom",
            "life_stage": "E",
            "sexual_dimorphism": "None",
        },
    ]
    term_pair_similarity_map = {("MP:1", "MP:1"): {"MP:1": 2.0}}
    term_ic_map = {"MP:1": 2.0}

    scores = list(calculate_phenodigm_score(records, term_pair_similarity_map, term_ic_map))

    assert scores == [{"gene1_symbol": "Gene1", "gene2_symbol": "Gene2", "phenotype_similarity_score": 100}]


def test_summarize_similarity_annotations_translates_names():
    ontology_terms = {
        "MP:1": {"id": "MP:1", "name": "Term One"},
        "MP:2": {"id": "MP:2", "name": "Term Two"},
    }
    phenotype_ancestors = [
        {
            "gene1_symbol": "GeneA",
            "gene2_symbol": "GeneB",
            "phenotype_shared_annotations": [
                {
                    "mp_term_name": "MP:1",
                    "zygosity": "Homo",
                    "life_stage": "Early",
                    "sexual_dimorphism": "None",
                }
            ],
        },
        {"gene1_symbol": "GeneA", "gene2_symbol": "GeneC", "phenotype_shared_annotations": []},
    ]
    phenodigm_scores = [
        {"gene1_symbol": "GeneA", "gene2_symbol": "GeneB", "phenotype_similarity_score": 80},
        {"gene1_symbol": "GeneA", "gene2_symbol": "GeneC", "phenotype_similarity_score": 50},
    ]

    summary = list(
        summarize_similarity_annotations(ontology_terms, phenotype_ancestors, phenodigm_scores, total_pairs=2)
    )

    assert summary[0] == {
        "gene1_symbol": "GeneA",
        "gene2_symbol": "GeneB",
        "phenotype_shared_annotations": [
            {
                "mp_term_name": "Term One",
                "zygosity": "Homo",
                "life_stage": "Early",
                "sexual_dimorphism": "None",
            }
        ],
        "phenotype_similarity_score": 80,
    }
    # When no ancestors exist, the score should be zeroed out
    assert summary[1] == {
        "gene1_symbol": "GeneA",
        "gene2_symbol": "GeneC",
        "phenotype_shared_annotations": [],
        "phenotype_similarity_score": 0,
    }
