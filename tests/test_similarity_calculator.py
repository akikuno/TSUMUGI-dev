import numpy as np
import pytest
from TSUMUGI.ontology_handler import build_term_hierarchy
from TSUMUGI.similarity_calculator import (
    _apply_phenodigm_scaling,
    _compute_pair_mica_and_resnik,
    _precompute_information_content,
    _prepare_similarity_maps,
    calculate_jaccard_indices,
    calculate_num_shared_phenotypes,
)


@pytest.fixture
def sample_ontology():
    """
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
def test_compute_pair_mica_and_resnik(sample_ontology, term1, term2, expected_mica):
    ontology_terms = sample_ontology["ontology_terms"]
    parent_map = sample_ontology["parent_map"]
    child_map = sample_ontology["child_map"]

    ic_map = _precompute_information_content(ontology_terms, child_map)

    mica, sim = _compute_pair_mica_and_resnik(term1, term2, parent_map, ic_map)

    assert mica == expected_mica
    assert sim == pytest.approx(ic_map[expected_mica])


def test_apply_phenodigm_scaling_identical_phenotypes():
    """
    Case 1: When phenotype sets match exactly, score should be 100.
    """

    term_pair_similarity_map = {
        frozenset(["MP:A"]): {"MP:A": 2.0},
        frozenset(["MP:B"]): {"MP:B": 4.0},
        frozenset(["MP:A", "MP:B"]): {"MP:A": 1.0},
    }
    _, term_ic_map = _prepare_similarity_maps(term_pair_similarity_map)
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

    term_pair_similarity_map = {
        frozenset(["MP:A"]): {"MP:A": 2.0},
        frozenset(["MP:B"]): {"MP:B": 4.0},
        frozenset(["MP:C"]): {"MP:C": 3.0},
        frozenset(["MP:D"]): {"MP:D": 5.0},
    }
    _, term_ic_map = _prepare_similarity_maps(term_pair_similarity_map)
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

    term_pair_similarity_map = {
        frozenset(["MP:A"]): {"MP:A": 4.0},
        frozenset(["MP:B"]): {"MP:B": 4.0},
    }
    _, term_ic_map = _prepare_similarity_maps(term_pair_similarity_map)

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


# ----------------------------------------------------------------------------
# Test Data for num_shared_phenotypes / jaccard_indices
# ----------------------------------------------------------------------------

records_basic = [
    {"marker_symbol": "GeneA", "mp_term_id": "MP:1", "zygosity": "hom", "life_stage": "E"},
    {"marker_symbol": "GeneA", "mp_term_id": "MP:2", "zygosity": "het", "life_stage": "A"},
    {"marker_symbol": "GeneB", "mp_term_id": "MP:2", "zygosity": "het", "life_stage": "A"},
    {"marker_symbol": "GeneB", "mp_term_id": "MP:3", "zygosity": "hom", "life_stage": "A"},
    {"marker_symbol": "GeneC", "mp_term_id": "MP:3", "zygosity": "hom", "life_stage": "A"},
]
expected_num_shared_basic = {
    frozenset(["GeneA", "GeneB"]): 1,
    frozenset(["GeneA", "GeneC"]): 0,
    frozenset(["GeneB", "GeneC"]): 1,
}
expected_jaccard_basic = {
    frozenset(["GeneA", "GeneB"]): 33,  # 1/3
    frozenset(["GeneA", "GeneC"]): 0,  # 0/3
    frozenset(["GeneB", "GeneC"]): 50,  # 1/2
}

records_no_overlap = [
    {"marker_symbol": "GeneX", "mp_term_id": "MP:1", "zygosity": "hom", "life_stage": "E"},
    {"marker_symbol": "GeneY", "mp_term_id": "MP:2", "zygosity": "het", "life_stage": "A"},
]
expected_num_shared_no_overlap = {frozenset(["GeneX", "GeneY"]): 0}
expected_jaccard_no_overlap = {frozenset(["GeneX", "GeneY"]): 0}

records_full_overlap = [
    {"marker_symbol": "GeneX", "mp_term_id": "MP:1", "zygosity": "hom", "life_stage": "E"},
    {"marker_symbol": "GeneX", "mp_term_id": "MP:2", "zygosity": "het", "life_stage": "A"},
    {"marker_symbol": "GeneY", "mp_term_id": "MP:1", "zygosity": "hom", "life_stage": "E"},
    {"marker_symbol": "GeneY", "mp_term_id": "MP:2", "zygosity": "het", "life_stage": "A"},
]
expected_num_shared_full_overlap = {frozenset(["GeneX", "GeneY"]): 2}
expected_jaccard_full_overlap = {frozenset(["GeneX", "GeneY"]): 100}

records_subset = [
    {"marker_symbol": "GeneX", "mp_term_id": "MP:1", "zygosity": "hom", "life_stage": "E"},
    {"marker_symbol": "GeneY", "mp_term_id": "MP:1", "zygosity": "hom", "life_stage": "E"},
    {"marker_symbol": "GeneY", "mp_term_id": "MP:2", "zygosity": "het", "life_stage": "A"},
]
expected_num_shared_subset = {frozenset(["GeneX", "GeneY"]): 1}
expected_jaccard_subset = {frozenset(["GeneX", "GeneY"]): 50}  # 1/2

records_duplicates = [
    {"marker_symbol": "GeneA", "mp_term_id": "MP:1", "zygosity": "hom", "life_stage": "E"},
    {"marker_symbol": "GeneA", "mp_term_id": "MP:1", "zygosity": "hom", "life_stage": "E"},  # Duplicate
    {"marker_symbol": "GeneB", "mp_term_id": "MP:1", "zygosity": "hom", "life_stage": "E"},
]
expected_num_shared_duplicates = {frozenset(["GeneA", "GeneB"]): 1}
expected_jaccard_duplicates = {frozenset(["GeneA", "GeneB"]): 100}


@pytest.mark.parametrize(
    "records_significants, expected_output",
    [
        (records_basic, expected_num_shared_basic),
        (records_no_overlap, expected_num_shared_no_overlap),
        (records_full_overlap, expected_num_shared_full_overlap),
        (records_subset, expected_num_shared_subset),
        (records_duplicates, expected_num_shared_duplicates),
        ([], {}),
        ([{"marker_symbol": "GeneA", "mp_term_id": "MP:1", "zygosity": "hom", "life_stage": "E"}], {}),
    ],
    ids=[
        "basic_case",
        "no_overlap",
        "full_overlap",
        "subset",
        "with_duplicates",
        "empty_input",
        "single_gene",
    ],
)
def test_calculate_num_shared_phenotypes(records_significants, expected_output):
    result = calculate_num_shared_phenotypes(records_significants)
    assert result == expected_output


@pytest.mark.parametrize(
    "records_significants, expected_output",
    [
        (records_basic, expected_jaccard_basic),
        (records_no_overlap, expected_jaccard_no_overlap),
        (records_full_overlap, expected_jaccard_full_overlap),
        (records_subset, expected_jaccard_subset),
        (records_duplicates, expected_jaccard_duplicates),
        ([], {}),
        ([{"marker_symbol": "GeneA", "mp_term_id": "MP:1", "zygosity": "hom", "life_stage": "E"}], {}),
    ],
    ids=[
        "basic_case",
        "no_overlap",
        "full_overlap",
        "subset",
        "with_duplicates",
        "empty_input",
        "single_gene",
    ],
)
def test_calculate_jaccard_indices(records_significants, expected_output):
    result = calculate_jaccard_indices(records_significants)
    assert result == expected_output
