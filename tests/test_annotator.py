import re

from TSUMUGI.annotator import annotate_life_stage, annotate_sexual_dimorphism


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
    assert annotate_life_stage(procedure_name, pipeline_name, embryo_pattern) == "embryo"

    procedure_name = "Calorimetry"
    pipeline_name = "KMPC interval pipeline"
    assert annotate_life_stage(procedure_name, pipeline_name, embryo_pattern) == "interval"

    pipeline_name = "KMPC late pipeline"
    assert annotate_life_stage(procedure_name, pipeline_name, embryo_pattern) == "late"

    pipeline_name = "IMPC Pipeline"
    assert annotate_life_stage(procedure_name, pipeline_name, embryo_pattern) == "early"


def test_annotate_sexual_dimorphism():
    female_ko_effect_p_values = [1e-5, 1, 1]
    male_ko_effect_p_values = [1, 1e-5, 1]
    expected_results = ["female", "male", ""]
    for f_p, m_p, expected in zip(female_ko_effect_p_values, male_ko_effect_p_values, expected_results):
        assert annotate_sexual_dimorphism(f_p, m_p) == expected
