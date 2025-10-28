import math

import numpy as np
import pytest
from TSUMUGI.ontology_handler import build_term_hierarchy
from TSUMUGI.similarity_calculator import (
    _apply_phenodigm_scaling,
    _calculate_information_content,
    _calculate_resnik_similarity,
    calculate_jaccard_indices,
    calculate_num_shared_phenotypes,
)


@pytest.fixture
def sample_ontology():
    """
    Fixture that supplies sample ontology data for testing.
    Hierarchy:
          A (root)
         / \\
        B   C
       / \\ /
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
    "term_id, num_descendants",
    [
        ("A", 5),  # B, C, D, E, F
        ("B", 3),  # D, E, F
        ("C", 2),  # E, F
        ("F", 0),  # Leaf node
    ],
)
def test_calculate_information_content(sample_ontology, term_id, num_descendants):
    total = sample_ontology["total_term_count"]
    # Number of descendants plus the term itself (1)
    term_count = num_descendants + 1
    expected_ic = -math.log(term_count / total)

    result = _calculate_information_content(term_id, sample_ontology["child_map"], total)
    assert result == pytest.approx(expected_ic)


@pytest.mark.parametrize(
    "term1, term2, mica_id",
    [
        ("D", "E", "B"),  # MICA is B
        ("D", "F", "B"),  # MICA is B
        ("B", "C", "A"),  # MICA is A
        ("F", "F", "F"),  # Same term
    ],
)
def test_calculate_resnik_similarity(sample_ontology, term1, term2, mica_id):
    # This dictionary is correct for the main function call below
    maps = {
        "parent_term_map": sample_ontology["parent_map"],
        "child_term_map": sample_ontology["child_map"],
        "total_term_count": sample_ontology["total_term_count"],
    }

    # FIX: Call _calculate_information_content with only the specific arguments it needs,
    # instead of unpacking the entire 'maps' dictionary.
    expected_similarity = _calculate_information_content(
        mica_id, sample_ontology["child_map"], sample_ontology["total_term_count"]
    )

    # This call was already correct as it uses all the arguments in 'maps'
    result = _calculate_resnik_similarity(term1, term2, **maps)
    assert result == pytest.approx(expected_similarity)


def test_apply_phenodigm_scaling_identical_phenotypes():
    """
    Test Case 1: When the phenotype sets match exactly, the score should reach 100 💯
    """
    # --- Data preparation ---
    gene1_mp_term_ids = {"MP:A", "MP:B"}
    gene2_mp_term_ids = {"MP:A", "MP:B"}

    term_pair_similarity_map = {
        frozenset(["MP:A"]): {"MP:A": 2.0},
        frozenset(["MP:B"]): {"MP:B": 4.0},
        frozenset(["MP:A", "MP:B"]): {"MP:A": 1.0},
    }

    weighted_similarity_matrix = np.array([[2.0, 1.0], [1.0, 4.0]])

    # --- Test execution ---
    result = _apply_phenodigm_scaling(
        weighted_similarity_matrix, gene1_mp_term_ids, gene2_mp_term_ids, term_pair_similarity_map
    )

    # --- Verification ---
    # The score should be 100
    assert result == 100


def test_apply_phenodigm_scaling_disjoint_phenotypes():
    """
    Test Case 2: Completely disjoint phenotype sets should produce a score of 0 🅾️
    """
    # --- Data preparation ---
    gene1_mp_term_ids = {"MP:A", "MP:B"}
    gene2_mp_term_ids = {"MP:C", "MP:D"}

    term_pair_similarity_map = {
        frozenset(["MP:A"]): {"MP:A": 2.0},
        frozenset(["MP:B"]): {"MP:B": 4.0},
        frozenset(["MP:C"]): {"MP:C": 3.0},
        frozenset(["MP:D"]): {"MP:D": 5.0},
    }

    weighted_similarity_matrix = np.array([[0.0, 0.0], [0.0, 0.0]])

    # --- Test execution ---
    result = _apply_phenodigm_scaling(
        weighted_similarity_matrix, gene1_mp_term_ids, gene2_mp_term_ids, term_pair_similarity_map
    )

    # --- Verification ---
    # The score should be 0
    assert result == 0


def test_apply_phenodigm_scaling_average_score_50():
    """
    Test Case 3: Observed similarity is exactly half of the theoretical maximum, yielding 50 🌗
    """
    # --- Data preparation ---
    gene1_mp_term_ids = {"MP:A"}
    gene2_mp_term_ids = {"MP:B"}

    term_pair_similarity_map = {
        frozenset(["MP:A"]): {"MP:A": 4.0},  # IC(A)
        frozenset(["MP:B"]): {"MP:B": 4.0},  # IC(B)
        # sim(A,B) is specified directly in weighted_similarity_matrix
    }

    weighted_similarity_matrix = np.array([[2.0]])

    # --- Test execution ---
    result = _apply_phenodigm_scaling(
        weighted_similarity_matrix, gene1_mp_term_ids, gene2_mp_term_ids, term_pair_similarity_map
    )

    # --- Verification ---
    # Each normalized score should be 0.5, so the final score becomes 50.
    # phenodigm_score = 100 * ( (2/4) + (2/4) ) / 2 = 50.0
    assert result == 50


# ----------------------------------------------------------------------------
# Test Data Setup
# ----------------------------------------------------------------------------

# Case 1: Basic scenario with partial overlap
records_basic = [
    {"marker_symbol": "GeneA", "mp_term_id": "MP:1", "zygosity": "hom", "life_stage": "E"},  # P1 for GeneA
    {"marker_symbol": "GeneA", "mp_term_id": "MP:2", "zygosity": "het", "life_stage": "A"},  # P2 for GeneA
    {"marker_symbol": "GeneB", "mp_term_id": "MP:2", "zygosity": "het", "life_stage": "A"},  # P2 for GeneB
    {"marker_symbol": "GeneB", "mp_term_id": "MP:3", "zygosity": "hom", "life_stage": "A"},  # P3 for GeneB
    {"marker_symbol": "GeneC", "mp_term_id": "MP:3", "zygosity": "hom", "life_stage": "A"},  # P3 for GeneC
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

# Case 2: Genes with no overlapping phenotypes
records_no_overlap = [
    {"marker_symbol": "GeneX", "mp_term_id": "MP:1", "zygosity": "hom", "life_stage": "E"},
    {"marker_symbol": "GeneY", "mp_term_id": "MP:2", "zygosity": "het", "life_stage": "A"},
]
expected_num_shared_no_overlap = {frozenset(["GeneX", "GeneY"]): 0}
expected_jaccard_no_overlap = {frozenset(["GeneX", "GeneY"]): 0}

# Case 3: Genes with identical phenotype sets
records_full_overlap = [
    {"marker_symbol": "GeneX", "mp_term_id": "MP:1", "zygosity": "hom", "life_stage": "E"},
    {"marker_symbol": "GeneX", "mp_term_id": "MP:2", "zygosity": "het", "life_stage": "A"},
    {"marker_symbol": "GeneY", "mp_term_id": "MP:1", "zygosity": "hom", "life_stage": "E"},
    {"marker_symbol": "GeneY", "mp_term_id": "MP:2", "zygosity": "het", "life_stage": "A"},
]
expected_num_shared_full_overlap = {frozenset(["GeneX", "GeneY"]): 2}
expected_jaccard_full_overlap = {frozenset(["GeneX", "GeneY"]): 100}

# Case 4: One gene's phenotypes are a subset of another's
records_subset = [
    {"marker_symbol": "GeneX", "mp_term_id": "MP:1", "zygosity": "hom", "life_stage": "E"},
    {"marker_symbol": "GeneY", "mp_term_id": "MP:1", "zygosity": "hom", "life_stage": "E"},
    {"marker_symbol": "GeneY", "mp_term_id": "MP:2", "zygosity": "het", "life_stage": "A"},
]
expected_num_shared_subset = {frozenset(["GeneX", "GeneY"]): 1}
expected_jaccard_subset = {frozenset(["GeneX", "GeneY"]): 50}  # 1/2

# Case 5: Input with duplicate records, which should be ignored
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
        ([], {}),  # Empty input
        ([{"marker_symbol": "GeneA", "mp_term_id": "MP:1", "zygosity": "hom", "life_stage": "E"}], {}),  # Single gene
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
    """
    Tests the calculation of the number of shared phenotypes for various scenarios.
    """
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
        ([], {}),  # Empty input
        ([{"marker_symbol": "GeneA", "mp_term_id": "MP:1", "zygosity": "hom", "life_stage": "E"}], {}),  # Single gene
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
    """
    Tests the calculation of Jaccard indices for various scenarios.
    """
    result = calculate_jaccard_indices(records_significants)
    assert result == expected_output
