<p align="center">
    <a href="https://larc-tsukuba.github.io/tsumugi/" target="_blank">
        <img src="image/tsumugi-logo.jpg" alt="Tsumugi Logo" width="80%">
    </a>
</p>

[![License](https://img.shields.io/badge/License-MIT-9cf.svg)](https://choosealicense.com/licenses/mit/)
[![Test](https://img.shields.io/github/actions/workflow/status/akikuno/tsumugi/pytest.yml?branch=main&label=Test&color=brightgreen)](https://github.com/akikuno/tsumugi/actions)
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
👉 [Phenotype List](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### 2. Gene

When you specify a single gene, TSUMUGI searches for **other gene groups whose KO mice have similar phenotype profiles** to that gene's KO mice.  
Gene names follow gene symbols registered in [MGI](http://www.informatics.jax.org/).

List of currently searchable gene names in TSUMUGI:  
👉 [Gene List](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)

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

### 📥 Raw Data Download

TSUMUGI publishes Gzip-compressed JSONL files that capture the curated phenotype knowledge.

#### `genewise_phenotype_annotations.jsonl.gz`

Gene-wise phenotype annotations. Each JSON line contains:

- Gene symbol and marker accession ID (e.g., `"1110059G10Rik"`, `"MGI:1913452"`)
- Mammalian Phenotype term name and ID
- Absolute effect size and significance flag
- Zygosity (`Homo`, `Hetero`, `Hemi`)
- Life stage (`Embryo`, `Early`, `Interval`, `Late`)
- Sexual dimorphism label (`""`, `Male`, `Female`)
- Disease annotations mapped from the IMPC Phenodigm resource

Example:

```
{"life_stage": "Early", "marker_symbol": "1110059G10Rik", "marker_accession_id": "MGI:1913452", "effect_size": 0.0, "mp_term_name": "fused joints", "disease_annotation": [], "significant": false, "zygosity": "Homo", "sexual_dimorphism": "", "mp_term_id": "MP:0000137"}
```

#### `pairwise_similarity_annotations.jsonl.gz`

Phenotypic similarity statistics for every gene pair. Fields:

- `gene1_symbol` / `gene2_symbol`
- `phenotype_shared_annotations`: phenotype names keyed to metadata (life stage, zygosity, sexual dimorphism)
- `phenotype_similarity_score`: Resnik-based Phenodigm score on a 0–100 scale

Example:

```
{"gene1_symbol": "1110059G10Rik", "gene2_symbol": "Cog6", "phenotype_shared_annotations": {"vertebral transformation": {"zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "Male"}}, "phenotype_similarity_score": 42}
```

> [!NOTE]
> Files are tens of megabytes. When loading them with `pandas`, `polars`, or similar tools, prefer streaming (e.g., iterating line by line) to avoid exhausting memory.

## 🌐 Network Visualization

Based on the input, the page transitions and the network is automatically drawn.  

> [!IMPORTANT]
> **Gene pairs with 3 or more shared abnormal phenotypes and phenotypic similarity scores of 0 or higher** are visualized.  

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

The `Phenotypes similarity` slider allows you to set thresholds for gene pairs displayed in the network based on **edge phenotypic similarity** (Resnik-based Phenodigm score).  

> [!NOTE]
> For details on phenotypic similarity, please see:  
> 👉 [🔍 Calculation Method for Phenotypically Similar Gene Groups](https://github.com/akikuno/TSUMUGI-dev#-calculation-method-for-phenotypically-similar-gene-groups)

#### Filter by Phenotype Severity

The `Phenotype severity` slider allows you to adjust node display based on **phenotype severity (effect size) in KO mice**.  
Higher effect sizes indicate stronger phenotypic impact.  

> [!NOTE]
> When IMPC phenotype evaluation is binary (present/absent) (e.g., [abnormal embryo development](https://larc-tsukuba.github.io/tsumugi/app/phenotype/abnormal_embryo_development.html): list of binary phenotypes available [here](https://github.com/larc-tsukuba/tsumugi/blob/main/data/binary_phenotypes.txt)) or when gene name is input, the `Phenotypes severity` slider is not available.

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

TSUMUGI now evaluates phenotypic similarity with **Resnik similarity** between Mammalian Phenotype (MP) terms and converts pairwise gene scores to a **Phenodigm scale (0-100)**.

### 1. Resnik Similarity Between Phenotype Terms

For each MP term, TSUMUGI builds the ontology hierarchy and computes its Information Content (IC) from the proportion of descendants (including the term itself) within the ontology:

```
IC(term) = -log( (|Descendants(term)| + 1) / |All MP terms| )
```

Given two MP terms, all common ancestors are identified and the Resnik similarity is defined as the IC of the **most informative common ancestor (MICA)**:

```
Resnik(term_1, term_2) = max_{c in intersection(Anc(term_1), Anc(term_2))} IC(c)
```

If the two terms do not share any ancestor, the similarity is 0.

### 2. Phenodigm Scaling for Gene Pairs

1. For every pair of genes, TSUMUGI creates a weighted similarity matrix whose entries are Resnik scores between their significant MP terms. Each cell is further scaled by metadata agreement (zygosity, life stage, sexual dimorphism) with weights of 1.0, 0.75, 0.5, or 0.25 depending on how many attributes match.  
2. Row-wise and column-wise maxima provide the **actual** maximum and average similarity observed between the two genes.  
3. Using the IC values of the individual terms, TSUMUGI derives **theoretical** maxima (best possible max and average) for the same pair.  
4. The Phenodigm score is obtained by normalizing the actual scores with the theoretical ones and averaging the normalized max and mean:

```
Phenodigm = 100 * 0.5 * ( actual_max / theoretical_max + actual_mean / theoretical_mean )
```

When the theoretical denominator is zero, the corresponding normalized value is set to zero. The resulting 0-100 score feeds both the downloadable tables and the `Phenotypes similarity` slider in the web UI.

# ✉️ Contact

For questions or requests, please feel free to contact us:

- **Google Form**  
  👉 [Contact Form](https://forms.gle/ME8EJZZHaRNgKZ979)

- **For GitHub account holders**  
  👉 [GitHub Issue](https://github.com/akikuno/TSUMUGI-dev/issues/new/choose)
