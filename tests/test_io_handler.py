import pytest

from TSUMUGI.io_handler import (
    parse_obo_file,
)

# Define test cases.
# Each tuple contains (OBO file contents, expected output dictionary).
TEST_CASES = [
    # 1. Basic case: two well-formed Term entries.
    (
        """
[Term]
id: MP:0000001
name: mammalian phenotype
is_a: OBO:SUPER_TERM ! a comment here

[Term]
id: MP:0000002
name: another term
is_a: MP:0000001
        """,
        {
            "MP:0000001": {"id": "MP:0000001", "name": "mammalian phenotype", "is_a": ["OBO:SUPER_TERM"]},
            "MP:0000002": {"id": "MP:0000002", "name": "another term", "is_a": ["MP:0000001"]},
        },
    ),
    # 2. A term with multiple is_a entries and a root term without is_a.
    (
        """
[Term]
id: ROOT:01
name: Root Term

[Term]
id: CHILD:01
name: Child Term
is_a: ROOT:01
is_a: ANOTHER:PARENT
        """,
        {
            "ROOT:01": {"id": "ROOT:01", "name": "Root Term"},
            "CHILD:01": {"id": "CHILD:01", "name": "Child Term", "is_a": ["ROOT:01", "ANOTHER:PARENT"]},
        },
    ),
    # 3. Terms with is_obsolete: true are ignored.
    (
        """
[Term]
id: VALID:01
name: Valid Term

[Term]
id: OBSOLETE:01
name: Obsolete Term
is_obsolete: true
        """,
        {
            "VALID:01": {"id": "VALID:01", "name": "Valid Term"},
        },
    ),
    # 4. Sections other than [Term] are ignored.
    (
        """
format-version: 1.2

[Typedef]
id: part_of
name: part of

[Term]
id: T:003
name: A Real Term
        """,
        {
            "T:003": {"id": "T:003", "name": "A Real Term"},
        },
    ),
    # 5. Empty file.
    ("", {}),
    # 6. File without any [Term] section.
    ("format-version: 1.2\ndata-version: 2025", {}),
]


@pytest.mark.parametrize("obo_content, expected_output", TEST_CASES)
def test_parse_obo_file(tmp_path, obo_content, expected_output):
    """
    Parameterized test for parse_obo_file.
    - Write the OBO content to a temporary file.
    - Call the function with both Path objects and str paths.
    - Assert that the results match expectations.
    """
    # Create a temporary file.
    p = tmp_path / "test.obo"
    p.write_text(obo_content, encoding="utf-8")

    # Test with a Path object argument.
    result_from_path = parse_obo_file(p)
    assert result_from_path == expected_output

    # Test with a string path argument.
    result_from_str = parse_obo_file(str(p))
    assert result_from_str == expected_output
