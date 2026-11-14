import json

import pytest

from TSUMUGI import argparser
from TSUMUGI.subcommands import gene_set_assigner

ONTOLOGY = {
    "MP:0000001": {"id": "MP:0000001", "name": "mammalian phenotype"},
    "MP:1": {"id": "MP:1", "name": "cellular phenotype", "is_a": ["MP:0000001"]},
    "MP:2": {"id": "MP:2", "name": "abnormal cilium morphology", "is_a": ["MP:1"]},
    "MP:3": {"id": "MP:3", "name": "abnormal ear morphology", "is_a": ["MP:0000001"]},
    "MP:4": {"id": "MP:4", "name": "abnormal ear physiology", "is_a": ["MP:0000001"]},
    "MP:5": {"id": "MP:5", "name": "deafness", "is_a": ["MP:4"]},
    "MP:6": {"id": "MP:6", "name": "mortality/aging", "is_a": ["MP:0000001"]},
    "MP:7": {"id": "MP:7", "name": "preweaning lethality", "is_a": ["MP:6"]},
    "MP:8": {"id": "MP:8", "name": "pigmentation phenotype", "is_a": ["MP:0000001"]},
}


def _pair(gene1, gene2, score, terms=()):
    return {
        "gene1_symbol": gene1,
        "gene2_symbol": gene2,
        "phenotype_shared_annotations": [{"mp_term_id": t, "mp_term_name": ONTOLOGY[t]["name"]} for t in terms],
        "phenotype_similarity_score": score,
    }


PAIRS = [
    _pair("Query", "A1", 90, ("MP:7", "MP:5", "MP:2")),
    _pair("Query", "A2", 60, ("MP:5", "MP:3")),
    _pair("A3", "Query", 30, ("MP:5",)),
    _pair("Query", "B1", 80),
    _pair("Query", "B2", 10),
    _pair("Query", "B3", 0),
    _pair("A1", "A2", 70),
    _pair("C1", "C2", 50),
]
GENE_SETS = {"SetA": ["A1", "A2", "A3", "Query"], "SetB": ["B1", "B2", "B3"], "SetC": ["C1", "C2", "Absent"]}


def test_classify_mp_term_levels_orders_from_cell_to_organism():
    levels = gene_set_assigner.classify_mp_term_levels(ONTOLOGY)

    assert levels["MP:2"] == "cell"
    assert levels["MP:3"] == "structure"
    assert levels["MP:5"] == "function"
    assert levels["MP:7"] == "organism"
    assert levels["MP:8"] == "other"


def test_read_gene_sets_parses_gmt(tmp_path):
    path = tmp_path / "sets.gmt"
    path.write_text("SetA\tdescription\tA1\tA2\t\nSetB\t\tB1\n\n", encoding="utf-8")

    assert gene_set_assigner.read_gene_sets(path) == {"SetA": ["A1", "A2"], "SetB": ["B1"]}


def test_read_gene_sets_rejects_empty_file(tmp_path):
    path = tmp_path / "empty.gmt"
    path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError):
        gene_set_assigner.read_gene_sets(path)


def test_rank_gene_sets_scores_by_mean_of_top_members_and_excludes_query():
    levels = gene_set_assigner.classify_mp_term_levels(ONTOLOGY)

    records = list(
        gene_set_assigner.rank_gene_sets(iter(PAIRS), GENE_SETS, query_genes={"Query"}, term_levels=levels)
    )

    assert [(r["gene_set"], r["rank"], r["assignment_score"]) for r in records] == [("SetA", 1, 60.0), ("SetB", 2, 30.0)]
    assert records[0]["is_member"] is True
    assert records[0]["gene_set_size"] == 3
    assert records[0]["candidate_gene_sets"] == 2  # SetC has only two members in the pairwise data
    assert [m["gene_symbol"] for m in records[0]["nearest_members"]] == ["A1", "A2", "A3"]
    assert [(p["mp_term_name"], p["level"], p["supporting_members"]) for p in records[0]["shared_phenotypes"]] == [
        ("abnormal cilium morphology", "cell", 1),
        ("abnormal ear morphology", "structure", 1),
        ("deafness", "function", 3),
        ("preweaning lethality", "organism", 1),
    ]


def test_rank_gene_sets_without_query_ranks_all_genes_and_omits_shared_phenotypes():
    records = list(gene_set_assigner.rank_gene_sets(iter(PAIRS), GENE_SETS, max_sets=1))

    by_gene = {r["gene_symbol"]: r for r in records}
    assert by_gene["Query"]["gene_set"] == "SetA"
    assert by_gene["B1"]["gene_set"] == "SetA"  # B1 is similar only to Query, a member of SetA
    assert by_gene["B1"]["assignment_score"] == pytest.approx(80 / 3, abs=1e-5)
    assert "C1" not in by_gene  # no positive score for any candidate set
    assert all("shared_phenotypes" not in r for r in records)


def test_assign_genes_to_gene_sets_writes_jsonl(tmp_path, monkeypatch, capsys):
    gene_sets = tmp_path / "sets.gmt"
    gene_sets.write_text("".join(f"{name}\t\t" + "\t".join(genes) + "\n" for name, genes in GENE_SETS.items()))
    genes = tmp_path / "genes.txt"
    genes.write_text("Query\n")
    monkeypatch.setattr(gene_set_assigner.io_handler, "read_jsonl", lambda path: iter(PAIRS))
    monkeypatch.setattr(gene_set_assigner.io_handler, "parse_obo_file", lambda path: ONTOLOGY)

    gene_set_assigner.assign_genes_to_gene_sets("pairwise-path", gene_sets, genes, "mp.obo", max_sets=1)

    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["gene_set"] == "SetA"


def test_parse_args_accepts_assign():
    args = argparser.parse_args(["assign", "-s", "sets.gmt", "-g", "genes.txt", "--max_sets", "3"])

    assert args.cmd == "assign"
    assert args.path_gene_sets == "sets.gmt"
    assert args.top_members == 3
    assert args.max_sets == 3
    assert args.mp_obo.endswith("mp.obo")
