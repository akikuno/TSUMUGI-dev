import copy
import gzip
import json
import math

from TSUMUGI import network_constructor


def _phenotype_annotation(
    mp_term_name,
    zygosity="Homo",
    life_stage="Early",
    sexual_dimorphism="Female",
):
    return {
        "mp_term_name": mp_term_name,
        "zygosity": zygosity,
        "life_stage": life_stage,
        "sexual_dimorphism": sexual_dimorphism,
    }


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


def test_convert_to_nodes_json_uses_min_color_for_nan_effect_size():
    connected_node_ids = {"GeneA", "GeneB"}
    mp_term_name = "increased circulating creatinine level"
    gene_records_map = {
        "GeneA": [
            {
                "mp_term_name": mp_term_name,
                "effect_size": float("nan"),
                "mp_term_name_with_metadata": f"{mp_term_name} (Homo, Early)",
            }
        ],
        "GeneB": [
            {
                "mp_term_name": mp_term_name,
                "effect_size": 43.5261880802177,
                "mp_term_name_with_metadata": f"{mp_term_name} (Homo, Early)",
            }
        ],
    }

    nodes_json = network_constructor._convert_to_nodes_json(connected_node_ids, mp_term_name, gene_records_map, {})
    node_colors = {node["data"]["id"]: node["data"]["node_color"] for node in nodes_json}

    assert node_colors["GeneA"] == 1
    assert node_colors["GeneB"] == 100
    assert all(math.isfinite(color) for color in node_colors.values())


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


def test_convert_to_edges_json_requires_target_metadata_match():
    related_genes = {"GeneA", "GeneB", "GeneC", "GeneD"}
    required_shared_annotations = {"target phenotype (Homo, Early, Female)"}
    pairwise_similarity_annotations = {
        ("GeneA", "GeneB"): {
            "phenotype_shared_annotations": [
                "similar phenotype (Homo, Early)",
                "target phenotype (Homo, Early, Female)",
            ],
            "phenotype_similarity_score": 10,
        },
        ("GeneA", "GeneC"): {
            "phenotype_shared_annotations": [
                "similar phenotype (Homo, Early)",
                "target phenotype (Homo, Early, Male)",
            ],
            "phenotype_similarity_score": 100,
        },
        ("GeneA", "GeneD"): {
            "phenotype_shared_annotations": [
                "similar phenotype (Homo, Early)",
            ],
            "phenotype_similarity_score": 100,
        },
    }

    edges_json = network_constructor._convert_to_edges_json(
        related_genes,
        pairwise_similarity_annotations,
        required_shared_annotations=required_shared_annotations,
    )

    assert len(edges_json) == 1
    assert edges_json[0]["data"]["source"] == "GeneA"
    assert edges_json[0]["data"]["target"] == "GeneB"
    assert edges_json[0]["data"]["edge_size"] == 100
    assert edges_json[0]["data"]["phenotype"] == [
        "similar phenotype (Homo, Early)",
        "target phenotype (Homo, Early, Female)",
    ]


def test_convert_to_edges_json_allows_any_target_metadata_variant():
    related_genes = {"GeneA", "GeneB", "GeneC", "GeneD"}
    required_shared_annotations = {
        "target phenotype (Homo, Early, Female)",
        "target phenotype (Hetero, Late)",
    }
    pairwise_similarity_annotations = {
        ("GeneA", "GeneB"): {
            "phenotype_shared_annotations": ["target phenotype (Homo, Early, Female)"],
            "phenotype_similarity_score": 10,
        },
        ("GeneC", "GeneD"): {
            "phenotype_shared_annotations": ["target phenotype (Hetero, Late)"],
            "phenotype_similarity_score": 20,
        },
        ("GeneA", "GeneC"): {
            "phenotype_shared_annotations": ["target phenotype (Homo, Early, Male)"],
            "phenotype_similarity_score": 100,
        },
    }

    edges_json = network_constructor._convert_to_edges_json(
        related_genes,
        pairwise_similarity_annotations,
        required_shared_annotations=required_shared_annotations,
    )

    assert [(edge["data"]["source"], edge["data"]["target"]) for edge in edges_json] == [
        ("GeneA", "GeneB"),
        ("GeneC", "GeneD"),
    ]


def test_find_optimal_scores_ignores_non_target_metadata_pairs():
    related_genes = {"GeneA", "GeneB", "GeneC", "GeneD"}
    required_shared_annotations = {"target phenotype (Homo, Early, Female)"}
    pairwise_similarity_annotations = {
        ("GeneA", "GeneB"): {
            "phenotype_shared_annotations": ["target phenotype (Homo, Early, Female)"],
            "phenotype_similarity_score": 10,
        },
        ("GeneC", "GeneD"): {
            "phenotype_shared_annotations": ["target phenotype (Homo, Early, Male)"],
            "phenotype_similarity_score": 100,
        },
    }

    optimal_score = network_constructor._find_optimal_scores(
        [10, 100],
        related_genes,
        pairwise_similarity_annotations,
        required_shared_annotations=required_shared_annotations,
        low_threshold=2,
        high_threshold=2,
    )

    assert optimal_score == 10


