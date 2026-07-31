import math

import pytest

from TSUMUGI.genewise_annotation_builder import build_genewise_phenotype_annotations


def _base_statistical_result():
    return {
        "p_value": "0.001",
        "female_ko_effect_p_value": "1",
        "female_ko_parameter_estimate": "",
        "male_ko_effect_p_value": "1",
        "male_ko_parameter_estimate": "",
        "marker_symbol": "GeneA",
        "marker_accession_id": "MGI:1",
        "mp_term_id": "MP:0005553",
        "mp_term_name": "increased circulating creatinine level",
        "zygosity": "homozygote",
        "procedure_name": "Clinical Chemistry",
        "pipeline_name": "IMPC Pipeline",
        "significant": True,
        "intermediate_mp_term_id": "MP:9999999",
        "intermediate_mp_term_name": "intermediate phenotype",
    }


def _build_annotation(effect_size_marker, include_effect_size=True):
    record = _base_statistical_result()
    if include_effect_size:
        record["effect_size"] = effect_size_marker

    ontology_terms = {"MP:0005553": {"id": "MP:0005553", "name": "increased circulating creatinine level"}}
    annotations = list(build_genewise_phenotype_annotations(iter([record]), ontology_terms, {}))
    assert len(annotations) == 1
    return annotations[0]


@pytest.mark.parametrize(
    "effect_size_marker, include_effect_size",
    [
        (None, False),
        (None, True),
        ("", True),
    ],
)
def test_build_genewise_phenotype_annotations_keeps_missing_effect_size_as_nan(
    effect_size_marker,
    include_effect_size,
):
    annotation = _build_annotation(effect_size_marker, include_effect_size=include_effect_size)

    assert annotation["significant"] is True
    assert math.isnan(annotation["effect_size"])


@pytest.mark.parametrize(
    "effect_size_marker, expected",
    [
        (43.5261880802177, 43.5261880802177),
        ("43.5261880802177", 43.5261880802177),
        (0.0, 0.0),
        ("0", 0.0),
    ],
)
def test_build_genewise_phenotype_annotations_preserves_numeric_effect_size(
    effect_size_marker,
    expected,
):
    annotation = _build_annotation(effect_size_marker, include_effect_size=True)

    assert annotation["effect_size"] == expected


def test_build_genewise_phenotype_annotations_keeps_non_significant_measurement():
    record = _base_statistical_result()
    record["mp_term_id"] = ""
    record["mp_term_name"] = ""
    record["intermediate_mp_term_id"] = "MP:0005553"
    record["intermediate_mp_term_name"] = "mismatched source name"
    ontology_terms = {"MP:0005553": {"id": "MP:0005553", "name": "increased circulating creatinine level"}}

    annotations = list(build_genewise_phenotype_annotations(iter([record]), ontology_terms, {}))

    assert len(annotations) == 1
    assert annotations[0]["mp_term_id"] == "MP:0005553"
    assert annotations[0]["mp_term_name"] == "increased circulating creatinine level"
    assert annotations[0]["significant"] is False
    assert annotations[0]["disease_annotation"] == []


def test_build_genewise_phenotype_annotations_prefers_significant_duplicate():
    significant_record = _base_statistical_result()
    significant_record["effect_size"] = ""

    non_significant_record = _base_statistical_result()
    non_significant_record["mp_term_id"] = ""
    non_significant_record["mp_term_name"] = ""
    non_significant_record["intermediate_mp_term_id"] = "MP:0005553"

    ontology_terms = {"MP:0005553": {"id": "MP:0005553", "name": "increased circulating creatinine level"}}
    annotations = list(
        build_genewise_phenotype_annotations(
            iter([significant_record, non_significant_record]),
            ontology_terms,
            {},
        )
    )

    assert len(annotations) == 1
    assert annotations[0]["significant"] is True
    assert math.isnan(annotations[0]["effect_size"])
