from __future__ import annotations

from pathlib import Path


def make_directories(ROOT_DIR: Path, sub_dirs: list[str]) -> None:
    for sub_dir in sub_dirs:
        sub_dir = Path(sub_dir)
        (ROOT_DIR / sub_dir).mkdir(parents=True, exist_ok=True)
