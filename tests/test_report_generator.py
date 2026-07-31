import gzip
import json

from TSUMUGI import report_generator


def _reject_nonstandard_constant(value):
    raise ValueError(f"Nonstandard JSON constant: {value}")


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
    assert json.loads(output_json.read_text(encoding="utf-8")) == {"available phenotype": "available_phenotype"}


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


def test_gene_symbol_lists_separate_gene_pages_from_gene_list_assets(tmp_path):
    gene_dir = tmp_path / "network" / "genesymbol"
    module_dir = tmp_path / "network" / "genesymbol_modules"
    gene_dir.mkdir(parents=True)
    module_dir.mkdir(parents=True)
    _write_network(gene_dir / "GeneA.json.gz", {})
    _write_network(gene_dir / "GeneB.json.gz", {})
    _write_network(module_dir / "GeneA.json.gz", {})

    gene_output = tmp_path / "available_gene_symbols.txt"
    gene_list_output = tmp_path / "available_gene_list_symbols.txt"
    report_generator.write_available_gene_symbols_txt(tmp_path, gene_output)
    report_generator.write_available_gene_list_symbols_txt(tmp_path, gene_list_output)

    assert gene_output.read_text(encoding="utf-8") == "GeneA\n"
    assert gene_list_output.read_text(encoding="utf-8") == "GeneA\nGeneB\n"


def test_write_records_jsonl_gz_uses_standard_json_null(tmp_path):
    output_path = tmp_path / "records.jsonl.gz"

    report_generator.write_records_jsonl_gz(
        [{"marker_symbol": "GeneA", "effect_size": float("nan")}],
        output_path,
    )

    with gzip.open(output_path, "rt", encoding="utf-8") as stream:
        raw_line = stream.read()
    record = json.loads(
        raw_line,
        parse_constant=_reject_nonstandard_constant,
    )
    assert record == {"marker_symbol": "GeneA", "effect_size": None}


def test_write_pairwise_similarity_annotations_uses_standard_json(tmp_path):
    output_path = tmp_path / "pairwise.jsonl.gz"
    annotations = {
        ("GeneB", "GeneA"): {
            "phenotype_shared_annotations": [{"mp_term_name": "phenotype"}],
            "phenotype_similarity_score": 42,
        }
    }

    report_generator.write_pairwise_similarity_annotations(
        annotations,
        output_path,
    )

    with gzip.open(output_path, "rt", encoding="utf-8") as stream:
        record = json.loads(stream.read())
    assert record == {
        "gene1_symbol": "GeneA",
        "gene2_symbol": "GeneB",
        "phenotype_shared_annotations": [{"mp_term_name": "phenotype"}],
        "phenotype_similarity_score": 42,
    }
