<p align="center">
    <a href="https://larc-tsukuba.github.io/tsumugi/" target="_blank">
        <img src="image/tsumugi-logo.jpg" alt="Tsumugi Logo" width="80%">
    </a>
</p>

[![License](https://img.shields.io/badge/License-MIT-9cf.svg)](https://choosealicense.com/licenses/mit/)
[![DOI](https://zenodo.org/badge/441025227.svg)](https://doi.org/10.5281/zenodo.14957711)
[![Contact](https://img.shields.io/badge/Contact-923DE2)](https://forms.gle/ME8EJZZHaRNgKZ979)


[日本語版 README はこちら](https://github.com/akikuno/TSUMUGI-dev/blob/main/doc/README_JP.md)

**TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification)** is a web tool that leverages knockout (KO) mouse phenotype data from the [International Mouse Phenotyping Consortium (IMPC)](https://www.mousephenotype.org/) to **extract and visualize gene modules based on phenotypic similarity**.

The tool is publicly available online for anyone to use 👇️  

🔗 https://larc-tsukuba.github.io/tsumugi/

**TSUMUGI** derives from the Japanese concept of "weaving together gene groups that form phenotypes."


# 📖 How to Use TSUMUGI

## 💬 Top Page

TSUMUGI supports three types of input:

### 1. Phenotype

When you input a phenotype of interest, TSUMUGI searches for **gene groups with similar overall phenotype profiles** among genes whose KO mice exhibit that phenotype.  
Phenotype names are based on [Mammalian Phenotype Ontology (MPO)](https://www.informatics.jax.org/vocab/mp_ontology).

List of currently searchable phenotypes in TSUMUGI:  
👉 [Phenotype List](https://github.com/akikuno/TSUMUGI-dev/blob/main/TSUMUGI/data/available_mp_terms.txt)

### 2. Gene

When you specify a single gene, TSUMUGI searches for **other gene groups whose KO mice have similar phenotype profiles** to that gene's KO mice.  
Gene names follow gene symbols registered in [MGI](http://www.informatics.jax.org/).

List of currently searchable gene names in TSUMUGI:  
👉 [Gene List](https://github.com/akikuno/TSUMUGI-dev/blob/main/TSUMUGI/data/available_gene_symbols.txt)

### 3. Gene List

Accepts input of multiple genes.  
Gene lists should be entered separated by line breaks.  

> [!NOTE]
> Gene List differs from single Gene input in that it extracts phenotypically similar genes **among the genes within the list**.

> [!CAUTION]
> **If no phenotypically similar genes are found**,
> `No similar phenotypes were found among the entered genes.` alert will be displayed and processing will stop.
>
> **If phenotypically similar genes exceed 200**,
> `Too many genes submitted. Please limit the number to 200 or fewer.` alert will be displayed and processing will stop to prevent browser overload.

### 📥 Raw Data Download (`TSUMUGI_{version}_raw_data`)

You can download raw data of phenotypic similarity between gene pairs (in Gzip-compressed CSV format or Parquet format).  

Contents include:  

- Paired gene names (Gene1, Gene2)
- Phenotypic similarity between pairs (Phenodigm Score)
- Phenotypic similarity between pairs (Jaccard Similarity)
- Number of shared phenotypes between pairs (Number of shared phenotype)
- List of shared phenotypes between pairs (List of shared phenotype)

> [!CAUTION]
> File size is approximately 50-100MB. Download may take some time.

We recommend using Parquet format when working with `Polars` or `Pandas`.  
You can load the data as follows:  

#### Polars

```bash
# Install Polars and PyArrow using conda
conda create -y -n env-tsumugi polars pyarrow
conda activate env-tsumugi
```

```python
# Load Parquet file using Polars
import polars as pl
df_tsumugi = pl.read_parquet("TSUMUGI_{version}_raw_data.parquet")
```

#### Pandas

```bash
# Install Pandas and PyArrow using conda
conda create -y -n env-tsumugi pandas pyarrow
conda activate env-tsumugi
```

```python
# Load Parquet file using Pandas
import pandas as pd
df_tsumugi = pd.read_parquet("TSUMUGI_{version}_raw_data.parquet")
```

## 🌐 Network Visualization

Based on the input, the page transitions and the network is automatically drawn.  

> [!IMPORTANT]
> **Gene pairs with 2 or more shared abnormal phenotypes AND Phenodigm score of 25 or higher** are subject to visualization.  

### Network Panel

#### Nodes (Points)

Each node represents one gene.  
Clicking displays a list of abnormal phenotypes observed in that gene's KO mice.  
You can freely adjust positions by dragging.  

#### Edges (Lines)

Clicking an edge shows details of shared phenotypes.  

### Control Panel

The left control panel allows you to adjust network display.  

#### Filter by Phenotypic Similarity

The `Phenotypes similarity` slider allows you to set thresholds for gene pairs displayed in the network based on **edge phenotypic similarity** (Phenodigm score).  
Similarity minimum and maximum values are converted to a 1-10 scale, allowing 10-level filtering.  
Note that the Phenodigm score values are log-transformed for ensuring a more uniform distribution.

> [!NOTE]
> For details on phenotypic similarity, please see:  
> 👉 [🔍 Calculation Method for Phenotypically Similar Gene Groups](https://github.com/akikuno/TSUMUGI-dev#-method-for-identifying-phenotypically-similar-gene-groups)

#### Filter by Phenotype Severity

The `Phenotype severity` slider allows you to adjust node display based on **phenotype severity (effect size) in KO mice**.  
Higher effect sizes indicate stronger phenotypic impact.  
This also scales the effect size range to 1-10, allowing 10-level filtering.  
Note that for non-binary phenotypes, effect size values are log-transformed for ensuring a more uniform distribution.  

> [!NOTE]
> When IMPC phenotype evaluation is binary (present/absent) (e.g., [abnormal embryo development](https://larc-tsukuba.github.io/tsumugi/app/phenotype/abnormal_embryo_development.html): list of binary phenotypes available [here](https://github.com/akikuno/TSUMUGI-dev/blob/main/TSUMUGI/data/binary_phenotypes.txt)) or when gene name is input, the `Phenotypes severity` slider is not available.

#### Specify Genotype

You can specify the genotype of KO mice exhibiting phenotypes:

- `Homo`: Phenotypes seen in homozygous mice
- `Hetero`: Phenotypes seen in heterozygous mice
- `Hemi`: Phenotypes seen in hemizygous mice

#### Specify Sex

You can extract sex-specific phenotypes:

- `Female`: Female-specific phenotypes
- `Male`: Male-specific phenotypes

#### Specify Life Stage

You can specify life stages when phenotypes appear:

- `Embryo`: Phenotypes appearing during embryonic stage
- `Early`: Phenotypes appearing at 0-16 weeks of age
- `Interval`: Phenotypes appearing at 17-48 weeks of age
- `Late`: Phenotypes appearing at 49+ weeks of age

### Markup Panel

#### Highlight Human Disease-Related Genes (Highlight: Human Disease)

You can highlight genes related to human diseases.  
The relationship between KO mice and human diseases uses public data from [IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/).  

#### Search Gene Names (Search: Specific Gene)

You can search for gene names included in the network.

#### Adjust Network Display Style (Layout & Display)

You can adjust the following elements:

- Network layout (layout)
- Font size (Font size)
- Edge thickness (Edge width)
- Distance between nodes (*Cose layout only) (Node repulsion)

#### Export

You can export current network images and data in PNG, CSV and GraphML formats.  
CSV includes connected component (module) IDs and lists of phenotypes shown by each gene's KO mice.  
GraphML is a format compatible with the desktop version of Cytoscape, allowing you to import the network into Cytoscape for further analysis.  


# 🔍 Calculation Method for Phenotypically Similar Gene Groups

## Data Source

IMPC dataset uses `statistical-results-ALL.csv.gz` from [Release-23.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-23.0/results).  
Information about columns included in the dataset: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)  

## Preprocessing

Extract gene-phenotype pairs where KO mouse phenotype P-values (`p_value`, `female_ko_effect_p_value`, or `male_ko_effect_p_value`) are 0.0001 or below.  
- Genotype-specific phenotypes are annotated with `homo`, `hetero`, or `hemi`
- Sex-specific phenotypes are annotated with `female` or `male`

## Phenotypic Similarity Calculation

TSUMUGI uses two complementary metrics to calculate phenotypic similarity between gene pairs:

### 1. Phenodigm Score

The **[Phenodigm](https://pmc.ncbi.nlm.nih.gov/articles/PMC3649640/)** is an advanced method for calculating phenotypic similarity that considers the semantic similarity between phenotype terms based on the Mammalian Phenotype (MP) ontology structure. This algorithm was originally developed for cross-species phenotype comparison and has been adapted for comparing KO mouse phenotypes.

#### Key Features:

- **Semantic Similarity**: Uses Resnik similarity based on Information Content (IC) to measure the relatedness of phenotype terms
- **Annotation Weighting**: Considers experimental conditions (genotype, sex, life stage) when calculating similarity
- **Asymmetric Scoring**: Accounts for differences in phenotype set sizes between genes

#### Algorithm Overview:

1. **Information Content Calculation**: For each MP term, calculate IC based on its frequency in the ontology:
   ```
   IC(term) = -log(P(term))
   ```
   where P(term) is the probability of observing the term or its descendants

2. **Pairwise Phenotype Similarity**: For each phenotype pair, calculate weighted Resnik similarity:
   - Base similarity: IC of the Most Informative Common Ancestor (MICA)
   - Apply annotation weight based on matching experimental conditions:
     - All 3 annotations match (genotype, sex, life stage): 1.0x
     - 2 annotations match: 0.75x
     - 1 annotation matches: 0.5x
     - No annotations match: 0.25x

3. **Gene-to-Gene Similarity**: Calculate Phenodigm score between gene A and B:
   ```
   Phenodigm(A,B) = 100 × (maxSim/maxIC) × ((avgSimA/avgICA + avgSimB/avgICB)/2)
   ```
   where:
   - maxSim: Maximum similarity across all phenotype pairs
   - maxIC: Maximum IC among all phenotypes
   - avgSimA/B: Average similarity for gene A/B phenotypes
   - avgICA/B: Average IC for gene A/B phenotypes

The Phenodigm score ranges from 0 to 100, with higher scores indicating greater phenotypic similarity.

### 2. Jaccard Coefficient

As a complementary metric, TSUMUGI also uses the **Jaccard coefficient** for a simpler set-based similarity measure.  
This is a similarity measure that expresses the proportion of shared phenotypes as a 0-1 numerical value.

```
Jaccard(A, B) = |A ∩ B| / |A ∪ B|
```

For example, suppose gene A and gene B KO mice have the following abnormal phenotypes:  

```
A: {abnormal embryo development, abnormal heart morphology, abnormal kidney morphology}
B: {abnormal embryo development, abnormal heart morphology, abnormal lung morphology}
```

In this case, there are 2 shared phenotypes and 4 total unique phenotypes, so the Jaccard coefficient is calculated as follows:

```
Jaccard(A, B) = 2 / 4 = 0.5
```

## Visualization Thresholds

For network visualization, TSUMUGI applies the following criteria:
- Minimum 2 shared abnormal phenotypes between gene pairs
- Phenodigm score ≥ 25 (indicating meaningful phenotypic similarity)

This dual-threshold approach ensures that visualized gene relationships are both statistically significant and biologically meaningful.

# ✉️ Contact

For questions or requests, please feel free to contact us:

- **Google Form**  
  👉 [Contact Form](https://forms.gle/ME8EJZZHaRNgKZ979)

- **For GitHub account holders**  
  👉 [GitHub Issue](https://github.com/akikuno/TSUMUGI-dev/issues/new/choose)
