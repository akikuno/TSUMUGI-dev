import re

from TSUMUGI.annotator import (
    _annotate_life_stage,
    _annotate_sexual_dimorphism,
    annotate_diseases,
    annotate_significant,
)


def test_annotate_life_stage():
    embryo_assays = {
        "E9.5",
        "E10.5",
        "E12.5",
        "Embryo LacZ",  # E12.5
        "E14.5",
        "E14.5-E15.5",
        "E18.5",
    }
    embryo_pattern = re.compile("|".join(map(re.escape, embryo_assays)))
    procedure_name = "Gross Morphology Embryo E9.5"
    pipeline_name = "TCP"
    assert _annotate_life_stage(procedure_name, pipeline_name, embryo_pattern) == "Embryo"

    procedure_name = "Calorimetry"
    pipeline_name = "KMPC interval pipeline"
    assert _annotate_life_stage(procedure_name, pipeline_name, embryo_pattern) == "Interval"

    pipeline_name = "KMPC late pipeline"
    assert _annotate_life_stage(procedure_name, pipeline_name, embryo_pattern) == "Late"

    pipeline_name = "IMPC Pipeline"
    assert _annotate_life_stage(procedure_name, pipeline_name, embryo_pattern) == "Early"


def test_annotate_sexual_dimorphism():
    female_ko_effect_p_values = [1e-5, 1, 1]
    male_ko_effect_p_values = [1, 1e-5, 1]
    expected_results = ["Female", "Male", "None"]
    for f_p, m_p, expected in zip(female_ko_effect_p_values, male_ko_effect_p_values, expected_results):
        assert _annotate_sexual_dimorphism(f_p, m_p) == expected


def test_annotate_significant_yields_significant_record_once():
    record = {
        "mp_term_id": "MP:0000003",
        "mp_term_name": "stale source name",
        "intermediate_mp_term_id": "MP:0000002,MP:0000001",
        "effect_size": 1.5,
        "p_value": 0.00001,
    }
    ontology_terms = {
        "MP:0000001": {"name": "mammalian phenotype"},
        "MP:0000002": {"name": "abnormal phenotype", "is_a": ["MP:0000001"]},
        "MP:0000003": {"name": "leaf phenotype", "is_a": ["MP:0000002"]},
    }

    result = list(annotate_significant([record], ontology_terms))

    assert result == [
        {
            "mp_term_id": "MP:0000003",
            "mp_term_name": "leaf phenotype",
            "intermediate_mp_term_id": "MP:0000002,MP:0000001",
            "effect_size": 1.5,
            "p_value": 0.00001,
            "significant": True,
        }
    ]


def test_annotate_significant_selects_most_specific_intermediate_term():
    record = {
        "mp_term_id": "",
        "mp_term_name": "",
        "intermediate_mp_term_id": "MP:0000002,MP:0000001,MP:0000003",
        "effect_size": 1.5,
        "p_value": 0.2,
    }
    ontology_terms = {
        "MP:0000001": {"name": "mammalian phenotype"},
        "MP:0000002": {"name": "abnormal phenotype", "is_a": ["MP:0000001"]},
        "MP:0000003": {"name": "specific phenotype", "is_a": ["MP:0000002"]},
    }

    result = list(annotate_significant([record], ontology_terms))

    assert result == [
        {
            "mp_term_id": "MP:0000003",
            "mp_term_name": "specific phenotype",
            "intermediate_mp_term_id": "MP:0000002,MP:0000001,MP:0000003",
            "effect_size": 0.0,
            "p_value": 1.0,
            "significant": False,
        }
    ]


def test_annotate_significant_expands_incomparable_intermediate_terms():
    record = {
        "mp_term_id": "",
        "mp_term_name": "",
        "intermediate_mp_term_id": "MP:0000004,MP:0000002,MP:0000003,MP:0000001",
        "effect_size": 1.5,
        "p_value": 0.2,
    }
    ontology_terms = {
        "MP:0000001": {"name": "mammalian phenotype"},
        "MP:0000002": {"name": "abnormal phenotype", "is_a": ["MP:0000001"]},
        "MP:0000003": {"name": "specific phenotype A", "is_a": ["MP:0000002"]},
        "MP:0000004": {"name": "specific phenotype B", "is_a": ["MP:0000002"]},
    }

    result = list(annotate_significant([record], ontology_terms))

    assert [item["mp_term_id"] for item in result] == ["MP:0000003", "MP:0000004"]
    assert [item["mp_term_name"] for item in result] == ["specific phenotype A", "specific phenotype B"]
    assert all(item["significant"] is False for item in result)


def test_annotate_significant_drops_unmapped_or_root_only_measurement():
    records = [
        {
            "mp_term_id": "",
            "intermediate_mp_term_id": "",
        },
        {
            "mp_term_id": "",
            "intermediate_mp_term_id": "MP:0000001",
        },
    ]
    ontology_terms = {
        "MP:0000001": {"name": "mammalian phenotype"},
    }

    assert list(annotate_significant(records, ontology_terms)) == []


def test_annotate_diseases_keeps_non_significant_record_without_disease():
    record = {
        "significant": False,
        "disease_annotation": ["Disease A"],
    }

    result = list(annotate_diseases([record], {}))

    assert result == [{"significant": False, "disease_annotation": []}]
