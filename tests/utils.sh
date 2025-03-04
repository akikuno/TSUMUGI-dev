#!/bin/bash


WORD="phenotypeForm"

find TSUMUGI/template -type f |
    xargs grep "$WORD"
