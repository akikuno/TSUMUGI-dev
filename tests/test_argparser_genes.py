import pytest
from TSUMUGI import argparser


def test_genes_pairwise_requires_file_path():
    with pytest.raises(SystemExit) as excinfo:
        argparser.parse_args(["genes", "--pairwise", "--keep", "GeneA,GeneB"])

    assert excinfo.value.code == 2
