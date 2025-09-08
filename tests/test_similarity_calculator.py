import math

import numpy as np
import pytest

from TSUMUGI.similarity_calculator import (
    apply_phenodigm_scaling,
    build_term_hierarchy,
    calculate_information_content,
    calculate_resnik_similarity,
    find_all_ancestor_terms,
    find_all_descendant_terms,
    find_common_ancestors,
    parse_obo_file,
)

# テストケースを定義
# (oboファイルの内容, 期待される出力の辞書)
TEST_CASES = [
    # 1. 基本的なケース: 2つの正常なTerm
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
    # 2. is_aが複数あるTermと、is_aがないルートTerm
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
    # 3. is_obsolete: trueを持つTermは無視される
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
    # 4. [Term]以外のセクションは無視される
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
    # 5. 空のファイル
    ("", {}),
    # 6. [Term]セクションがないファイル
    ("format-version: 1.2\ndata-version: 2025", {}),
]


@pytest.mark.parametrize("obo_content, expected_output", TEST_CASES)
def test_parse_obo_file(tmp_path, obo_content, expected_output):
    """
    parse_obo_file関数をパラメータ化してテストする。
    - 一時ファイルにOBOコンテントを書き込む
    - Pathオブジェクトとstrの両方のパスタイプで関数を呼び出す
    - 結果が期待通りであることを確認する
    """
    # 一時ファイルを作成
    p = tmp_path / "test.obo"
    p.write_text(obo_content, encoding="utf-8")

    # Pathオブジェクトを引数にしてテスト
    result_from_path = parse_obo_file(p)
    assert result_from_path == expected_output

    # 文字列のパスを引数にしてテスト
    result_from_str = parse_obo_file(str(p))
    assert result_from_str == expected_output


@pytest.fixture
def sample_ontology():
    """
    テスト用のサンプルオントロジーデータを提供するフィクスチャ。
    Hierarchy:
          A (root)
         / \\
        B   C
       / \\ /
      D   E
          |
          F
    """
    ontology_terms = {
        "A": {"id": "A", "name": "Root"},
        "B": {"id": "B", "name": "Term B", "is_a": ["A"]},
        "C": {"id": "C", "name": "Term C", "is_a": ["A"]},
        "D": {"id": "D", "name": "Term D", "is_a": ["B"]},
        "E": {"id": "E", "name": "Term E", "is_a": ["B", "C"]},
        "F": {"id": "F", "name": "Term F", "is_a": ["E"]},
    }
    parent_map, child_map = build_term_hierarchy(ontology_terms)
    return {
        "ontology_terms": ontology_terms,
        "parent_map": parent_map,
        "child_map": child_map,
        "total_term_count": len(ontology_terms),
    }


def test_build_term_hierarchy(sample_ontology):
    expected_parent_map = {
        "B": ["A"],
        "C": ["A"],
        "D": ["B"],
        "E": ["B", "C"],
        "F": ["E"],
    }
    expected_child_map = {
        "A": ["B", "C"],
        "B": ["D", "E"],
        "C": ["E"],
        "E": ["F"],
    }
    assert sample_ontology["parent_map"] == expected_parent_map
    assert sample_ontology["child_map"] == expected_child_map


@pytest.mark.parametrize(
    "term_id, expected_ancestors",
    [
        ("F", {"E", "B", "C", "A"}),
        ("D", {"B", "A"}),
        ("B", {"A"}),
        ("A", set()),
        ("Z", set()),  # 存在しないID
    ],
)
def test_find_all_ancestor_terms(sample_ontology, term_id, expected_ancestors):
    result = find_all_ancestor_terms(term_id, sample_ontology["parent_map"])
    assert result == expected_ancestors


@pytest.mark.parametrize(
    "term1, term2, expected_common",
    [
        ("D", "F", {"D", "B", "A", "F", "E", "C"}),  # 自分自身も含む
        ("D", "E", {"D", "B", "A", "E", "C"}),
        ("B", "C", {"B", "C", "A"}),
        ("F", "F", {"F", "E", "B", "C", "A"}),  # 自分自身
        ("A", "F", {"A", "F", "E", "B", "C"}),
        ("D", "C", {"D", "B", "A", "C"}),
    ],
)
def test_find_common_ancestors(sample_ontology, term1, term2, expected_common):
    # 関数の仕様上、自分自身も祖先集合に含まれるため、期待値もそれに合わせる
    ancestors1 = find_all_ancestor_terms(term1, sample_ontology["parent_map"]) | {term1}
    ancestors2 = find_all_ancestor_terms(term2, sample_ontology["parent_map"]) | {term2}
    expected = ancestors1.intersection(ancestors2)

    result = find_common_ancestors(term1, term2, sample_ontology["parent_map"])
    assert result == expected


