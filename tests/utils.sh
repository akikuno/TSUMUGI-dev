#!/bin/bash


WORD="REMOVE FROM"

find TSUMUGI/template -type f |
    xargs grep "$WORD"
