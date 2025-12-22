import math

from TSUMUGI.formatter import _to_float, abs_effect_size, floatinize_columns


def test_to_float():
    assert _to_float("3.14") == 3.14
    assert math.isnan(_to_float(""))
    assert math.isnan(_to_float(None))


def test_floatinize_columns():
    record = {
        "p_value": "0.001",
        "female_ko_effect_p_value": "0.002",
        "male_ko_effect_p_value": "0.003",
        "effect_size": "0.4",
    }
    columns = ["p_value", "female_ko_effect_p_value", "male_ko_effect_p_value", "effect_size"]
    result = list(floatinize_columns([record], columns))[0]
    assert result["p_value"] == 0.001
    assert result["female_ko_effect_p_value"] == 0.002
    assert result["male_ko_effect_p_value"] == 0.003
    assert result["effect_size"] == 0.4


def test_abs_effect_size():
    record_plus = {"effect_size": 1}
    record_minus = {"effect_size": -1}
    columns = ["effect_size"]
    assert list(abs_effect_size([record_plus], columns))[0] == {"effect_size": 1}
    assert list(abs_effect_size([record_minus], columns))[0] == {"effect_size": 1}
