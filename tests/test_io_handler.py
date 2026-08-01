import gzip
import hashlib
import json
import math

import pytest

from TSUMUGI.io_handler import (
    parse_obo_file,
    read_jsonl,
    write_jsonl,
    write_jsonl_to_stdout,
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


def test_write_jsonl_accepts_gzip_compresslevel(tmp_path):
    output_path = tmp_path / "records.jsonl.gz"
    records = [{"id": "A"}, {"id": "B"}]

    write_jsonl(records, output_path, compresslevel=1)

    with gzip.open(output_path, "rt", encoding="utf-8") as f:
        assert [json.loads(line) for line in f] == records


def test_write_jsonl_deterministic_gzip_has_stable_sha256(tmp_path):
    first = tmp_path / "first.jsonl.gz"
    second = tmp_path / "second.jsonl.gz"
    records = [{"id": "A"}, {"id": "B"}]

    write_jsonl(records, first, compresslevel=1, deterministic=True)
    write_jsonl(records, second, compresslevel=1, deterministic=True)

    assert hashlib.sha256(first.read_bytes()).hexdigest() == hashlib.sha256(second.read_bytes()).hexdigest()


def test_write_jsonl_deterministic_gzip_replaces_output_atomically(tmp_path):
    output_path = tmp_path / "records.jsonl.gz"
    write_jsonl([{"id": "old"}], output_path, deterministic=True)
    old_digest = hashlib.sha256(output_path.read_bytes()).hexdigest()

    def interrupted_records():
        yield {"id": "new"}
        raise RuntimeError("interrupted")

    with pytest.raises(RuntimeError, match="interrupted"):
        write_jsonl(interrupted_records(), output_path, deterministic=True)

    assert hashlib.sha256(output_path.read_bytes()).hexdigest() == old_digest
    assert not (tmp_path / "records.jsonl.gz.partial").exists()


def _reject_nonstandard_constant(value):
    raise ValueError(f"Nonstandard JSON constant: {value}")


def test_write_jsonl_serializes_missing_effect_size_as_null(tmp_path):
    output_path = tmp_path / "records.jsonl.gz"
    record = {"effect_size": float("nan")}

    write_jsonl([record], output_path, compresslevel=1)

    with gzip.open(output_path, "rt", encoding="utf-8") as f:
        raw_line = f.read()

    loaded_standard_json = json.loads(
        raw_line,
        parse_constant=_reject_nonstandard_constant,
    )
    loaded_tsumugi = list(read_jsonl(output_path))

    assert '"effect_size": null' in raw_line
    assert loaded_standard_json["effect_size"] is None
    assert math.isnan(loaded_tsumugi[0]["effect_size"])
    assert math.isnan(record["effect_size"])


@pytest.mark.parametrize("effect_size", [0.0, 1.25, -2.5])
def test_write_jsonl_preserves_finite_effect_size(tmp_path, effect_size):
    output_path = tmp_path / "records.jsonl"

    write_jsonl([{"effect_size": effect_size}], output_path)

    loaded = json.loads(
        output_path.read_text(encoding="utf-8"),
        parse_constant=_reject_nonstandard_constant,
    )
    assert loaded["effect_size"] == effect_size


def test_write_jsonl_to_stdout_serializes_missing_effect_size_as_null(capsys):
    record = {"effect_size": float("nan")}

    write_jsonl_to_stdout(record)

    raw_line = capsys.readouterr().out
    loaded = json.loads(raw_line, parse_constant=_reject_nonstandard_constant)
    assert loaded["effect_size"] is None
    assert math.isnan(record["effect_size"])


def test_write_jsonl_rejects_nonfinite_values_outside_effect_size(tmp_path):
    output_path = tmp_path / "records.jsonl"

    with pytest.raises(ValueError, match="Out of range float values"):
        write_jsonl(
            [{"effect_size": 1.0, "phenotype_similarity_score": float("nan")}],
            output_path,
        )

    assert output_path.read_text(encoding="utf-8") == ""


def test_read_jsonl_accepts_legacy_nan_effect_size(tmp_path):
    output_path = tmp_path / "legacy.jsonl"
    output_path.write_text('{"effect_size": NaN}\n', encoding="utf-8")

    loaded = list(read_jsonl(output_path))

    assert math.isnan(loaded[0]["effect_size"])
