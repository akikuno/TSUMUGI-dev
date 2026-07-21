import gzip
import json

from TSUMUGI import report_generator


def _write_network(path, network):
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(network, f)


def test_available_mp_terms_exclude_empty_networks(tmp_path):
    phenotype_dir = tmp_path / "network" / "phenotype"
    phenotype_dir.mkdir(parents=True)
    _write_network(phenotype_dir / "available_phenotype.json.gz", [{"data": {"id": "GeneA"}}])
    _write_network(phenotype_dir / "empty_phenotype.json.gz", [])

    output_txt = tmp_path / "available_mp_terms.txt"
    output_json = tmp_path / "available_mp_terms.json"
    report_generator.write_available_mp_terms_txt(tmp_path, output_txt)
    report_generator.write_available_mp_terms_json(tmp_path, output_json)

    assert output_txt.read_text(encoding="utf-8") == "available phenotype\n"
    assert json.loads(output_json.read_text(encoding="utf-8")) == {
        "available phenotype": "available_phenotype"
    }


def test_binary_phenotypes_exclude_empty_networks(tmp_path):
    phenotype_dir = tmp_path / "network" / "phenotype"
    phenotype_dir.mkdir(parents=True)
    _write_network(phenotype_dir / "available_phenotype.json.gz", [{"data": {"id": "GeneA"}}])
    _write_network(phenotype_dir / "empty_phenotype.json.gz", [])
    records = [
        {"mp_term_name": "available phenotype", "effect_size": 1},
        {"mp_term_name": "empty phenotype", "effect_size": 1},
    ]

    output_file = tmp_path / "binary_phenotypes.txt"
    report_generator.write_binary_phenotypes_txt(records, tmp_path, output_file)

    assert output_file.read_text(encoding="utf-8") == "available phenotype\n"


def test_write_mp_term_id_lookup(tmp_path):
    available = {
        "Phenotype Alpha": "phenotype_alpha",
        "Phenotype Beta": "phenotype_beta",
        "Phenotype Gamma": "phenotype_gamma",
    }
    available_file = tmp_path / "available.json"
    available_file.write_text(json.dumps(available))

    records = [
        {"mp_term_name": "Phenotype Alpha", "mp_term_id": "MP:0001"},
        {"mp_term_name": "Phenotype Alpha", "mp_term_id": "MP:0001"},
        {"mp_term_name": "Phenotype Alpha", "mp_term_id": "MP:9999"},  # minority ID
        {"mp_term_name": "Phenotype Beta", "mp_term_id": "MP:0002"},
        {"mp_term_name": "Phenotype Gamma", "mp_term_id": ""},  # missing ID should be ignored
        {"mp_term_name": "Phenotype Delta", "mp_term_id": "MP:0003"},  # not in available map
    ]

    output_file = tmp_path / "lookup.json"
    report_generator.write_mp_term_id_lookup(records, available_file, output_file)

    result = json.loads(output_file.read_text())

    assert result == {
        "phenotype_alpha": "MP:0001",  # picks most frequent ID
        "phenotype_beta": "MP:0002",  # included when available and has ID
    }
