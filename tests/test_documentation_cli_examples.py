from __future__ import annotations

import re
import shlex
from pathlib import Path

import pytest

from TSUMUGI import argparser

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FENCED_SHELL_BLOCK = re.compile(r"```(?:bash|sh)\n(.*?)```", re.DOTALL)
INLINE_PIPELINE = re.compile(r"`(tsumugi [^`\n]*\|\s*tsumugi [^`\n]*)`")


def _documentation_paths() -> list[Path]:
    paths = [PROJECT_ROOT / "README.md", PROJECT_ROOT / "doc" / "CLI.md"]
    paths.extend(sorted((PROJECT_ROOT / "doc").glob("README_*.md")))
    return paths


def _extract_fenced_commands(text: str) -> tuple[list[str], list[str]]:
    runnable_commands = []
    synopses = []

    for block in FENCED_SHELL_BLOCK.findall(text):
        lines = block.splitlines()
        index = 0
        while index < len(lines):
            line = lines[index].strip()
            if not line.startswith("tsumugi "):
                index += 1
                continue

            command = line
            while command.rstrip().endswith("\\") and index + 1 < len(lines):
                index += 1
                command = command.rstrip()[:-1] + " " + lines[index].strip()

            if "[-h]" in command:
                synopses.append(command)
            else:
                runnable_commands.append(command)
            index += 1

    return runnable_commands, synopses


def _arguments_from_invocation(invocation: str) -> list[str]:
    tokens = shlex.split(invocation)
    redirect_index = next(
        (index for index, token in enumerate(tokens) if token in {">", ">>"}),
        len(tokens),
    )
    return tokens[1:redirect_index]


def _replace_gene_input_path(argv: list[str], genes_path: Path, pairs_path: Path) -> None:
    if not argv or argv[0] != "genes":
        return

    for flag in ("--keep", "--drop", "-k", "-d"):
        if flag not in argv:
            continue
        value_index = argv.index(flag) + 1
        is_pairwise = "--pairwise" in argv or "-p" in argv
        argv[value_index] = str(pairs_path if is_pairwise else genes_path)
        return


def test_documentation_cli_examples_are_parseable(tmp_path: Path) -> None:
    genes_path = tmp_path / "genes.txt"
    genes_path.write_text("Maf\nAamp\n", encoding="utf-8")
    pairs_path = tmp_path / "gene_pairs.csv"
    pairs_path.write_text("Maf,Aamp\n", encoding="utf-8")

    runnable_example_count = 0
    parsed_invocation_count = 0

    for path in _documentation_paths():
        text = path.read_text(encoding="utf-8")
        runnable_commands, synopses = _extract_fenced_commands(text)
        pipeline_commands = INLINE_PIPELINE.findall(text)

        for synopsis in synopses:
            if synopsis.startswith(("tsumugi mp ", "tsumugi genes ")):
                assert "[-g | -p]" not in synopsis, f"{path}: required mode is shown as optional"

        for command in [*runnable_commands, *pipeline_commands]:
            runnable_example_count += 1
            for invocation in (part.strip() for part in command.split("|")):
                assert "$" not in invocation, f"{path}: unresolved shell variable in {invocation}"
                assert "..." not in invocation, f"{path}: placeholder in runnable example: {invocation}"

                argv = _arguments_from_invocation(invocation)
                _replace_gene_input_path(argv, genes_path, pairs_path)

                try:
                    argparser.parse_args(argv)
                except SystemExit as error:
                    pytest.fail(f"{path}: argument parsing failed for {invocation}: {error}", pytrace=False)
                parsed_invocation_count += 1

    assert runnable_example_count > 0
    assert parsed_invocation_count >= runnable_example_count
