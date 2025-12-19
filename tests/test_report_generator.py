import json

from TSUMUGI import report_generator


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
