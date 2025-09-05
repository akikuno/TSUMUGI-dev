import math

from TSUMUGI.formatter import abs_effect_size, distinct_records, floatinize_columns, to_float


def test_to_float():
    assert to_float("3.14") == 3.14
    assert math.isnan(to_float(""))
    assert math.isnan(to_float(None))


def test_floatinize_columns():
    record = {
        "p_value": "0.001",
        "female_ko_effect_p_value": "0.002",
        "male_ko_effect_p_value": "0.003",
        "effect_size": "0.4",
    }
    columns = ["p_value", "female_ko_effect_p_value", "male_ko_effect_p_value", "effect_size"]
    result = floatinize_columns(record, columns)
    assert result["p_value"] == 0.001
    assert result["female_ko_effect_p_value"] == 0.002
    assert result["male_ko_effect_p_value"] == 0.003
    assert result["effect_size"] == 0.4


def test_abs_effect_size():
    record_plus = {"effect_size": 1}
    record_minus = {"effect_size": -1}
    assert abs_effect_size(record_plus) == {"effect_size": 1}
    assert abs_effect_size(record_minus) == {"effect_size": 1}


def test_distinct_records():
    records = [
        {"marker_symbol": "Ap1ar", "mp_term_name": "term1", "effect_size": 0.5},
        {"marker_symbol": "Ap1ar", "mp_term_name": "term1", "effect_size": 0.6},
        {"marker_symbol": "Ap1ar", "mp_term_name": "term2", "effect_size": -1},
        {"marker_symbol": "Ap1ar", "mp_term_name": "term2", "effect_size": -10},
    ]
    result = distinct_records(records)
    assert len(result) == 2
    for record in result:
        if record["mp_term_name"] == "term1":
            assert record["effect_size"] == 0.6
        elif record["mp_term_name"] == "term2":
            assert record["effect_size"] == -10