@pytest.mark.parametrize(
    "term_id, expected_descendants",
    [
        ("A", {"B", "C", "D", "E", "F"}),
        ("B", {"D", "E", "F"}),
        ("C", {"E", "F"}),
        ("F", set()),  # リーフノード
        ("Z", set()),  # 存在しないID
    ],
)
def test_find_all_descendant_terms(sample_ontology, term_id, expected_descendants):
    result = find_all_descendant_terms(term_id, sample_ontology["child_map"])
    assert result == expected_descendants


@pytest.mark.parametrize(
    "term_id, num_descendants",
    [
        ("A", 5),  # B, C, D, E, F
        ("B", 3),  # D, E, F
        ("C", 2),  # E, F
        ("F", 0),  # Leaf node
    ],
)
def test_calculate_information_content(sample_ontology, term_id, num_descendants):
    total = sample_ontology["total_term_count"]
    # 子孫の数 + 自分自身(1)
    term_count = num_descendants + 1
    expected_ic = -math.log(term_count / total)

    result = calculate_information_content(term_id, sample_ontology["child_map"], total)
    assert result == pytest.approx(expected_ic)


@pytest.mark.parametrize(
    "term1, term2, mica_id",
    [
        ("D", "E", "B"),  # MICA is B
        ("D", "F", "B"),  # MICA is B
        ("B", "C", "A"),  # MICA is A
        ("F", "F", "F"),  # Same term
    ],
)
def test_calculate_resnik_similarity(sample_ontology, term1, term2, mica_id):
    # This dictionary is correct for the main function call below
    maps = {
        "parent_term_map": sample_ontology["parent_map"],
        "child_term_map": sample_ontology["child_map"],
        "total_term_count": sample_ontology["total_term_count"],
    }

    # FIX: Call calculate_information_content with only the specific arguments it needs,
    # instead of unpacking the entire 'maps' dictionary.
    expected_similarity = calculate_information_content(
        mica_id, sample_ontology["child_map"], sample_ontology["total_term_count"]
    )

    # This call was already correct as it uses all the arguments in 'maps'
    result = calculate_resnik_similarity(term1, term2, **maps)
    assert result == pytest.approx(expected_similarity)


def test_apply_phenodigm_scaling_identical_phenotypes():
    """
    Test Case 1: 完全に一致する表現型セットを持つ場合、スコアが100になることをテスト 💯
    """
    # --- データ準備 ---
    gene1_mp_term_ids = {"MP:A", "MP:B"}
    gene2_mp_term_ids = {"MP:A", "MP:B"}

    term_pair_similarity_map = {
        frozenset(["MP:A"]): 2.0,
        frozenset(["MP:B"]): 4.0,
        frozenset(["MP:A", "MP:B"]): 1.0,
    }

    weighted_similarity_matrix = np.array([[2.0, 1.0], [1.0, 4.0]])

    # --- テスト実行 ---
    result = apply_phenodigm_scaling(
        weighted_similarity_matrix, gene1_mp_term_ids, gene2_mp_term_ids, term_pair_similarity_map
    )

    # --- 検証 ---
    # スコアが100になるはず
    assert result == pytest.approx(100.0)


def test_apply_phenodigm_scaling_disjoint_phenotypes():
    """
    Test Case 2: 完全に無関係な表現型セットを持つ場合、スコアが0になることをテスト 🅾️
    """
    # --- データ準備 ---
    gene1_mp_term_ids = {"MP:A", "MP:B"}
    gene2_mp_term_ids = {"MP:C", "MP:D"}

    term_pair_similarity_map = {
        frozenset(["MP:A"]): 2.0,
        frozenset(["MP:B"]): 4.0,
        frozenset(["MP:C"]): 3.0,
        frozenset(["MP:D"]): 5.0,
    }

    weighted_similarity_matrix = np.array([[0.0, 0.0], [0.0, 0.0]])

    # --- テスト実行 ---
    result = apply_phenodigm_scaling(
        weighted_similarity_matrix, gene1_mp_term_ids, gene2_mp_term_ids, term_pair_similarity_map
    )

    # --- 検証 ---
    # スコアが0になるはず
    assert result == pytest.approx(0.0)


def test_apply_phenodigm_scaling_average_score_50():
    """
    Test Case 3: 実測値が理論値のちょうど半分で、スコアが50になるケースをテスト 🌗
    """
    # --- データ準備 ---
    gene1_mp_term_ids = {"MP:A"}
    gene2_mp_term_ids = {"MP:B"}

    term_pair_similarity_map = {
        frozenset(["MP:A"]): 4.0,  # IC(A)
        frozenset(["MP:B"]): 4.0,  # IC(B)
        # sim(A,B)は weighted_similarity_matrix で直接指定
    }

    weighted_similarity_matrix = np.array([[2.0]])

    # --- テスト実行 ---
    result = apply_phenodigm_scaling(
        weighted_similarity_matrix, gene1_mp_term_ids, gene2_mp_term_ids, term_pair_similarity_map
    )

    # --- 検証 ---
    # 正規化スコアがそれぞれ0.5になり、最終スコアは50になるはず
    # phenodigm_score = 100 * ( (2/4) + (2/4) ) / 2 = 50.0
    assert result == pytest.approx(50.0)
