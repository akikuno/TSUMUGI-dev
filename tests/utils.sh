#!/bin/bash


WORD="0.4.0"

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
