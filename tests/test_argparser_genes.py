import pytest

from TSUMUGI import argparser


def test_run_help_uses_release_24_statistical_results(capsys):
    with pytest.raises(SystemExit) as excinfo:
        argparser.parse_args(["run", "--help"])

    assert excinfo.value.code == 0
    help_text = capsys.readouterr().out
    assert "IMPC Release 24.0" in help_text
    assert "statistical-results-ALL.csv.gz" in help_text
    assert "release-24.0/results/statistical-results-ALL.csv.gz" in help_text
    assert "statistical_results_ALL.csv" not in help_text


def test_mp_help_describes_measured_non_significant_records(capsys):
    with pytest.raises(SystemExit) as excinfo:
        argparser.parse_args(["mp", "--help"])

    assert excinfo.value.code == 0
    help_text = capsys.readouterr().out
    assert "mapped non-significant measurement" in help_text
    assert "no matching significant" in help_text
    assert "--genewise_annotations" in help_text
    assert "showed no phenotype" not in help_text


def test_mp_exclude_error_uses_public_option_name(capsys):
    with pytest.raises(SystemExit) as excinfo:
        argparser.parse_args(["mp", "--exclude", "MP:0001146", "--genewise"])

    assert excinfo.value.code == 2
    error_text = capsys.readouterr().err
    assert "--genewise_annotations" in error_text
    assert "--path_genewise" not in error_text


def test_genes_pairwise_requires_file_path():
    with pytest.raises(SystemExit) as excinfo:
        argparser.parse_args(["genes", "--pairwise", "--keep", "GeneA,GeneB"])

    assert excinfo.value.code == 2


def test_run_rejects_gzip_compresslevel():
    with pytest.raises(SystemExit) as excinfo:
        argparser.parse_args(
            [
                "run",
                "--output_dir",
                "out",
                "--statistical_results",
                "statistical-results.csv.gz",
                "--gzip-compresslevel",
                "1",
            ]
        )

    assert excinfo.value.code == 2


def test_run_has_no_gzip_compresslevel_attribute():
    args = argparser.parse_args(
        [
            "run",
            "--output_dir",
            "out",
            "--statistical_results",
            "statistical-results.csv.gz",
        ]
    )

    assert not hasattr(args, "gzip_compresslevel")


def test_run_integrates_mgi_by_default():
    args = argparser.parse_args(
        [
            "run",
            "--output_dir",
            "out",
            "--statistical_results",
            "statistical-results.csv.gz",
            "--annotations-only",
            "--pair-block-size",
            "16",
        ]
    )

    assert args.integrate_mgi is True
    assert args.annotations_only is True
    assert args.pair_block_size == 16
    assert args.mgi_gene_pheno.endswith("data/mgi/MGI_GenePheno.rpt")
    assert args.mgi_phenotypic_allele.endswith("data/mgi/MGI_PhenotypicAllele.rpt")
    assert args.mgi_pheno_sex.endswith("data/mgi/MGI_Pheno_Sex.rpt")


def test_run_explicit_integrate_mgi_remains_supported():
    args = argparser.parse_args(
        [
            "run",
            "--output_dir",
            "out",
            "--statistical_results",
            "statistical-results.csv.gz",
            "--integrate-mgi",
        ]
    )

    assert args.integrate_mgi is True
    assert args.mgi_gene_pheno.endswith("data/mgi/MGI_GenePheno.rpt")


def test_run_no_integrate_mgi_uses_legacy_pipeline_without_mgi_defaults():
    args = argparser.parse_args(
        [
            "run",
            "--output_dir",
            "out",
            "--statistical_results",
            "statistical-results.csv.gz",
            "--no-integrate-mgi",
        ]
    )

    assert args.integrate_mgi is False
    assert args.mgi_gene_pheno is None
    assert args.mgi_phenotypic_allele is None
    assert args.mgi_pheno_sex is None


def test_run_custom_mgi_paths_are_not_overwritten():
    args = argparser.parse_args(
        [
            "run",
            "--output_dir",
            "out",
            "--statistical_results",
            "statistical-results.csv.gz",
            "--mgi-gene-pheno",
            "custom-gene-pheno.rpt",
            "--mgi-phenotypic-allele",
            "custom-allele.rpt",
            "--mgi-pheno-sex",
            "custom-sex.rpt",
        ]
    )

    assert args.mgi_gene_pheno == "custom-gene-pheno.rpt"
    assert args.mgi_phenotypic_allele == "custom-allele.rpt"
    assert args.mgi_pheno_sex == "custom-sex.rpt"


def test_run_rejects_conflicting_mgi_modes():
    with pytest.raises(SystemExit) as excinfo:
        argparser.parse_args(
            [
                "run",
                "--output_dir",
                "out",
                "--statistical_results",
                "statistical-results.csv.gz",
                "--integrate-mgi",
                "--no-integrate-mgi",
            ]
        )

    assert excinfo.value.code == 2


def test_run_help_describes_default_and_legacy_mgi_modes(capsys):
    with pytest.raises(SystemExit) as excinfo:
        argparser.parse_args(["run", "--help"])

    assert excinfo.value.code == 0
    help_text = capsys.readouterr().out
    assert "--integrate-mgi" in help_text
    assert "--no-integrate-mgi" in help_text
    assert "(default)" in help_text


def test_run_rejects_nonpositive_pair_block_size():
    with pytest.raises(SystemExit) as excinfo:
        argparser.parse_args(
            [
                "run",
                "--output_dir",
                "out",
                "--statistical_results",
                "statistical-results.csv.gz",
                "--pair-block-size",
                "0",
            ]
        )

    assert excinfo.value.code == 2
