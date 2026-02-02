from copy import deepcopy

import pytest
from TSUMUGI.subcommands.sex_filterer import _filter_annotations_by_sex


@pytest.fixture
def base_input():
    return [
        {
            "gene1_symbol": "GeneA",
            "gene2_symbol": "GeneB",
            "phenotype_shared_annotations": [
                {
                    "mp_term_name": "abnormal embryo size",
                    "life_stage": "Embryo",
                    "sexual_dimorphism": "None",
                    "zygosity": "Homo",
                },
                {
                    "mp_term_name": "preweaning lethality",
                    "life_stage": "Early",
                    "sexual_dimorphism": "Male",
                    "zygosity": "Homo",
                },
                {
                    "mp_term_name": "decreased survival",
                    "life_stage": "Late",
                    "sexual_dimorphism": "Female",
                    "zygosity": "Homo",
                },
            ],
            "phenotype_similarity_score": 70,
        }
    ]


def build_expected_list(kept_terms):
    """Construct the expected output list assuming a single-record input."""
    if not kept_terms:
        return []
    all_terms = [
        {
            "mp_term_name": "abnormal embryo size",
            "life_stage": "Embryo",
            "sexual_dimorphism": "None",
            "zygosity": "Homo",
        },
        {
            "mp_term_name": "preweaning lethality",
            "life_stage": "Early",
            "sexual_dimorphism": "Male",
            "zygosity": "Homo",
        },
        {
            "mp_term_name": "decreased survival",
            "life_stage": "Late",
            "sexual_dimorphism": "Female",
            "zygosity": "Homo",
        },
    ]
    kept = [term for term in all_terms if term["mp_term_name"] in kept_terms]
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
        # --- neither flag on → produce no output ---
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
            "phenotype_shared_annotations": [],
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


def test_invalid_structure_raises_typeerror():
    data = [
        {
            "gene1_symbol": "GeneX",
            "gene2_symbol": "GeneY",
            "phenotype_shared_annotations": {
                "abnormal embryo size": {
                    "life_stage": "Embryo",
                    "sexual_dimorphism": "None",
                    "zygosity": "Homo",
                }
            },
            "phenotype_similarity_score": 42,
        }
    ]

    with pytest.raises(TypeError):
        list(
            _filter_annotations_by_sex(
                pairwise_similarity_annotations=data,
                sex="Male",
                keep=True,
                drop=False,
            )
        )
