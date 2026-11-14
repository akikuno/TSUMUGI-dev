from types import SimpleNamespace

from TSUMUGI import core
from TSUMUGI.core import _filter_pairwise_similarity_annotations_for_web


def test_filter_pairwise_similarity_annotations_for_web_uses_count_and_score():
    records = [
        {
            "gene1_symbol": "GeneA",
            "gene2_symbol": "GeneB",
            "phenotype_shared_annotations": [{}, {}, {}],
            "phenotype_similarity_score": 39.49,
        },
        {
            "gene1_symbol": "GeneC",
            "gene2_symbol": "GeneD",
            "phenotype_shared_annotations": [{}, {}],
            "phenotype_similarity_score": 80,
        },
        {
            "gene1_symbol": "GeneE",
            "gene2_symbol": "GeneF",
            "phenotype_shared_annotations": [{}, {}, {}],
            "phenotype_similarity_score": 39.51,
        },
    ]

    filtered = _filter_pairwise_similarity_annotations_for_web(
        iter(records),
        min_shared_annotations=3,
        min_phenotype_similarity_score=40,
    )

    assert filtered == [records[2]]


def _web_pair(gene1, gene2, score, shared=1):
    return {
        "gene1_symbol": gene1,
        "gene2_symbol": gene2,
        "phenotype_shared_annotations": [{}] * shared,
        "phenotype_similarity_score": score,
    }


def test_filter_pairwise_similarity_annotations_for_web_keeps_top_neighbors_of_either_gene():
    records = [
        _web_pair("Hub", "A", 90),
        _web_pair("Hub", "B", 80),
        _web_pair("Hub", "C", 70),  # not in the top 2 of Hub, but the best partner of C
        _web_pair("A", "B", 60),  # third partner of A, but the second of B
        _web_pair("A", "D", 50),  # third partner of A, but the only partner of D
        _web_pair("Hub", "E", 0.4),  # rounded score below the minimum
        _web_pair("A", "F", 85),
        _web_pair("B", "F", 20),  # third partner of B and second of F
        _web_pair("Hub", "F", 10),  # fourth partner of Hub and third of F
    ]

    filtered = _filter_pairwise_similarity_annotations_for_web(
        iter(records),
        min_shared_annotations=1,
        min_phenotype_similarity_score=1,
        top_neighbors=2,
    )

    assert filtered == [records[0], records[1], records[2], records[3], records[4], records[6], records[7]]


def test_filter_pairwise_similarity_annotations_for_web_top_neighbors_respects_min_shared():
    records = [_web_pair("A", "B", 90, shared=2), _web_pair("A", "C", 50, shared=3)]

    filtered = _filter_pairwise_similarity_annotations_for_web(
        iter(records),
        min_shared_annotations=3,
        min_phenotype_similarity_score=1,
        top_neighbors=1,
    )

    assert filtered == [records[1]]


def test_resolve_web_thresholds_uses_defaults_and_cli_overrides():
    assert core._resolve_web_thresholds(SimpleNamespace()) == (
        core.WEB_MIN_SHARED_ANNOTATIONS,
        core.WEB_TOP_NEIGHBORS,
    )
    assert core._resolve_web_thresholds(SimpleNamespace(web_min_shared=3, web_top_neighbors=0)) == (3, None)


def test_run_pipeline_routes_integrated_mode_to_integrated_outputs(monkeypatch, tmp_path):
    args = SimpleNamespace(
        output_dir=str(tmp_path / "output"),
        statistical_results="statistical-results.csv",
        mp_obo="mp.obo",
        impc_phenodigm="impc_phenodigm.csv",
        integrate_mgi=True,
    )
    integrated_calls = []

    monkeypatch.setattr(core.io_handler, "load_csv_as_dicts", lambda _path: iter(()))
    monkeypatch.setattr(core.io_handler, "parse_obo_file", lambda _path: {"MP:0000001": {}})
    monkeypatch.setattr(core.io_handler, "parse_impc_phenodigm", lambda _path: {})
    monkeypatch.setattr(
        core.integrated_pipeline,
        "run_integrated_pipeline",
        lambda **kwargs: integrated_calls.append(kwargs),
    )
    monkeypatch.setattr(
        core.genewise_annotation_builder,
        "build_genewise_phenotype_annotations",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("legacy pipeline was called")),
    )

    core.run_pipeline(args)

    assert len(integrated_calls) == 1
    assert integrated_calls[0]["args"] is args
    assert integrated_calls[0]["root_dir"] == tmp_path / "output"
