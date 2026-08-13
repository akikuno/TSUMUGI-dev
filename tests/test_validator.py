import csv

import pytest

from TSUMUGI.validator import validate_statistical_results

REQUIRED_STATISTICAL_RESULT_COLUMNS = {
    "marker_symbol",
    "marker_accession_id",
    "mp_term_name",
    "mp_term_id",
    "p_value",
    "effect_size",
    "female_ko_effect_p_value",
    "female_ko_parameter_estimate",
    "male_ko_effect_p_value",
    "male_ko_parameter_estimate",
    "zygosity",
    "pipeline_name",
    "procedure_name",
    "allele_symbol",
    "intermediate_mp_term_id",
}


def _write_csv(path, columns):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=sorted(columns))
        writer.writeheader()
        writer.writerow(dict.fromkeys(columns, "value"))


def test_validate_statistical_results_accepts_all_required_columns(tmp_path):
    path = tmp_path / "statistical-results-ALL.csv"
    _write_csv(path, REQUIRED_STATISTICAL_RESULT_COLUMNS)

    validate_statistical_results(path)


def test_validate_statistical_results_requires_strain_for_mgi_integration(tmp_path):
    path = tmp_path / "statistical-results-ALL.csv"
    _write_csv(path, REQUIRED_STATISTICAL_RESULT_COLUMNS)

    with pytest.raises(ValueError, match="strain_name"):
        validate_statistical_results(path, require_strain=True)


def test_validate_statistical_results_accepts_strain_for_mgi_integration(tmp_path):
    path = tmp_path / "statistical-results-ALL.csv"
    _write_csv(path, REQUIRED_STATISTICAL_RESULT_COLUMNS | {"strain_name"})

    validate_statistical_results(path, require_strain=True)


@pytest.mark.parametrize(
    "missing_column",
    [
        "female_ko_parameter_estimate",
        "male_ko_parameter_estimate",
        "intermediate_mp_term_id",
    ],
)
def test_validate_statistical_results_rejects_columns_used_by_pipeline(tmp_path, missing_column):
    path = tmp_path / "statistical-results-ALL.csv"
    columns = REQUIRED_STATISTICAL_RESULT_COLUMNS - {missing_column}
    _write_csv(path, columns)

    with pytest.raises(ValueError, match=missing_column):
        validate_statistical_results(path)
