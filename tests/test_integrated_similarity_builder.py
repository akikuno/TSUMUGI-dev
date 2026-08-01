import gzip
import hashlib
import json

from TSUMUGI import integrated_similarity_builder, similarity_calculator
from TSUMUGI.integrated_similarity_builder import (
    build_integrated_profiles,
    build_similarity_state,
    prepare_profiles,
    score_profile_pair,
    write_integrated_pairwise_annotations,
)


def _ontology():
    return {
        "R": {"id": "R", "name": "Root"},
        "A": {"id": "A", "name": "Branch A", "is_a": ["R"]},
        "B": {"id": "B", "name": "Branch B", "is_a": ["R"]},
        "X": {"id": "X", "name": "Term X", "is_a": ["A"]},
        "Y": {"id": "Y", "name": "Term Y", "is_a": ["A"]},
        "Z": {"id": "Z", "name": "Term Z", "is_a": ["B"]},
    }


def _records():
    return [
        {
            "marker_accession_id": "MGI:1",
            "marker_symbol": "GeneA",
            "mp_term_id": "X",
            "significant": True,
            "source": "impc",
            "pubmed_ids": [],
        },
        {
            "marker_accession_id": "MGI:1",
            "marker_symbol": "GeneA-old",
            "mp_term_id": "X",
            "significant": True,
            "source": "mgi",
            "genotype_id": "G1",
            "genotype_state": "homozygous",
            "strain": "C57BL/6",
            "pubmed_ids": ["1"],
        },
        {
            "marker_accession_id": "MGI:2",
            "marker_symbol": "GeneB",
            "mp_term_id": "Y",
            "significant": True,
            "source": "mgi",
            "genotype_id": "G2",
            "genotype_state": "homozygous",
            "strain": "BALB/c",
            "pubmed_ids": ["2"],
        },
        {
            "marker_accession_id": "MGI:3",
            "marker_symbol": "GeneC",
            "mp_term_id": "Z",
            "significant": True,
            "source": "impc",
            "pubmed_ids": [],
        },
    ]


def _prepared(tmp_path):
    profile_data = build_integrated_profiles(_records(), _ontology())
    state = build_similarity_state(
        ontology_terms=_ontology(),
        profiles=profile_data["profiles"],
        cache_dir=tmp_path / "cache",
    )
    profiles = prepare_profiles(profile_data["profiles"], state)
    return profile_data, state, profiles


def test_integrated_profiles_use_marker_ids_and_joint_ic(tmp_path):
    profile_data, state, profiles = _prepared(tmp_path)

    assert [profile["marker_id"] for profile in profiles] == ["MGI:1", "MGI:2", "MGI:3"]
    assert profiles[0]["gene_symbol"] == "GeneA"
    assert profiles[0]["gene_symbol_aliases"] == ("GeneA", "GeneA-old")
    assert state["ic_map"]["Y"] > 0
    assert len(profile_data["evidence_audit"]) == 3


def test_term_cache_upgrades_versionless_v1_metadata(tmp_path):
    profile_data, _, _ = _prepared(tmp_path)
    metadata_path = tmp_path / "cache" / "term-cache-metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    signature = metadata["signature"]
    metadata.pop("algorithm_version", None)
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    state = integrated_similarity_builder.build_similarity_state(
        ontology_terms=_ontology(),
        profiles=profile_data["profiles"],
        cache_dir=tmp_path / "cache",
    )

    upgraded = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert upgraded["algorithm_version"] == 1
    assert upgraded["signature"] == signature
    assert state["cache_metadata"]["signature"] == signature


def test_term_cache_signature_changes_for_future_algorithm_version(tmp_path, monkeypatch):
    profile_data, state_v1, _ = _prepared(tmp_path)
    monkeypatch.setattr(integrated_similarity_builder, "TERM_SIMILARITY_ALGORITHM_VERSION", 2)

    state_v2 = integrated_similarity_builder.build_similarity_state(
        ontology_terms=_ontology(),
        profiles=profile_data["profiles"],
        cache_dir=tmp_path / "cache-v2",
    )

    assert state_v2["cache_metadata"]["algorithm_version"] == 2
    assert state_v2["cache_metadata"]["signature"] != state_v1["cache_metadata"]["signature"]


def test_score_profile_pair_ignores_metadata_and_keeps_source_pairs(tmp_path):
    _, state, profiles = _prepared(tmp_path)

    result = score_profile_pair(profiles[0], profiles[1], state)

    assert result["phenotype_similarity_score"] > 0
    assert result["gene1_marker_accession_id"] == "MGI:1"
    assert result["gene2_marker_accession_id"] == "MGI:2"
    assert result["phenotype_shared_annotations"] == [
        {
            "mp_term_id": "A",
            "mp_term_name": "Branch A",
            "source_pairs": [["impc", "mgi"], ["mgi", "mgi"]],
        }
    ]
    assert "life_stage" not in result["phenotype_shared_annotations"][0]


