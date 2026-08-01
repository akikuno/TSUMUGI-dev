from pathlib import Path

import pytest

from TSUMUGI.mgi_annotation_builder import (
    build_life_stage_inference,
    collect_impc_life_stage_evidence,
    extract_mgi_lof_annotations,
    load_ontology_index,
    normalize_strain,
    summarize_impc_life_stage_evidence,
)


def _write_ontology(path: Path) -> None:
    path.write_text(
        """format-version: 1.2
data-version: test

[Term]
id: MP:0000001
name: mammalian phenotype

[Term]
id: MP:0000002
name: abnormal test phenotype
alt_id: MP:ALT0002
is_a: MP:0000001 ! mammalian phenotype

[Term]
id: MP:0002873
name: normal phenotype
is_a: MP:0000001 ! mammalian phenotype

[Term]
id: MP:0002874
name: normal test phenotype
is_a: MP:0002873 ! normal phenotype
""",
        encoding="utf-8",
    )


@pytest.mark.parametrize(
    "background, expected",
    [
        ("C57BL/6J", "C57BL/6"),
        ("B6N(Cg)-Gene<tm1>", "C57BL/6"),
        ("B6(Cg)-Gene<tm1>", "C57BL/6"),
        ("B6J.B6N-Gene<tm1>", "C57BL/6"),
        ("involves: BALB/cJ", "BALB/c"),
        ("involves: C57BL/6J * 129S1", "129;C57BL/6"),
        ("Not Specified", None),
        ("either: C57BL/6J or BALB/cJ", None),
    ],
)
def test_normalize_strain(background, expected):
    strain, _ = normalize_strain(background)
    assert strain == expected


def test_build_life_stage_inference_uses_all_rows_and_requires_one_stage():
    records = [
        {
            "mp_term_id": "MP:1",
            "mp_term_name": "Embryo term",
            "life_stage": "Embryo",
            "marker_symbol": "A",
            "significant": False,
        },
        {
            "mp_term_id": "MP:1",
            "mp_term_name": "Embryo term",
            "life_stage": "Embryo",
            "marker_symbol": "B",
            "significant": False,
        },
        {
            "mp_term_id": "MP:2",
            "mp_term_name": "Mixed term",
            "life_stage": "Early",
            "marker_symbol": "A",
            "significant": True,
        },
        {
            "mp_term_id": "MP:2",
            "mp_term_name": "Mixed term",
            "life_stage": "Late",
            "marker_symbol": "B",
            "significant": True,
        },
    ]

    inferred, audit = build_life_stage_inference(records)

    assert inferred == {"MP:1": "Embryo"}
    audit_by_id = {row["canonical_mp_id"]: row for row in audit}
    assert audit_by_id["MP:1"]["impc_non_significant_row_count"] == 2
    assert audit_by_id["MP:1"]["impc_gene_count"] == 2
    assert audit_by_id["MP:2"]["inference_status"] == "multiple_stages"


def test_collect_impc_life_stage_evidence_uses_raw_direct_and_intermediate_rows(tmp_path):
    ontology_path = tmp_path / "mp.obo"
    _write_ontology(ontology_path)
    ontology_index = load_ontology_index(ontology_path)
    groups = {}
    rows = [
        {
            "marker_accession_id": "MGI:M1",
            "mp_term_id": "MP:0000002",
            "intermediate_mp_term_id": "",
            "procedure_name": "Adult procedure",
            "pipeline_name": "Late adult pipeline",
            "procedure_stable_id": "IMP_PRO_1",
            "pipeline_stable_id": "IMP_PIPE_1",
            "phenotyping_center": "Center A",
        },
        {
            "marker_accession_id": "MGI:M2",
            "mp_term_id": "",
            "intermediate_mp_term_id": "MP:0000001,MP:0000002",
            "procedure_name": "E12.5 morphology",
            "pipeline_name": "Early pipeline",
            "procedure_stable_id": "IMP_PRO_2",
            "pipeline_stable_id": "IMP_PIPE_2",
            "phenotyping_center": "Center B",
        },
    ]

    assert list(collect_impc_life_stage_evidence(rows, ontology_index, groups)) == rows
    inferred, audit = summarize_impc_life_stage_evidence(groups)

    assert inferred == {}
    row = audit[0]
    assert row["canonical_mp_id"] == "MP:0000002"
    assert row["impc_life_stages"] == "Embryo;Late"
    assert row["impc_direct_mp_row_count"] == 1
    assert row["impc_intermediate_mp_row_count"] == 1
    assert row["impc_gene_count"] == 2
    assert row["impc_procedure_count"] == 2


