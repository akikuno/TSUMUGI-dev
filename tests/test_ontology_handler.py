import pytest
from TSUMUGI.ontology_handler import (
    build_term_hierarchy,
    find_all_ancestor_terms,
    find_all_descendant_terms,
    find_common_ancestors,
)


@pytest.fixture
def sample_ontology():
    """
    Fixture that provides sample ontology data for testing.
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


def test_build_term_hierarchy(sample_ontology):
    expected_parent_map = {
        "B": {"A"},
        "C": {"A"},
        "D": {"B"},
        "E": {"B", "C"},
        "F": {"E"},
    }
    expected_child_map = {
        "A": {"B", "C"},
        "B": {"D", "E"},
        "C": {"E"},
        "E": {"F"},
    }
    assert sample_ontology["parent_map"] == expected_parent_map
    assert sample_ontology["child_map"] == expected_child_map


@pytest.mark.parametrize(
    "term_id, expected_ancestors",
    [
        ("F", {"E", "B", "C", "A"}),
        ("D", {"B", "A"}),
        ("B", {"A"}),
        ("A", set()),
        ("Z", set()),  # Non-existent ID
    ],
)
def test_find_all_ancestor_terms(sample_ontology, term_id, expected_ancestors):
    result = find_all_ancestor_terms(term_id, sample_ontology["parent_map"])
    assert result == expected_ancestors


@pytest.mark.parametrize(
    "term1, term2, expected_common",
    [
        ("D", "F", {"D", "B", "A", "F", "E", "C"}),  # Includes each term itself
        ("D", "E", {"D", "B", "A", "E", "C"}),
        ("B", "C", {"B", "C", "A"}),
        ("F", "F", {"F", "E", "B", "C", "A"}),  # Identical term comparison
        ("A", "F", {"A", "F", "E", "B", "C"}),
        ("D", "C", {"D", "B", "A", "C"}),
    ],
)
def test_find_common_ancestors(sample_ontology, term1, term2, expected_common):
    # By specification, each term is included in its own ancestor set, so expectations incorporate that.
    ancestors1 = find_all_ancestor_terms(term1, sample_ontology["parent_map"]) | {term1}
    ancestors2 = find_all_ancestor_terms(term2, sample_ontology["parent_map"]) | {term2}
    expected = ancestors1.intersection(ancestors2)

    result = find_common_ancestors(term1, term2, sample_ontology["parent_map"])
    assert result == expected


@pytest.mark.parametrize(
    "term_id, expected_descendants",
    [
        ("A", {"B", "C", "D", "E", "F"}),
        ("B", {"D", "E", "F"}),
        ("C", {"E", "F"}),
        ("F", set()),  # Leaf node
        ("Z", set()),  # Non-existent ID
    ],
)
def test_find_all_descendant_terms(sample_ontology, term_id, expected_descendants):
    result = find_all_descendant_terms(term_id, sample_ontology["child_map"])
    assert result == expected_descendants
