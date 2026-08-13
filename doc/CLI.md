# TSUMUGI Command-Line Interface (CLI)

[Back to README](../README.md) | [日本語README](README_JP.md)

This reference documents the TSUMUGI v1.2.0 CLI. Run `tsumugi COMMAND --help` to confirm the exact syntax supported by the installed version.

The TSUMUGI CLI integrates a locally downloaded IMPC Release 24.0 statistical-results file with bundled MGI loss-of-function phenotype reports by default.

## Features

- Integrate IMPC `statistical-results-ALL.csv.gz` with bundled MGI reports (optionally override `mp.obo`, `impc_phenodigm.csv`, or the MGI reports).
- Filter by significant MP annotations or measured non-significant records.
- Filter by a gene-symbol file or a CSV/TSV gene-pair file.
- Outputs: source-aware genewise annotations and pairwise phenotype similarities. Legacy IMPC-only output, GraphML, and a local webapp remain available with `--no-integrate-mgi`.

## Installation

TSUMUGI requires Python 3.10 or later.

BioConda:
```bash
conda install -c conda-forge -c bioconda tsumugi
```

PyPI:
```bash
pip install tsumugi
```

You are ready if `tsumugi --version` prints the version.

## Available commands

- `tsumugi run`: Integrate IMPC and MGI annotations and compute pairwise similarity
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: Filter gene pairs or genes by significant MP annotations or measured non-significant records
- `tsumugi count --pairwise/--genewise (--min/--max)`: Filter by phenotype counts (pairwise or per gene)
- `tsumugi score (--min/--max)`: Filter by phenotype similarity score (pairwise)
- `tsumugi genes --keep/--drop`: Keep/drop using a gene-symbol file or CSV/TSV gene-pair file
- `tsumugi life-stage --keep/--drop`: Filter by life stage (Embryo/Early/Interval/Late)
- `tsumugi sex --keep/--drop`: Filter by sex (Male/Female/None)
- `tsumugi zygosity --keep/--drop`: Filter by zygosity (Homo/Hetero/Hemi)
- `tsumugi build-graphml`: Generate GraphML (Cytoscape, etc.)
- `tsumugi build-webapp`: Generate TSUMUGI webapp assets (local HTML/CSS/JS)

> [!NOTE]
> All filtering subcommands stream JSONL to STDOUT.
> Redirect with `>` if you want to save results to a file.

