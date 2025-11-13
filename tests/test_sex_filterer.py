from copy import deepcopy

import pytest
from TSUMUGI.subcommands.sex_filterer import _filter_annotations_by_sex


@pytest.fixture
def base_input():
    return [
        {
            "gene1_symbol": "GeneA",
            "gene2_symbol": "GeneB",
            "phenotype_shared_annotations": {
                "abnormal embryo size": {
                    "life_stage": "Embryo",
                    "sexual_dimorphism": "None",
                    "zygosity": "Homo",
                },
                "preweaning lethality": {
                    "life_stage": "Early",
                    "sexual_dimorphism": "Male",
                    "zygosity": "Homo",
                },
                "decreased survival": {
                    "life_stage": "Late",
                    "sexual_dimorphism": "Female",
                    "zygosity": "Homo",
                },
            },
            "phenotype_similarity_score": 70,
        }
    ]


def build_expected_list(kept_terms):
    """単一レコード入力を前提とした期待出力リストを構築"""
    if not kept_terms:
        return []
    all_terms = {
        "abnormal embryo size": {
            "life_stage": "Embryo",
            "sexual_dimorphism": "None",
            "zygosity": "Homo",
        },
        "preweaning lethality": {
            "life_stage": "Early",
            "sexual_dimorphism": "Male",
            "zygosity": "Homo",
        },
        "decreased survival": {
            "life_stage": "Late",
            "sexual_dimorphism": "Female",
            "zygosity": "Homo",
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
    "sex,keep,drop,kept_terms",
    [
        # --- keep-only cases ---
        ("Male", True, False, {"preweaning lethality"}),
        ("Female", True, False, {"decreased survival"}),
        ("None", True, False, {"abnormal embryo size"}),
        # --- drop-only cases (keep everything NOT equal to sex) ---
        ("Male", False, True, {"abnormal embryo size", "decreased survival"}),
        ("Female", False, True, {"abnormal embryo size", "preweaning lethality"}),
        ("None", False, True, {"preweaning lethality", "decreased survival"}),
        # --- both flags on → equal (keep) + not-equal (drop) ⇒ 全て残る ---
        ("Male", True, True, {"abnormal embryo size", "preweaning lethality", "decreased survival"}),
        ("Female", True, True, {"abnormal embryo size", "preweaning lethality", "decreased survival"}),
        ("None", True, True, {"abnormal embryo size", "preweaning lethality", "decreased survival"}),
        # --- neither flag on → 何も出力しない ---
        ("Male", False, False, set()),
        ("Female", False, False, set()),
        ("None", False, False, set()),
    ],
)
def test_filter_annotations_by_sex_generator_outputs(base_input, sex, keep, drop, kept_terms):
    data = deepcopy(base_input)

    out_list = list(
        _filter_annotations_by_sex(
            pairwise_similarity_annotations=data,
            sex=sex,
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
        _filter_annotations_by_sex(
            pairwise_similarity_annotations=data,
            sex="Male",
            keep=True,
            drop=False,
        )
    )

    assert out_list == []
