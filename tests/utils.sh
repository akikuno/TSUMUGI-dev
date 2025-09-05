#!/bin/bash

PYTHONPATH="src" python src/TSUMUGI/main.py
PYTHONPATH="src" pytest -vv tests/


WORD="inf"
find src/ -type f | grep ".py$" | xargs grep "$WORD"


find notebooks/ -type f | xargs grep "$WORD"
find TSUMUGI/template -type f | xargs grep "$WORD"
find TSUMUGI/js -type f | xargs grep "$WORD"

conda activate env-tsumugi

ruff check notebooks/ --fix
ruff format notebooks/

type prettier || conda install -y -n env-tsumugi conda-forge::prettier
prettier --write "TSUMUGI/template/**/*" --print-width 120 --prose-wrap never --tab-width 4
prettier --write "test-tsumugi/**/*" --print-width 120 --prose-wrap never --tab-width 4


prettier --write "TSUMUGI/app/**/*" --print-width 120 --prose-wrap never --tab-width 4
