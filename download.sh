#!/bin/bash

mkdir -p data/impc

rm -rf ftp*
wget - O - http://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/latest/results |
    grep "^<a href=" |
    cut -d '"' -f 2 |
    while read -r line; do
        wget -P data/impc http://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/latest/results/"$line"
    done

###############################################################################
# すべてのデータを保存（Release: 15.1）
###############################################################################

time wget -c -r -np -l 0 ftp://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/latest/