def test_filter_related_genes_ranks_only_target_metadata_matching_pairs(monkeypatch):
    monkeypatch.setattr(network_constructor, "MAX_GENE_COUNT", 2)
    records = [
        {"marker_symbol": "GeneA", "effect_size": 1.0},
        {"marker_symbol": "GeneB", "effect_size": 2.0},
        {"marker_symbol": "GeneC", "effect_size": 100.0},
        {"marker_symbol": "GeneD", "effect_size": 200.0},
    ]
    related_genes = {"GeneA", "GeneB", "GeneC", "GeneD"}
    required_shared_annotations = {"target phenotype (Homo, Early, Female)"}
    pairwise_similarity_annotations = {
        ("GeneA", "GeneB"): {
            "phenotype_shared_annotations": ["target phenotype (Homo, Early, Female)"],
            "phenotype_similarity_score": 10,
        },
        ("GeneC", "GeneD"): {
            "phenotype_shared_annotations": ["target phenotype (Homo, Early, Male)"],
            "phenotype_similarity_score": 100,
        },
    }

    filtered_genes = network_constructor._filter_related_genes(
        records,
        related_genes,
        pairwise_similarity_annotations,
        required_shared_annotations=required_shared_annotations,
    )

    assert filtered_genes == {"GeneA", "GeneB"}


def test_build_phenotype_network_json_requires_target_metadata_match(tmp_path):
    genewise_phenotype_significants = [
        {
            "mp_term_name": "target phenotype",
            "marker_symbol": "GeneA",
            "zygosity": "Homo",
            "life_stage": "Early",
            "sexual_dimorphism": "Female",
            "effect_size": 1.0,
        },
        {
            "mp_term_name": "target phenotype",
            "marker_symbol": "GeneB",
            "zygosity": "Homo",
            "life_stage": "Early",
            "sexual_dimorphism": "Female",
            "effect_size": 2.0,
        },
        {
            "mp_term_name": "target phenotype",
            "marker_symbol": "GeneC",
            "zygosity": "Homo",
            "life_stage": "Early",
            "sexual_dimorphism": "Female",
            "effect_size": 3.0,
        },
        {
            "mp_term_name": "target phenotype",
            "marker_symbol": "GeneD",
            "zygosity": "Homo",
            "life_stage": "Early",
            "sexual_dimorphism": "Female",
            "effect_size": 4.0,
        },
    ]
    pairwise_similarity_annotations = [
        {
            "gene1_symbol": "GeneA",
            "gene2_symbol": "GeneB",
            "phenotype_shared_annotations": [
                _phenotype_annotation("target phenotype", sexual_dimorphism="Female"),
                _phenotype_annotation("similar phenotype", sexual_dimorphism="None"),
            ],
            "phenotype_similarity_score": 10,
        },
        {
            "gene1_symbol": "GeneA",
            "gene2_symbol": "GeneC",
            "phenotype_shared_annotations": [
                _phenotype_annotation("target phenotype", sexual_dimorphism="Male"),
                _phenotype_annotation("similar phenotype", sexual_dimorphism="None"),
            ],
            "phenotype_similarity_score": 100,
        },
        {
            "gene1_symbol": "GeneA",
            "gene2_symbol": "GeneD",
            "phenotype_shared_annotations": [
                _phenotype_annotation("similar phenotype", sexual_dimorphism="None"),
            ],
            "phenotype_similarity_score": 100,
        },
    ]

    network_constructor.build_phenotype_network_json(
        genewise_phenotype_significants,
        pairwise_similarity_annotations,
        {},
        tmp_path,
    )

    output_file = tmp_path / "target_phenotype.json.gz"
    assert output_file.exists()

    with gzip.open(output_file, "rt", encoding="utf-8") as f:
        network_json = json.load(f)

    edge_items = [item for item in network_json if "source" in item["data"]]
    node_items = [item for item in network_json if "source" not in item["data"]]

    assert [(edge["data"]["source"], edge["data"]["target"]) for edge in edge_items] == [("GeneA", "GeneB")]
    assert {node["data"]["id"] for node in node_items} == {"GeneA", "GeneB"}


def test_build_phenotype_network_json_writes_empty_json_when_no_target_metadata_match(tmp_path):
    genewise_phenotype_significants = [
        {
            "mp_term_name": "target phenotype",
            "marker_symbol": "GeneA",
            "zygosity": "Homo",
            "life_stage": "Early",
            "sexual_dimorphism": "Female",
            "effect_size": 1.0,
        },
        {
            "mp_term_name": "target phenotype",
            "marker_symbol": "GeneB",
            "zygosity": "Homo",
            "life_stage": "Early",
            "sexual_dimorphism": "Female",
            "effect_size": 2.0,
        },
    ]
    pairwise_similarity_annotations = [
        {
            "gene1_symbol": "GeneA",
            "gene2_symbol": "GeneB",
            "phenotype_shared_annotations": [
                _phenotype_annotation("target phenotype", sexual_dimorphism="Male"),
                _phenotype_annotation("similar phenotype", sexual_dimorphism="None"),
            ],
            "phenotype_similarity_score": 100,
        }
    ]

    network_constructor.build_phenotype_network_json(
        genewise_phenotype_significants,
        pairwise_similarity_annotations,
        {},
        tmp_path,
    )

    output_file = tmp_path / "target_phenotype.json.gz"
    assert output_file.exists()

    with gzip.open(output_file, "rt", encoding="utf-8") as f:
        network_json = json.load(f)

    assert network_json == []
