from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import logging
import math
import multiprocessing as mp
import os
import re
import shutil
import statistics
import threading
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

from TSUMUGI import io_handler, similarity_calculator
from TSUMUGI.ontology_handler import (
    build_term_hierarchy,
    find_all_ancestor_terms,
    find_all_descendant_terms,
)

_worker_profiles: Sequence[Mapping[str, Any]] | None = None
_worker_state: dict[str, Any] | None = None
_worker_compresslevel = 6
TERM_SIMILARITY_ALGORITHM_VERSION = 1
PAIRWISE_ALGORITHM_VERSION = 3


def sha256_file(path: str | Path) -> str:
    """Return the streaming SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _json_scalar(value: Any) -> Any:
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    raise TypeError(f"Cannot serialize {type(value).__name__}")


def _write_json(data: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True, default=_json_scalar) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_tsv(rows: Sequence[Mapping[str, Any]], path: str | Path) -> None:
    """Write a deterministic TSV with stable columns and JSON-safe missing values."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        if output_path.suffix == ".gz":
            with output_path.open("wb") as raw_stream:
                with gzip.GzipFile(filename="", mode="wb", fileobj=raw_stream, mtime=0):
                    pass
        else:
            output_path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0])

    def write_rows(handle: io.TextIOBase) -> None:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            normalized = {}
            for key in fieldnames:
                value = row.get(key)
                if value is None:
                    normalized[key] = ""
                elif isinstance(value, (list, tuple, set, frozenset)):
                    normalized[key] = "|".join(str(item) for item in value)
                elif isinstance(value, bool):
                    normalized[key] = "true" if value else "false"
                else:
                    normalized[key] = value
            writer.writerow(normalized)

    if output_path.suffix == ".gz":
        with output_path.open("wb") as raw_stream:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw_stream, mtime=0) as gzip_stream:
                with io.TextIOWrapper(gzip_stream, encoding="utf-8", newline="") as text_stream:
                    write_rows(text_stream)
        return

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        write_rows(handle)


