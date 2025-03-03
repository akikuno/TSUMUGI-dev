#!/bin/bash

zcat test-tsumugi/data/genesymbol/Asxl1.json.gz | jq -c '.[]' | grep "Rab10" | grep "Asxl1" | jq -s '.'
zcat test-tsumugi/data/genesymbol/Asxl1.json.gz | grep -n "Rab10"
zcat test-tsumugi/data/genesymbol/Asxl1.json.gz | grep -n "Asxl1"
zcat test-tsumugi/data/genesymbol/Asxl1.json.gz | head -n 50 | tail -n 50
zcat test-tsumugi/data/genesymbol/Asxl1.json.gz | head -n 450 | tail -n 50
zcat test-tsumugi/data/genesymbol/Asxl1.json.gz | head -n 800 | tail -n 50
zcat test-tsumugi/data/genesymbol/Asxl1.json.gz | head -n 950 | tail -n 50

zcat test-tsumugi/data/genesymbol/Rab10.json.gz | jq -c '.[]' | grep "Rab10" | grep "Asxl1"
zcat test-tsumugi/data/genesymbol/Rab10.json.gz | grep -n "Rab10"
zcat test-tsumugi/data/genesymbol/Rab10.json.gz | grep -n "Asxl1"
zcat test-tsumugi/data/genesymbol/Rab10.json.gz | head -n 50 | tail -n 50
zcat test-tsumugi/data/genesymbol/Rab10.json.gz | head -n 450 | tail -n 50
zcat test-tsumugi/data/genesymbol/Rab10.json.gz | head -n 850 | tail -n 50
zcat test-tsumugi/data/genesymbol/Rab10.json.gz | head -n 950 | tail -n 50

zcat test-tsumugi/data/genesymbol/Ddx46.json.gz | grep -n "Ddx46"
zcat test-tsumugi/data/genesymbol/Ddx46.json.gz | head -n 50 | tail -n 50
