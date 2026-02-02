import gzip
import json

import pytest
from TSUMUGI.subcommands import webapp_builder


def test_create_annotation_string_omits_empty():
    assert webapp_builder._create_annotation_string("Homo", "Early", "Male") == "Homo, Early, Male"
    assert webapp_builder._create_annotation_string("Homo", "Early", "") == "Homo, Early"


def test_safe_filename_replaces_invalid_chars():
    assert webapp_builder._safe_filename("Gene List!") == "Gene_List_"
    assert webapp_builder._safe_filename("") == "gene_list"


def test_build_edges_formats_annotations():
    pairwise = [
        {
            "gene1_symbol": "GeneA",
            "gene2_symbol": "GeneB",
            "phenotype_similarity_score": 12,
            "phenotype_shared_annotations": [
                {
                    "mp_term_name": "abnormal movement",
                    "zygosity": "Homo",
                    "life_stage": "Early",
                    "sexual_dimorphism": "None",
                },
                {
                    "mp_term_name": "eye defect",
                    "zygosity": "Hetero",
                    "life_stage": "Late",
                    "sexual_dimorphism": "Male",
                },
            ],
        }
    ]

    edges = webapp_builder._build_edges(pairwise)

    assert len(edges) == 1
    data = edges[0]["data"]
    assert data["source"] == "GeneA"
    assert data["target"] == "GeneB"
    assert data["edge_size"] == 12
    assert set(data["phenotype"]) == {
        "abnormal movement (Homo, Early)",
        "eye defect (Hetero, Late, Male)",
    }


def test_build_nodes_includes_hide_severity():
    gene_to_records = {
        "GeneA": [
            {
                "mp_term_name": "abnormal movement",
                "zygosity": "Homo",
                "life_stage": "Early",
                "sexual_dimorphism": "None",
                "disease_annotation": ["DiseaseA"],
            },
            {
                "mp_term_name": "abnormal movement",
                "zygosity": "Homo",
                "life_stage": "Early",
                "sexual_dimorphism": "None",
                "disease_annotation": ["DiseaseA"],
            },
        ]
    }
    all_genes = {"GeneA", "GeneB"}

    nodes = webapp_builder.build_nodes(gene_to_records, all_genes, hide_severity=True)
    node_map = {node["data"]["id"]: node["data"] for node in nodes}

    assert node_map["GeneA"]["hide_severity"] is True
    assert set(node_map["GeneA"]["phenotype"]) == {"abnormal movement (Homo, Early)"}
    assert set(node_map["GeneA"]["disease"]) == {"DiseaseA (Homo, Early)"}
    assert node_map["GeneB"]["phenotype"] == []
    assert node_map["GeneB"]["disease"] == ""


def test_build_webapp_network_rejects_large_network(monkeypatch):
    pairwise = [
        {
            "gene1_symbol": "GeneA",
            "gene2_symbol": "GeneB",
            "phenotype_similarity_score": 12,
            "phenotype_shared_annotations": [],
        }
    ]
    genewise = [
        {
            "marker_symbol": "GeneA",
            "marker_accession_id": "MGI:1",
            "mp_term_name": "abnormal movement",
            "zygosity": "Homo",
            "life_stage": "Early",
            "sexual_dimorphism": "None",
            "disease_annotation": [],
        },
        {
            "marker_symbol": "GeneB",
            "marker_accession_id": "MGI:2",
            "mp_term_name": "eye defect",
            "zygosity": "Homo",
            "life_stage": "Late",
            "sexual_dimorphism": "None",
            "disease_annotation": [],
        },
    ]

    def fake_read_jsonl(path):
        if path == "pairwise-path":
            return pairwise
        return genewise

    monkeypatch.setattr(webapp_builder.io_handler, "read_jsonl", fake_read_jsonl)
    monkeypatch.setattr(webapp_builder, "MAX_NODE_COUNT", 1)

    with pytest.raises(ValueError, match="exceeds the maximum allowed"):
        webapp_builder.build_webapp_network("genewise-path", "pairwise-path")


def test_build_and_save_webapp_network_writes_outputs(tmp_path, monkeypatch):
    pairwise = [
        {
            "gene1_symbol": "GeneA",
            "gene2_symbol": "GeneB",
            "phenotype_similarity_score": 12,
            "phenotype_shared_annotations": [
                {
                    "mp_term_name": "abnormal movement",
                    "zygosity": "Homo",
                    "life_stage": "Early",
                    "sexual_dimorphism": "None",
                }
            ],
        }
    ]
    genewise = [
        {
            "marker_symbol": "GeneA",
            "marker_accession_id": "MGI:1",
            "mp_term_name": "abnormal movement",
            "zygosity": "Homo",
            "life_stage": "Early",
            "sexual_dimorphism": "None",
            "disease_annotation": ["DiseaseA"],
        },
        {
            "marker_symbol": "GeneB",
            "marker_accession_id": "",
            "mp_term_name": "eye defect",
            "zygosity": "Hetero",
            "life_stage": "Late",
            "sexual_dimorphism": "Male",
            "disease_annotation": [],
        },
        {
            "marker_symbol": "GeneB",
            "marker_accession_id": "MGI:2",
            "mp_term_name": "eye defect",
            "zygosity": "Hetero",
            "life_stage": "Late",
            "sexual_dimorphism": "Male",
            "disease_annotation": [],
        },
    ]

    def fake_read_jsonl(path):
        if path == "pairwise-path":
            return pairwise
        return genewise

    calls = []

    def fake_create_bundle(output_dir, data_filename, network_label):
        calls.append((output_dir, data_filename, network_label))

    monkeypatch.setattr(webapp_builder.io_handler, "read_jsonl", fake_read_jsonl)
    monkeypatch.setattr(webapp_builder, "_create_webapp_bundle", fake_create_bundle)

    webapp_builder.build_and_save_webapp_network("genewise-path", "pairwise-path", tmp_path)

    network_path = tmp_path / "network.json.gz"
    symbol_path = tmp_path / "marker_symbol_accession_id.json"

    assert network_path.exists()
    assert symbol_path.exists()
    assert calls == [(tmp_path, "network.json.gz", "Gene List")]

    with gzip.open(network_path, "rt", encoding="utf-8") as fh:
        elements = json.load(fh)

    node_data = [elem["data"] for elem in elements if "source" not in elem["data"]]
    edge_data = [elem["data"] for elem in elements if "source" in elem["data"]]

    assert {node["id"] for node in node_data} == {"GeneA", "GeneB"}
    assert all(node.get("hide_severity") is True for node in node_data)
    assert edge_data[0]["edge_size"] == 12

    with open(symbol_path, encoding="utf-8") as fh:
        symbol_map = json.load(fh)

    assert symbol_map == {"GeneA": "MGI:1", "GeneB": "MGI:2"}
