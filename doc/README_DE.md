> ⚠️ Dies ist eine von KI erzeugte Übersetzung; bei Unklarheiten siehe das Original (README.md).  
> Original: https://github.com/akikuno/TSUMUGI-dev/blob/main/README.md

<p align="center">
    <a href="https://larc-tsukuba.github.io/tsumugi/" target="_blank">
        <img src="https://raw.githubusercontent.com/akikuno/TSUMUGI-dev/refs/heads/main/image/tsumugi-logo.jpg" alt="Tsumugi Logo" width="80%">
    </a>
</p>

[![License](https://img.shields.io/badge/License-MIT-9cf.svg)](https://choosealicense.com/licenses/mit/)
[![Test](https://img.shields.io/github/actions/workflow/status/akikuno/tsumugi-dev/unit-test.yml?branch=main&label=Test&color=brightgreen)](https://github.com/akikuno/tsumugi-dev/actions)
[![PyPI](https://img.shields.io/pypi/v/tsumugi.svg?label=PyPI&color=orange)](https://pypi.org/project/tsumugi/)
[![Bioconda](https://img.shields.io/conda/v/bioconda/tsumugi?label=Bioconda&color=orange)](https://anaconda.org/bioconda/tsumugi)
[![Preprint](https://img.shields.io/badge/bioRxiv-10.64898/2026.02.18.706720-red)](https://doi.org/10.64898/2026.02.18.706720)
[![DOI](https://zenodo.org/badge/441025227.svg)](https://doi.org/10.5281/zenodo.14957711)
[![Contact](https://img.shields.io/badge/Contact-923DE2)](https://forms.gle/ME8EJZZHaRNgKZ979)

**TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification)** nutzt KO-Maus-Phänotypdaten des [IMPC](https://www.mousephenotype.org/), um **genetische Module basierend auf phänotypischer Ähnlichkeit zu extrahieren und zu visualisieren**.  
Online für alle nutzbar 👇️  
🔗https://larc-tsukuba.github.io/tsumugi/

Diese Dokumentation beschreibt den aktuellen Stand von **TSUMUGI v1.2.0**. Die öffentliche Webanwendung verwendet IMPC-Daten aus **Release 24.0**.

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
> Werden keine ähnlichen Gene gefunden: `No similar phenotypes were found among the entered genes.`
> Gene List akzeptiert höchstens 200 verschiedene verfügbare Gene. Duplikate und Leerzeilen werden vor dem Zählen entfernt; nicht verfügbare Symbole werden gemeldet und ausgeschlossen. Eine Liste mit mindestens 201 verfügbaren Genen wird abgelehnt, bevor Netzwerkdaten geladen werden.

### 📥 Rohdaten herunterladen
TSUMUGI veröffentlicht gzip-komprimierte JSONL.

#### `genewise_phenotype_annotations.jsonl.gz`
- Gen-Symbol (z. B. "1110059G10Rik")  
- Marker accession ID (z. B. "MGI:1913452")  
- Phänotypname/-ID (z. B. "fused joints", "MP:0000137")  
- Effect size (`number` oder `null`; z. B. 0.0, 1.324)
- Signifikanzflag (`true` für eine IMPC-Annotation eines abweichenden Phänotyps; `false` für eine zugeordnete Messung ohne signifikante Abnormalität)
- Zygosität („Homo“, „Hetero“, „Hemi“)  
- Lebensphase („Embryo“, „Early“, „Interval“, „Late“)  
- Geschlechtsdimorphismus (`None`, `Male`, `Female`)
- Krankheitsannotation (z. B. [] oder „Premature Ovarian Failure 18“)

Beispiel:
```
{"significant": true, "sexual_dimorphism": "Female", "effect_size": 0.0119677350763567, "marker_symbol": "4930447C04Rik", "zygosity": "Homo", "marker_accession_id": "MGI:1923051", "mp_term_id": "MP:0000063", "disease_annotation": ["Male Infertility With Azoospermia Or Oligozoospermia Due To Single Gene Mutation", "Premature Ovarian Failure 18", "Spermatogenic Failure 52"], "life_stage": "Early", "mp_term_name": "decreased bone mineral density"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- Genpaar (`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations` (MICA-Kontexte mit übereinstimmenden Metadaten: MP-Term, Lebensphase, Zygosität, Geschlechtslabel)
- `phenotype_similarity_score` (Phenodigm-Score, 0–100)

Beispiel:
```
{"gene1_symbol": "1500009L16Rik", "gene2_symbol": "Aak1", "phenotype_shared_annotations": [{"mp_term_name": "increased circulating enzyme level", "life_stage": "Early", "zygosity": "Homo", "sexual_dimorphism": "None"}], "phenotype_similarity_score": 47}
```

## Hinweise zur Interpretation

- **Gemeinsame Kontexte:** Jeder Eintrag in `phenotype_shared_annotations` ist der informativste gemeinsame Vorfahr (MICA) zweier signifikanter MP-Annotationen, deren Zygosität, Lebensphase und Geschlechtslabel übereinstimmen. Dies bedeutet nicht zwingend, dass beide Gene denselben direkt annotierten terminalen MP-Term besitzen. Derselbe MICA kann bei unterschiedlichen Metadaten als getrennter Kontext erscheinen.
- **Anzeigeregeln:** Gene- und Phänotypseiten zeigen Genpaare mit mindestens drei gemeinsamen abnormalen Phänotypkontexten und einem Ähnlichkeitsscore über 0. Die Gene-List-Seite benötigt unter den eingegebenen Genen mindestens einen gemeinsamen Kontext. Dies sind Anzeigeregeln und keine Kriterien statistischer Signifikanz.
- **Ähnlichkeitsanzeige:** Der verteilte `phenotype_similarity_score` ist ein Phenodigm-Score von 0–100. Die Webanwendung skaliert die im jeweiligen Netzwerk vorhandenen Werte auf 1–100; Slider- und Tooltip-Werte verschiedener Seiten sind daher nicht als gemeinsame absolute Skala vergleichbar.
- **Effect-size-Anzeige:** TSUMUGI verwendet den Absolutbetrag des IMPC-Effect-size, wendet `log1p` an und skaliert die Werte für den Zielphänotyp auf 1–100. Dieser Wert zeigt nur die Rangfolge innerhalb der Seite, ist nicht der rohe Effect-size und ist nicht zwischen Phänotypseiten vergleichbar. Fehlende Werte bleiben JSON-`null` und werden weiß dargestellt.
- **Module:** Module sind visuelle Gruppen und kein Nachweis für einen molekularen Signalweg oder Proteinkomplex. `Similarity` bezeichnet verbundene Komponenten, `Top-level MP` ontologiebasierte Gruppen; die weichen/fuzzy Module der Gene-Seite erlauben mehrere Mitgliedschaften. Der Filter nach Modul-Knotenzahl begrenzt nur die angezeigten Module.
- **Geschlechtslabel:** `Female` bedeutet, dass nur der P-Wert des weiblichen KO-Effekts ≤ 0.0001 ist; `Male` bedeutet dasselbe für den männlichen KO-Effekt. Die Optionen schließen sich in der Weboberfläche aus und ersetzen keinen formalen Test der Geschlecht×Genotyp-Interaktion.
- **Phänotyp-Highlights:** Metadatenvarianten desselben Phänotyps werden zu einer Option zusammengefasst. Überlappen Human Disease und ein oder mehrere Phänotyp-Highlights bei einem Gen, erscheinen die Kategorien als konzentrische Ringe.
- **Krankheits-Highlights:** Annotationen aus dem IMPC Disease Models Portal sind Evidenz für Modellähnlichkeit und begründen allein keinen kausalen Zusammenhang zwischen menschlichem Gen und Krankheit.
- **Nicht signifikante Datensätze:** Sie bezeichnen eine zugeordnete Messung ohne signifikante abnorme Annotation unter der jeweiligen Bedingung. Sie beweisen weder Normalität noch das Fehlen des Phänotyps; `disease_annotation` bleibt dabei leer.
- **Bedeutung des Scores:** Der TSUMUGI-Score ist weder P-Wert noch Effect-size, Bindungsaffinität oder Evidenz für eine kausale Geninteraktion.

# 🌐 Netzwerk

Die Seite wechselt und zeichnet das Netzwerk automatisch basierend auf der Eingabe.

> [!IMPORTANT]
> Gene- und Phänotypseiten zeigen Paare mit mindestens drei gemeinsamen abnormalen Phänotypkontexten und einem Ähnlichkeitsscore über 0; die Gene-List-Seite benötigt unter den eingegebenen Genen mindestens einen gemeinsamen Kontext. Dies sind Anzeigeregeln und keine Kriterien statistischer Signifikanz.

### Netzwerk-Panel
**Knoten** repräsentieren Gene. Klick: Liste der anomalen Phänotypen; Drag: Position ändern.  
**Kanten**: Klick für Details der geteilten Phänotypen.
**Module** umrahmen Gen-Subnetzwerke. Klick: Phänotypen der Modul-Gene anzeigen; Drag: Module verschieben und Überlappungen vermeiden.
Gen-Seiten verwenden weiche/fuzzy Top-level-MP-Module, sodass ein Gen mehreren Modulen angehören kann. Phänotyp- und Gene-List-Seiten können zwischen verbundenen `Similarity`-Modulen und `Top-level MP`-Modulen wechseln.

### Kontroll-Panel
Anzeige im linken Panel anpassen.

#### Nach phänotypischer Ähnlichkeit filtern
`Phenotypes similarity` filtert Kanten nach dem angezeigten Ähnlichkeitswert. Der verteilte `phenotype_similarity_score` reicht von 0–100, wird aber für jedes angezeigte Netzwerk auf 1–100 skaliert; Werte verschiedener Seiten sind nicht direkt vergleichbar.
> Details: 👉 [🔍 Berechnung ähnlicher Gen-Gruppen](#-berechnung-ähnlicher-gen-gruppen)

#### Nach Effect size filtern
`Effect size` filtert Knoten nach einem seitenspezifischen Anzeigewert. TSUMUGI verwendet den Absolutbetrag des IMPC-Effect-size, wendet `log1p` an und skaliert die Werte des Zielphänotyps auf 1–100. Dies ist eine Ranghilfe innerhalb der Seite, nicht der rohe Effect-size, und nicht zwischen Phänotypseiten vergleichbar.
Fehlende effect sizes werden in JSONL als standardkonformes JSON `null` serialisiert, bleiben semantisch fehlend statt in den Zahlenwert 0 konvertiert zu werden und erscheinen als weiße Knoten.
> Ausgeblendet bei binären Phänotypen (z. B. abnormal embryo development; binäre Liste [hier](https://github.com/larc-tsukuba/tsumugi/blob/main/data/binary_phenotypes.txt)) oder Single-Gene-Eingabe.

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
#### Modulanzeige
Im rechten Panel können Moduldefinition und sichtbares Modul gewählt werden. Modulrahmen lassen sich ausblenden, ohne Gene oder Kanten aus dem Netzwerk zu entfernen.

#### Highlight: Phenotype
Hebt Gene anhand ihrer Phänotypannotation hervor. Metadatenvarianten desselben Phänotyps werden zu einer Option zusammengefasst. Wenn Human Disease und mindestens ein Phänotyp-Highlight bei einem Gen überlappen, werden die Kategorien als konzentrische Ringe dargestellt.

#### Highlight: Human Disease
Hebt KO-Gene mit Krankheitsmodell-Annotationen im IMPC Disease Models Portal hervor. Diese Annotation belegt Modellähnlichkeit und begründet allein keinen kausalen Zusammenhang zwischen menschlichem Gen und Krankheit.

#### Search: Specific Gene
Gene im Netzwerk suchen.

#### Layout & Display
Layout, Schriftgröße, Kantendicke, Knotenabstoßung (Cose) anpassen.

#### Export
Export als PNG, JPG, SVG, CSV oder GraphML. Modulrahmen können in PNG-, JPG- und SVG-Dateien aufgenommen werden. CSV enthält die aktive Similarity- oder Top-level-MP-Modulzuordnung und Phänotyp-Listen; GraphML ist Cytoscape-kompatibel.

# 🛠 Kommandozeilen-Interface

Die TSUMUGI-CLI ermöglicht die lokale Nutzung der neuesten IMPC-Daten und bietet feinere Filter und Ausgaben als das Web-Tool.

## Funktionen

- Neu berechnen mit IMPC `statistical-results-ALL.csv.gz` (optional `mp.obo`, `impc_phenodigm.csv`).  
- Nach signifikanten MP-Annotationen oder zugeordneten nicht signifikanten Messdatensätzen filtern.
- Filtern nach Genliste (kommagetrennt oder Textdatei).  
- Ausgaben: GraphML (`tsumugi build-graphml`), Offline-Webapp-Bundle (`tsumugi build-webapp`).

## Installation

BioConda:
```bash
conda install -c conda-forge -c bioconda tsumugi
```

PyPI:
```bash
pip install tsumugi
```

Bereit, wenn `tsumugi --version` die Version ausgibt.

## Verfügbare Befehle

- `tsumugi run`: Netzwerk aus IMPC-Daten neu berechnen  
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: Genpaare oder Gene anhand signifikanter MP-Annotationen oder zugeordneter nicht signifikanter Messdatensätze filtern
- `tsumugi count --pairwise/--genewise (--min/--max)`: Nach Phänotyp-Anzahl filtern (Paare/Gene)  
- `tsumugi score (--min/--max)`: Nach Ähnlichkeitsscore filtern (Paare)  
- `tsumugi genes --keep/--drop`: Nach Genliste behalten/verwerfen (Komma oder Textdatei)  
- `tsumugi life-stage --keep/--drop`: Nach Lebensphase filtern (Embryo/Early/Interval/Late)  
- `tsumugi sex --keep/--drop`: Nach Geschlecht filtern (Male/Female/None)  
- `tsumugi zygosity --keep/--drop`: Nach Zygosität filtern (Homo/Hetero/Hemi)  
- `tsumugi build-graphml`: GraphML erzeugen (Cytoscape, etc.)  
- `tsumugi build-webapp`: TSUMUGI-Webapp-Assets erzeugen (lokales HTML/CSS/JS)

> [!NOTE]
> Alle Filter-Subcommands schreiben JSONL nach STDOUT.  
> Mit `>` umleiten, wenn du in eine Datei speichern möchtest.

> [!IMPORTANT]
> Alle Befehle außer `tsumugi run` benötigen entweder `pairwise_similarity_annotations.jsonl.gz` oder `genewise_phenotype_annotations.jsonl.gz`.
> Beide Dateien können von der [TSUMUGI-Startseite](https://larc-tsukuba.github.io/tsumugi/) heruntergeladen werden.

## Verwendung

### Neu berechnen aus IMPC-Daten (`tsumugi run`)
Wenn `--mp_obo` weggelassen wird, nutzt TSUMUGI das mitgelieferte `data-version: releases/2025-08-27/mp.obo`.  
Wenn `--impc_phenodigm` weggelassen wird, nutzt es die am 2025-10-01 vom [IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/) bezogene Datei.
```bash
tsumugi run   --output_dir ./tsumugi-output   --statistical_results ./statistical-results-ALL.csv.gz   --threads 8
```
Ausgaben: `./tsumugi-output` enthält genewise-Annotationen (genewise_phenotype_annotations.jsonl.gz), pairwise-Ähnlichkeitsdaten (pairwise_similarity_annotations.jsonl.gz) und Visualisierungs-Assets (`TSUMUGI-webapp`).

> [!IMPORTANT]  
> Das Verzeichnis `TSUMUGI-webapp` enthält OS-spezifische Startskripte; doppelklicken, um die lokale Webapp zu öffnen:  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### Nach MP-Begriff filtern (`tsumugi mp --include/--exclude`)
Extrahiert Genpaare (oder Gene), die interessierende Phänotypen enthalten, oder Paare, bei denen diese gemessen wurden, aber keine signifikanten Anomalien vorlagen.

```bash
tsumugi mp [-h] (-i MP_ID | -e MP_ID) (-g | -p) [-m PATH_MP_OBO] [-a PATH_GENEWISE_ANNOTATIONS] [--in PATH_PAIRWISE_ANNOTATIONS]
                  [--life_stage LIFE_STAGE] [--sex SEX] [--zygosity ZYGOSITY]
```

#### `-i MP_ID`, `--include MP_ID`
Schließt Gene/Paare mit dem angegebenen MP-Begriff ein (inkl. Nachfolger).

#### `-e MP_ID`, `--exclude MP_ID`
Gibt Gene/Paare zurück, die für den MP-Begriff (inkl. Nachfolger) gemessen wurden, aber keinen signifikanten Phänotyp zeigten. `-a/--genewise_annotations` erforderlich.

> [!CAUTION]
> Ein nicht signifikanter Datensatz beweist weder, dass das Tier normal ist, noch dass der Phänotyp fehlt. Er besagt nur, dass die zugeordnete Messung unter dieser Bedingung keine signifikante abnorme Annotation ergab.

#### `-g`, `--genewise`
Filter auf Genebene. Liest `genewise_phenotype_annotations.jsonl(.gz)`. Bei `--genewise` `-a/--genewise_annotations` angeben.

#### `-p`, `--pairwise`
Filter auf Paar-Ebene. Ziel: `pairwise_similarity_annotations.jsonl(.gz)`. Wenn `--in` fehlt, wird STDIN gelesen.

#### `-m PATH_MP_OBO`, `--mp_obo PATH_MP_OBO`
Pfad zur Mammalian-Phenotype-Ontologie (mp.obo). Wenn weggelassen, wird `data/mp.obo` verwendet.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Pfad zur genewise-Annotationsdatei (JSONL/.gz). Erforderlich für `--exclude`; auch bei `--genewise` angeben.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Pfad zur pairwise-Annotationsdatei (JSONL/.gz). Wenn weggelassen, wird STDIN gelesen.

#### `--life_stage LIFE_STAGE`
Zusatzfilter nach Lebensphase. Werte: `Embryo`, `Early`, `Interval`, `Late`.

#### `--sex SEX`
Zusatzfilter nach Sexualdimorphismus. Verwende Werte aus den Annotationen (z. B. `Male`, `Female`, `None`).

#### `--zygosity ZYGOSITY`
Zusatzfilter nach Zygosität. Werte: `Homo`, `Hetero`, `Hemi`.

```bash
# Nur Genpaare extrahieren, die MP:0001146 (abnormal testis morphology) oder Nachfolger enthalten (z. B. MP:0004849 abnormal testis size)
tsumugi mp --include MP:0001146   --pairwise   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_filtered.jsonl

# Paare extrahieren, bei denen MP:0001146 und Nachfolger gemessen wurden, ohne signifikante Anomalie
tsumugi mp --exclude MP:0001146   --pairwise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_without_significant_testis_phenotype.jsonl

# Signifikante Annotationen auf Genebene mit MP:0001146 (inkl. Nachfolger)
tsumugi mp --include MP:0001146   --genewise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > genewise_filtered.jsonl

# Gene extrahieren, die für MP:0001146 (inkl. Nachfolger) gemessen wurden, ohne signifikante Anomalie
tsumugi mp --exclude MP:0001146   --genewise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > genewise_no_phenotype.jsonl
```

> [!IMPORTANT]
> **Nachfolgerterme der angegebenen MP-ID werden ebenfalls berücksichtigt.**  
> Zum Beispiel werden bei `MP:0001146 (abnormal testis morphology)` auch Nachfolger wie `MP:0004849 (abnormal testis size)` einbezogen.

### Nach Phänotyp-Anzahl filtern (`tsumugi count`)
```bash
tsumugi count [-h] (-g | -p) [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS] [-a PATH_GENEWISE_ANNOTATIONS]
```

Filtert Gene oder Paare nach der Anzahl der Phänotypen. Mindestens `--min` oder `--max` ist erforderlich.

#### `-g`, `--genewise`
Filtert nach der Anzahl signifikanter Phänotypen pro Gen. Erfordert `-a/--genewise_annotations` mit `genewise_phenotype_annotations.jsonl(.gz)`.

#### `-p`, `--pairwise`
Filtert nach der Anzahl gemeinsamer Phänotypen pro Paar. Wenn `--in` fehlt, wird von STDIN gelesen.

#### `--min MIN`, `--max MAX`
Untere/obere Grenze der Phänotyp-Anzahl. Eine Grenze reicht für einseitiges Filtern.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Pfad zur pairwise-Annotationsdatei (JSONL/.gz). Wenn weggelassen, wird STDIN gelesen.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Pfad zur genewise-Annotationsdatei (JSONL/.gz). Erforderlich mit `--genewise`.

- Gemeinsame Phänotypen pro Paar:
```bash
tsumugi count --pairwise --min 3 --max 20   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_min3_max20.jsonl
```

- Phänotypen pro Gen (genewise erforderlich):
```bash
tsumugi count --genewise --min 5 --max 50   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_genes_with_5_to_50_phenotypes.jsonl
```

`--min` oder `--max` allein ist möglich.

### Nach Ähnlichkeitsscore filtern (`tsumugi score`)
```bash
tsumugi score [-h] [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS]
```

Filtert Genpaare nach `phenotype_similarity_score` (0–100). Mindestens `--min` oder `--max` ist erforderlich.

#### `--min MIN`, `--max MAX`
Untere/obere Grenze des Scores. Eine Grenze reicht für einseitiges Filtern.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Pfad zur pairwise-Annotationsdatei (JSONL/.gz). Wenn weggelassen, wird STDIN gelesen.

```bash
tsumugi score --min 50 --max 80   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_score50_80.jsonl
```

`--min` oder `--max` allein ist möglich.

### Nach Genliste filtern (`tsumugi genes --keep/--drop`)
```bash
tsumugi genes [-h] (-k GENE_SYMBOL | -d GENE_SYMBOL) (-g | -p) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k GENE_SYMBOL`, `--keep GENE_SYMBOL`
Behält nur Paare, die die angegebenen Gene aus einer Textdatei enthalten.

#### `-d GENE_SYMBOL`, `--drop GENE_SYMBOL`
Entfernt Paare, die die angegebenen Gene aus einer Textdatei enthalten.

#### `-g`, `--genewise`
Filtert nach vom Nutzer angegebenen Gensymbolen.

#### `-p`, `--pairwise`
Filtert nach vom Nutzer angegebenen Genpaaren.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Pfad zur pairwise-Annotationsdatei (JSONL/.gz). Wenn weggelassen, wird STDIN gelesen.

```bash
cat << EOF > genes.txt
Maf
Aamp
Cacna1c
EOF

tsumugi genes --genewise --keep genes.txt   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_keep_genes.jsonl

cat << EOF > gene_pairs.csv
Maf,Aamp
Maf,Cacna1c
EOF

tsumugi genes --pairwise --drop gene_pairs.csv   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_drop_genes.jsonl

```

### Nach Lebensphase filtern (`tsumugi life-stage --keep/--drop`)
```bash
tsumugi life-stage [-h] (-k LIFE_STAGE | -d LIFE_STAGE) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k LIFE_STAGE`, `--keep LIFE_STAGE`
Behält nur die angegebene Lebensphase (`Embryo`, `Early`, `Interval`, `Late`).

#### `-d LIFE_STAGE`, `--drop LIFE_STAGE`
Entfernt die angegebene Lebensphase.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Pfad zur pairwise-Annotationsdatei (JSONL/.gz). Wenn weggelassen, wird STDIN gelesen.

```bash
tsumugi life-stage --keep Early   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_lifestage_early.jsonl
```

### Nach Geschlecht filtern (`tsumugi sex --keep/--drop`)
```bash
tsumugi sex [-h] (-k SEX | -d SEX) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k SEX`, `--keep SEX`
Behält nur das angegebene Geschlecht (`Male`, `Female`, `None`).

#### `-d SEX`, `--drop SEX`
Entfernt das angegebene Geschlecht.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Pfad zur pairwise-Annotationsdatei (JSONL/.gz). Wenn weggelassen, wird STDIN gelesen.

```bash
tsumugi sex --drop Male   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_no_male.jsonl
```

### Nach Zygosität filtern (`tsumugi zygosity --keep/--drop`)
```bash
tsumugi zygosity [-h] (-k ZYGOSITY | -d ZYGOSITY) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k ZYGOSITY`, `--keep ZYGOSITY`
Behält nur die angegebene Zygosität (`Homo`, `Hetero`, `Hemi`).

#### `-d ZYGOSITY`, `--drop ZYGOSITY`
Entfernt die angegebene Zygosität.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Pfad zur pairwise-Annotationsdatei (JSONL/.gz). Wenn weggelassen, wird STDIN gelesen.

```bash
tsumugi zygosity --keep Homo   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_homo.jsonl
```

### GraphML / Webapp exportieren
```bash
tsumugi build-graphml [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Pfad zur pairwise-Annotationsdatei (JSONL/.gz). Wenn weggelassen, wird STDIN gelesen.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Pfad zur genewise-Annotationsdatei (JSONL/.gz). Erforderlich.

```bash
tsumugi build-graphml   --in pairwise_similarity_annotations.jsonl.gz   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > network.graphml
```

```bash
tsumugi build-webapp [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS -o OUT
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Pfad zur pairwise-Annotationsdatei (JSONL/.gz). Wenn weggelassen, wird STDIN gelesen.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Pfad zur genewise-Annotationsdatei (JSONL/.gz). Erforderlich.

#### `-o OUT`, `--out OUT`
Ausgabeverzeichnis des Webapp-Bundles (HTML/CSS/JS + Netzwerkdaten). Kein Dateiname mit Endung angeben.

```bash
tsumugi build-webapp   --in pairwise_similarity_annotations.jsonl.gz   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   --out ./webapp_output
```

Die CLI unterstützt STDIN/STDOUT, sodass du Befehle verketten kannst:  
`tsumugi score --min 50 --in pairwise_similarity_annotations.jsonl.gz | tsumugi sex --drop Male > pairwise_score50_no_male.jsonl`

# 🔍 Berechnung ähnlicher Gen-Gruppen

## Datenquelle

Wir verwenden den IMPC-Datensatz [Release 24.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-24.0/results) `statistical-results-ALL.csv.gz`.
Spalten des Datensatzes: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)  

## Vorverarbeitung

TSUMUGI behandelt einen nicht leeren IMPC-`mp_term_id` als IMPC-Annotation eines abweichenden Phänotyps. Zugeordnete Messungen ohne signifikante abnorme Annotation bleiben für messungsbezogene Ausschlussabfragen erhalten.
Für nicht signifikante Messungen wird jeder ontologisch spezifischste Nicht-Root-Term aus `intermediate_mp_term_id`, der mit den anderen ausgewählten Termen nicht vergleichbar ist, als eigener Datensatz ausgegeben. Messungen, die nur `MP:0000001` oder keinen gültigen MP-Term enthalten, werden nicht ausgegeben, da sie keine phänotypspezifische Abfrage unterstützen.

- Zygosität wird in `Homo`, `Hetero` oder `Hemi` umgewandelt.
- `Female` wird vergeben, wenn nur `female_ko_effect_p_value` ≤ 0.0001 ist, und `Male`, wenn nur `male_ko_effect_p_value` ≤ 0.0001 ist; andernfalls `None`.
- Verwendet wird der Absolutbetrag des Effect-size. Fehlende Werte bleiben fehlend und werden in JSON als `null` ausgegeben.

## Phänotypische Ähnlichkeit

TSUMUGI wendet die ursprüngliche PhenoDigm-Bewertungsformel ([Smedley D, et al. (2013)](https://doi.org/10.1093/database/bat025)) auf den Vergleich von Phänotypprofilen von IMPC-KO-Mausgenen innerhalb der Mammalian Phenotype Ontology an.

> [!NOTE]
> TSUMUGI verwendet die PhenoDigm-Bewertungsformel, führt aber nicht die ursprüngliche artenübergreifende HPO-MP/ZP-OWLSim-Pipeline aus. Verglichen werden MP-Annotationen von IMPC-KO-Mausgenen.

### 1. Definition der MP-Term-Paar-Similarität

* Die MP-Ontologie aufbauen und den Information Content (IC) aus signifikanten IMPC-Annotationen berechnen:
   `IC(term) = -log2(|zum Term propagierte Annotationen| / |alle signifikanten Annotationen|)`
   Jede direkte Annotation wird zum annotierten MP-Term und zu allen seinen Vorfahren propagiert.

* Für jedes MP-Term-Paar die gemeinsamen Vorfahren mit dem höchsten annotationsbasierten IC bestimmen. Bei Gleichstand wird deterministisch zuerst der Kandidat mit den wenigsten transitiven Nachfahren in der MP-Ontologie und danach die lexikografisch kleinste MP-Term-ID gewählt. Der IC des ausgewählten MICA ist die Resnik-Similarität. Diese Tie-Break-Regel verändert weder den Similarity Score noch das Ausgabeschema.
   Gleichrangige Kandidaten haben denselben numerischen Termpaar-Score; das gewählte MICA-Label kann jedoch die Anzahl gemeinsamer Kontexte und damit die Anzeigeeignung verändern.

* Für zwei MP-Terme den Jaccard-Index ihrer abgeleiteten Attributmengen berechnen, definiert als der Term selbst plus alle Vorfahren.

* Die MP-Term-Paar-Similarität als `sqrt(Resnik * Jaccard)` definieren.

### 2. Genpaar-Similaritätsmatrix

* Für jedes Genpaar aus den Termpaar-Scores eine MP-Term × MP-Term-Similaritätsmatrix erstellen.

* MICA wird nur dann in `phenotype_shared_annotations` gespeichert, wenn Zygosität, Lebensphase und Geschlechtslabel übereinstimmen. Diese Metadaten gewichten den PhenoDigm-Score selbst nicht.

### 3. Phenodigm-Skalierung

* PhenoDigm-Maximum-/Durchschnittsskalierung anwenden, um die Ähnlichkeit jedes KO-Maus-Genpaars auf 0–100 zu normalisieren:
   Beobachtetes Best-Match-Maximum und -Mittel berechnen und durch den symmetrischen optimalen Self-Match-Score der beiden Gene normalisieren.
   `Score = 100 * (normalized_max + normalized_mean) / 2`  
   Wenn der Nenner 0 ist, wird der Score auf 0 gesetzt.

Der resultierende Score misst die Ähnlichkeit von Phänotypprofilen. Er ist weder P-Wert noch Effect-size, Bindungsaffinität oder Evidenz für eine kausale Interaktion zwischen Genen.

---

# ✉️ Kontakt
- Google-Formular: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose


---

# 📄 Zitation

Kuno A, Matsumoto K, Taki T, Takahashi S, and Mizuno S  
**TSUMUGI: a platform for phenotype-driven gene network identification from comprehensive knockout mouse phenotyping data**  
*bioRxiv*. (2026) https://doi.org/10.64898/2026.02.18.706720  
