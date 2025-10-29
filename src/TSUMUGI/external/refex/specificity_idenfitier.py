from __future__ import annotations

import csv
import json
import re
import urllib.request
import zipfile
from collections import defaultdict
from io import TextIOWrapper
from pathlib import Path

###########################################################
# Download and prepare RefEx data
###########################################################


def download_refex_data(path_dir: str | Path) -> None:
    path_dir = Path(path_dir)
    path_dir.mkdir(parents=True, exist_ok=True)

    files = [
        (
            path_dir / "RefEx_tissue_specific_genechip_mouse_GSE10246.tsv.zip",
            "https://refex.dbcls.jp/download/RefEx_tissue_specific_genechip_mouse_GSE10246.tsv.zip",
        ),
        (
            path_dir / "RefEx_ID_Relation_mouse.tsv.zip",
            "https://refex.dbcls.jp/download/RefEx_ID_Relation_mouse.tsv.zip",
        ),
        (
            path_dir / "HOM_MouseHumanSequence.rpt",
            "https://www.informatics.jax.org/downloads/reports/HOM_MouseHumanSequence.rpt",
        ),
    ]

    for local_path, url in files:
        if not local_path.exists():
            print(f"Downloading: {url}")
            urllib.request.urlretrieve(url, local_path)
        else:
            print(f"Exists: {local_path}")


###########################################################
# Map RefSeq IDs to Affymetrix Probe IDs
###########################################################


def build_refseq_to_probe_map(path_RefEx_ID_Relation_mouse: str | Path) -> dict[str, str]:
    refseq_probe_map = {}

    with zipfile.ZipFile(path_RefEx_ID_Relation_mouse) as zf:
        tsv_name = zf.namelist()[0]
        print(f"Extracting {tsv_name} from the zip file.")
        with zf.open(tsv_name) as f:
            wrapper = TextIOWrapper(f, encoding="utf-8")
            reader = csv.DictReader(wrapper, delimiter="\t")

            for row in reader:
                if row["NCBI_RefSeqID"] and row["Affymetrix_probesetID"]:
                    refseq_probe_map[row["NCBI_RefSeqID"]] = row["Affymetrix_probesetID"]
    return refseq_probe_map


###########################################################
# Map RefSeq IDs to Gene Symbols
###########################################################


def build_refseq_to_symbol_map(path_HOM_MouseHumanSequence: str | Path) -> dict[str, str]:
    refseq_symbol_map = {}
    with open(path_HOM_MouseHumanSequence) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            refseq_ids = row["Nucleotide RefSeq IDs"].split(",")
            for refseq_id in refseq_ids:
                if not refseq_id.startswith("NM_"):
                    continue
                refseq_symbol_map[refseq_id] = row["Symbol"]
    return refseq_symbol_map


###########################################################
# Map Affymetrix Probe IDs to Gene Symbols
###########################################################


def build_probe_to_symbol_map(refseq_probe_map: dict[str, str], refseq_symbol_map: dict[str, str]) -> dict[str, str]:
    probe_symbol_map = {}
    for refseq_id, probe_id in refseq_probe_map.items():
        if refseq_id in refseq_symbol_map:
            gene_symbol = refseq_symbol_map[refseq_id]
            probe_symbol_map[probe_id] = gene_symbol

    return probe_symbol_map


###########################################################
# Process RefEx tissue-specific gene expression data
###########################################################


def process_refex_data(path_genechip: str | Path, probe_symbol_map: dict[str, str]) -> list[dict]:
    tissue_specific_genechip = []

    with zipfile.ZipFile(path_genechip) as zf:
        tsv_name = zf.namelist()[0]
        print(f"Extracting {tsv_name} from the zip file.")
        with zf.open(tsv_name) as f:
            wrapper = TextIOWrapper(f, encoding="utf-8")
            reader = csv.DictReader(wrapper, delimiter="\t")

            for row in reader:
                if row["Affymetrix_probesetID"] in probe_symbol_map:
                    row["Symbol"] = probe_symbol_map[row["Affymetrix_probesetID"]]
                    tissue_specific_genechip.append(row)

    return tissue_specific_genechip


###########################################################
# Map Gene Symbols to Tissues
###########################################################


def build_symbol_to_tissue_map(tissue_specific_genechip: list[dict]) -> dict[str, list[str]]:
    symbol_tissue_map = defaultdict(list)

    for record in tissue_specific_genechip:
        for key in record:
            if not key.startswith("v"):
                continue
            if record[key] == "1":
                # Trim version prefix from tissue key
                key_trimmed = re.sub(r"^v[0-9]+_", "", key)
                symbol_tissue_map[record["Symbol"]].append(key_trimmed)

    return symbol_tissue_map


###########################################################
# Save symbol to tissue mapping as JSONL
###########################################################


def main():
    refex_dir = Path("./external/refex")
    refex_dir.mkdir(parents=True, exist_ok=True)
    download_refex_data(refex_dir)

    # Build mappings
    refseq_probe_map = build_refseq_to_probe_map(refex_dir / "RefEx_ID_Relation_mouse.tsv.zip")
    refseq_symbol_map = build_refseq_to_symbol_map(refex_dir / "HOM_MouseHumanSequence.rpt")
    probe_symbol_map = build_probe_to_symbol_map(refseq_probe_map, refseq_symbol_map)

    # Process RefEx tissue-specific gene expression data
    tissue_specific_genechip = process_refex_data(
        refex_dir / "RefEx_tissue_specific_genechip_mouse_GSE10246.tsv.zip", probe_symbol_map
    )

    # Extract tissues where expression value starting with vXX_ is "1" (high expression in that tissue)
    symbol_tissue_map = build_symbol_to_tissue_map(tissue_specific_genechip)

    output_path = refex_dir / "symbol_tissue_map.jsonl"
    with open(output_path, "w") as out_f:
        for symbol, tissues in symbol_tissue_map.items():
            json_line = {"marker_symbol": symbol, "tissues": tissues}
            out_f.write(json.dumps(json_line) + "\n")

    print(f"Saved symbol to tissue mapping to {output_path}")


if __name__ == "__main__":
    main()
