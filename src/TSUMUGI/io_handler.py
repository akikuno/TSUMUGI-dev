from __future__ import annotations

import csv
import gzip
import pickle
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from pathlib import Path

from tqdm import tqdm


def _looks_gzip(url: str, headers: dict | None) -> bool:
    """Determine if content is gzipped based on response headers and URL"""
    if headers is None:
        headers = {}
    enc = headers.get("Content-Encoding", "").lower()
    ctype = headers.get("Content-Type", "").lower()
    return "gzip" in enc or "application/gzip" in ctype or "application/x-gzip" in ctype or url.endswith(".gz")


def download_file(
    url: str,
    error_message: str,
    retries: int = 3,
    timeout: int = 10,
    encoding: str = "utf-8",
    chunk_size: int = 1024 * 32,  # Read in 32KB chunks
) -> str:
    """
    Download data from URL. Automatically decompress if gzipped.
    Display progress with tqdm.
    - Success: returns text (str)
    - Failure (after 3 attempts): raises specified RuntimeError
    """
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                headers = dict(resp.headers.items())
                total_size = int(resp.getheader("Content-Length", 0))
                raw = bytearray()

                with tqdm(
                    total=total_size,
                    unit="B",
                    unit_scale=True,
                    desc=f"Downloading (attempt {attempt})",
                ) as pbar:
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        raw.extend(chunk)
                        pbar.update(len(chunk))

            # Check if gzip and decompress
            if _looks_gzip(url, headers):
                try:
                    raw = gzip.decompress(raw)
                except OSError:
                    pass  # If detected as gzip but actually not, keep as is

            return raw.decode(encoding)

        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            TimeoutError,
            UnicodeDecodeError,
        ) as e:
            last_err = e
            if attempt < retries:
                time.sleep(2)

    # Failed after 3 attempts
    raise RuntimeError(error_message) from last_err


def save_csv(rows: Iterator[list[str]], output_path: str, *, csv_encoding: str = "utf-8") -> None:
    """
    Save CSV row data to file
    """
    with open(output_path, "w", newline="", encoding=csv_encoding) as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def load_csv_as_dicts(file_path: str | Path, encoding: str = "utf-8") -> Iterator[dict[str, str]]:
    """
    Read CSV file and return each row as a {header: value} dict
    """
    with open(file_path, newline="", encoding=encoding) as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield dict(row)  # Convert OrderedDict to regular dict


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
