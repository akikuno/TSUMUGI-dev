from copy import deepcopy

import pytest
from TSUMUGI.subcommands.zygosity_filterer import _filter_annotations_by_zygosity


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
                    "zygosity": "Homo",
                    "sexual_dimorphism": "None",
                },
                {
                    "mp_term_name": "preweaning lethality",
                    "life_stage": "Early",
                    "zygosity": "Hetero",
                    "sexual_dimorphism": "Male",
                },
                {
                    "mp_term_name": "decreased survival",
                    "life_stage": "Late",
                    "zygosity": "Hemi",
                    "sexual_dimorphism": "Female",
                },
            ],
            "phenotype_similarity_score": 70,
        }
    ]


def build_expected_list(kept_terms):
    """Build the expected (yielded dict) list assuming a single-record input."""
    if not kept_terms:
        return []
    all_terms = [
        {
            "mp_term_name": "abnormal embryo size",
            "life_stage": "Embryo",
            "zygosity": "Homo",
            "sexual_dimorphism": "None",
        },
        {
            "mp_term_name": "preweaning lethality",
            "life_stage": "Early",
            "zygosity": "Hetero",
            "sexual_dimorphism": "Male",
        },
        {
            "mp_term_name": "decreased survival",
            "life_stage": "Late",
            "zygosity": "Hemi",
            "sexual_dimorphism": "Female",
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
    "zygosity,keep,drop,kept_terms",
    [
        # --- keep-only ---
        ("Homo", True, False, {"abnormal embryo size"}),
        ("Hetero", True, False, {"preweaning lethality"}),
        ("Hemi", True, False, {"decreased survival"}),
        # --- drop-only (keep entries other than specified) ---
        ("Homo", False, True, {"preweaning lethality", "decreased survival"}),
        ("Hetero", False, True, {"abnormal embryo size", "decreased survival"}),
        ("Hemi", False, True, {"abnormal embryo size", "preweaning lethality"}),
        # --- both flags on → keep matching + drop non-matching ⇒ keep everything ---
        ("Homo", True, True, {"abnormal embryo size", "preweaning lethality", "decreased survival"}),
        ("Hetero", True, True, {"abnormal embryo size", "preweaning lethality", "decreased survival"}),
        ("Hemi", True, True, {"abnormal embryo size", "preweaning lethality", "decreased survival"}),
        # --- neither flag on → produce no output ---
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
            "phenotype_shared_annotations": [],
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


def test_invalid_structure_raises_typeerror():
    data = [
        {
            "gene1_symbol": "GeneX",
            "gene2_symbol": "GeneY",
            "phenotype_shared_annotations": {
                "abnormal embryo size": {
                    "life_stage": "Embryo",
                    "zygosity": "Homo",
                    "sexual_dimorphism": "None",
                }
            },
            "phenotype_similarity_score": 42,
        }
    ]

    with pytest.raises(TypeError):
        list(
            _filter_annotations_by_zygosity(
                pairwise_similarity_annotations=data,
                zygosity="Homo",
                keep=True,
                drop=False,
            )
        )
