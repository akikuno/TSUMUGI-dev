import csv
import gzip
import json
import sys

from TSUMUGI import main


def _write_statistical_results(path):
    fieldnames = [
        "marker_symbol",
        "marker_accession_id",
        "mp_term_name",
        "mp_term_id",
        "p_value",
        "effect_size",
        "female_ko_effect_p_value",
        "female_ko_parameter_estimate",
        "male_ko_effect_p_value",
        "male_ko_parameter_estimate",
        "zygosity",
        "pipeline_name",
        "procedure_name",
        "allele_symbol",
        "intermediate_mp_term_id",
        "strain_name",
    ]
    rows = [
        ("GeneA", "MGI:M1", "abnormal alpha", "MP:0000002"),
        ("GeneB", "MGI:M2", "abnormal alpha", "MP:0000002"),
        ("GeneC", "MGI:M3", "abnormal beta", "MP:0000003"),
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for marker, marker_id, term_name, term_id in rows:
            writer.writerow(
                {
                    "marker_symbol": marker,
                    "marker_accession_id": marker_id,
                    "mp_term_name": term_name,
                    "mp_term_id": term_id,
                    "p_value": "0.01",
                    "effect_size": "1.0",
                    "female_ko_effect_p_value": "1.0",
                    "female_ko_parameter_estimate": "0.0",
                    "male_ko_effect_p_value": "1.0",
                    "male_ko_parameter_estimate": "0.0",
                    "zygosity": "homozygote",
                    "pipeline_name": "Early adult pipeline",
                    "procedure_name": "Adult procedure",
                    "allele_symbol": f"{marker}<em1(IMPC)Bay>",
                    "intermediate_mp_term_id": "",
                    "strain_name": "C57BL/6N",
                }
            )


def _read_jsonl_gz(path):
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def test_default_cli_writes_mgi_integrated_genewise_and_pairwise_outputs(monkeypatch, tmp_path):
    ontology_path = tmp_path / "mp.obo"
    ontology_path.write_text(
        """format-version: 1.2
data-version: test

[Term]
id: MP:0000001
name: mammalian phenotype

[Term]
id: MP:0000002
name: abnormal alpha
is_a: MP:0000001 ! mammalian phenotype

[Term]
id: MP:0000003
name: abnormal beta
is_a: MP:0000001 ! mammalian phenotype

""",
        encoding="utf-8",
    )
    statistical_results = tmp_path / "statistical-results-ALL.csv"
    _write_statistical_results(statistical_results)

    gene_pheno = tmp_path / "MGI_GenePheno.rpt"
    gene_pheno.write_text(
        "GeneA<tm1>/GeneA<tm1>\tGeneA<tm1>\tMGI:A1\tC57BL/6J\tMP:0000003\t12345\tMGI:M1\tMGI:G1\n",
        encoding="utf-8",
    )
    phenotypic_allele = tmp_path / "MGI_PhenotypicAllele.rpt"
    phenotypic_allele.write_text(
        "MGI:A1\tGeneA<tm1>\tGene A null\tTargeted\tNull/knockout\t\tMGI:M1\tGeneA\t\t\t\t\tGene A\n",
        encoding="utf-8",
    )
    pheno_sex = tmp_path / "MGI_Pheno_Sex.rpt"
    pheno_sex.write_text(
        "Genotype ID\tSex\tMP ID\tMP Term\tAllelic Composition\tBackground Strain\tSex-specific Normal Y/N\tCitation (PubMed/MGI)\n"
        "MGI:G1\tF\tMP:0000003\tabnormal beta\tGeneA<tm1>/GeneA<tm1>\tC57BL/6J\tN\t12345\n",
        encoding="utf-8",
    )
    output_dir = tmp_path / "output"

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tsumugi",
            "run",
            "--output_dir",
            str(output_dir),
            "--statistical_results",
            str(statistical_results),
            "--mp_obo",
            str(ontology_path),
            "--mgi-gene-pheno",
            str(gene_pheno),
            "--mgi-phenotypic-allele",
            str(phenotypic_allele),
            "--mgi-pheno-sex",
            str(pheno_sex),
            "--pair-block-size",
            "2",
        ],
    )

    main.main()

    genewise_path = output_dir / "genewise_phenotype_annotations.jsonl.gz"
    pairwise_path = output_dir / "pairwise_similarity_annotations.jsonl.gz"
    assert genewise_path.is_file()
    assert pairwise_path.is_file()
    assert not (output_dir / "TSUMUGI-webapp").exists()

    genewise = _read_jsonl_gz(genewise_path)
    pairwise = _read_jsonl_gz(pairwise_path)
    assert {record["source"] for record in genewise} == {"impc", "mgi"}
    assert any(record["significance_basis"] == "mgi_curated_annotation" for record in genewise)
    assert len(pairwise) == 3
    assert all("source_pairs" in shared for record in pairwise for shared in record["phenotype_shared_annotations"])
