from __future__ import annotations

import csv
import gzip
import json
import pickle
import sys
from collections.abc import Iterator
from pathlib import Path


def load_csv_as_dicts(file_path: str | Path, encoding: str = "utf-8") -> Iterator[dict[str, str]]:
    """
    Read CSV file and return each row as a {header: value} dict
    """
    file_path = Path(file_path)

    # Detect gzip-compressed file
    open_func = gzip.open if file_path.suffix == ".gz" else open

    # Open and read as text
    with open_func(file_path, mode="rt", newline="", encoding=encoding) as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield dict(row)


def write_pickle(obj: any, file_path: str | Path) -> None:
    """
    Save any Python object in pickle format
    """
    with open(file_path, "wb") as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)


def read_pickle(file_path: str | Path) -> any:
    """
    Load pickle file and return as Python object
    """
    with open(file_path, "rb") as f:
        return pickle.load(f)


def write_pickle_iter(iterable: Iterator, file_path: str | Path) -> None:
    """
    Sequential (streaming) pickle save.
    Write element by element from iterable (including generators) without loading into memory.
    """
    with open(file_path, "wb") as f:
        for item in iterable:
            pickle.dump(item, f, protocol=pickle.HIGHEST_PROTOCOL)


def read_pickle_iter(file_path: str | Path) -> Iterator[any]:
    """
    Generator that reads pickle sequentially (yields until EOF)
    """
    with open(file_path, "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break


def parse_obo_file(file_path: str | Path) -> dict[str, dict[str, str]]:
    """Parse ontology file (OBO format) and extract term information.
    Returns dict with keys: id, name, is_a (parent terms), is_obsolete
    """
    ontology_terms = {}
    current_term_data = None
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line == "[Term]":
                current_term_data = {}
                continue

            if line.startswith("[") and line.endswith("]") and line != "[Term]":
                current_term_data = None
                continue

            if current_term_data is None:
                continue

            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                if key == "id":
                    current_term_data["id"] = value
                elif key == "name":
                    current_term_data["name"] = value
                elif key == "is_a":
                    if "is_a" not in current_term_data:
                        current_term_data["is_a"] = []
                    parent_id = value.split("!")[0].strip()
                    current_term_data["is_a"].append(parent_id)
                elif key == "is_obsolete":
                    current_term_data["is_obsolete"] = value.lower() == "true"

            if line == "" and current_term_data and "id" in current_term_data:
                if not current_term_data.get("is_obsolete", False):
                    ontology_terms[current_term_data["id"]] = current_term_data
                current_term_data = None

    return ontology_terms


###########################################################
# Parse report (jsonl.gz) files to `pair_similarity_annotations`:
# dict[frozenset[str], dict[str, dict[str, str] | int]]
###########################################################


def parse_jsonl_gz_to_pair_map(
    path_jsonl_gz: str | Path | None,
) -> dict[frozenset[str], dict[str, dict[str, str] | int]]:
    """
    Read a JSONL (.gz) file or standard input and return a mapping of gene pairs to their annotations.
    """
    pair_similarity_annotations = {}

    # --- When reading from standard input ---
    if path_jsonl_gz in (None, sys.stdin):
        file_iter = (json.loads(line) for line in sys.stdin if line.strip())
    else:
        path_jsonl_gz = Path(path_jsonl_gz)
        if path_jsonl_gz.suffix == ".gz":
            f = gzip.open(path_jsonl_gz, "rt", encoding="utf-8")
        else:
            f = open(path_jsonl_gz, encoding="utf-8")
        file_iter = map(json.loads, f)

    # --- Common reading process ---
    for obj in file_iter:
        gene1 = obj["gene1_symbol"]
        gene2 = obj["gene2_symbol"]
        pair = frozenset([gene1, gene2])
        del obj["gene1_symbol"], obj["gene2_symbol"]
        pair_similarity_annotations[pair] = obj

    # Explicitly close gzip.open() / open() only when used
    if "f" in locals():
        f.close()

    return pair_similarity_annotations


###########################################################
# Parse report (jsonl.gz) files to `records_significants`:
###########################################################


def parse_jsonl_gz_to_records_significants(
    path_jsonl_gz: str | Path | None,
) -> list[dict[str, str | float]]:
    """
    Read a JSONL (.gz) file or standard input and return a mapping of gene pairs to their annotations.
    """
    records_significants = []

    # --- When reading from standard input ---
    if path_jsonl_gz in (None, sys.stdin):
        file_iter = (json.loads(line) for line in sys.stdin if line.strip())
    else:
        path_jsonl_gz = Path(path_jsonl_gz)
        if path_jsonl_gz.suffix == ".gz":
            f = gzip.open(path_jsonl_gz, "rt", encoding="utf-8")
        else:
            f = open(path_jsonl_gz, encoding="utf-8")
        file_iter = map(json.loads, f)

    records_significants = list(file_iter)

    # Explicitly close gzip.open() / open() only when used
    if "f" in locals():
        f.close()

    return records_significants
