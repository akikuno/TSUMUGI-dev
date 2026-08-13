from types import SimpleNamespace

from TSUMUGI import core
from TSUMUGI.core import _filter_pairwise_similarity_annotations_for_web


def test_filter_pairwise_similarity_annotations_for_web_uses_count_and_score():
    records = [
        {
            "gene1_symbol": "GeneA",
            "gene2_symbol": "GeneB",
            "phenotype_shared_annotations": [{}, {}, {}],
            "phenotype_similarity_score": 39,
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
            "phenotype_similarity_score": 40,
        },
    ]

    filtered = _filter_pairwise_similarity_annotations_for_web(
        iter(records),
        min_shared_annotations=3,
        min_phenotype_similarity_score=40,
    )

    assert filtered == [records[2]]


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
