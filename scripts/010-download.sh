#!/bin/bash

mkdir -p data/impc

wget -c https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-21.1/results/statistical-results-ALL.csv.gz -O - | gzip -dc > data/impc/statistical-results-ALL.csv

