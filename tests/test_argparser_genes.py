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
