#!/bin/bash

mkdir -p data/impc
echo "*" >data/impc/.gitignore

# rm -rf ftp*
# wget - O - http://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/latest/results |
#     grep "^<a href=" |
#     cut -d '"' -f 2 |
#     while read -r line; do
#         wget -P data/impc http://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/latest/results/"$line"
#     done

###############################################################################
# Download  IMPC Release: 15.1
###############################################################################

time wget -c -r -np -l 0 ftp://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/latest/

# move to "data/impc" manually

###############################################################################
# MD Check Sum
###############################################################################

(
    cd data/impc
    find cores/*.md5 |
        while read -r file; do
            md5sum -c "$file" ||
                echo "$file is not propary downloaded"
        done
)

###############################################################################
# Open TAR files
###############################################################################

ls -l data/impc/cores/*tar -S

find data/impc/cores/*tar |
    while read -r tar; do
        echo $tar
        tar -xf "$tar" -C "$(dirname $tar)"
    done

# END