def test_extract_mgi_lof_annotations_filters_and_preserves_metadata(tmp_path):
    ontology_path = tmp_path / "mp.obo"
    _write_ontology(ontology_path)
    gene_pheno_path = tmp_path / "MGI_GenePheno.rpt"
    gene_pheno_path.write_text(
        "GeneA<tm1>/GeneA<tm1>\tGeneA<tm1>\tMGI:A1\tC57BL/6J\tMP:ALT0002\t12345\tMGI:M1\tMGI:G1\n"
        "GeneA<tm1>/GeneA<tm1>\tGeneA<tm1>\tMGI:A1\tC57BL/6J\tMP:0002874\t12345\tMGI:M1\tMGI:G1\n"
        "GeneB<tm1>/GeneB<+>\tGeneB<tm1>\tMGI:B1\tBALB/cJ\tMP:0000002\t67890\tMGI:M2\tMGI:G2\n",
        encoding="utf-8",
    )
    allele_path = tmp_path / "MGI_PhenotypicAllele.rpt"
    allele_path.write_text(
        "MGI:A1\tGeneA<tm1>\tGene A null\tTargeted\tNull/knockout\t\tMGI:M1\tGeneA\t\t\t\t\tGene A\n"
        "MGI:B1\tGeneB<tm1>\tGene B null\tTargeted\tNull/knockout\t\tMGI:M2\tGeneB\t\t\t\t\tGene B\n",
        encoding="utf-8",
    )
    sex_path = tmp_path / "MGI_Pheno_Sex.rpt"
    sex_path.write_text(
        "Genotype ID\tSex\tMP ID\tMP Term\tAllelic Composition\tBackground Strain\tSex-specific Normal Y/N\tCitation (PubMed/MGI)\n"
        "MGI:G1\tF\tMP:ALT0002\tabnormal test phenotype\tGeneA<tm1>/GeneA<tm1>\tC57BL/6J\tN\t12345\n",
        encoding="utf-8",
    )

    result = extract_mgi_lof_annotations(
        gene_pheno_path=gene_pheno_path,
        phenotypic_allele_path=allele_path,
        pheno_sex_path=sex_path,
        ontology_index=load_ontology_index(ontology_path),
        life_stage_by_mp={"MP:0000002": "Embryo"},
    )

    assert len(result["records"]) == 1
    record = result["records"][0]
    assert record["marker_symbol"] == "GeneA"
    assert record["marker_accession_id"] == "MGI:M1"
    assert record["source_mp_id"] == "MP:ALT0002"
    assert record["mp_term_id"] == "MP:0000002"
    assert record["life_stage"] == "Embryo"
    assert record["observed_sex"] == "Female"
    assert record["strain"] == "C57BL/6"
    assert record["effect_size"] is None
    assert record["source"] == "mgi"
    assert record["significance_basis"] == "mgi_curated_annotation"
    assert record["zygosity"] == "Homo"

    reasons = {row["genotype_id"]: row["reason"] for row in result["eligibility_audit"]}
    assert reasons["MGI:G2"] == "genotype_state:heterozygous"
    assert result["excluded_mp_audit"][0]["reason"] == "normal_phenotype"
