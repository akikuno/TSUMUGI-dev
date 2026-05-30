import pytest

from TSUMUGI import argparser


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
