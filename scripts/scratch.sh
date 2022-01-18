#!/bin/sh

zcat data/impc/results/dataOverview.csv.gz | less
zcat data/impc/results/fertility.csv.gz | less -N
zcat data/impc/results/phenotypeHitsPerGene.csv.gz | less -N
