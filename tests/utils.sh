#!/bin/bash


WORD="phenotypeForm"

find TSUMUGI/template -type f |
    xargs grep "$WORD"


prettier --write "TSUMUGI/template/**/*.js" --tab-width 4
