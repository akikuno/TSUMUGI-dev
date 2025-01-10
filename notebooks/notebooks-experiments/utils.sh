#!/bin/bash


word="marker_symbol_accession_id.json"

find notebooks/ -type f | xargs grep "$word"
