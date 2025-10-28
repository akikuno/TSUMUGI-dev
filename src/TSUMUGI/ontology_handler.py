from __future__ import annotations

from collections import defaultdict


def build_term_hierarchy(
    ontology_terms: dict[str, dict],
) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Build parent-child hierarchy relationships from ontology terms."""
    parent_term_map = defaultdict(set)  # term_id -> [parent_ids]
    child_term_map = defaultdict(set)  # term_id -> [child_ids]

    for term_id, term_data in ontology_terms.items():
        if "is_a" in term_data:
            for parent_id in term_data["is_a"]:
                parent_term_map[term_id].add(parent_id)
                child_term_map[parent_id].add(term_id)

    return dict(parent_term_map), dict(child_term_map)


def find_all_ancestor_terms(term_id: str, parent_term_map: dict[str, set[str]]) -> set[str]:
    """Find all ancestor terms for a given term."""
    ancestor_terms = set()
    terms_to_process = [term_id]

    while terms_to_process:
        current_term = terms_to_process.pop(0)
        if current_term in parent_term_map:
            for parent_term in parent_term_map[current_term]:
                if parent_term not in ancestor_terms:
                    ancestor_terms.add(parent_term)
                    terms_to_process.append(parent_term)

    return ancestor_terms


def find_all_descendant_terms(term_id: str, child_term_map: dict[str, set[str]]) -> set[str]:
    """Find all descendant terms for a given term."""
    descendant_terms = set()
    terms_to_process = [term_id]

    while terms_to_process:
        current_term = terms_to_process.pop(0)
        if current_term in child_term_map:
            for child_term in child_term_map[current_term]:
                if child_term not in descendant_terms:
                    descendant_terms.add(child_term)
                    terms_to_process.append(child_term)

    return descendant_terms


def find_common_ancestors(term1_id: str, term2_id: str, parent_term_map: dict[str, set[str]]) -> set[str]:
    """Find common ancestors of two terms."""
    term1_ancestors = find_all_ancestor_terms(term1_id, parent_term_map)
    term1_ancestors.add(term1_id)  # Include the term itself

    term2_ancestors = find_all_ancestor_terms(term2_id, parent_term_map)
    term2_ancestors.add(term2_id)  # Include the term itself

    return term1_ancestors.intersection(term2_ancestors)
