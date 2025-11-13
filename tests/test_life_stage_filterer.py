from copy import deepcopy

import pytest
from TSUMUGI.subcommands.life_stage_filterer import _filter_annotations_by_life_stage


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
                    "sexual_dimorphism": "None",
                    "zygosity": "Homo",
                },
                "decreased survival": {
                    "life_stage": "Late",
                    "sexual_dimorphism": "None",
                    "zygosity": "Homo",
                },
                "abnormal gait": {
                    "life_stage": "Interval",
                    "sexual_dimorphism": "None",
                    "zygosity": "Homo",
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
        "abnormal embryo size": {"life_stage": "Embryo", "sexual_dimorphism": "None", "zygosity": "Homo"},
        "preweaning lethality": {"life_stage": "Early", "sexual_dimorphism": "None", "zygosity": "Homo"},
        "decreased survival": {"life_stage": "Late", "sexual_dimorphism": "None", "zygosity": "Homo"},
        "abnormal gait": {"life_stage": "Interval", "sexual_dimorphism": "None", "zygosity": "Homo"},
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
    "life_stage,keep,drop,kept_terms",
    [
        # keep matching Embryo
        ("Embryo", True, False, {"abnormal embryo size"}),
        # drop Early (keep others)
        ("Early", False, True, {"abnormal embryo size", "decreased survival", "abnormal gait"}),
        # both flags on → keep all (equal + not-equal)
        ("Late", True, True, {"abnormal embryo size", "preweaning lethality", "decreased survival", "abnormal gait"}),
        # keep Interval (single match)
        ("Interval", True, False, {"abnormal gait"}),
        # drop Interval (keep others)
        ("Interval", False, True, {"abnormal embryo size", "preweaning lethality", "decreased survival"}),
        # keep Late (single match)
        ("Late", True, False, {"decreased survival"}),
        # neither flag true → remove everything
        ("Early", False, False, set()),
    ],
)
def test_filter_annotations_by_life_stage_generator(base_input, life_stage, keep, drop, kept_terms):
    data = deepcopy(base_input)

    out_list = list(
        _filter_annotations_by_life_stage(
            pairwise_similarity_annotations=data,
            life_stage=life_stage,
            keep=keep,
            drop=drop,
        )
    )

    expected = build_expected_list(kept_terms)
    assert out_list == expected


def test_empty_annotations_skipped():
    data = [
        {
            "gene1_symbol": "GeneX",
            "gene2_symbol": "GeneY",
            "phenotype_shared_annotations": {},
            "phenotype_similarity_score": 42,
        }
    ]
    result = list(
        _filter_annotations_by_life_stage(
            pairwise_similarity_annotations=data,
            life_stage="Embryo",
            keep=True,
            drop=False,
        )
    )
    assert result == []
