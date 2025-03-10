#!/bin/bash


WORD="phenotypeForm"

find TSUMUGI/template -type f |
    xargs grep "$WORD"

type prettier || conda install -y -n env-tsumugi conda-forge::prettier
prettier --write "TSUMUGI/template/**/*" --print-width 120 --prose-wrap never --tab-width 4
