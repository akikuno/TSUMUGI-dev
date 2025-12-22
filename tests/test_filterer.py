import pytest
from TSUMUGI.filterer import distinct_records_with_max_effect


@pytest.mark.parametrize(
    "records, unique_keys, expected",
    [
        # Test Case 1: Basic behavior—group by 'gene' and pick the record with the maximum effect_size per group.
        (
            [
                {"gene": "A", "effect_size": 1.0},
                {"gene": "A", "effect_size": 5.0},  # Max within group A
                {"gene": "B", "effect_size": 2.0},  # Max within group B (only entry)
            ],
            ["gene"],
            [
                {"gene": "A", "effect_size": 5.0},
                {"gene": "B", "effect_size": 2.0},
            ],
        ),
        # Test Case 2: Grouping by multiple keys.
        (
            [
                {"gene": "A", "phenotype": "P1", "effect_size": 10.0},  # Max within group (A, P1)
                {"gene": "A", "phenotype": "P1", "effect_size": 2.0},
                {"gene": "A", "phenotype": "P2", "effect_size": 5.0},  # Max within group (A, P2)
            ],
            ["gene", "phenotype"],
            [
                {"gene": "A", "phenotype": "P1", "effect_size": 10.0},
                {"gene": "A", "phenotype": "P2", "effect_size": 5.0},
            ],
        ),
        # Test Case 3: Records lacking effect_size fall back to the default value (-1).
        (
            [
                {"gene": "C", "effect_size": 3.0},  # Max within group C
                {"gene": "C"},  # Missing effect_size -> treated as -1
                {"gene": "D", "effect_size": 0.0},  # Max within group D
                {"gene": "D"},
            ],
            ["gene"],
            [
                {"gene": "C", "effect_size": 3.0},
                {"gene": "D", "effect_size": 0.0},
            ],
        ),
        # Test Case 4: Edge case—input list is empty.
        (
            [],
            ["gene"],
            [],
        ),
        # Test Case 5: Edge case—all records are already unique.
        (
            [
                {"gene": "E", "effect_size": 1.0},
                {"gene": "F", "effect_size": 2.0},
            ],
            ["gene"],
            [
                {"gene": "E", "effect_size": 1.0},
                {"gene": "F", "effect_size": 2.0},
            ],
        ),
        # Test Case 6: When all effect_size values match, the first record after sorting is kept.
        (
            [
                {"gene": "G", "id": 1, "effect_size": 5.0},
                {"gene": "G", "id": 2, "effect_size": 5.0},
            ],
            ["gene"],
            # max() is stable, so tied values return the first element
            [{"gene": "G", "id": 1, "effect_size": 5.0}],
        ),
    ],
)
def test_distinct_records_with_max_effect(records, unique_keys, expected):
    """
    Verify that distinct_records_with_max_effect behaves correctly across a range of inputs.
    """
    result = list(distinct_records_with_max_effect(records, unique_keys))
    assert result == expected
