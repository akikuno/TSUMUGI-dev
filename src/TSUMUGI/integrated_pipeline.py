from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from itertools import chain
from pathlib import Path
from typing import Any

from TSUMUGI import (
    genewise_annotation_builder,
    integrated_similarity_builder,
    io_handler,
    mgi_annotation_builder,
)


def _write_json(data: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _load_mgi_source_metadata(path: Path) -> dict[str, Any]:
    metadata_path = path.parent / "input-provenance.json"
    if not metadata_path.is_file():
        return {}
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    return dict(metadata.get("files", {}).get(path.name, {}))


def _input_provenance(args, mgi_result: dict[str, Any]) -> list[dict[str, Any]]:
    inputs = (
        ("impc_statistical_results", Path(args.statistical_results)),
        ("mp_ontology", Path(args.mp_obo)),
        ("impc_phenodigm", Path(args.impc_phenodigm)),
        ("mgi_gene_pheno", Path(args.mgi_gene_pheno)),
        ("mgi_phenotypic_allele", Path(args.mgi_phenotypic_allele)),
        ("mgi_pheno_sex", Path(args.mgi_pheno_sex)),
    )
    diagnostics = mgi_result["source_diagnostics"]
    shapes = {
        "mgi_gene_pheno": {
            "line_count": diagnostics["gene_pheno"]["raw_rows"],
            "data_row_count": diagnostics["gene_pheno"]["raw_rows"],
            "column_count": len(mgi_annotation_builder.GENE_PHENO_COLUMNS),
        },
        "mgi_phenotypic_allele": {
            "line_count": (
                diagnostics["phenotypic_allele"]["comment_rows"]
                + diagnostics["phenotypic_allele"]["data_rows"]
            ),
            "data_row_count": diagnostics["phenotypic_allele"]["data_rows"],
            "column_count": len(mgi_annotation_builder.PHENOTYPIC_ALLELE_COLUMNS),
        },
        "mgi_pheno_sex": {
            "line_count": diagnostics["pheno_sex"]["raw_rows"] + 1,
            "data_row_count": diagnostics["pheno_sex"]["raw_rows"],
            "column_count": len(mgi_annotation_builder.SEX_COLUMNS),
        },
    }
    rows = []
    for input_name, path in inputs:
        digest = integrated_similarity_builder.sha256_file(path)
        source_metadata = _load_mgi_source_metadata(path) if input_name.startswith("mgi_") else {}
        metadata_digest = source_metadata.get("local_sha256")
        metadata_matches = metadata_digest == digest if metadata_digest else None
        row = {
            "input_name": input_name,
            "path": str(path.resolve()),
            "bytes": path.stat().st_size,
            "sha256": digest,
            "input_file_mtime": datetime.fromtimestamp(
                path.stat().st_mtime,
                tz=timezone.utc,
            ).isoformat(),
            "line_count": None,
            "data_row_count": None,
            "column_count": None,
            "source_url": source_metadata.get("source_url"),
            "retrieved_at": source_metadata.get("retrieved_at"),
            "recorded_original_mtime": (
                source_metadata.get("recorded_original_mtime") if metadata_matches else None
            ),
            "remote_checked_at": source_metadata.get("remote_checked_at"),
            "remote_last_modified_at_check": source_metadata.get(
                "remote_last_modified_at_check"
            ),
            "remote_matches_local_at_check": (
                source_metadata.get("remote_matches_local_at_check")
                if metadata_matches
                else None
            ),
            "source_metadata_matches_sha256": metadata_matches,
        }
        row.update(shapes.get(input_name, {}))
        rows.append(row)
    return rows


def run_integrated_pipeline(
    *,
    args,
    root_dir: Path,
    ontology_terms: dict[str, dict[str, Any]],
    disease_annotations_by_gene: dict[str, list[dict[str, str]]],
) -> None:
    """Run the source-aware IMPC-MGI annotation pipeline."""
    temp_dir = root_dir / ".tempdir" / "integrated"
    audit_dir = root_dir / "audit"
    shard_dir = root_dir / "shards"
    cache_dir = root_dir / ".pairwise-cache"
    for path in (temp_dir, audit_dir, shard_dir, cache_dir):
        path.mkdir(parents=True, exist_ok=True)

    ontology_index = mgi_annotation_builder.load_ontology_index(args.mp_obo)
    active_ids = set(ontology_index["active_terms"])
    if active_ids != set(ontology_terms):
        raise ValueError("MGI and IMPC ontology parsers produced different active MP ID sets")

    logging.info("Building source-aware IMPC genewise annotations...")
    life_stage_groups: dict[str, dict[str, Any]] = {}
    impc_records = mgi_annotation_builder.collect_impc_life_stage_evidence(
        io_handler.load_csv_as_dicts(Path(args.statistical_results)),
        ontology_index,
        life_stage_groups,
    )
    impc_annotations = genewise_annotation_builder.build_genewise_phenotype_annotations(
        impc_records,
        ontology_terms,
        disease_annotations_by_gene,
        include_integration_fields=True,
    )
    impc_path = temp_dir / "impc-genewise.jsonl.gz"
    io_handler.write_jsonl(impc_annotations, impc_path, compresslevel=6, deterministic=True)

    logging.info("Inferring MGI life stages from all raw IMPC annotation rows...")
    life_stage_by_mp, life_stage_audit = (
        mgi_annotation_builder.summarize_impc_life_stage_evidence(life_stage_groups)
    )
    integrated_similarity_builder.write_tsv(
        life_stage_audit,
        audit_dir / "life-stage-inference-audit.tsv",
    )

    logging.info("Extracting all-background primary MGI LOF annotations...")
    mgi_result = mgi_annotation_builder.extract_mgi_lof_annotations(
        gene_pheno_path=args.mgi_gene_pheno,
        phenotypic_allele_path=args.mgi_phenotypic_allele,
        pheno_sex_path=args.mgi_pheno_sex,
        ontology_index=ontology_index,
        life_stage_by_mp=life_stage_by_mp,
    )
    integrated_similarity_builder.write_tsv(
        mgi_result["eligibility_audit"],
        audit_dir / "mgi-lof-eligibility-audit.tsv",
    )
    integrated_similarity_builder.write_tsv(
        mgi_result["excluded_mp_audit"],
        audit_dir / "mgi-excluded-mp-audit.tsv",
    )
    integrated_similarity_builder.write_tsv(
        mgi_result["strain_audit"],
        audit_dir / "strain-normalization-audit.tsv",
    )
    integrated_similarity_builder.write_tsv(
        mgi_result["stage_counts"],
        audit_dir / "mgi-extraction-stage-counts.tsv",
    )
    _write_json(mgi_result["source_diagnostics"], audit_dir / "mgi-source-diagnostics.json")
    integrated_similarity_builder.write_tsv(
        mgi_result["records"],
        audit_dir / "mgi-all-background-lof-genotype-mp.tsv.gz",
    )

    logging.info("Writing combined IMPC-MGI genewise annotations...")
    genewise_path = root_dir / "genewise_phenotype_annotations.jsonl.gz"
    io_handler.write_jsonl(
        chain(io_handler.read_jsonl(impc_path), mgi_result["records"]),
        genewise_path,
        compresslevel=6,
        deterministic=True,
    )

    logging.info("Building marker-MP union profiles and joint IC...")
    profile_data = integrated_similarity_builder.build_integrated_profiles(
        io_handler.read_jsonl(genewise_path),
        ontology_terms,
    )
    state = integrated_similarity_builder.build_similarity_state(
        ontology_terms=ontology_terms,
        profiles=profile_data["profiles"],
        cache_dir=cache_dir,
    )
    prepared_profiles = integrated_similarity_builder.prepare_profiles(
        profile_data["profiles"],
        state,
    )
    integrated_similarity_builder.write_integrated_audits(
        profile_data=profile_data,
        state=state,
        output_dir=audit_dir,
    )

    logging.info("Writing all integrated marker pairs in deterministic shards...")
    pairwise_path = root_dir / "pairwise_similarity_annotations.jsonl.gz"
    pairwise_summary = integrated_similarity_builder.write_integrated_pairwise_annotations(
        profiles=prepared_profiles,
        state=state,
        output_path=pairwise_path,
        shard_dir=shard_dir,
        block_size=args.pair_block_size,
        workers=args.threads,
    )
    integrated_similarity_builder.write_tsv(
        pairwise_summary.pop("manifest"),
        audit_dir / "pairwise-shard-manifest.tsv",
    )

    provenance = _input_provenance(args, mgi_result)
    integrated_similarity_builder.write_tsv(provenance, audit_dir / "input-provenance.tsv")
    summary = {
        "schema_version": 1,
        "mode": "impc_mgi_integrated",
        "ontology_version": ontology_index["version"],
        "impc_genewise_path": str(impc_path),
        "mgi_genotype_mp_count": len(mgi_result["records"]),
        "integrated_marker_count": len(prepared_profiles),
        "integrated_marker_mp_count": sum(len(profile["term_ids"]) for profile in prepared_profiles),
        "joint_direct_mp_term_count": len(state["relevant_terms"]),
        "life_stage_inferred_mp_count": len(life_stage_by_mp),
        "pairwise": pairwise_summary,
    }
    _write_json(summary, root_dir / "integrated-run-summary.json")
    (root_dir / "README.md").write_text(
        "# IMPCとMGIを統合した注釈\n\n"
        "`genewise_phenotype_annotations.jsonl.gz`は、IMPCの行と、MGIが整理したLOF遺伝子型–異常MP関連を収録しています。"
        "情報源は`source`で区別できます。欠測値はJSONの`null`です。\n\n"
        "MGIの`life_stage`は実測値ではありません。同じMP用語がIMPCの1つのライフステージだけに現れる場合に限り、その値を推定して保存しています。"
        "推定根拠は`audit/life-stage-inference-audit.tsv`で確認できます。\n\n"
        "`pairwise_similarity_annotations.jsonl.gz`は、IMPCとMGIのMP用語を遺伝子ごとにまとめ、統合後の注釈頻度からICを計算して作成した全遺伝子対です。"
        "`phenotype_similarity_score`は0–100のPhenodigmスコアで、小数第6位に丸めた浮動小数点数として保存します。"
        "共有表現型を決めるときは、遺伝型、ライフステージ、性別、系統名を一致条件にしていません。\n\n"
        "MGIの異常MPはキュレーションされた関連であり、統計的有意差を表しません。"
        "また、異なるMGI遺伝子型を遺伝子単位でまとめるため、条件固有の表現型が同時に起きることを意味しません。\n\n"
        "現在のメタデータ絞り込みやWebには対応していません。"
        "従来のIMPC単独処理とWeb生成が必要な場合は`--no-integrate-mgi`を指定してください。\n",
        encoding="utf-8",
        newline="\n",
    )
