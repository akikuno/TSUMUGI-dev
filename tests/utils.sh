#!/bin/bash


WORD="phenotypeForm"

find TSUMUGI/template -type f |
    xargs grep "$WORD"

prettier --write "TSUMUGI/template/**/*" --print-width 120 --prose-wrap never --tab-width 4