> [!IMPORTANT]
> Filtering and export commands use `pairwise_similarity_annotations.jsonl.gz`, `genewise_phenotype_annotations.jsonl.gz`, or both, depending on the command.
> Both files can be downloaded from the [TSUMUGI top page](https://larc-tsukuba.github.io/tsumugi/). Run `tsumugi COMMAND --help` for the exact inputs.


## Usage

### Integrate IMPC and MGI data (`tsumugi run`)
If `--mp_obo` is omitted, TSUMUGI uses the bundled `data-version: releases/2026-07-22/mp.obo`.
If `--impc_phenodigm` is omitted, it uses the file fetched on 2025-10-01 from the [IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/).
If the three MGI report options are omitted, TSUMUGI uses the bundled snapshot documented in the [data provenance inventory](../src/TSUMUGI/data/README.md). The IMPC input must contain `strain_name` in the default integrated mode.
```bash
tsumugi run \
  --output_dir ./tsumugi-output \
  --statistical_results ./statistical-results-ALL.csv.gz \
  --threads 8
```
Outputs: `./tsumugi-output` contains MGI-integrated genewise annotations (`genewise_phenotype_annotations.jsonl.gz`), pairwise similarity data (`pairwise_similarity_annotations.jsonl.gz`), audit summaries, and pair shards. Web assets are not generated in this mode.

> [!IMPORTANT]
> Use `--no-integrate-mgi` for the legacy IMPC-only pipeline. That mode retains `TSUMUGI-webapp` generation and its OS-specific launch scripts:
> - Windows: `open_webapp_windows.bat`
> - macOS: `open_webapp_mac.command`
> - Linux: `open_webapp_linux.sh`

The explicit `--integrate-mgi` option remains accepted for backward compatibility. Custom snapshots can be supplied with `--mgi-gene-pheno`, `--mgi-phenotypic-allele`, and `--mgi-pheno-sex`.

#### Integrated-output semantics and limitations

- Genewise records retain `source` and `significance_basis`. MGI abnormal annotations are curated assertions, not IMPC statistical-test results; `effect_size` is `null`, and life stage is inferred where possible.
- MGI inclusion is restricted to all-background primary loss-of-function records meeting the pipeline's allele and zygosity rules. Multiple genotypes and backgrounds are aggregated to marker-level phenotype profiles; co-occurrence in one animal is not implied.
- Pairwise shared terms are MICA contexts and include `source_pairs`. Pairwise scoring uses joint information content recalculated from the integrated profiles.
- Integrated scores are not directly comparable with public-webapp or legacy IMPC-only scores because both phenotype profiles and the information-content background differ.
- Metadata-specific filtering (`life-stage`, `sex`, and `zygosity`), `build-graphml`, and `build-webapp` currently require legacy-schema output generated with `--no-integrate-mgi`.

### Filter by MP term (`tsumugi mp --include/--exclude`)
Extract gene pairs (or genes) that include phenotypes of interest, or identify measurements for which no statistically significant abnormality was recorded under the selected conditions.

```bash
tsumugi mp [-h] (-i MP_ID | -e MP_ID) (-g | -p) [-m PATH_MP_OBO] [-a PATH_GENEWISE_ANNOTATIONS] [--in PATH_PAIRWISE_ANNOTATIONS]
                  [--life_stage LIFE_STAGE] [--sex SEX] [--zygosity ZYGOSITY]
```

#### `-i MP_ID`, `--include MP_ID`
Include genes/gene pairs that have the specified MP term (descendants included).

#### `-e MP_ID`, `--exclude MP_ID`
Return genes/gene pairs with a mapped measurement for the specified MP term (related ancestor and descendant terms included) and no significant abnormal annotation under the selected metadata conditions. Requires `-a/--genewise_annotations`.

> [!CAUTION]
> A non-significant record does not prove that the animal is normal or that the phenotype is absent. It records that the mapped measurement did not produce a significant abnormal annotation under that condition.
> Each non-significant measurement is expanded to every ontology-incomparable, most-specific non-root term in `intermediate_mp_term_id`. Root-only and unmapped measurements are omitted because they cannot support phenotype-specific exclusion queries.

#### `-g`, `--genewise`
Filter at gene level. Reads `genewise_phenotype_annotations.jsonl(.gz)`. When using `--genewise`, specify `-a/--genewise_annotations`.

#### `-p`, `--pairwise`
Filter at gene-pair level. Targets `pairwise_similarity_annotations.jsonl(.gz)`. If `--in` is omitted, reads from STDIN.

#### `-m PATH_MP_OBO`, `--mp_obo PATH_MP_OBO`
Path to Mammalian Phenotype ontology (mp.obo). If omitted, uses the bundled `data/mp.obo`.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Path to the genewise annotation file (JSONL/.gz). Required for `--exclude`; also specify when using `--genewise`.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Path to the pairwise annotation file (JSONL/.gz). If omitted, reads from STDIN.

#### `--life_stage LIFE_STAGE`
Additional filter by life stage. Available values: `Embryo`, `Early`, `Interval`, `Late`.

#### `--sex SEX`
Additional filter by sexual dimorphism. Use the values present in annotations (e.g., `Male`, `Female`, `None`).

#### `--zygosity ZYGOSITY`
Additional filter by zygosity. Available values: `Homo`, `Hetero`, `Hemi`.

```bash
# Extract only gene pairs that include MP:0001146 (abnormal testis morphology) or descendant terms (e.g., MP:0004849 abnormal testis size)
tsumugi mp --include MP:0001146 \
  --pairwise \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

# Extract gene pairs whose measured genes include MP:0001146 and descendant terms and did not show a significant abnormality
tsumugi mp --exclude MP:0001146 \
  --pairwise \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_without_significant_testis_phenotype.jsonl

# Extract significant gene-level annotations containing MP:0001146 (descendants included)
tsumugi mp --include MP:0001146 \
  --genewise \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  > genewise_filtered.jsonl

# Extract genes measured for MP:0001146 (descendants included) that did not show a significant abnormality
tsumugi mp --exclude MP:0001146 \
  --genewise \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  > genewise_no_phenotype.jsonl
```

> [!IMPORTANT]
> **Descendant MP terms of the specified ID are also handled.**
> For example, if you specify `MP:0001146 (abnormal testis morphology)`, descendant terms such as `MP:0004849 (abnormal testis size)` are considered as well.

### Filter by phenotype counts (`tsumugi count`)
```bash
tsumugi count [-h] (-g | -p) [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS] [-a PATH_GENEWISE_ANNOTATIONS]
```

Filter gene pairs by a phenotype-count condition. At least one of `--min` or `--max` is required.

#### `-g`, `--genewise`
Keep pairwise records only when both genes have a number of significant phenotypes within the requested range. Requires `-a/--genewise_annotations` with `genewise_phenotype_annotations.jsonl(.gz)`.

#### `-p`, `--pairwise`
Filter by the number of shared phenotypes per gene pair. If `--in` is omitted, reads `pairwise_similarity_annotations.jsonl(.gz)` from STDIN.

#### `--min MIN`, `--max MAX`
Lower/upper bounds for phenotype counts. Use either flag alone for one-sided filtering.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Path to the pairwise annotation file (JSONL/.gz). If omitted, reads from STDIN.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Path to the genewise annotation file (JSONL/.gz). Required with `--genewise`.

- Shared phenotypes per pair:

```bash
tsumugi count --pairwise --min 3 --max 20 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_min3_max20.jsonl
```

- Gene-level counts applied to pairwise output:
```bash
tsumugi count --genewise --min 5 --max 50 \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_genes_with_5_to_50_phenotypes.jsonl
```

`--min` or `--max` alone is fine.

### Filter by similarity score (`tsumugi score`)
```bash
tsumugi score [-h] [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS]
```

Filter gene pairs by `phenotype_similarity_score` (0–100). At least one of `--min` or `--max` is required.

#### `--min MIN`, `--max MAX`
Lower/upper bounds for phenotype similarity score. Use either flag alone for one-sided filtering.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Path to the pairwise annotation file (JSONL/.gz). If omitted, reads from STDIN.

```bash
tsumugi score --min 50 --max 80 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_score50_80.jsonl
```

`--min` or `--max` alone is fine.

### Filter by gene list (`tsumugi genes --keep/--drop`)
```bash
tsumugi genes [-h] (-k GENE_SYMBOL | -d GENE_SYMBOL) (-g | -p) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k GENE_SYMBOL`, `--keep GENE_SYMBOL`
Keep only pairs containing specified genes in a text file.

#### `-d GENE_SYMBOL`, `--drop GENE_SYMBOL`
Drop pairs containing specified genes in a text file.

####  `-g, --genewise`
Read one gene symbol per non-empty line.

####  `-p, --pairwise`
Read one gene pair per non-empty line, separated by a comma or tab.


#### `--in PATH_PAIRWISE_ANNOTATIONS`
Path to the pairwise annotation file (JSONL/.gz). If omitted, reads from STDIN.

```bash
cat << EOF > genes.txt
Maf
Aamp
Cacna1c
EOF

tsumugi genes --genewise --keep genes.txt \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_keep_genes.jsonl

cat << EOF > gene_pairs.csv
Maf,Aamp
Maf,Cacna1c
EOF

tsumugi genes --pairwise --drop gene_pairs.csv \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_drop_genes.jsonl

```

### Filter by life stage (`tsumugi life-stage --keep/--drop`)
```bash
tsumugi life-stage [-h] (-k LIFE_STAGE | -d LIFE_STAGE) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k LIFE_STAGE`, `--keep LIFE_STAGE`
Keep only annotations with the specified life stage (`Embryo`, `Early`, `Interval`, `Late`).

#### `-d LIFE_STAGE`, `--drop LIFE_STAGE`
Drop annotations with the specified life stage.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Path to the pairwise annotation file (JSONL/.gz). If omitted, reads from STDIN.

```bash
tsumugi life-stage --keep Early \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_lifestage_early.jsonl
```

### Filter by sex (`tsumugi sex --keep/--drop`)
```bash
tsumugi sex [-h] (-k SEX | -d SEX) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k SEX`, `--keep SEX`
Keep only annotations with the specified sexual dimorphism (`Male`, `Female`, `None`).

#### `-d SEX`, `--drop SEX`
Drop annotations with the specified sexual dimorphism.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Path to the pairwise annotation file (JSONL/.gz). If omitted, reads from STDIN.

```bash
tsumugi sex --drop Male \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_no_male.jsonl
```

### Filter by zygosity (`tsumugi zygosity --keep/--drop`)
```bash
tsumugi zygosity [-h] (-k ZYGOSITY | -d ZYGOSITY) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k ZYGOSITY`, `--keep ZYGOSITY`
Keep only annotations with the specified zygosity (`Homo`, `Hetero`, `Hemi`).

#### `-d ZYGOSITY`, `--drop ZYGOSITY`
Drop annotations with the specified zygosity.

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Path to the pairwise annotation file (JSONL/.gz). If omitted, reads from STDIN.

```bash
tsumugi zygosity --keep Homo \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_homo.jsonl
```

### Export GraphML / webapp
```bash
tsumugi build-graphml [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Path to the pairwise annotation file (JSONL/.gz). If omitted, reads from STDIN.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Path to the genewise annotation file (JSONL/.gz). Required.

```bash
tsumugi build-graphml \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  > network.graphml
```

```bash
tsumugi build-webapp [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS -o OUT
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
Path to the pairwise annotation file (JSONL/.gz). If omitted, reads from STDIN.

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
Path to the genewise annotation file (JSONL/.gz). Required.

#### `-o OUT`, `--out OUT`
Output directory for the webapp bundle (HTML/CSS/JS + network data). Do not specify a filename with an extension.

```bash
tsumugi build-webapp \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  --out ./webapp_output
```

`build-webapp` accepts at most 150 nodes. Use `build-graphml` for larger networks. The generated bundle is served locally by the included launcher, but it loads Cytoscape.js, noUiSlider, pako, fonts, and icons from external content delivery networks; an internet connection is therefore required unless those resources are already cached or vendored separately.

CLI supports STDIN/STDOUT, so you can chain commands:
`tsumugi score --min 50 --in pairwise_similarity_annotations.jsonl.gz | tsumugi sex --drop Male > pairwise_score50_no_male.jsonl`
