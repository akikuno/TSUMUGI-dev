import csv
import gzip
import json

from TSUMUGI import gene_phenotype_module_builder


def _write_network(path, elements):
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(elements, f)


def test_build_gene_phenotype_module_json(tmp_path):
    ontology_terms = {
        "MP:0000001": {"id": "MP:0000001", "name": "mammalian phenotype"},
        "MP:0005390": {
            "id": "MP:0005390",
            "name": "skeleton phenotype",
            "is_a": ["MP:0000001"],
        },
        "MP:0005386": {
            "id": "MP:0005386",
            "name": "behavior/neurological phenotype",
            "is_a": ["MP:0000001"],
        },
        "MP:0000063": {
            "id": "MP:0000063",
            "name": "decreased bone mineral density",
            "is_a": ["MP:0005390"],
        },
        "MP:0001392": {
            "id": "MP:0001392",
            "name": "abnormal behavior",
            "is_a": ["MP:0005386"],
        },
    }
    pairwise_similarity_annotations = [
        {
            "gene1_symbol": "GeneA",
            "gene2_symbol": "GeneB",
            "phenotype_shared_annotations": [
                {"mp_term_name": "decreased bone mineral density"},
                {"mp_term_name": "abnormal behavior"},
            ],
        },
        {
            "gene1_symbol": "GeneA",
            "gene2_symbol": "GeneC",
            "phenotype_shared_annotations": [{"mp_term_name": "abnormal behavior"}],
        },
        {
            "gene1_symbol": "GeneB",
            "gene2_symbol": "GeneC",
            "phenotype_shared_annotations": [{"mp_term_name": "decreased bone mineral density"}],
        },
    ]
    gene_network_dir = tmp_path / "genesymbol"
    gene_network_dir.mkdir()
    _write_network(
        gene_network_dir / "GeneA.json.gz",
        [
            {"data": {"id": "GeneA", "label": "GeneA"}},
            {"data": {"id": "GeneB", "label": "GeneB"}},
            {"data": {"id": "GeneC", "label": "GeneC"}},
            {"data": {"source": "GeneA", "target": "GeneB", "edge_size": 100}},
            {"data": {"source": "GeneA", "target": "GeneC", "edge_size": 50}},
            {"data": {"source": "GeneB", "target": "GeneC", "edge_size": 25}},
        ],
    )

    output_dir = tmp_path / "genesymbol_modules"
    summary_path = tmp_path / "gene_phenotype_module_summary.csv"
    gene_phenotype_module_builder.build_gene_phenotype_module_json(
        pairwise_similarity_annotations,
        ontology_terms,
        gene_network_dir,
        output_dir,
        summary_path,
    )

    with gzip.open(output_dir / "GeneA.json.gz", "rt", encoding="utf-8") as f:
        payload = json.load(f)

    assert payload["target"] == "GeneA"
    assert [module["name"] for module in payload["modules"]] == [
        "behavior/neurological phenotype",
        "skeleton phenotype",
    ]
    assert {module["name"]: module["target_edge_count"] for module in payload["modules"]} == {
        "behavior/neurological phenotype": 2,
        "skeleton phenotype": 1,
    }
    assert payload["edges"]["GeneA||GeneB"]["modules"] == [
        {
            "id": "MP:0005386",
            "name": "behavior/neurological phenotype",
            "label": "behavior/neurological phenotype",
            "count": 1,
            "support_count": 1,
            "weight": 0.5,
        },
        {
            "id": "MP:0005390",
            "name": "skeleton phenotype",
            "label": "skeleton phenotype",
            "count": 1,
            "support_count": 1,
            "weight": 0.5,
        },
    ]
    assert payload["nodes"]["GeneA"]["dominant_module"] == "MP:0005386"
    assert payload["nodes"]["GeneA"]["modules"][0]["weight"] == 0.666667

    with summary_path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert rows == [
        {
            "target": "GeneA",
            "nodes": "3",
            "edges": "3",
            "module_count": "2",
            "module_edge_count": "3",
            "missing_edge_items": "0",
            "missing_unique_terms": "0",
            "missing_term_items": "0",
        }
    ]
