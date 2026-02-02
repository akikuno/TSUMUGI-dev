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

### Phänotyp (Phenotype)
Geben Sie einen Phänotyp ein, um **Gene mit ähnlichen KO-Phänotyp-Profilen** zu finden.  
Phänotypnamen folgen [MPO](https://www.informatics.jax.org/vocab/mp_ontology).  
👉 [Phänotyp-Liste](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### Gen (Gene)
Ein Gen angeben, um **andere Gene mit ähnlichen KO-Phänotypen** zu finden.  
Symbole nach [MGI](http://www.informatics.jax.org/).  
👉 [Gen-Liste](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)

### Gen-Liste (Gene List)
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
{"significant": true, "sexual_dimorphism": "Female", "effect_size": 0.0119677350763567, "marker_symbol": "4930447C04Rik", "zygosity": "Homo", "marker_accession_id": "MGI:1923051", "mp_term_id": "MP:0000063", "disease_annotation": ["Male Infertility With Azoospermia Or Oligozoospermia Due To Single Gene Mutation", "Premature Ovarian Failure 18", "Spermatogenic Failure 52"], "life_stage": "Early", "mp_term_name": "decreased bone mineral density"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- Genpaar (`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations`: Metadaten zu geteilten Phänotypen (Lebensphase, Zygosität, Geschlecht)  
- `phenotype_similarity_score`: Resnik→Phenodigm (0–100)

Beispiel:
```
{"gene1_symbol": "1500009L16Rik", "gene2_symbol": "Aak1", "phenotype_shared_annotations": [{"mp_term_name": "increased circulating enzyme level", "life_stage": "Early", "zygosity": "Homo", "sexual_dimorphism": "None"}], "phenotype_similarity_score": 47}
```

# 🌐 Netzwerk

Die Seite wechselt und zeichnet das Netzwerk automatisch basierend auf der Eingabe.

> [!IMPORTANT]  
> Visualisiert werden Paare mit **≥3 geteilten anomalen Phänotypen** und **Ähnlichkeit > 0.0**.

### Netzwerk-Panel
**Knoten** repräsentieren Gene. Klick: Liste der anomalen Phänotypen; Drag: Position ändern.  
**Kanten**: Klick für Details der geteilten Phänotypen.
**Module** umrahmen Gen-Subnetzwerke. Klick: Phänotypen der Modul-Gene anzeigen; Drag: Module verschieben und Überlappungen vermeiden.

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
- `tsumugi count --pairwise/--genewise (--min/--max)`: nach Phänotypanzahl filtern (Paar/Gen)  
- `tsumugi score (--min/--max)`: nach Ähnlichkeitsscore filtern (Genpaare)
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

### Aus IMPC-Daten neu berechnen (`tsumugi run`)
Ohne `--mp_obo`: nutzt `data-version: releases/2025-08-27/mp.obo`.  
Ohne `--impc_phenodigm`: nutzt die Datei vom 01.10.2025 aus dem [IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/).
```bash
tsumugi run \
  --statistical_results ./statistical-results-ALL.csv.gz \
  --threads 8
```
Ausgabe: `./tsumugi-output` enthält genewise_phenotype_annotations.jsonl.gz, pairwise_similarity_annotations.jsonl.gz und `TSUMUGI-webapp`.

> [!IMPORTANT]  
> In `TSUMUGI-webapp` liegen OS-spezifische Startskripte; Doppelklick öffnet die lokale Webapp:  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### Nach MP-Term filtern (`tsumugi mp --include/--exclude`)
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

### Nach Phänotypanzahl filtern (`tsumugi count`)
At least one of `--min` or `--max` is required. Use either alone for one-sided filtering.
- Geteilte Phänotypen je Paar:
```bash
tsumugi count --pairwise --min 3 --max 20 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_min3_max20.jsonl
```
- Phänotypen je Gen (genewise nötig):
```bash
tsumugi count --genewise --min 5 --max 50 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > genewise_min5_max50.jsonl
```


### Nach Ähnlichkeitsscore filtern (`tsumugi score`)
```txt
tsumugi score [-h] [--min MIN] [--max MAX] [--in IN]
```

Genpaare nach `phenotype_similarity_score` (0–100) filtern. Mindestens eines von `--min` oder `--max` ist erforderlich.

#### `--min MIN`, `--max MAX`
Unter-/Obergrenze für den Ähnlichkeitsscore. Nur eine Grenze setzen ist möglich.

#### `--in IN`
Pfad zur pairwise-Annotationsdatei (JSONL/.gz); ohne Angabe wird aus STDIN gelesen.

```bash
tsumugi score --min 50 --max 80 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_score50_80.jsonl
```

`--min` oder `--max` allein ist ausreichend.

### Über Genliste filtern (`tsumugi genes --keep/--drop`)
```bash
tsumugi genes --keep genes.txt \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_keep_genes.jsonl

tsumugi genes --drop geneA,geneB \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_drop_genes.jsonl
```

### Lebensphase / Geschlecht / Zygosität
```bash
tsumugi life-stage --keep Early --in pairwise_similarity_annotations.jsonl.gz > pairwise_lifestage_early.jsonl
tsumugi sex --drop Male --in pairwise_similarity_annotations.jsonl.gz > pairwise_no_male.jsonl
tsumugi zygosity --keep Homo --in pairwise_similarity_annotations.jsonl.gz > pairwise_homo.jsonl
```

### GraphML / Webapp erzeugen
```bash
tsumugi build-graphml \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  > network.graphml

tsumugi build-webapp \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise genewise_phenotype_annotations.jsonl.gz \
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
TSUMUGI folgt aktuell einem Phenodigm-ähnlichen Ansatz. Wir berechnen die **Resnik-Ähnlichkeit** zwischen MP-Begriffen und die **Jaccard-Ähnlichkeit** der Vorfahrenmengen und kombinieren beides über das **geometrische Mittel**. Der wichtigste Unterschied zu Phenodigm ist eine Metadaten-Gewichtung (Zygosität, Lebensphase, sexueller Dimorphismus) bei der Aggregation.

1. MP-Ontologie aufbauen und IC berechnen:  
   `IC(term) = -log((|Descendants(term)| + 1) / |All MP terms|)`  
   Begriffe unter dem 5. Perzentil der IC werden auf 0 gesetzt.
2. Für jedes MP-Begriffs-Paar den spezifischsten gemeinsamen Vorfahren (MICA) bestimmen und dessen IC als Resnik verwenden.  
   Jaccard-Index über die Vorfahrenmengen berechnen.  
   Begriffs-Ähnlichkeit = `sqrt(Resnik * Jaccard)`.
3. Für jedes Genpaar eine Begriff×Begriff-Matrix aufbauen und Metadaten-Gewichtung anwenden.  
   Übereinstimmungen von Zygosität/Lebensphase/sexuellem Dimorphismus liefern Gewichte 0.25/0.5/0.75/1.0 für 0/1/2/3 Matches.
4. Phenodigm-Skalierung auf 0–100 anwenden:  
   Zeilen-/Spaltenmaxima für reales Max/Mean verwenden.  
   Mit theoretischem Max/Mean aus IC normalisieren und berechnen  
   `Score = 100 * (normalized_max + normalized_mean) / 2`.  
   Theoretischer Nenner 0 → 0.

# ✉️ Kontakt
- Google-Formular: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose
