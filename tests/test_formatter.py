from TSUMUGI.formatter import floatinize_columns, to_float


def test_to_float():
    assert to_float("3.14") == 3.14
    assert to_float("") == float("inf")
    assert to_float(None) == float("inf")


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
