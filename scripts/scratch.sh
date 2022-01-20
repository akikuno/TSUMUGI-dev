#!/bin/sh

ls -l -S data/impc/results/*.csv.gz
find data/impc/results/*.csv.gz |
    zcat data/impc/results/dataOverview.csv.gz | less
zcat data/impc/results/fertility.csv.gz | less -N
zcat data/impc/results/phenotypeHitsPerGene.csv.gz | less -N

# geneAndMPTermAssociationにはMGIのPhoenotype Overviewに関わるMPリストしか情報がない
zcat data/impc/results/geneAndMPTermAssociation.csv.gz | less -N
zcat data/impc/results/geneAndMPTermAssociation.csv.gz |
    head |
    awk -F, '{print $1, $2, $3}'
zcat data/impc/results/geneAndMPTermAssociation.csv.gz |
    grep -e "heterozygote" -e "hemizygote" -e "homozygote" |
    cut -d, -f 1
zcat data/impc/results/geneAndMPTermAssociation.csv.gz |
    grep "Hnrnph2"

# data/impc/results/statistical-results-ALL.csv.gz

zcat data/impc/results/statistical-results-ALL.csv.gz |
    head -n 1 >tmp.csv
zcat data/impc/results/statistical-results-ALL.csv.gz |
    grep Maf, >>tmp.csv

gzip -c tmp.csv >tmp.csv.gz
# END
