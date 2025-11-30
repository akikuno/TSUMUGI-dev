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

### 1. Phenotype
Enter a phenotype of interest to search for **genes whose KO mice have similar overall phenotype profiles**.  
Phenotype names follow [Mammalian Phenotype Ontology (MPO)](https://www.informatics.jax.org/vocab/mp_ontology).

👉 [Phenotype list](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### 2. Gene
Specify one gene to search for **other genes whose KO mice show similar phenotypes**.  
Gene symbols follow [MGI](http://www.informatics.jax.org/).

👉 [Gene list](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)

### 3. Gene List
Paste multiple genes (one per line). This extracts phenotypically similar genes **among the genes in the list**.

> [!CAUTION]  
> If no similar genes are found: `No similar phenotypes were found among the entered genes.`  
> If more than 200 similar genes are found: `Too many genes submitted. Please limit the number to 200 or fewer.`

### 📥 Download raw data
TSUMUGI publishes gzipped JSONL files.

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
- `phenotype_similarity_score` (Resnik-based Phenodigm score, 0–100)

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
- `tsumugi n-phenos --pairwise/--genewise (--min/--max)`: Filter by phenotype counts (pairwise or per gene)  
- `tsumugi genes --keep/--drop`: Keep/drop by gene list (comma-separated or text file)  
- `tsumugi life-stage --keep/--drop`: Filter by life stage (Embryo/Early/Interval/Late)  
- `tsumugi sex --keep/--drop`: Filter by sex (Male/Female/None)  
- `tsumugi zygosity --keep/--drop`: Filter by zygosity (Homo/Hetero/Hemi)  
- `tsumugi build-graphml`: Generate GraphML (Cytoscape, etc.)  
- `tsumugi build-webapp`: Generate TSUMUGI webapp assets (local HTML/CSS/JS)

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

### 1. Recompute from IMPC data (`tsumugi run`)
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

### 2. Filter by MP term (`tsumugi mp --include/--exclude`)
Extract only gene pairs that include phenotypes of interest, or pairs whose relevant phenotypes were measured but did not show significant abnormalities.

- `--pairwise` (default if neither is set): outputs gene pairs. Provide `--in pairwise_similarity_annotations.jsonl(.gz)`.
- `--genewise`: outputs individual genes. Provide `--genewise_annotations genewise_phenotype_annotations.jsonl(.gz)` (required for `--exclude`, recommended for `--include`).

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

### 3. Filter by phenotype counts (`tsumugi n-phenos`)
- Shared phenotypes per pair:
```bash
tsumugi n-phenos --pairwise --min 3 --max 20 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_min3_max20.jsonl
```
- Phenotypes per gene (genewise required):
```bash
tsumugi n-phenos --genewise --min 5 --max 50 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > genewise_min5_max50.jsonl
```
`--min` or `--max` alone is fine.

### 4. Filter by gene list (`tsumugi genes --keep/--drop`)
```bash
tsumugi genes --keep genes.txt \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_keep_genes.jsonl

tsumugi genes --drop geneA,geneB \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_drop_genes.jsonl
```

### 5. Filter by life stage (`tsumugi life-stage --keep/--drop`)
```bash
tsumugi life-stage --keep Early \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_lifestage_early.jsonl
```

### 6. Filter by sex (`tsumugi sex --keep/--drop`)
```bash
tsumugi sex --drop Male \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_no_male.jsonl
```

### 7. Filter by zygosity (`tsumugi zygosity --keep/--drop`)
```bash
tsumugi zygosity --keep Homo \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_homo.jsonl
```

### 8. Export GraphML / webapp
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
TSUMUGI computes **Resnik similarity** between MP terms and rescales pairwise gene scores to **Phenodigm (0–100)**.

1. Build the MP ontology and compute Information Content (IC):  
   `IC(term) = -log((|Descendants(term)| + 1) / |All MP terms|)`  
2. Resnik(t1, t2) = IC of the most informative common ancestor (MICA); if no common ancestor, similarity = 0.  
3. For each gene pair, create a matrix of significant MP terms and weight each Resnik score by metadata match (zygosity / life stage / sex) with factors 1.0 / 0.75 / 0.5 / 0.25. Take row/column maxima to obtain the **actual** max and mean similarity observed.  
4. Derive **theoretical** max and mean from IC values of the terms, then normalize:  
   `Phenodigm = 100 * 0.5 * ( actual_max / theoretical_max + actual_mean / theoretical_mean )`  
   If a theoretical denominator is 0, set that term to 0. The resulting 0–100 score feeds the downloadable tables and the `Phenotypes similarity` slider.

# ✉️ Contact
- Google Form: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose
