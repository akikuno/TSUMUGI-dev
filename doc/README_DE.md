> ⚠️ Dies ist eine von KI erzeugte Übersetzung; bei Unklarheiten siehe das Original (README.md).  
> Original: https://github.com/akikuno/TSUMUGI-dev/blob/main/README.md

<p align="center">
    <a href="https://larc-tsukuba.github.io/tsumugi/" target="_blank">
        <img src="https://raw.githubusercontent.com/akikuno/TSUMUGI-dev/refs/heads/main/image/tsumugi-logo.jpg" alt="Tsumugi Logo" width="80%">
    </a>
</p>

[![License](https://img.shields.io/badge/License-MIT-9cf.svg)](https://choosealicense.com/licenses/mit/)
[![Test](https://img.shields.io/github/actions/workflow/status/akikuno/tsumugi-dev/pytest.yml?branch=main&label=Test&color=brightgreen)](https://github.com/akikuno/tsumugi-dev/actions)
[![PyPI](https://img.shields.io/pypi/v/tsumugi.svg?label=PyPI&color=orange)](https://pypi.org/project/tsumugi/)
[![Bioconda](https://img.shields.io/conda/v/bioconda/tsumugi?label=Bioconda&color=orange)](https://anaconda.org/bioconda/tsumugi)
[![DOI](https://zenodo.org/badge/441025227.svg)](https://doi.org/10.5281/zenodo.14957711)
[![Contact](https://img.shields.io/badge/Contact-923DE2)](https://forms.gle/ME8EJZZHaRNgKZ979)

**TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification)** nutzt KO-Maus-Phänotypdaten des [IMPC](https://www.mousephenotype.org/), um **genetische Module basierend auf phänotypischer Ähnlichkeit zu extrahieren und zu visualisieren**.  
Online für alle nutzbar 👇️  
🔗https://larc-tsukuba.github.io/tsumugi/

**TSUMUGI (紡ぎ)** leitet sich von „Gen-Gruppen, die einen Phänotyp formen, miteinander verweben“ ab.

# 📖 TSUMUGI verwenden

TSUMUGI unterstützt drei Eingabetypen.

### 1. Phänotyp (Phenotype)
Geben Sie einen Phänotyp ein, um **Gene mit ähnlichen KO-Phänotyp-Profilen** zu finden.  
Phänotypnamen folgen [MPO](https://www.informatics.jax.org/vocab/mp_ontology).  
👉 [Phänotyp-Liste](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### 2. Gen (Gene)
Ein Gen angeben, um **andere Gene mit ähnlichen KO-Phänotypen** zu finden.  
Symbole nach [MGI](http://www.informatics.jax.org/).  
👉 [Gen-Liste](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)

### 3. Gen-Liste (Gene List)
Mehrere Gene (eine Zeile pro Gen) einfügen, um **innerhalb der Liste** zu suchen.  
> [!CAUTION]  
> Keine ähnlichen Gene: `No similar phenotypes were found among the entered genes.`  
> Mehr als 200: `Too many genes submitted. Please limit the number to 200 or fewer.`

### 📥 Rohdaten herunterladen
TSUMUGI veröffentlicht gzip-komprimierte JSONL.

#### `genewise_phenotype_annotations.jsonl.gz`
- Gen-Symbol (z. B. "1110059G10Rik")  
- Marker accession ID (z. B. "MGI:1913452")  
- Phänotypname/-ID (z. B. "fused joints", "MP:0000137")  
- Effect size (z. B. 0.0, 1.324)  
- Signifikanz (True/false)  
- Zygosität („Homo“, „Hetero“, „Hemi“)  
- Lebensphase („Embryo“, „Early“, „Interval“, „Late“)  
- Geschlechtsdimorphismus („“, „Male“, „Female“)  
- Krankheitsannotation (z. B. [] oder „Premature Ovarian Failure 18“)

Beispiel:
```
{"life_stage": "Early", "marker_symbol": "1110059G10Rik", "marker_accession_id": "MGI:1913452", "effect_size": 0.0, "mp_term_name": "fused joints", "disease_annotation": [], "significant": false, "zygosity": "Homo", "sexual_dimorphism": "", "mp_term_id": "MP:0000137"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- Genpaar (`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations`: Metadaten zu geteilten Phänotypen (Lebensphase, Zygosität, Geschlecht)  
- `phenotype_similarity_score`: Resnik→Phenodigm (0–100)

Beispiel:
```
{"gene1_symbol": "1110059G10Rik", "gene2_symbol": "Cog6", "phenotype_shared_annotations": {"vertebral transformation": {"zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "Male"}}, "phenotype_similarity_score": 42}
```

# 🌐 Netzwerk

Die Seite wechselt und zeichnet das Netzwerk automatisch basierend auf der Eingabe.

> [!IMPORTANT]  
> Visualisiert werden Paare mit **≥3 geteilten anomalen Phänotypen** und **Ähnlichkeit > 0.0**.

### Netzwerk-Panel
**Knoten** repräsentieren Gene. Klick: Liste der anomalen Phänotypen; Drag: Position ändern.  
**Kanten**: Klick für Details der geteilten Phänotypen.

### Kontroll-Panel
Anzeige im linken Panel anpassen.

#### Nach phänotypischer Ähnlichkeit filtern
`Phenotypes similarity` setzt den Schwellenwert für Kanten via Resnik→Phenodigm.  
> Details: 👉 [🔍 Berechnung ähnlicher Gen-Gruppen](#-berechnung-ähnlicher-gen-gruppen)

#### Nach Schweregrad filtern
`Phenotype severity` filtert Knoten nach Effect size (Schwere in KO). Höhere Werte = stärkere Ausprägung.  
> Ausgeblendet bei binären Phänotypen (z. B. [abnormal embryo development](https://larc-tsukuba.github.io/tsumugi/app/phenotype/abnormal_embryo_development.html); binäre Liste [hier](https://github.com/larc-tsukuba/tsumugi/blob/main/data/binary_phenotypes.txt)) oder Single-Gene-Eingabe.

#### Genotyp festlegen
- `Homo`
- `Hetero`
- `Hemi`

#### Geschlecht festlegen
- `Female`
- `Male`

#### Lebensphase festlegen
- `Embryo`
- `Early` (0–16 Wochen)
- `Interval` (17–48 Wochen)
- `Late` (49+ Wochen)

### Markup-Panel
#### Highlight: Human Disease
Markiert Krankheits-assoziierte Gene (IMPC Disease Models Portal).

#### Search: Specific Gene
Gene im Netzwerk suchen.

#### Layout & Display
Layout, Schriftgröße, Kantendicke, Knotenabstoßung (Cose) anpassen.

#### Export
Export als PNG/CSV/GraphML. CSV enthält Modul-IDs und Phänotyp-Listen je Gen; GraphML ist Cytoscape-kompatibel.

# 🛠 Kommandozeile

CLI hinzugefügt: mit IMPC-Daten neu berechnen, feiner filtern, GraphML oder Offline-Webapp erzeugen.

- Neu berechnen mit `statistical-results-ALL.csv.gz` (optional `mp.obo`, `impc_phenodigm.csv`)  
- MP-Term ein-/ausschließen  
- Nach Genliste filtern (CSV oder Text)  
- Ausgaben: GraphML (`tsumugi build-graphml`), Offline-Webapp (`tsumugi build-webapp`)

## Verfügbare Befehle
- `tsumugi run`: Netzwerk aus IMPC-Daten neu berechnen  
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: MP-Term-bezogene Paare oder Gene ein-/ausschließen  
- `tsumugi n-phenos --pairwise/--genewise (--min/--max)`: nach Phänotypanzahl filtern (Paar/Gen)  
- `tsumugi genes --keep/--drop`: über Genliste behalten/entfernen  
- `tsumugi life-stage --keep/--drop`: nach Lebensphase filtern  
- `tsumugi sex --keep/--drop`: nach Geschlecht filtern  
- `tsumugi zygosity --keep/--drop`: nach Zygosität filtern  
- `tsumugi build-graphml`: GraphML erzeugen  
- `tsumugi build-webapp`: Webapp-Assets erzeugen

## Installation
BioConda:
```bash
conda install -c conda-forge -c bioconda tsumugi
```
PyPI:
```bash
pip install tsumugi
```
Bereit, wenn `tsumugi --version` die Version anzeigt.

## Häufige Nutzung

### 1. Aus IMPC-Daten neu berechnen (`tsumugi run`)
Ohne `--mp_obo`: nutzt `data-version: releases/2025-08-27/mp.obo`.  
Ohne `--impc_phenodigm`: nutzt die Datei vom 01.10.2025 aus dem [IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/).
```bash
tsumugi run \
  --output_dir ./tsumugi-output \
  --statistical_results ./statistical-results-ALL.csv.gz \
  --threads 8
```
Ausgabe: `./tsumugi-output` enthält genewise_phenotype_annotations.jsonl.gz, pairwise_similarity_annotations.jsonl.gz und `TSUMUGI-webapp`.

> [!IMPORTANT]  
> In `TSUMUGI-webapp` liegen OS-spezifische Startskripte; Doppelklick öffnet die lokale Webapp:  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### 2. Nach MP-Term filtern (`tsumugi mp --include/--exclude`)
Extrahiere nur Genpaare mit interessierenden Phänotypen oder Genpaare, bei denen der betreffende Phänotyp gemessen wurde, aber keine signifikante Abweichung zeigte.

- `--pairwise` (Standard, wenn nichts gesetzt): gibt Genpaare aus. Nutze `--in pairwise_similarity_annotations.jsonl(.gz)`.
- `--genewise`: gibt einzelne Gene aus. Nutze `--genewise_annotations genewise_phenotype_annotations.jsonl(.gz)` (für `--exclude` erforderlich, für `--include` empfohlen).

```bash
# Nur Genpaare extrahieren, die MP:0001146 (abnormal testis morphology) oder untergeordnete Begriffe (z. B. MP:0004849 abnormal testis size) enthalten
tsumugi mp --include MP:0001146 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

# Genpaare extrahieren, bei denen MP:0001146 und untergeordnete Begriffe gemessen wurden und keine signifikante Abnormalität vorlag
tsumugi mp --exclude MP:0001146 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

# Signifikante Gen-Annotationen mit MP:0001146 (inkl. Unterbegriffe) extrahieren
tsumugi mp --include MP:0001146 \
  --genewise \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  > genewise_filtered.jsonl

# Gene extrahieren, die für MP:0001146 (inkl. Unterbegriffe) gemessen wurden und keine signifikante Abnormalität zeigten
tsumugi mp --exclude MP:0001146 \
  --genewise \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  > genewise_no_phenotype.jsonl
```

> [!IMPORTANT]
> **Untergeordnete MP-Begriffe des angegebenen IDs werden ebenfalls berücksichtigt.**  
> Beispielsweise werden bei `MP:0001146 (abnormal testis morphology)` auch untergeordnete Begriffe wie `MP:0004849 (abnormal testis size)` berücksichtigt.

### 3. Nach Phänotypanzahl filtern (`tsumugi n-phenos`)
- Geteilte Phänotypen je Paar:
```bash
tsumugi n-phenos --pairwise --min 3 --max 20 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_min3_max20.jsonl
```
- Phänotypen je Gen (genewise nötig):
```bash
tsumugi n-phenos --genewise --min 5 --max 50 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > genewise_min5_max50.jsonl
```

### 4. Über Genliste filtern (`tsumugi genes --keep/--drop`)
```bash
tsumugi genes --keep genes.txt \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_keep_genes.jsonl

tsumugi genes --drop geneA,geneB \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_drop_genes.jsonl
```

### 5. Lebensphase / Geschlecht / Zygosität
```bash
tsumugi life-stage --keep Early --in pairwise_similarity_annotations.jsonl.gz > pairwise_lifestage_early.jsonl
tsumugi sex --drop Male --in pairwise_similarity_annotations.jsonl.gz > pairwise_no_male.jsonl
tsumugi zygosity --keep Homo --in pairwise_similarity_annotations.jsonl.gz > pairwise_homo.jsonl
```

### 6. GraphML / Webapp erzeugen
```bash
tsumugi build-graphml \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  > network.graphml

tsumugi build-webapp \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --output_dir ./webapp_output
```

Pipeline-Beispiel: `zcat ... | tsumugi mp ... | tsumugi genes ... > out.jsonl`

# 🔍 Berechnung ähnlicher Gen-Gruppen

## Datenquelle
[IMPC Release-23.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-23.0/results) `statistical-results-ALL.csv.gz`  
Felder: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)

## Vorverarbeitung
Extrahiere Gen–Phänotyp-Paare mit P ≤ 0.0001 (`p_value`, `female_ko_effect_p_value`, `male_ko_effect_p_value`).  
- Zygosität annotieren: `homo`, `hetero`, `hemi`  
- Geschlecht annotieren: `female`, `male`

## Phänotypische Ähnlichkeit
Resnik zwischen MP-Begriffen, skaliert zu **Phenodigm (0–100)**.

1. MP-Ontologie bauen, IC berechnen:  
   `IC(term) = -log((|Descendants(term)| + 1) / |All MP terms|)`  
2. Resnik(t1, t2) = IC des informativsten gemeinsamen Vorfahren (MICA); wenn keiner, 0.  
3. Für jede Gen-Paar-Matrix Resnik-Werte mit Metadaten-Übereinstimmung (Zygosität/Lebensphase/Geschlecht: 1.0/0.75/0.5/0.25) gewichten; reale Max/Mean nehmen.  
4. Theoretische Max/Mean aus IC ableiten, normalisieren und mitteln:  
   `Phenodigm = 100 * 0.5 * ( actual_max / theoretical_max + actual_mean / theoretical_mean )`  
   Theoretischer Nenner 0 → 0. Ergebnis 0–100 für Downloads und `Phenotypes similarity`-Regler.

# ✉️ Kontakt
- Google-Formular: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose


## CLI option details (updated)

### 2. Filter by MP term (`tsumugi mp --include/--exclude`)
```
tsumugi mp [-h] (-i MP_ID | -e MP_ID) [-g | -p] [-m MP_OBO] [-a GENEWISE_ANNOTATIONS] [--in IN] [--out OUT] [--life_stage LIFE_STAGE] [--sex SEX] [--zygosity ZYGOSITY]
```
- `-i/--include`: include specified MP term (descendants included)
- `-e/--exclude`: measured for the term but no significant phenotype (descendants included); requires `-a/--genewise_annotations`
- `-g/--genewise`: gene-level filtering; specify `-a/--genewise_annotations`
- `-p/--pairwise`: pairwise filtering; if `--in` is omitted, reads from STDIN
- `-m/--mp_obo`: path to mp.obo; defaults to bundled file if omitted
- `-a/--genewise_annotations`: path to genewise annotations (JSONL/.gz)
- `--in`: path to pairwise annotations (JSONL/.gz); if omitted, reads from STDIN
- `--out`: path to output file (JSONL/.gz); if omitted, writes to STDOUT
- `--life_stage`: filter by life stage (`Embryo`, `Early`, `Interval`, `Late`)
- `--sex`: filter by sexual dimorphism (`Male`, `Female`, `None`)
- `--zygosity`: filter by zygosity (`Homo`, `Hetero`, `Hemi`)

### 3. Filter by phenotype counts (`tsumugi n-phenos`)
```
tsumugi n-phenos [-h] (-g | -p) [--min MIN] [--max MAX] [--in IN] [--out OUT] [-a GENEWISE_ANNOTATIONS]
```
- `-g/--genewise`: per-gene counts; requires `-a/--genewise_annotations`
- `-p/--pairwise`: shared phenotype counts per pair; if `--in` omitted, reads from STDIN
- `--min/--max`: thresholds (at least one required)
- `--in`: path to pairwise annotations (JSONL/.gz); if omitted, reads from STDIN
- `--out`: path to output file (JSONL/.gz); if omitted, writes to STDOUT
- `-a/--genewise_annotations`: path to genewise annotations (JSONL/.gz); required with `--genewise`

### 4. Filter by gene list (`tsumugi genes --keep/--drop`)
```
tsumugi genes [-h] (-k GENE_SYMBOL | -d GENE_SYMBOL) [--in IN] [--out OUT]
```
- `-k/--keep`: keep only pairs containing specified genes (comma-separated or text file)
- `-d/--drop`: drop pairs containing specified genes
- `--in`: path to pairwise annotations (JSONL/.gz); if omitted, reads from STDIN
- `--out`: path to output file (JSONL/.gz); if omitted, writes to STDOUT

### 5. Filter by life stage (`tsumugi life-stage --keep/--drop`)
```
tsumugi life-stage [-h] (-k LIFE_STAGE | -d LIFE_STAGE) [--in IN] [--out OUT]
```
- `-k/--keep`: keep only the specified life stage (`Embryo`, `Early`, `Interval`, `Late`)
- `-d/--drop`: drop the specified life stage
- `--in`: path to pairwise annotations (JSONL/.gz); if omitted, reads from STDIN
- `--out`: path to output file (JSONL/.gz); if omitted, writes to STDOUT

### 6. Filter by sex (`tsumugi sex --keep/--drop`)
```
tsumugi sex [-h] (-k SEX | -d SEX) [--in IN] [--out OUT]
```
- `-k/--keep`: keep only the specified sex (`Male`, `Female`, `None`)
- `-d/--drop`: drop the specified sex
- `--in`: path to pairwise annotations (JSONL/.gz); if omitted, reads from STDIN
- `--out`: path to output file (JSONL/.gz); if omitted, writes to STDOUT

### 7. Filter by zygosity (`tsumugi zygosity --keep/--drop`)
```
tsumugi zygosity [-h] (-k ZYGOSITY | -d ZYGOSITY) [--in IN] [--out OUT]
```
- `-k/--keep`: keep only the specified zygosity (`Homo`, `Hetero`, `Hemi`)
- `-d/--drop`: drop the specified zygosity
- `--in`: path to pairwise annotations (JSONL/.gz); if omitted, reads from STDIN
- `--out`: path to output file (JSONL/.gz); if omitted, writes to STDOUT

### 8. Export GraphML / webapp
```
tsumugi build-graphml [-h] [--in IN] -a GENEWISE_ANNOTATIONS
```
- `--in`: path to pairwise annotations (JSONL/.gz); if omitted, reads from STDIN
- `-a/--genewise_annotations`: path to genewise annotations (JSONL/.gz); required
```
tsumugi build-webapp [-h] [--in IN] -a GENEWISE_ANNOTATIONS -o OUT
```
- `--in`: path to pairwise annotations (JSONL/.gz); if omitted, reads from STDIN
- `-a/--genewise_annotations`: path to genewise annotations (JSONL/.gz); required
- `-o/--out`: output directory for the webapp bundle (do not pass a filename with extension)