def build_integrated_profiles(
    records: Iterable[dict[str, Any]],
    ontology_terms: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Collapse source-aware significant records to marker-MP profiles."""
    markers: dict[str, dict[str, Any]] = {}
    evidence_groups: dict[tuple[str, str], dict[str, Any]] = {}

    for record in records:
        if record.get("significant") is not True:
            continue
        marker_id = str(record.get("marker_accession_id") or "").strip()
        term_id = str(record.get("mp_term_id") or "").strip()
        source = str(record.get("source") or "").strip().lower()
        symbol = str(record.get("marker_symbol") or "").strip()
        if not marker_id or not term_id or term_id not in ontology_terms:
            continue
        if source not in {"impc", "mgi"}:
            raise ValueError(f"Unexpected annotation source: {source!r}")

        marker = markers.setdefault(
            marker_id,
            {
                "marker_id": marker_id,
                "symbols_by_source": defaultdict(set),
                "term_sources": defaultdict(set),
                "mgi_genotype_terms": defaultdict(set),
                "mgi_genotype_states": set(),
                "mgi_strains": set(),
                "mgi_backgrounds": set(),
                "mgi_pubmed_ids": set(),
            },
        )
        if symbol:
            marker["symbols_by_source"][source].add(symbol)
        marker["term_sources"][term_id].add(source)
        if source == "mgi":
            genotype_id = str(record.get("genotype_id") or "").strip()
            if genotype_id:
                marker["mgi_genotype_terms"][genotype_id].add(term_id)
            if record.get("genotype_state"):
                marker["mgi_genotype_states"].add(str(record["genotype_state"]))
            if record.get("strain"):
                marker["mgi_strains"].add(str(record["strain"]))
            if record.get("background_raw"):
                marker["mgi_backgrounds"].add(str(record["background_raw"]))
            marker["mgi_pubmed_ids"].update(
                str(pubmed_id)
                for pubmed_id in record.get("pubmed_ids") or []
                if pubmed_id
            )

        key = (marker_id, term_id)
        evidence = evidence_groups.setdefault(
            key,
            {
                "marker_id": marker_id,
                "mp_term_id": term_id,
                "mp_term_name": str(ontology_terms[term_id].get("name", "")),
                "gene_symbols": set(),
                "sources": set(),
                "genotype_ids": set(),
                "genotype_states": set(),
                "strains": set(),
                "backgrounds": set(),
                "pubmed_ids": set(),
            },
        )
        if symbol:
            evidence["gene_symbols"].add(symbol)
        evidence["sources"].add(source)
        if record.get("genotype_id"):
            evidence["genotype_ids"].add(str(record["genotype_id"]))
        if record.get("genotype_state"):
            evidence["genotype_states"].add(str(record["genotype_state"]))
        if record.get("strain"):
            evidence["strains"].add(str(record["strain"]))
        if record.get("background_raw"):
            evidence["backgrounds"].add(str(record["background_raw"]))
        for pubmed_id in record.get("pubmed_ids") or []:
            if pubmed_id:
                evidence["pubmed_ids"].add(str(pubmed_id))

    profiles: list[dict[str, Any]] = []
    alias_audit: list[dict[str, Any]] = []
    burden_audit: list[dict[str, Any]] = []
    genotype_union_audit: list[dict[str, Any]] = []
    for marker_id in sorted(markers):
        marker = markers[marker_id]
        impc_symbols = sorted(marker["symbols_by_source"].get("impc", set()))
        mgi_symbols = sorted(marker["symbols_by_source"].get("mgi", set()))
        all_symbols = sorted(set(impc_symbols).union(mgi_symbols))
        symbol = (impc_symbols or mgi_symbols)[0]
        term_sources = {
            term_id: tuple(sorted(sources))
            for term_id, sources in marker["term_sources"].items()
        }
        profiles.append(
            {
                "marker_id": marker_id,
                "gene_symbol": symbol,
                "gene_symbol_aliases": tuple(all_symbols),
                "term_ids": tuple(sorted(term_sources)),
                "term_sources": term_sources,
            }
        )
        alias_audit.append(
            {
                "marker_id": marker_id,
                "selected_gene_symbol": symbol,
                "impc_gene_symbols": "|".join(impc_symbols),
                "mgi_gene_symbols": "|".join(mgi_symbols),
                "all_gene_symbols": "|".join(all_symbols),
                "symbol_conflict": len(all_symbols) > 1,
            }
        )
        impc_terms = {term for term, sources in term_sources.items() if "impc" in sources}
        mgi_terms = {term for term, sources in term_sources.items() if "mgi" in sources}
        burden_audit.append(
            {
                "marker_id": marker_id,
                "gene_symbol": symbol,
                "impc_mp_count": len(impc_terms),
                "mgi_mp_count": len(mgi_terms),
                "overlap_mp_count": len(impc_terms.intersection(mgi_terms)),
                "union_mp_count": len(term_sources),
                "mgi_added_mp_count": len(mgi_terms - impc_terms),
            }
        )
        genotype_terms = marker["mgi_genotype_terms"]
        genotype_term_sets = [set(terms) for terms in genotype_terms.values()]
        genotype_jaccards = []
        for left_index, left_terms in enumerate(genotype_term_sets):
            for right_terms in genotype_term_sets[left_index + 1 :]:
                union = left_terms.union(right_terms)
                genotype_jaccards.append(
                    len(left_terms.intersection(right_terms)) / len(union) if union else 1.0
                )
        genotype_term_support = defaultdict(int)
        for terms in genotype_term_sets:
            for term_id in terms:
                genotype_term_support[term_id] += 1
        max_single_genotype = max((len(terms) for terms in genotype_term_sets), default=0)
        mgi_union_count = len(mgi_terms)
        genotype_union_audit.append(
            {
                "marker_id": marker_id,
                "gene_symbol": symbol,
                "mgi_genotype_count": len(genotype_terms),
                "mgi_genotype_states": "|".join(sorted(marker["mgi_genotype_states"])),
                "mgi_strain_count": len(marker["mgi_strains"]),
                "mgi_background_count": len(marker["mgi_backgrounds"]),
                "mgi_pubmed_count": len(marker["mgi_pubmed_ids"]),
                "mgi_union_mp_count": mgi_union_count,
                "max_single_genotype_mp_count": max_single_genotype,
                "union_to_max_single_genotype_ratio": (
                    mgi_union_count / max_single_genotype if max_single_genotype else None
                ),
                "median_pairwise_genotype_jaccard": (
                    statistics.median(genotype_jaccards) if genotype_jaccards else None
                ),
                "single_genotype_supported_mp_count": sum(
                    count == 1 for count in genotype_term_support.values()
                ),
                "per_genotype_mp_counts": "|".join(
                    f"{genotype_id}:{len(genotype_terms[genotype_id])}"
                    for genotype_id in sorted(genotype_terms)
                ),
            }
        )

    evidence_audit: list[dict[str, Any]] = []
    for key in sorted(evidence_groups):
        group = evidence_groups[key]
        evidence_audit.append(
            {
                "marker_id": group["marker_id"],
                "gene_symbols": "|".join(sorted(group["gene_symbols"])),
                "canonical_mp_id": group["mp_term_id"],
                "mp_term_name": group["mp_term_name"],
                "sources": "|".join(sorted(group["sources"])),
                "supporting_genotype_count": len(group["genotype_ids"]),
                "supporting_genotype_ids": "|".join(sorted(group["genotype_ids"])),
                "genotype_states": "|".join(sorted(group["genotype_states"])),
                "strains": "|".join(sorted(group["strains"])),
                "backgrounds": "|".join(sorted(group["backgrounds"])),
                "pubmed_ids": "|".join(sorted(group["pubmed_ids"])),
            }
        )

    return {
        "profiles": profiles,
        "alias_audit": alias_audit,
        "burden_audit": burden_audit,
        "genotype_union_audit": genotype_union_audit,
        "evidence_audit": evidence_audit,
    }


def _packed_upper_index(left: int, right: int, size: int) -> int:
    if left > right:
        left, right = right, left
    return left * size - left * (left - 1) // 2 + (right - left)


def _state_signature(
    relevant_terms: Sequence[str],
    ic_map: Mapping[str, float],
    ontology_terms: Mapping[str, Mapping[str, Any]],
) -> str:
    relevant_payload = "\n".join(f"{term}\t{ic_map.get(term, 0.0):.17g}" for term in relevant_terms)
    ontology_payload = "\n".join(
        f"{term}\t{','.join(sorted(str(parent) for parent in ontology_terms[term].get('is_a', [])))}"
        for term in sorted(ontology_terms)
    )
    payload = relevant_payload + "\n--ontology--\n" + ontology_payload
    if TERM_SIMILARITY_ALGORITHM_VERSION != 1:
        payload = f"algorithm_version={TERM_SIMILARITY_ALGORITHM_VERSION}\n" + payload
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_similarity_state(
    *,
    ontology_terms: Mapping[str, Mapping[str, Any]],
    profiles: Sequence[Mapping[str, Any]],
    cache_dir: str | Path,
) -> dict[str, Any]:
    """Build joint IC and a restartable packed term-similarity cache."""
    terms = dict(ontology_terms)
    parent_map, child_map = build_term_hierarchy(terms)
    annotation_records = [
        {"mp_term_id": term_id}
        for profile in profiles
        for term_id in profile["term_ids"]
    ]
    ic_map = similarity_calculator._calculate_term_ic_map(terms, parent_map, annotation_records)
    relevant_terms = tuple(sorted({term for profile in profiles for term in profile["term_ids"]}))
    term_to_index = {term: index for index, term in enumerate(relevant_terms)}

    ontology_ids = tuple(sorted(terms))
    ontology_to_index = {term: index for index, term in enumerate(ontology_ids)}
    ontology_ic = np.asarray([ic_map.get(term, 0.0) for term in ontology_ids], dtype=np.float64)
    relevant_to_ontology = np.asarray(
        [ontology_to_index[term] for term in relevant_terms],
        dtype=np.int32,
    )
    inferred_ontology_indices = []
    for term in relevant_terms:
        inferred = find_all_ancestor_terms(term, parent_map)
        inferred.add(term)
        inferred_ontology_indices.append(
            frozenset(ontology_to_index[item] for item in inferred if item in ontology_to_index)
        )

    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)
    score_path = cache_path / "term-similarity.float32.mmap"
    mica_path = cache_path / "term-mica.int32.mmap"
    metadata_path = cache_path / "term-cache-metadata.json"
    size = len(relevant_terms)
    packed_size = size * (size + 1) // 2
    signature = _state_signature(relevant_terms, ic_map, terms)
    metadata = {
        "schema_version": 2,
        "algorithm_version": TERM_SIMILARITY_ALGORITHM_VERSION,
        "relevant_term_count": size,
        "packed_pair_count": packed_size,
        "signature": signature,
        "complete": False,
    }
    can_resume = False
    cache_complete = False
    if metadata_path.is_file() and score_path.is_file() and mica_path.is_file():
        try:
            existing = json.loads(metadata_path.read_text(encoding="utf-8"))
            existing_algorithm_version = existing.get("algorithm_version", 1)
            can_resume = (
                existing_algorithm_version == TERM_SIMILARITY_ALGORITHM_VERSION
                and all(
                    existing.get(key) == value
                    for key, value in metadata.items()
                    if key not in {"complete", "algorithm_version"}
                )
                and score_path.stat().st_size == packed_size * np.dtype(np.float32).itemsize
                and mica_path.stat().st_size == packed_size * np.dtype(np.int32).itemsize
            )
            cache_complete = can_resume and existing.get("complete") is True
            if can_resume and "algorithm_version" not in existing:
                existing["algorithm_version"] = TERM_SIMILARITY_ALGORITHM_VERSION
                _write_json(existing, metadata_path)
        except (OSError, ValueError, json.JSONDecodeError):
            can_resume = False

    if can_resume:
        scores = np.memmap(score_path, mode="r+", dtype=np.float32, shape=(packed_size,))
        micas = np.memmap(mica_path, mode="r+", dtype=np.int32, shape=(packed_size,))
    else:
        scores = np.memmap(score_path, mode="w+", dtype=np.float32, shape=(packed_size,))
        micas = np.memmap(mica_path, mode="w+", dtype=np.int32, shape=(packed_size,))
        scores[:] = np.nan
        micas[:] = -2
        for term_index, ontology_index in enumerate(relevant_to_ontology):
            packed_index = _packed_upper_index(term_index, term_index, size)
            scores[packed_index] = math.sqrt(max(0.0, ontology_ic[int(ontology_index)]))
            micas[packed_index] = int(ontology_index)
        scores.flush()
        micas.flush()
        _write_json(metadata, metadata_path)

    return {
        "ontology_terms": terms,
        "parent_map": parent_map,
        "child_map": child_map,
        "ic_map": ic_map,
        "relevant_terms": relevant_terms,
        "term_to_index": term_to_index,
        "ontology_ids": ontology_ids,
        "ontology_to_index": ontology_to_index,
        "ontology_ic": ontology_ic,
        "relevant_to_ontology": relevant_to_ontology,
        "inferred_ontology_indices": tuple(inferred_ontology_indices),
        "scores": scores,
        "micas": micas,
        "packed_size": packed_size,
        "descendant_count_cache": {},
        "mica_ancestor_cache": {},
        "computed_pair_count": 0,
        "resumed_cache": can_resume,
        "term_cache_complete": cache_complete,
        "cache_metadata": metadata,
        "cache_metadata_path": metadata_path,
    }


def _descendant_count(state: dict[str, Any], ontology_index: int) -> int:
    cache: dict[int, int] = state["descendant_count_cache"]
    if ontology_index not in cache:
        term_id = state["ontology_ids"][ontology_index]
        cache[ontology_index] = len(find_all_descendant_terms(term_id, state["child_map"]))
    return cache[ontology_index]


def term_similarity_and_mica(
    state: dict[str, Any],
    left_index: int,
    right_index: int,
) -> tuple[float, int]:
    """Return cached sqrt(Resnik*Jaccard) and the ontology index of its MICA."""
    size = len(state["relevant_terms"])
    packed_index = _packed_upper_index(left_index, right_index, size)
    cached_score = state["scores"][packed_index]
    cached_mica = int(state["micas"][packed_index])
    if np.isfinite(cached_score) and cached_mica != -2:
        return float(cached_score), cached_mica

    left_ancestors = state["inferred_ontology_indices"][left_index]
    right_ancestors = state["inferred_ontology_indices"][right_index]
    common = left_ancestors.intersection(right_ancestors)
    if not common:
        score = 0.0
        mica = -1
    else:
        ontology_ic = state["ontology_ic"]
        ontology_ids = state["ontology_ids"]
        mica = min(
            common,
            key=lambda index: (
                -ontology_ic[index],
                _descendant_count(state, index),
                ontology_ids[index],
            ),
        )
        resnik = float(ontology_ic[mica])
        jaccard = len(common) / (len(left_ancestors) + len(right_ancestors) - len(common))
        score = math.sqrt(max(0.0, resnik * jaccard))

    state["micas"][packed_index] = mica
    state["scores"][packed_index] = score
    state["computed_pair_count"] += 1
    return score, mica


def _process_context():
    """Choose a multiprocessing context compatible with shared file-backed arrays."""
    available = mp.get_all_start_methods()
    if threading.active_count() <= 1 and "fork" in available:
        return mp.get_context("fork")
    if "fork" in available:
        logging.warning(
            "Using fork multiprocessing while non-TSUMUGI threads remain active; "
            "the integrated pipeline stops the tqdm monitor before reaching this point."
        )
        return mp.get_context("fork")
    for method in ("forkserver", "spawn"):
        if method in available:
            return mp.get_context(method)
    return mp.get_context()


def _stop_tqdm_monitor() -> None:
    """Stop tqdm's optional monitor thread before creating worker processes."""
    try:
        from tqdm import tqdm

        monitor = getattr(tqdm, "monitor", None)
        if monitor is not None:
            monitor.exit()
            tqdm.monitor = None
    except (AttributeError, RuntimeError):
        logging.warning("Could not stop the tqdm monitor before multiprocessing", exc_info=True)


def _worker_state_payload(state: Mapping[str, Any]) -> dict[str, Any]:
    """Serialize compact state while reopening large memmaps inside workers."""
    excluded = {
        "scores",
        "micas",
        "descendant_count_cache",
        "mica_ancestor_cache",
        "computed_pair_count",
    }
    payload = {key: value for key, value in state.items() if key not in excluded}
    payload["score_path"] = str(state["scores"].filename)
    payload["mica_path"] = str(state["micas"].filename)
    return payload


def _init_integrated_worker(
    profiles: Sequence[Mapping[str, Any]] | None,
    state_payload: Mapping[str, Any],
    compresslevel: int,
    writable_cache: bool,
) -> None:
    """Initialize one portable worker with reopened packed memmaps."""
    global _worker_profiles, _worker_state, _worker_compresslevel
    worker_state = dict(state_payload)
    score_path = worker_state.pop("score_path")
    mica_path = worker_state.pop("mica_path")
    mode = "r+" if writable_cache else "r"
    packed_size = int(worker_state["packed_size"])
    worker_state["scores"] = np.memmap(
        score_path,
        mode=mode,
        dtype=np.float32,
        shape=(packed_size,),
    )
    worker_state["micas"] = np.memmap(
        mica_path,
        mode=mode,
        dtype=np.int32,
        shape=(packed_size,),
    )
    worker_state["descendant_count_cache"] = {}
    worker_state["mica_ancestor_cache"] = {}
    worker_state["computed_pair_count"] = 0
    _worker_profiles = profiles
    _worker_state = worker_state
    _worker_compresslevel = compresslevel


def _precompute_term_rows(task: tuple[int, int]) -> int:
    """Fill one disjoint triangular row block in a forked worker."""
    if _worker_state is None:
        raise RuntimeError("Integrated similarity worker state is not initialized")
    start, end = task
    before = int(_worker_state["computed_pair_count"])
    term_count = len(_worker_state["relevant_terms"])
    for left_index in range(start, min(end, term_count)):
        for right_index in range(left_index, term_count):
            term_similarity_and_mica(_worker_state, left_index, right_index)
    return int(_worker_state["computed_pair_count"]) - before


def precompute_all_term_similarities(
    state: dict[str, Any],
    *,
    workers: int,
    row_block_size: int = 16,
) -> dict[str, Any]:
    """Complete the packed term cache before parallel marker-pair scoring."""
    if workers <= 1:
        return {"completed": bool(state["term_cache_complete"]), "workers": 1, "new_pairs": 0}
    if row_block_size <= 0:
        raise ValueError("row_block_size must be positive")
    if state["term_cache_complete"]:
        return {"completed": True, "workers": workers, "new_pairs": 0}

    _stop_tqdm_monitor()
    context = _process_context()
    term_count = len(state["relevant_terms"])
    tasks = [
        (start, min(start + row_block_size, term_count))
        for start in range(0, term_count, row_block_size)
    ]
    new_pairs = 0
    logging.info(
        "Precomputing %d packed term similarities with %d workers...",
        state["packed_size"],
        workers,
    )
    try:
        with context.Pool(
            processes=workers,
            initializer=_init_integrated_worker,
            initargs=(None, _worker_state_payload(state), 6, True),
        ) as pool:
            for count in pool.imap_unordered(_precompute_term_rows, tasks, chunksize=1):
                new_pairs += count
    finally:
        state["scores"].flush()
        state["micas"].flush()

    state["computed_pair_count"] += new_pairs
    state["term_cache_complete"] = True
    metadata = dict(state["cache_metadata"])
    metadata["complete"] = True
    state["cache_metadata"] = metadata
    _write_json(metadata, state["cache_metadata_path"])
    return {"completed": True, "workers": workers, "new_pairs": new_pairs}


def prepare_profiles(
    profiles: Sequence[Mapping[str, Any]],
    state: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Convert stable MP IDs to compact indices and precompute ideal self scores."""
    prepared = []
    term_to_index = state["term_to_index"]
    ic_map = state["ic_map"]
    for profile in profiles:
        indices = np.asarray([term_to_index[term] for term in profile["term_ids"]], dtype=np.int32)
        self_scores = np.sqrt(
            np.asarray([max(0.0, ic_map.get(term, 0.0)) for term in profile["term_ids"]], dtype=np.float64)
        )
        prepared.append(
            {
                **profile,
                "term_indices": indices,
                "self_scores": self_scores,
                "self_max": float(self_scores.max(initial=0.0)),
                "self_average": float(self_scores.mean()) if self_scores.size else 0.0,
            }
        )
    return prepared


def _candidate_mica_ancestors(state: dict[str, Any], ontology_index: int) -> set[str]:
    cache: dict[int, set[str]] = state["mica_ancestor_cache"]
    if ontology_index not in cache:
        term_id = state["ontology_ids"][ontology_index]
        cache[ontology_index] = find_all_ancestor_terms(term_id, state["parent_map"])
    return cache[ontology_index]


def _prune_parent_micas(state: dict[str, Any], candidate_indices: set[int]) -> set[int]:
    retained = set(candidate_indices)
    for specific_index in candidate_indices:
        ancestors = _candidate_mica_ancestors(state, specific_index)
        for possible_parent in candidate_indices:
            if possible_parent == specific_index:
                continue
            if state["ontology_ids"][possible_parent] in ancestors:
                retained.discard(possible_parent)
    return retained


def score_profile_pair(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
    state: dict[str, Any],
) -> dict[str, Any]:
    """Calculate one integrated marker-pair score and source-aware shared MICAs."""
    left_indices = left["term_indices"]
    right_indices = right["term_indices"]
    matrix = np.empty((len(left_indices), len(right_indices)), dtype=np.float32)
    candidate_sources: dict[int, set[tuple[str, str]]] = defaultdict(set)

    for left_position, left_index in enumerate(left_indices):
        left_term = left["term_ids"][left_position]
        for right_position, right_index in enumerate(right_indices):
            right_term = right["term_ids"][right_position]
            similarity, mica = term_similarity_and_mica(state, int(left_index), int(right_index))
            matrix[left_position, right_position] = similarity
            if similarity <= 0.0 or mica < 0:
                continue
            for left_source in left["term_sources"][left_term]:
                for right_source in right["term_sources"][right_term]:
                    candidate_sources[mica].add((left_source, right_source))

    if not np.any(matrix > 0):
        score = 0.0
    else:
        row_max = matrix.max(axis=1)
        column_max = matrix.max(axis=0)
        observed_max = float(max(row_max.max(initial=0.0), column_max.max(initial=0.0)))
        observed_average = float(np.mean(np.concatenate([row_max, column_max])))
        ideal_max = max(left["self_max"], right["self_max"])
        ideal_average = float(np.mean(np.concatenate([left["self_scores"], right["self_scores"]])))
        normalized_max = observed_max / ideal_max if ideal_max > 0 else 0.0
        normalized_average = observed_average / ideal_average if ideal_average > 0 else 0.0
        score = similarity_calculator.round_phenodigm_score(
            float(np.clip(100.0 * (normalized_max + normalized_average) / 2.0, 0.0, 100.0))
        )

    shared_annotations = []
    for mica in sorted(
        _prune_parent_micas(state, set(candidate_sources)),
        key=lambda index: state["ontology_ids"][index],
    ):
        term_id = state["ontology_ids"][mica]
        shared_annotations.append(
            {
                "mp_term_id": term_id,
                "mp_term_name": str(state["ontology_terms"][term_id].get("name", "")),
                "source_pairs": [list(pair) for pair in sorted(candidate_sources[mica])],
            }
        )

    return {
        "gene1_symbol": left["gene_symbol"],
        "gene1_marker_accession_id": left["marker_id"],
        "gene2_symbol": right["gene_symbol"],
        "gene2_marker_accession_id": right["marker_id"],
        "phenotype_shared_annotations": shared_annotations,
        "phenotype_similarity_score": score,
    }


def _expected_block_pair_count(marker_count: int, start: int, end: int) -> int:
    return sum(marker_count - left_index - 1 for left_index in range(start, min(end, marker_count)))


def _valid_completed_shard(
    shard_path: Path,
    metadata_path: Path,
    expected_count: int,
    *,
    run_signature: str,
    start: int,
    end: int,
) -> dict[str, Any] | None:
    if not shard_path.is_file() or not metadata_path.is_file():
        return None
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    if metadata.get("record_count") != expected_count:
        return None
    if metadata.get("algorithm_version", 1) != PAIRWISE_ALGORITHM_VERSION:
        return None
    if metadata.get("run_signature") != run_signature:
        return None
    if metadata.get("gene1_start_index") != start or metadata.get("gene1_end_index_exclusive") != end:
        return None
    if metadata.get("sha256") != sha256_file(shard_path):
        return None
    if "algorithm_version" not in metadata:
        metadata["algorithm_version"] = PAIRWISE_ALGORITHM_VERSION
        _write_json(metadata, metadata_path)
    return metadata


def _write_pairwise_shard(
    *,
    profiles: Sequence[Mapping[str, Any]],
    state: dict[str, Any],
    start: int,
    end: int,
    shard_path: Path,
    compresslevel: int,
) -> dict[str, Any]:
    partial_path = shard_path.with_suffix(shard_path.suffix + ".partial")
    record_count = 0
    first_pair = ""
    last_pair = ""
    with partial_path.open("wb") as raw_stream:
        with gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=raw_stream,
            compresslevel=compresslevel,
            mtime=0,
        ) as gzip_stream:
            with io.TextIOWrapper(gzip_stream, encoding="utf-8", newline="\n") as text_stream:
                for left_index in range(start, min(end, len(profiles))):
                    left = profiles[left_index]
                    for right_index in range(left_index + 1, len(profiles)):
                        right = profiles[right_index]
                        record = score_profile_pair(left, right, state)
                        text_stream.write(io_handler.serialize_jsonl_record(record) + "\n")
                        pair_label = f"{left['marker_id']}|{right['marker_id']}"
                        if not first_pair:
                            first_pair = pair_label
                        last_pair = pair_label
                        record_count += 1
    os.replace(partial_path, shard_path)
    return {
        "record_count": record_count,
        "first_pair": first_pair,
        "last_pair": last_pair,
        "sha256": sha256_file(shard_path),
        "bytes": shard_path.stat().st_size,
    }


def _write_pairwise_shard_worker(
    task: tuple[int, int, int, Path],
) -> tuple[int, int, int, dict[str, Any]]:
    """Write one pairwise shard using state inherited by a forked worker."""
    if _worker_profiles is None or _worker_state is None:
        raise RuntimeError("Integrated pairwise worker state is not initialized")
    shard_index, start, end, shard_path = task
    metadata = _write_pairwise_shard(
        profiles=_worker_profiles,
        state=_worker_state,
        start=start,
        end=end,
        shard_path=shard_path,
        compresslevel=_worker_compresslevel,
    )
    return shard_index, start, end, metadata


def _complete_shard_metadata(
    *,
    metadata: dict[str, Any],
    metadata_path: Path,
    shard_index: int,
    start: int,
    end: int,
    expected_count: int,
    run_signature: str,
) -> dict[str, Any]:
    if metadata["record_count"] != expected_count:
        raise AssertionError(
            f"Shard {shard_index} wrote {metadata['record_count']} records, expected {expected_count}"
        )
    metadata.update(
        {
            "schema_version": 1,
            "algorithm_version": PAIRWISE_ALGORITHM_VERSION,
            "run_signature": run_signature,
            "gene1_start_index": start,
            "gene1_end_index_exclusive": end,
        }
    )
    _write_json(metadata, metadata_path)
    return metadata


def _remove_stale_pairwise_shards(shards: Path, expected_paths: set[Path]) -> list[str]:
    """Remove generated shard files that do not belong to the completed run."""
    shard_pattern = re.compile(
        r"^pairwise-\d{5}(?:\.jsonl\.gz(?:\.partial)?|\.metadata\.json)$"
    )
    removed: list[str] = []
    for path in sorted(shards.glob("pairwise-*")):
        if not path.is_file() or not shard_pattern.fullmatch(path.name):
            continue
        if path in expected_paths:
            continue
        path.unlink()
        removed.append(str(path))
    return removed


def write_integrated_pairwise_annotations(
    *,
    profiles: Sequence[Mapping[str, Any]],
    state: dict[str, Any],
    output_path: str | Path,
    shard_dir: str | Path,
    block_size: int,
    compresslevel: int = 6,
    workers: int = 1,
) -> dict[str, Any]:
    """Write all canonical marker pairs as restartable deterministic gzip shards."""
    if block_size <= 0:
        raise ValueError("block_size must be positive")
    if workers <= 0:
        raise ValueError("workers must be positive")
    sorted_profiles = sorted(profiles, key=lambda profile: profile["marker_id"])
    marker_count = len(sorted_profiles)
    output = Path(output_path)
    shards = Path(shard_dir)
    shards.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []
    profile_payload = "\n".join(
        "\t".join(
            (
                str(profile["marker_id"]),
                str(profile["gene_symbol"]),
                ";".join(
                    f"{term}:{','.join(profile['term_sources'][term])}"
                    for term in profile["term_ids"]
                ),
            )
        )
        for profile in sorted_profiles
    )
    run_signature = hashlib.sha256(
        (
            state["cache_metadata"]["signature"]
            + "\n"
            + profile_payload
            + f"\ncompresslevel={compresslevel}"
        ).encode("utf-8")
    ).hexdigest()

    metadata_by_index: dict[int, dict[str, Any]] = {}
    pending_tasks: list[tuple[int, int, int, Path]] = []
    shard_specs: list[dict[str, Any]] = []
    for shard_index, start in enumerate(range(0, marker_count, block_size)):
        end = min(start + block_size, marker_count)
        expected_count = _expected_block_pair_count(marker_count, start, end)
        shard_path = shards / f"pairwise-{shard_index:05d}.jsonl.gz"
        metadata_path = shards / f"pairwise-{shard_index:05d}.metadata.json"
        metadata = _valid_completed_shard(
            shard_path,
            metadata_path,
            expected_count,
            run_signature=run_signature,
            start=start,
            end=end,
        )
        shard_specs.append(
            {
                "shard_index": shard_index,
                "start": start,
                "end": end,
                "expected_count": expected_count,
                "shard_path": shard_path,
                "metadata_path": metadata_path,
                "resumed": metadata is not None,
            }
        )
        if metadata is not None:
            metadata_by_index[shard_index] = metadata
        else:
            pending_tasks.append((shard_index, start, end, shard_path))

    parallel_workers = 1
    term_cache_summary = {"completed": bool(state["term_cache_complete"]), "workers": 1, "new_pairs": 0}
    context = _process_context() if workers > 1 and pending_tasks else None
    if context is not None:
        term_cache_summary = precompute_all_term_similarities(state, workers=workers)
        if term_cache_summary["completed"]:
            parallel_workers = min(workers, len(pending_tasks))

    if parallel_workers > 1:
        logging.info(
            "Writing %d integrated pairwise shards with %d workers...",
            len(pending_tasks),
            parallel_workers,
        )
        with context.Pool(
            processes=parallel_workers,
            initializer=_init_integrated_worker,
            initargs=(
                sorted_profiles,
                _worker_state_payload(state),
                compresslevel,
                False,
            ),
        ) as pool:
            completed = pool.imap_unordered(_write_pairwise_shard_worker, pending_tasks, chunksize=1)
            for shard_index, start, end, metadata in completed:
                spec = shard_specs[shard_index]
                metadata_by_index[shard_index] = _complete_shard_metadata(
                    metadata=metadata,
                    metadata_path=spec["metadata_path"],
                    shard_index=shard_index,
                    start=start,
                    end=end,
                    expected_count=spec["expected_count"],
                    run_signature=run_signature,
                )
                logging.info("Completed integrated pairwise shard %d", shard_index)
    else:
        for shard_index, start, end, shard_path in pending_tasks:
            logging.info(
                "Writing integrated pairwise shard %d for gene1 indices [%d, %d)",
                shard_index,
                start,
                end,
            )
            spec = shard_specs[shard_index]
            metadata = _write_pairwise_shard(
                profiles=sorted_profiles,
                state=state,
                start=start,
                end=end,
                shard_path=shard_path,
                compresslevel=compresslevel,
            )
            metadata_by_index[shard_index] = _complete_shard_metadata(
                metadata=metadata,
                metadata_path=spec["metadata_path"],
                shard_index=shard_index,
                start=start,
                end=end,
                expected_count=spec["expected_count"],
                run_signature=run_signature,
            )
            state["scores"].flush()
            state["micas"].flush()

    for spec in shard_specs:
        shard_index = spec["shard_index"]
        metadata = metadata_by_index[shard_index]
        manifest.append(
            {
                "shard_index": shard_index,
                "gene1_start_index": spec["start"],
                "gene1_end_index_exclusive": spec["end"],
                "record_count": metadata["record_count"],
                "first_pair": metadata["first_pair"],
                "last_pair": metadata["last_pair"],
                "bytes": metadata["bytes"],
                "sha256": metadata["sha256"],
                "resumed": spec["resumed"],
                "path": str(spec["shard_path"]),
            }
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    partial_output = output.with_suffix(output.suffix + ".partial")
    with partial_output.open("wb") as destination:
        for row in manifest:
            with Path(row["path"]).open("rb") as source:
                shutil.copyfileobj(source, destination, length=1 << 20)
    os.replace(partial_output, output)

    expected_total = marker_count * (marker_count - 1) // 2
    actual_total = sum(int(row["record_count"]) for row in manifest)
    if actual_total != expected_total:
        raise AssertionError(f"Pair count mismatch: expected {expected_total}, found {actual_total}")

    expected_shard_paths = {
        path
        for spec in shard_specs
        for path in (spec["shard_path"], spec["metadata_path"])
    }
    removed_stale_shards = _remove_stale_pairwise_shards(shards, expected_shard_paths)

    return {
        "algorithm_version": PAIRWISE_ALGORITHM_VERSION,
        "marker_count": marker_count,
        "pair_count": actual_total,
        "shard_count": len(manifest),
        "output_path": str(output),
        "output_bytes": output.stat().st_size,
        "output_sha256": sha256_file(output),
        "run_signature": run_signature,
        "parallel_workers": parallel_workers,
        "term_cache": term_cache_summary,
        "manifest": manifest,
        "removed_stale_shards": removed_stale_shards,
        "new_term_pair_calculations": state["computed_pair_count"],
    }


def write_integrated_audits(
    *,
    profile_data: Mapping[str, Any],
    state: Mapping[str, Any],
    output_dir: str | Path,
) -> dict[str, Path]:
    """Write profile, evidence, alias, and joint-IC audit tables."""
    audit_dir = Path(output_dir)
    audit_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "aliases": audit_dir / "gene-symbol-aliases.tsv",
        "burden": audit_dir / "gene-annotation-burden.tsv",
        "genotype_union": audit_dir / "marker-genotype-union-audit.tsv",
        "evidence": audit_dir / "marker-mp-evidence.tsv",
        "term_ic": audit_dir / "term-ic-audit.tsv",
    }
    write_tsv(profile_data["alias_audit"], paths["aliases"])
    write_tsv(profile_data["burden_audit"], paths["burden"])
    write_tsv(profile_data["genotype_union_audit"], paths["genotype_union"])
    write_tsv(profile_data["evidence_audit"], paths["evidence"])

    direct_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"impc": 0, "mgi": 0, "union": 0})
    for profile in profile_data["profiles"]:
        for term_id, sources in profile["term_sources"].items():
            direct_counts[term_id]["union"] += 1
            for source in sources:
                direct_counts[term_id][source] += 1
    propagated_annotation_counts: dict[str, int] = defaultdict(int)
    propagated_marker_sets: dict[str, set[str]] = defaultdict(set)
    for profile in profile_data["profiles"]:
        marker_id = profile["marker_id"]
        for direct_term_id in profile["term_ids"]:
            inferred_terms = find_all_ancestor_terms(direct_term_id, state["parent_map"])
            inferred_terms.add(direct_term_id)
            for inferred_term_id in inferred_terms:
                propagated_annotation_counts[inferred_term_id] += 1
                propagated_marker_sets[inferred_term_id].add(marker_id)

    term_rows = []
    for term_id in sorted(state["ontology_terms"]):
        counts = direct_counts[term_id]
        term_rows.append(
            {
                "canonical_mp_id": term_id,
                "mp_term_name": state["ontology_terms"][term_id].get("name", ""),
                "impc_direct_marker_count": counts["impc"],
                "mgi_direct_marker_count": counts["mgi"],
                "union_direct_marker_count": counts["union"],
                "propagated_annotation_count": propagated_annotation_counts[term_id],
                "propagated_unique_marker_count": len(propagated_marker_sets[term_id]),
                "joint_ic": state["ic_map"].get(term_id, 0.0),
            }
        )
    write_tsv(term_rows, paths["term_ic"])
    return paths
