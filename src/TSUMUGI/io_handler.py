from __future__ import annotations

import csv
import gzip
import json
import pickle
import sys
from collections.abc import Iterable, Iterator
from pathlib import Path

from TSUMUGI import formatter


def count_newline(file_path: str | Path, chunk_size: int = 1024 * 1024) -> int:
    """Count newline characters in plain text or gzip-compressed file efficiently."""
    open_func = gzip.open if Path(file_path).suffix == ".gz" else open
    count = 0
    with open_func(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            count += chunk.count(b"\n")
    return count


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


def parse_impc_phenodigm(file_path: str | Path) -> dict[str, list[dict[str, str]]]:
    with open(Path(file_path)) as f:
        disease_annotations_by_gene: dict[str, list[dict[str, str]]] = formatter.format_disease_annotations(
            list(csv.DictReader(f))
        )
    return disease_annotations_by_gene


def read_jsonl(path_jsonl: str | Path | None) -> Iterator[dict]:
    """
    Stream JSONL (.jsonl or .jsonl.gz). If path_jsonl is None or "-", read from stdin.
    Keeps the file open during iteration (no 'I/O operation on closed file').
    """
    # stdin
    if path_jsonl is None or str(path_jsonl) == "-" or path_jsonl == sys.stdin:
        for line in sys.stdin:
            if line.strip():
                yield json.loads(line)
        return

    # file / gzip
    p = Path(path_jsonl)
    open_func = gzip.open if p.suffix == ".gz" else open

    with open_func(p, "rt", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def write_jsonl(records: Iterable[dict], path_jsonl: str | Path | None) -> None:
    """
    Write an iterable of records as JSONL (.jsonl or .jsonl.gz).
    If path_jsonl is None or "-", write to stdout.
    Each record is dumped as one line of JSON.
    """
    # stdout
    if path_jsonl is None or str(path_jsonl) == "-" or path_jsonl == sys.stdout:
        for record in records:
            json.dump(record, sys.stdout, ensure_ascii=False)
            sys.stdout.write("\n")
        return

    # file / gzip
    p = Path(path_jsonl)
    open_func = gzip.open if p.suffix == ".gz" else open

    with open_func(p, "wt", encoding="utf-8") as f:
        for record in records:
            json.dump(record, f, ensure_ascii=False)
            f.write("\n")


def write_jsonl_to_stdout(record: dict) -> None:
    """Write record as JSONL and suppress BrokenPipeError cleanly."""
    try:
        json.dump(record, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
    except BrokenPipeError:
        try:
            sys.stdout.close()
        except Exception:
            pass
        sys.exit(0)
