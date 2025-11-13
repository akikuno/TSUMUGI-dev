from copy import deepcopy

import pytest
from TSUMUGI.subcommands.zygosity_filterer import _filter_annotations_by_zygosity


@pytest.fixture
def base_input():
    return [
        {
            "gene1_symbol": "GeneA",
            "gene2_symbol": "GeneB",
            "phenotype_shared_annotations": {
                "abnormal embryo size": {
                    "life_stage": "Embryo",
                    "zygosity": "Homo",
                    "sexual_dimorphism": "None",
                },
                "preweaning lethality": {
                    "life_stage": "Early",
                    "zygosity": "Hetero",
                    "sexual_dimorphism": "Male",
                },
                "decreased survival": {
                    "life_stage": "Late",
                    "zygosity": "Hemi",
                    "sexual_dimorphism": "Female",
                },
            },
            "phenotype_similarity_score": 70,
        }
    ]


def build_expected_list(kept_terms):
    """単一レコード入力を前提とした期待出力（yield される dict）のリストを構築。"""
    if not kept_terms:
        return []
    all_terms = {
        "abnormal embryo size": {
            "life_stage": "Embryo",
            "zygosity": "Homo",
            "sexual_dimorphism": "None",
        },
        "preweaning lethality": {
            "life_stage": "Early",
            "zygosity": "Hetero",
            "sexual_dimorphism": "Male",
        },
        "decreased survival": {
            "life_stage": "Late",
            "zygosity": "Hemi",
            "sexual_dimorphism": "Female",
        },
    }
    kept = {k: all_terms[k] for k in kept_terms}
    return [
        {
            "gene1_symbol": "GeneA",
            "gene2_symbol": "GeneB",
            "phenotype_shared_annotations": kept,
            "phenotype_similarity_score": 70,
        }
    ]


@pytest.mark.parametrize(
    "zygosity,keep,drop,kept_terms",
    [
        # --- keep-only ---
        ("Homo", True, False, {"abnormal embryo size"}),
        ("Hetero", True, False, {"preweaning lethality"}),
        ("Hemi", True, False, {"decreased survival"}),
        # --- drop-only（指定以外を保持）---
        ("Homo", False, True, {"preweaning lethality", "decreased survival"}),
        ("Hetero", False, True, {"abnormal embryo size", "decreased survival"}),
        ("Hemi", False, True, {"abnormal embryo size", "preweaning lethality"}),
        # --- both flags on → 等しい（keep）＋ 等しくない（drop） ⇒ 全て保持 ---
        ("Homo", True, True, {"abnormal embryo size", "preweaning lethality", "decreased survival"}),
        ("Hetero", True, True, {"abnormal embryo size", "preweaning lethality", "decreased survival"}),
        ("Hemi", True, True, {"abnormal embryo size", "preweaning lethality", "decreased survival"}),
        # --- neither → 何も出力しない ---
        ("Homo", False, False, set()),
        ("Hetero", False, False, set()),
        ("Hemi", False, False, set()),
    ],
)
def test_filter_annotations_by_zygosity_generator(base_input, zygosity, keep, drop, kept_terms):
    data = deepcopy(base_input)

    out_list = list(
        _filter_annotations_by_zygosity(
            pairwise_similarity_annotations=data,
            zygosity=zygosity,
            keep=keep,
            drop=drop,
        )
    )

    expected = build_expected_list(kept_terms)
    assert out_list == expected


def test_empty_annotations_row_yields_nothing():
    data = [
        {
            "gene1_symbol": "GeneX",
            "gene2_symbol": "GeneY",
            "phenotype_shared_annotations": {},
            "phenotype_similarity_score": 42,
        }
    ]

    out_list = list(
        _filter_annotations_by_zygosity(
            pairwise_similarity_annotations=data,
            zygosity="Homo",
            keep=True,
            drop=False,
        )
    )
    assert out_list == []
