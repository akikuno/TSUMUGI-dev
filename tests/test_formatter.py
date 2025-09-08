import math

import pytest

from TSUMUGI.formatter import abs_effect_size, floatinize_columns, get_distinct_records_with_max_effect, to_float


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


@pytest.mark.parametrize(
    "records, unique_keys, expected",
    [
        # Test Case 1: 基本的な動作。'gene'でグループ化し、各グループで最大のeffect_sizeを持つレコードが選ばれる。
        (
            [
                {"gene": "A", "effect_size": 1.0},
                {"gene": "A", "effect_size": 5.0},  # group Aの最大
                {"gene": "B", "effect_size": 2.0},  # group Bの最大 (唯一)
            ],
            ["gene"],
            [
                {"gene": "A", "effect_size": 5.0},
                {"gene": "B", "effect_size": 2.0},
            ],
        ),
        # Test Case 2: 複数のキーでグループ化する。
        (
            [
                {"gene": "A", "phenotype": "P1", "effect_size": 10.0},  # group (A, P1) の最大
                {"gene": "A", "phenotype": "P1", "effect_size": 2.0},
                {"gene": "A", "phenotype": "P2", "effect_size": 5.0},  # group (A, P2) の最大
            ],
            ["gene", "phenotype"],
            [
                {"gene": "A", "phenotype": "P1", "effect_size": 10.0},
                {"gene": "A", "phenotype": "P2", "effect_size": 5.0},
            ],
        ),
        # Test Case 3: effect_sizeキーが存在しないレコードが含まれる場合。デフォルト値(-1)と比較される。
        (
            [
                {"gene": "C", "effect_size": 3.0},  # group Cの最大
                {"gene": "C"},  # effect_sizeがない -> -1として扱われる
                {"gene": "D", "effect_size": 0.0},  # group Dの最大
                {"gene": "D"},
            ],
            ["gene"],
            [
                {"gene": "C", "effect_size": 3.0},
                {"gene": "D", "effect_size": 0.0},
            ],
        ),
        # Test Case 4: エッジケース - 入力リストが空の場合。
        (
            [],
            ["gene"],
            [],
        ),
        # Test Case 5: エッジケース - 全てのレコードがユニークな場合。
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
        # Test Case 6: effect_sizeがすべて同じ値の場合、先に出てくる（ソート後）レコードが選ばれる。
        (
            [
                {"gene": "G", "id": 1, "effect_size": 5.0},
                {"gene": "G", "id": 2, "effect_size": 5.0},
            ],
            ["gene"],
            # max()は安定なので、同値の場合は最初の要素を返す
            [{"gene": "G", "id": 1, "effect_size": 5.0}],
        ),
    ],
)
def test_get_distinct_records_with_max_effect(records, unique_keys, expected):
    """
    get_distinct_records_with_max_effect関数が、様々な入力に対して
    正しく動作することを検証します。
    """
    assert get_distinct_records_with_max_effect(records, unique_keys) == expected
