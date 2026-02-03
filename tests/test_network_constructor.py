import copy

from TSUMUGI import network_constructor


def test_convert_to_nodes_json():
    connected_node_ids = {"1700010I14Rik", "1700093K21Rik"}
    mp_term_name = "hyperactivity"
    disease_annotations_composed = {
        "Arhgap31": {
            "Adams-Oliver Syndrome (Hetero, Embryo)",
        }
    }

    gene_records_map = {
        "1700010I14Rik": [
            {
                "mp_term_name": "hyperactivity",
                "effect_size": 1,
                "mp_term_name_with_metadata": "hyperactivity (Homo, Early, Female)",
            },
            {
                "mp_term_name": "abnormal behavior",
                "effect_size": 1.30925887361181,
                "mp_term_name_with_metadata": "abnormal behavior (Homo, Early)",
            },
            {
                "mp_term_name": "decreased thigmotaxis",
                "effect_size": 1.30954000587253,
                "mp_term_name_with_metadata": "decreased thigmotaxis (Homo, Early)",
            },
        ],
        "1700093K21Rik": [
            {
                "mp_term_name": "hyperactivity",
                "effect_size": 100,
                "mp_term_name_with_metadata": "hyperactivity (Homo, Early, Female)",
            },
            {
                "mp_term_name": "increased circulating phosphate level",
                "effect_size": 2.5505238817119,
                "mp_term_name_with_metadata": "increased circulating phosphate level (Homo, Early, Female)",
            },
        ],
    }

    nodes_json = network_constructor._convert_to_nodes_json(
        connected_node_ids,
        mp_term_name,
        gene_records_map,
        disease_annotations_composed,
        hide_severity=False,
    )
    expected = [
        {
            "data": {
                "disease": "",
                "id": "1700010I14Rik",
                "label": "1700010I14Rik",
                "node_color": 1,
                "phenotype": [
                    "abnormal behavior (Homo, Early)",
                    "decreased thigmotaxis (Homo, Early)",
                    "hyperactivity (Homo, Early, Female)",
                ],
            }
        },
        {
            "data": {
                "disease": "",
                "id": "1700093K21Rik",
                "label": "1700093K21Rik",
                "node_color": 100,
                "phenotype": [
                    "hyperactivity (Homo, Early, Female)",
                    "increased circulating phosphate level (Homo, Early, Female)",
                ],
            }
        },
    ]
    expected.sort(key=lambda x: x["data"]["id"])

    assert nodes_json == expected


def test_compose_genewise_phenotype_significants():
    genewise_phenotype_significants = [
        {
            "mp_term_id": "MP:0003036",
            "effect_size": 56.6660680199426,
            "life_stage": "Early",
            "mp_term_name": "vertebral transformation",
            "marker_accession_id": "MGI:1913452",
            "disease_annotation": [],
            "significant": True,
            "sexual_dimorphism": "None",
            "zygosity": "Homo",
            "marker_symbol": "1110059G10Rik",
        },
        {
            "mp_term_id": "MP:0000063",
            "effect_size": 0.00559025173502752,
            "life_stage": "Early",
            "mp_term_name": "decreased bone mineral density",
            "marker_accession_id": "MGI:1917034",
            "disease_annotation": [],
            "significant": True,
            "sexual_dimorphism": "Male",
            "zygosity": "Homo",
            "marker_symbol": "1500009L16Rik",
        },
    ]
    results = network_constructor._compose_genewise_phenotype_significants(genewise_phenotype_significants)
    expected = {
        "1110059G10Rik": [
            {
                "effect_size": 56.6660680199426,
                "mp_term_name": "vertebral transformation",
                "mp_term_name_with_metadata": "vertebral transformation (Homo, Early)",
            }
        ],
        "1500009L16Rik": [
            {
                "effect_size": 0.00559025173502752,
                "mp_term_name": "decreased bone mineral density",
                "mp_term_name_with_metadata": "decreased bone mineral density (Homo, Early, Male)",
            }
        ],
    }

    assert results == expected


def test_scale_phenotype_similarity_scores_does_not_mutate_input():
    input_data = {
        ("GeneA", "GeneB"): {
            "phenotype_shared_annotations": [
                {"mp_term_name": "P1", "zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "None"}
            ],
            "phenotype_similarity_score": 10,
        },
        ("GeneC", "GeneD"): {
            "phenotype_shared_annotations": [
                {"mp_term_name": "P2", "zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "None"},
                {"mp_term_name": "P3", "zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "None"},
            ],
            "phenotype_similarity_score": 30,
        },
    }
    original = copy.deepcopy(input_data)

    scaled = network_constructor._scale_phenotype_similarity_scores(input_data)

    assert input_data == original
    assert scaled is not input_data
    assert scaled[("GeneA", "GeneB")] is not input_data[("GeneA", "GeneB")]
    assert scaled[("GeneA", "GeneB")]["phenotype_similarity_score"] == 1
    assert scaled[("GeneC", "GeneD")]["phenotype_similarity_score"] == 100


def test_scale_phenotype_similarity_scores_all_same_value():
    input_data = {
        ("GeneA", "GeneB"): {
            "phenotype_shared_annotations": [
                {"mp_term_name": "P1", "zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "None"}
            ],
            "phenotype_similarity_score": 42,
        },
        ("GeneC", "GeneD"): {
            "phenotype_shared_annotations": [
                {"mp_term_name": "P2", "zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "None"}
            ],
            "phenotype_similarity_score": 42,
        },
    }

    scaled = network_constructor._scale_phenotype_similarity_scores(input_data)

    assert scaled[("GeneA", "GeneB")]["phenotype_similarity_score"] == 100
    assert scaled[("GeneC", "GeneD")]["phenotype_similarity_score"] == 100


def test_scale_phenotype_similarity_scores_target_gene_only():
    input_data = {
        ("GeneA", "GeneB"): {
            "phenotype_shared_annotations": [
                {"mp_term_name": "P1", "zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "None"}
            ],
            "phenotype_similarity_score": 30,
        },
        ("GeneA", "GeneC"): {
            "phenotype_shared_annotations": [
                {"mp_term_name": "P2", "zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "None"}
            ],
            "phenotype_similarity_score": 40,
        },
        ("GeneB", "GeneC"): {
            "phenotype_shared_annotations": [
                {"mp_term_name": "P3", "zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "None"}
            ],
            "phenotype_similarity_score": 10,
        },
    }

    scaled = network_constructor._scale_phenotype_similarity_scores(input_data, target_gene="GeneA")

    assert scaled[("GeneA", "GeneB")]["phenotype_similarity_score"] == 1
    assert scaled[("GeneA", "GeneC")]["phenotype_similarity_score"] == 100
