#!/bin/bash


# | awk '{ print toupper(substr($0, 1, 1)) substr($0, 2, length($0) - 1) }'
find data/mp_term_name -type f |
sed "s|data/mp_term_name/||" |
sed "s|.csv$||" |
grep -e ^male_infertility -e ^increased_circulating_glucose_level | # TODO: Remove this line
while read mp_term; do
    mp_term_capitalized=$(echo $mp_term | awk '{ print toupper(substr($0, 1, 1)) substr($0, 2, length($0) - 1) }' | sed "s|_| |g")
    echo "Generating HTML and JS for $mp_term", capitalized as $mp_term_capitalized
    # HTML
    cat web/network/template.html |
    sed "s|XXX_capital_case|$mp_term_capitalized|g" |
    sed "s|XXX_snake_case|$mp_term|g" > web/network/$mp_term.html
    # Javascript
    cat web/network/js/template.js |
    sed "s|XXX_snake_case|$mp_term|g" > web/network/js/$mp_term.js
done

# cat web/network/template.html
