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

Translations: [日本語](https://github.com/akikuno/TSUMUGI-dev/blob/main/doc/README_JP.md) | [한국어](https://github.com/akikuno/TSUMUGI-dev/blob/main/doc/README_KR.md) | [简体中文](https://github.com/akikuno/TSUMUGI-dev/blob/main/doc/README_ZH_CN.md) | [繁體中文](https://github.com/akikuno/TSUMUGI-dev/blob/main/doc/README_ZH_TW.md) | [हिन्दी](https://github.com/akikuno/TSUMUGI-dev/blob/main/doc/README_HI.md) | [Bahasa Indonesia](https://github.com/akikuno/TSUMUGI-dev/blob/main/doc/README_ID.md) | [Tiếng Việt](https://github.com/akikuno/TSUMUGI-dev/blob/main/doc/README_VN.md) | [Español](https://github.com/akikuno/TSUMUGI-dev/blob/main/doc/README_ES.md) | [Français](https://github.com/akikuno/TSUMUGI-dev/blob/main/doc/README_FR.md) | [Deutsch](https://github.com/akikuno/TSUMUGI-dev/blob/main/doc/README_DE.md) | [Português](https://github.com/akikuno/TSUMUGI-dev/blob/main/doc/README_PT.md)

**TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification)** is a web tool that uses knockout (KO) mouse phenotype data from the [International Mouse Phenotyping Consortium (IMPC)](https://www.mousephenotype.org/) to **extract and visualize gene modules based on phenotypic similarity**.  

**TSUMUGI (紡ぎ)** comes from the idea of “weaving together gene groups that form phenotypes.”

This web app is available to everyone online👇️  

🔗https://larc-tsukuba.github.io/tsumugi/

# 📖 How to Use TSUMUGI

TSUMUGI supports three kinds of input.

### Phenotype
Enter a phenotype of interest to search for **genes whose KO mice have similar overall phenotype profiles**.  
Phenotype names follow [Mammalian Phenotype Ontology (MPO)](https://www.informatics.jax.org/vocab/mp_ontology).

👉 [Phenotype list](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### Gene
Specify one gene to search for **other genes whose KO mice show similar phenotypes**.  
Gene symbols follow [MGI](http://www.informatics.jax.org/).

👉 [Gene list](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)

### Gene List
Paste multiple genes (one per line). This extracts phenotypically similar genes **among the genes in the list**.

> [!CAUTION]  
> If no similar genes are found: `No similar phenotypes were found among the entered genes.`  
> If more than 200 similar genes are found: `Too many genes submitted. Please limit the number to 200 or fewer.`

### 📥 Download data

TSUMUGI reports gzipped JSONL files.

#### `genewise_phenotype_annotations.jsonl.gz`
- Gene symbol (e.g., "1110059G10Rik")  
- Marker accession ID (e.g., "MGI:1913452")  
- Phenotype term name/ID (e.g., "fused joints", "MP:0000137")  
- Effect size (e.g., 0.0, 1.324)  
- Significance flag (true/false)  
- Zygosity ("Homo", "Hetero", "Hemi")  
- Life stage ("Embryo", "Early", "Interval", "Late")  
- Sexual dimorphism ("None", "Male", "Female")  
- Disease annotation (e.g., [] or "Premature Ovarian Failure 18")

Example:
```
{"life_stage": "Early", "marker_symbol": "1110059G10Rik", "marker_accession_id": "MGI:1913452", "effect_size": 0.0, "mp_term_name": "fused joints", "disease_annotation": [], "significant": false, "zygosity": "Homo", "sexual_dimorphism": "None", "mp_term_id": "MP:0000137"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- Gene pair (`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations` (per-phenotype metadata: life stage, zygosity, sexual dimorphism)  
- `phenotype_similarity_score` (Phenodigm score, 0–100)

Example:
```
{"gene1_symbol": "1110059G10Rik", "gene2_symbol": "Cog6", "phenotype_shared_annotations": {"vertebral transformation": {"zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "Male"}}, "phenotype_similarity_score": 42}
```

# 🌐 Network

The page transitions and draws the network automatically.

> [!IMPORTANT]  
> Gene pairs with **3 or more shared abnormal phenotypes** and **phenotypic similarity > 0.0** are visualized.

### Network panel
**Nodes** represent genes. Click to see the list of abnormal phenotypes observed in that KO mouse; drag to rearrange positions.  
**Edges** show shared phenotypes; click to view details.
**Modules** outline subnetworks of genes. Click a module to list phenotypes involving its member genes; drag modules to reposition them and avoid overlap.

### Control panel
Adjust network display from the left panel.

#### Filter by phenotypic similarity
`Phenotypes similarity` slider thresholds edges by Resnik→Phenodigm score.  
> For how we compute similarity, see: 👉 [🔍 How We Calculate Phenotypically Similar Genes](#-how-we-calculate-phenotypically-similar-genes)

#### Filter by phenotype severity
`Phenotype severity` slider filters nodes by effect size (severity in KO mice). Higher values mean stronger impact.  
> Hidden for binary phenotypes (e.g., [abnormal embryo development](https://larc-tsukuba.github.io/tsumugi/app/phenotype/abnormal_embryo_development.html); binary list [here](https://github.com/larc-tsukuba/tsumugi/blob/main/data/binary_phenotypes.txt)) or single-gene input.

#### Specify genotype
Choose the genotype in which phenotypes appear:
- `Homo`: homozygous
- `Hetero`: heterozygous
- `Hemi`: hemizygous

#### Specify sex
Extract sex-specific phenotypes:
- `Female`
- `Male`

#### Specify life stage
Filter by life stage in which phenotypes appear:
- `Embryo`
- `Early` (0–16 weeks)
- `Interval` (17–48 weeks)
- `Late` (49+ weeks)

### Markup panel

#### Highlight: Human Disease
Highlight genes linked to human disease (IMPC Disease Models Portal data).

#### Search: Specific Gene
Search gene names within the network.

#### Layout & Display
Adjust layout, font size, edge width, and node repulsion (Cose layout).

#### Export
Export the current network as PNG/CSV/GraphML.  
CSV includes connected-component (module) IDs and phenotype lists per gene; GraphML is Cytoscape-compatible.

# 🛠 Command-Line Edition

This release adds a CLI so you can download the latest IMPC updates yourself, rerun TSUMUGI, and apply finer filters and output options.

- Recompute with IMPC `statistical-results-ALL.csv.gz` (optionally `mp.obo`, `impc_phenodigm.csv`).  
- Filter by presence/absence of MP terms.  
- Filter by gene list (comma-separated or text file).  
- Outputs: GraphML (`tsumugi build-graphml`), offline webapp bundle (`tsumugi build-webapp`).

## Available commands
- `tsumugi run`: Recompute the network from IMPC data  
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: Filter gene pairs or genes that contain / do not show an MP term  
- `tsumugi count --pairwise/--genewise (--min/--max)`: Filter by phenotype counts (pairwise or per gene)  
- `tsumugi score (--min/--max)`: Filter by phenotype similarity score (pairwise)  
- `tsumugi genes --keep/--drop`: Keep/drop by gene list (comma-separated or text file)  
- `tsumugi life-stage --keep/--drop`: Filter by life stage (Embryo/Early/Interval/Late)  
- `tsumugi sex --keep/--drop`: Filter by sex (Male/Female/None)  
- `tsumugi zygosity --keep/--drop`: Filter by zygosity (Homo/Hetero/Hemi)  
- `tsumugi build-graphml`: Generate GraphML (Cytoscape, etc.)  
- `tsumugi build-webapp`: Generate TSUMUGI webapp assets (local HTML/CSS/JS)

All filtering subcommands stream JSONL to STDOUT. Redirect with `>` if you want to save results to a file.

## Installation

BioConda:
```bash
conda install -c conda-forge -c bioconda tsumugi
```

PyPI:
```bash
pip install tsumugi
```

You are ready if `tsumugi --version` prints the version.

## Usage

### Recompute from IMPC data (`tsumugi run`)
If `--mp_obo` is omitted, TSUMUGI uses the bundled `data-version: releases/2025-08-27/mp.obo`.  
If `--impc_phenodigm` is omitted, it uses the file fetched on 2025-10-01 from the [IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/).
```bash
tsumugi run \
  --output_dir ./tsumugi-output \
  --statistical_results ./statistical-results-ALL.csv.gz \
  --threads 8
```
Outputs: `./tsumugi-output` contains genewise annotations (genewise_phenotype_annotations.jsonl.gz), pairwise similarity data (pairwise_similarity_annotations.jsonl.gz), and visualization assets (`TSUMUGI-webapp`).

> [!IMPORTANT]  
> The `TSUMUGI-webapp` directory includes OS-specific launch scripts; double-click to open the local web app:  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### Filter by MP term (`tsumugi mp --include/--exclude`)
Extract gene pairs (or genes) that include phenotypes of interest, or pairs whose relevant phenotypes were measured but did not show significant abnormalities.

```txt
tsumugi mp [-h] (-i MP_ID | -e MP_ID) [-g | -p] [-m MP_OBO] [-a GENEWISE_ANNOTATIONS] [--in IN] [--life_stage LIFE_STAGE] [--sex SEX] [--zygosity ZYGOSITY]
```

#### `-i MP_ID`, `--include MP_ID`
Include genes/gene pairs that have the specified MP term (descendants included).

#### `-e MP_ID`, `--exclude MP_ID`
Return genes/gene pairs that were measured for the specified MP term (descendants included) and did **not** show a significant phenotype. Requires `-a/--genewise_annotations`.

#### `-g`, `--genewise`
Filter at gene level. Reads `genewise_phenotype_annotations.jsonl(.gz)`. When using `--genewise`, specify `-a/--genewise_annotations`.

#### `-p`, `--pairwise`
Filter at gene-pair level. Targets `pairwise_similarity_annotations.jsonl(.gz)`. If `--in` is omitted, reads from STDIN.

#### `-m MP_OBO`, `--mp_obo MP_OBO`
Path to Mammalian Phenotype ontology (mp.obo). If omitted, uses the bundled `data/mp.obo`.

#### `-a GENEWISE_ANNOTATIONS`, `--genewise_annotations GENEWISE_ANNOTATIONS`
Path to the genewise annotation file (JSONL/.gz). Required for `--exclude`; also specify when using `--genewise`.

#### `--in IN`
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
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

# Extract gene pairs whose measured genes include MP:0001146 and descendant terms and did not show a significant abnormality
tsumugi mp --exclude MP:0001146 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

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
```txt
tsumugi count [-h] (-g | -p) [--min MIN] [--max MAX] [--in IN] [-a GENEWISE_ANNOTATIONS]
```

Filter genes or gene pairs by the number of phenotypes. At least one of `--min` or `--max` is required.

#### `-g`, `--genewise`
Filter by the number of significant phenotypes per gene. Requires `-a/--genewise_annotations` with `genewise_phenotype_annotations.jsonl(.gz)`.

#### `-p`, `--pairwise`
Filter by the number of shared phenotypes per gene pair. If `--in` is omitted, reads `pairwise_similarity_annotations.jsonl(.gz)` from STDIN.

#### `--min MIN`, `--max MAX`
Lower/upper bounds for phenotype counts. Use either flag alone for one-sided filtering.

#### `--in IN`
Path to the pairwise annotation file (JSONL/.gz). If omitted, reads from STDIN.

#### `-a GENEWISE_ANNOTATIONS`, `--genewise_annotations GENEWISE_ANNOTATIONS`
Path to the genewise annotation file (JSONL/.gz). Required with `--genewise`.

- Shared phenotypes per pair:
```bash
tsumugi count --pairwise --min 3 --max 20 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_min3_max20.jsonl
```
- Phenotypes per gene (genewise required):
```bash
tsumugi count --genewise --min 5 --max 50 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > genewise_min5_max50.jsonl
```
`--min` or `--max` alone is fine.

### Filter by similarity score (`tsumugi score`)
```txt
tsumugi score [-h] [--min MIN] [--max MAX] [--in IN]
```

Filter gene pairs by `phenotype_similarity_score` (0–100). At least one of `--min` or `--max` is required.

#### `--min MIN`, `--max MAX`
Lower/upper bounds for phenotype similarity score. Use either flag alone for one-sided filtering.

#### `--in IN`
Path to the pairwise annotation file (JSONL/.gz). If omitted, reads from STDIN.

```bash
tsumugi score --min 50 --max 80 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_score50_80.jsonl
```

`--min` or `--max` alone is fine.

### Filter by gene list (`tsumugi genes --keep/--drop`)
```txt
tsumugi genes [-h] (-k GENE_SYMBOL | -d GENE_SYMBOL) [--in IN]
```

#### `-k GENE_SYMBOL`, `--keep GENE_SYMBOL`
Keep only pairs containing specified genes (comma-separated list or text file).

#### `-d GENE_SYMBOL`, `--drop GENE_SYMBOL`
Drop pairs containing specified genes (comma-separated list or text file).

#### `--in IN`
Path to the pairwise annotation file (JSONL/.gz). If omitted, reads from STDIN.

```bash
tsumugi genes --keep genes.txt \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_keep_genes.jsonl

tsumugi genes --drop geneA,geneB \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_drop_genes.jsonl
```

### Filter by life stage (`tsumugi life-stage --keep/--drop`)
```txt
tsumugi life-stage [-h] (-k LIFE_STAGE | -d LIFE_STAGE) [--in IN]
```

#### `-k LIFE_STAGE`, `--keep LIFE_STAGE`
Keep only annotations with the specified life stage (`Embryo`, `Early`, `Interval`, `Late`).

#### `-d LIFE_STAGE`, `--drop LIFE_STAGE`
Drop annotations with the specified life stage.

#### `--in IN`
Path to the pairwise annotation file (JSONL/.gz). If omitted, reads from STDIN.

```bash
tsumugi life-stage --keep Early \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_lifestage_early.jsonl
```

### Filter by sex (`tsumugi sex --keep/--drop`)
```txt
tsumugi sex [-h] (-k SEX | -d SEX) [--in IN]
```

#### `-k SEX`, `--keep SEX`
Keep only annotations with the specified sexual dimorphism (`Male`, `Female`, `None`).

#### `-d SEX`, `--drop SEX`
Drop annotations with the specified sexual dimorphism.

#### `--in IN`
Path to the pairwise annotation file (JSONL/.gz). If omitted, reads from STDIN.

```bash
tsumugi sex --drop Male \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_no_male.jsonl
```

### Filter by zygosity (`tsumugi zygosity --keep/--drop`)
```txt
tsumugi zygosity [-h] (-k ZYGOSITY | -d ZYGOSITY) [--in IN]
```

#### `-k ZYGOSITY`, `--keep ZYGOSITY`
Keep only annotations with the specified zygosity (`Homo`, `Hetero`, `Hemi`).

#### `-d ZYGOSITY`, `--drop ZYGOSITY`
Drop annotations with the specified zygosity.

#### `--in IN`
Path to the pairwise annotation file (JSONL/.gz). If omitted, reads from STDIN.

```bash
tsumugi zygosity --keep Homo \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_homo.jsonl
```

### Export GraphML / webapp
```txt
tsumugi build-graphml [-h] [--in IN] -a GENEWISE_ANNOTATIONS
```

#### `--in IN`
Path to the pairwise annotation file (JSONL/.gz). If omitted, reads from STDIN.

#### `-a GENEWISE_ANNOTATIONS`, `--genewise_annotations GENEWISE_ANNOTATIONS`
Path to the genewise annotation file (JSONL/.gz). Required.

```bash
tsumugi build-graphml \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  > network.graphml
```

```txt
tsumugi build-webapp [-h] [--in IN] -a GENEWISE_ANNOTATIONS -o OUT
```

#### `--in IN`
Path to the pairwise annotation file (JSONL/.gz). If omitted, reads from STDIN.

#### `-a GENEWISE_ANNOTATIONS`, `--genewise_annotations GENEWISE_ANNOTATIONS`
Path to the genewise annotation file (JSONL/.gz). Required.

#### `-o OUT`, `--out OUT`
Output directory for the webapp bundle (HTML/CSS/JS + network data). Do not specify a filename with an extension.

```bash
tsumugi build-webapp \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --output_dir ./webapp_output
```

CLI supports STDIN/STDOUT, so you can chain commands:  
`zcat pairwise_similarity_annotations.jsonl.gz | tsumugi mp ... | tsumugi genes ... > out.jsonl`

# 🔍 How We Calculate Phenotypically Similar Genes

## Data source
[IMPC Release-23.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-23.0/results) `statistical-results-ALL.csv.gz`  
Columns: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)

## Preprocessing
Extract gene–phenotype pairs with KO mouse P-value (`p_value`, `female_ko_effect_p_value`, or `male_ko_effect_p_value`) ≤ 0.0001.  
- Annotate genotype-specific phenotypes: `homo`, `hetero`, `hemi`  
- Annotate sex-specific phenotypes: `female`, `male`

## Phenotypic similarity
TSUMUGI currently follows a **Phenodigm-like** approach ([Smedley D, et al. (2013)](https://doi.org/10.1093/database/bat025)). We compute **Resnik similarity** between MP terms and **Jaccard similarity** between term sets, then combine them by the **geometric mean**. The key difference from the original Phenodigm is that TSUMUGI adds **metadata weighting** (zygosity, life stage, sexual dimorphism) when aggregating similarities.

1. Build the MP ontology and compute Information Content(IC) for each term:  
   `IC(term) = -log((|Descendants(term)| + 1) / |All MP terms|)`  
   Terms below the 5th percentile of IC are set to 0.
2. For each MP term pair, find the most specific common ancestor and compute Resnik similarity as its IC.  
   Compute Jaccard index over the ancestor sets.  
   Pairwise term similarity = `sqrt(Resnik * Jaccard)`.
3. For each gene pair, build a term-by-term similarity matrix and apply metadata weighting.  
   Zygosity, life stage, and sexual dimorphism matches contribute weights of 0.25/0.5/0.75/1.0 for 0/1/2/3 matches.
4. Apply Phenodigm-style scaling to 0–100:  
   Use row/column maxima to get actual max and mean similarity.  
   Normalize by theoretical max/mean based on IC, then compute  
   `Score = 100 * (normalized_max + normalized_mean) / 2`.  
   If a theoretical denominator is 0, that term is set to 0.


# ✉️ Contact
- Google Form: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose
