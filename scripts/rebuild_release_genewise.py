from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import shlex
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from TSUMUGI import genewise_annotation_builder, io_handler

ROOT_MP_TERM_ID = "MP:0000001"
NATURAL_KEY_FIELDS = (
    "marker_symbol",
    "mp_term_id",
    "zygosity",
    "life_stage",
    "sexual_dimorphism",
)
PAIRWISE_INPUT_FIELDS = (
    "marker_symbol",
    "mp_term_id",
    "zygosity",
    "life_stage",
    "sexual_dimorphism",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rebuild and audit Release 24 genewise phenotype annotations.",
    )
    parser.add_argument("--statistical-results", type=Path, required=True)
    parser.add_argument("--mp-obo", type=Path, required=True)
    parser.add_argument("--impc-phenodigm", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--reference-genewise", type=Path)
    parser.add_argument("--audit-only", action="store_true")
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_record_bytes(record: dict) -> bytes:
    normalized = dict(record)
    effect_size = normalized.get("effect_size")
    if isinstance(effect_size, float) and not math.isfinite(effect_size):
        normalized["effect_size"] = None
    return (
        json.dumps(
            normalized,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        + b"\n"
    )


def annotation_digest(path: Path, significant_only: bool = False) -> tuple[int, str]:
    count = 0
    digest = hashlib.sha256()
    for record in io_handler.read_jsonl(path):
        if significant_only and record["significant"] is not True:
            continue
        count += 1
        digest.update(canonical_record_bytes(record))
    return count, digest.hexdigest()


def projected_significant_digest(path: Path, fields: tuple[str, ...]) -> tuple[int, str]:
    count = 0
    digest = hashlib.sha256()
    for record in io_handler.read_jsonl(path):
        if record["significant"] is not True:
            continue
        count += 1
        projected = {field: record.get(field) for field in fields}
        digest.update(canonical_record_bytes(projected))
    return count, digest.hexdigest()


def audit_annotations(path: Path, ontology_terms: dict[str, dict]) -> dict[str, object]:
    counts: Counter[str] = Counter()
    seen_keys: set[tuple[object, ...]] = set()
    semantic_digest = hashlib.sha256()

    for record in io_handler.read_jsonl(path):
        counts["records"] += 1
        significant = record.get("significant") is True
        counts["significant" if significant else "non_significant"] += 1

        term_id = record.get("mp_term_id", "")
        if term_id == ROOT_MP_TERM_ID:
            counts["root_term_records"] += 1
        expected_name = ontology_terms.get(term_id, {}).get("name")
        if expected_name != record.get("mp_term_name"):
            counts["id_name_mismatches"] += 1
        if not significant and record.get("disease_annotation"):
            counts["non_significant_disease_annotations"] += 1

        key = tuple(record.get(field) for field in NATURAL_KEY_FIELDS)
        if key in seen_keys:
            counts["duplicate_natural_keys"] += 1
        seen_keys.add(key)
        semantic_digest.update(canonical_record_bytes(record))

    return {
        "record_counts": {
            "all": counts["records"],
            "significant": counts["significant"],
            "non_significant": counts["non_significant"],
        },
        "validation": {
            "id_name_mismatches": counts["id_name_mismatches"],
            "root_term_records": counts["root_term_records"],
            "non_significant_disease_annotations": counts["non_significant_disease_annotations"],
            "duplicate_natural_keys": counts["duplicate_natural_keys"],
        },
        "canonical_semantic_sha256": semantic_digest.hexdigest(),
    }


def assert_release_invariants(audit: dict[str, object]) -> None:
    validation = audit["validation"]
    failures = {key: value for key, value in validation.items() if value != 0}
    if failures:
        raise RuntimeError(f"Genewise release invariants failed: {failures}")


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    ontology_terms = io_handler.parse_obo_file(args.mp_obo)
    output_path = args.output_dir / "genewise_phenotype_annotations.jsonl.gz"
    if args.audit_only:
        if not output_path.is_file():
            raise FileNotFoundError(f"Genewise output not found: {output_path}")
    else:
        disease_annotations = io_handler.parse_impc_phenodigm(args.impc_phenodigm)
        records = io_handler.load_csv_as_dicts(args.statistical_results)
        annotations = genewise_annotation_builder.build_genewise_phenotype_annotations(
            records,
            ontology_terms,
            disease_annotations,
        )
        io_handler.write_jsonl(annotations, output_path)

    audit = audit_annotations(output_path, ontology_terms)

    reference_comparison = None
    if args.reference_genewise is not None:
        output_count, output_digest = annotation_digest(output_path, significant_only=True)
        reference_count, reference_digest = annotation_digest(args.reference_genewise, significant_only=True)
        output_pairwise_count, output_pairwise_digest = projected_significant_digest(
            output_path,
            PAIRWISE_INPUT_FIELDS,
        )
        reference_pairwise_count, reference_pairwise_digest = projected_significant_digest(
            args.reference_genewise,
            PAIRWISE_INPUT_FIELDS,
        )
        reference_comparison = {
            "reference_path": str(args.reference_genewise.resolve()),
            "output_significant_count": output_count,
            "reference_significant_count": reference_count,
            "output_significant_canonical_sha256": output_digest,
            "reference_significant_canonical_sha256": reference_digest,
            "significant_records_equal": output_count == reference_count and output_digest == reference_digest,
            "output_pairwise_input_sha256": output_pairwise_digest,
            "reference_pairwise_input_sha256": reference_pairwise_digest,
            "pairwise_inputs_equal": (
                output_pairwise_count == reference_pairwise_count
                and output_pairwise_digest == reference_pairwise_digest
            ),
        }

    summary = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "python": platform.python_version(),
        "command": shlex.join([sys.executable, *sys.argv]),
        "inputs": {
            "statistical_results": str(args.statistical_results.resolve()),
            "statistical_results_sha256": sha256_file(args.statistical_results),
            "mp_obo": str(args.mp_obo.resolve()),
            "mp_obo_sha256": sha256_file(args.mp_obo),
            "impc_phenodigm": str(args.impc_phenodigm.resolve()),
            "impc_phenodigm_sha256": sha256_file(args.impc_phenodigm),
        },
        "output": {
            "path": str(output_path.resolve()),
            "sha256": sha256_file(output_path),
            "release_invariants_passed": all(value == 0 for value in audit["validation"].values()),
            **audit,
        },
        "reference_comparison": reference_comparison,
    }
    summary_path = args.output_dir / "genewise-validation-summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    assert_release_invariants(audit)


if __name__ == "__main__":
    main()
