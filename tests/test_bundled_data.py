import hashlib
import json
from importlib.resources import files
from pathlib import Path

from TSUMUGI.validator import validate_mgi_reports, validate_obo_file


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def test_bundled_mp_snapshot_version_and_checksum():
    mp_path = Path(str(files("TSUMUGI") / "data" / "mp.obo"))
    with mp_path.open(encoding="utf-8") as handle:
        header = "".join(next(handle) for _ in range(40))

    assert "data-version: releases/2026-07-22/mp.obo" in header
    assert _sha256(mp_path) == "5206452e73771e241837f905b708804f228f422a1575340b3e489e46bc52bf56"
    validate_obo_file(mp_path)


def test_bundled_mgi_snapshot_matches_provenance():
    mgi_dir = Path(str(files("TSUMUGI") / "data" / "mgi"))
    provenance = json.loads((mgi_dir / "input-provenance.json").read_text(encoding="utf-8"))
    expected_names = {
        "MGI_GenePheno.rpt",
        "MGI_PhenotypicAllele.rpt",
        "MGI_Pheno_Sex.rpt",
    }

    assert set(provenance["files"]) == expected_names
    for name in expected_names:
        metadata = provenance["files"][name]
        path = mgi_dir / name
        assert path.is_file()
        assert metadata["retrieved_at"]
        assert metadata["remote_matches_local_at_check"] is True
        assert _sha256(path) == metadata["local_sha256"]

    validate_mgi_reports(
        mgi_dir / "MGI_GenePheno.rpt",
        mgi_dir / "MGI_PhenotypicAllele.rpt",
        mgi_dir / "MGI_Pheno_Sex.rpt",
    )