def test_integrated_score_matches_current_phenodigm_scaling(tmp_path):
    profile_data, state, profiles = _prepared(tmp_path)
    annotations = [
        {"marker_symbol": profile["gene_symbol"], "mp_term_id": term_id}
        for profile in profile_data["profiles"]
        for term_id in profile["term_ids"]
    ]
    term_ids = {record["mp_term_id"] for record in annotations}
    term_map, ic_map = similarity_calculator.calculate_all_pairwise_similarities(
        _ontology(),
        term_ids,
        annotations,
        threads=1,
    )
    current_scores = {
        (row["gene1_symbol"], row["gene2_symbol"]): row["phenotype_similarity_score"]
        for row in similarity_calculator.calculate_phenodigm_score(annotations, term_map, ic_map)
    }

    integrated = score_profile_pair(profiles[0], profiles[1], state)

    assert integrated["phenotype_similarity_score"] == current_scores[("GeneA", "GeneB")]


def test_pairwise_shards_are_complete_and_deterministic(tmp_path):
    _, state, profiles = _prepared(tmp_path)
    output = tmp_path / "pairwise.jsonl.gz"
    summary1 = write_integrated_pairwise_annotations(
        profiles=profiles,
        state=state,
        output_path=output,
        shard_dir=tmp_path / "shards",
        block_size=2,
        compresslevel=1,
        workers=2,
    )
    digest1 = hashlib.sha256(output.read_bytes()).hexdigest()
    summary2 = write_integrated_pairwise_annotations(
        profiles=profiles,
        state=state,
        output_path=output,
        shard_dir=tmp_path / "shards",
        block_size=2,
        compresslevel=1,
    )
    digest2 = hashlib.sha256(output.read_bytes()).hexdigest()

    with gzip.open(output, "rt", encoding="utf-8") as handle:
        records = [json.loads(line) for line in handle]

    assert summary1["pair_count"] == 3
    assert summary1["algorithm_version"] == 1
    assert summary2["pair_count"] == 3
    assert len(records) == 3
    assert digest1 == digest2
    assert summary1["parallel_workers"] == 2
    assert summary1["term_cache"]["completed"] is True
    assert all(row["resumed"] is True for row in summary2["manifest"])
    pairs = {
        (record["gene1_marker_accession_id"], record["gene2_marker_accession_id"])
        for record in records
    }
    assert pairs == {("MGI:1", "MGI:2"), ("MGI:1", "MGI:3"), ("MGI:2", "MGI:3")}


def test_pairwise_writer_upgrades_versionless_v1_metadata(tmp_path):
    _, state, profiles = _prepared(tmp_path)
    shard_dir = tmp_path / "shards"
    output = tmp_path / "pairwise.jsonl.gz"
    write_integrated_pairwise_annotations(
        profiles=profiles,
        state=state,
        output_path=output,
        shard_dir=shard_dir,
        block_size=2,
        compresslevel=1,
    )
    metadata_path = shard_dir / "pairwise-00000.metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata.pop("algorithm_version")
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    summary = write_integrated_pairwise_annotations(
        profiles=profiles,
        state=state,
        output_path=output,
        shard_dir=shard_dir,
        block_size=2,
        compresslevel=1,
    )

    upgraded = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert upgraded["algorithm_version"] == 1
    assert summary["manifest"][0]["resumed"] is True


def test_pairwise_writer_removes_stale_generated_shards(tmp_path):
    _, state, profiles = _prepared(tmp_path)
    shard_dir = tmp_path / "shards"
    output = tmp_path / "pairwise.jsonl.gz"
    write_integrated_pairwise_annotations(
        profiles=profiles,
        state=state,
        output_path=output,
        shard_dir=shard_dir,
        block_size=1,
        compresslevel=1,
    )
    unrelated = shard_dir / "pairwise-notes.txt"
    unrelated.write_text("keep\n", encoding="utf-8")

    summary = write_integrated_pairwise_annotations(
        profiles=profiles,
        state=state,
        output_path=output,
        shard_dir=shard_dir,
        block_size=2,
        compresslevel=1,
    )

    assert not (shard_dir / "pairwise-00002.jsonl.gz").exists()
    assert not (shard_dir / "pairwise-00002.metadata.json").exists()
    assert unrelated.is_file()
    assert len(summary["removed_stale_shards"]) == 2
