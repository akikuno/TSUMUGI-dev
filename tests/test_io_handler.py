import pytest

from TSUMUGI.io_handler import (
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

