import pytest

from TSUMUGI import argparser


def test_genes_defaults_to_pairwise_when_no_level(tmp_path):
    gene_file = tmp_path / "gene_pairs.txt"
    gene_file.write_text("GeneA,GeneB\nGeneC,GeneD\n")

    args = argparser.parse_args(["genes", "--keep", str(gene_file)])

    assert args.cmd == "genes"
    assert args.pairwise is True
    assert args.genewise is False
    assert args.keep == str(gene_file)


def test_genes_genewise_accepts_comma_separated_list():
    args = argparser.parse_args(["genes", "--genewise", "--keep", "GeneA,GeneB"])

    assert args.cmd == "genes"
    assert args.genewise is True
    assert args.pairwise is False
    assert args.keep == "GeneA,GeneB"


def test_genes_pairwise_requires_file_path():
    with pytest.raises(SystemExit) as excinfo:
        argparser.parse_args(["genes", "--pairwise", "--keep", "GeneA,GeneB"])

    assert excinfo.value.code == 2
