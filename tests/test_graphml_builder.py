import pytest
import networkx as nx
from TSUMUGI.subcommands import graphml_builder as gb


###############################################################################
# format_suffix
###############################################################################


@pytest.mark.parametrize(
    "zygosity, life_stage, sexual_dimorphism, expected",
    [
        ("Homo", "Early", "Male", "(Homo, Early, Male)"),
        ("Homo", "Early", "Female", "(Homo, Early, Female)"),
        ("Homo", "Early", "None", "(Homo, Early)"),
        ("Hetero", "Late", "None", "(Hetero, Late)"),
        ("Hemi", "Embryo", "Male", "(Hemi, Embryo, Male)"),
    ],
)
def test_format_suffix(zygosity, life_stage, sexual_dimorphism, expected):
    assert gb.format_suffix(zygosity, life_stage, sexual_dimorphism) == expected


###############################################################################
# build_nodes
###############################################################################


@pytest.mark.parametrize(
    "records, expected",
    [
        (
            # --- テストケース1：phenotype + disease ---
            [
                {
                    "mp_term_name": "decreased bone mineral density",
                    "sexual_dimorphism": "Female",
                    "significant": True,
                    "effect_size": 0.5,
                    "mp_term_id": "MP:0000063",
                    "zygosity": "Homo",
                    "marker_accession_id": "MGI:1923051",
                    "marker_symbol": "4930447C04Rik",
                    "life_stage": "Early",
                    "disease_annotation": [
                        "Male Infertility",
                        "Premature Ovarian Failure 18",
                    ],
                }
            ],
            {
                "4930447C04Rik": {
                    "label": "4930447C04Rik",
                    "effect_size": 1.0,
                    "node_annotations": (
                        "Phenotypes of 4930447C04Rik KO mice\n"
                        "- decreased bone mineral density (Homo, Early, Female)\n"
                        "Associated Human Diseases\n"
                        "- Male Infertility (Homo, Early, Female)\n"
                        "- Premature Ovarian Failure 18 (Homo, Early, Female)"
                    ),
                }
            },
        ),
        (
            # --- テストケース2：sexual_dimorphism=None（省略） ---
            [
                {
                    "mp_term_name": "fused joints",
                    "sexual_dimorphism": "None",
                    "significant": False,
                    "effect_size": 0.0,
                    "mp_term_id": "MP:0000137",
                    "zygosity": "Homo",
                    "marker_accession_id": "MGI:1913452",
                    "marker_symbol": "GeneX",
                    "life_stage": "Early",
                    "disease_annotation": [],
                }
            ],
            {
                "GeneX": {
                    "label": "GeneX",
                    "effect_size": 1.0,
                    "node_annotations": ("Phenotypes of GeneX KO mice\n- fused joints (Homo, Early)"),
                }
            },
        ),
    ],
)
def test_build_nodes(records, expected):
    result = gb.build_nodes(records)
    assert result == expected


###############################################################################
# build_graph
###############################################################################


@pytest.mark.parametrize(
    "pairwise_records, initial_nodes, expected_new_nodes, expected_edges",
    [
        (
            # Case 1: 両方既存ノード
            [
                {
                    "gene1_symbol": "GeneA",
                    "gene2_symbol": "GeneB",
                    "phenotype_similarity_score": 42,
                    "phenotype_shared_annotations": {
                        "vertebral transformation": {
                            "sexual_dimorphism": "Male",
                            "zygosity": "Homo",
                            "life_stage": "Early",
                        }
                    },
                }
            ],
            {
                "GeneA": {"label": "GeneA", "effect_size": 1.0, "node_annotations": "A1"},
                "GeneB": {"label": "GeneB", "effect_size": 1.0, "node_annotations": "B1"},
            },
            {},
            {
                ("GeneA", "GeneB"): {
                    "id": "e0",
                    "weight": 42,
                    "edge_annotations": (
                        "Shared phenotypes of GeneA and GeneB KOs (Similarity: 42)\n"
                        "- vertebral transformation (Homo, Early, Male)"
                    ),
                }
            },
        ),
        (
            # Case 2: GeneC が新規作成
            [
                {
                    "gene1_symbol": "GeneA",
                    "gene2_symbol": "GeneC",
                    "phenotype_similarity_score": 10,
                    "phenotype_shared_annotations": {
                        "some phenotype": {
                            "sexual_dimorphism": "None",
                            "zygosity": "Hetero",
                            "life_stage": "Late",
                        }
                    },
                }
            ],
            {
                "GeneA": {"label": "GeneA", "effect_size": 1.0, "node_annotations": "A1"},
            },
            {
                "GeneC": {
                    "label": "GeneC",
                    "effect_size": 1.0,
                    "node_annotations": "",
                }
            },
            {
                ("GeneA", "GeneC"): {
                    "id": "e0",
                    "weight": 10,
                    "edge_annotations": (
                        "Shared phenotypes of GeneA and GeneC KOs (Similarity: 10)\n- some phenotype (Hetero, Late)"
                    ),
                }
            },
        ),
    ],
)
def test_build_graph(pairwise_records, initial_nodes, expected_new_nodes, expected_edges):
    G = gb.build_graph(pairwise_records, initial_nodes)

    # initial_nodes が保持される
    for node_id, attrs in initial_nodes.items():
        assert node_id in G.nodes
        for k, v in attrs.items():
            assert G.nodes[node_id][k] == v

    # 新規ノード
    for node_id, attrs in expected_new_nodes.items():
        assert node_id in G.nodes
        for k, v in attrs.items():
            assert G.nodes[node_id][k] == v

    # エッジ
    def find_edge(a, b):
        if G.has_edge(a, b):
            return (a, b)
        if G.has_edge(b, a):
            return (b, a)
        return None

    for (u, v), exp in expected_edges.items():
        edge = find_edge(u, v)
        assert edge is not None
        uu, vv = edge
        data = G[uu][vv]
        assert data["id"] == exp["id"]
        assert data["weight"] == exp["weight"]
        assert data["edge_annotations"] == exp["edge_annotations"]
