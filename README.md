<p align="center">
    <a href="https://larc-tsukuba.github.io/tsumugi/" target="_blank">
        <img src="image/tsumugi-logo.jpg" alt="Tsumugi Logo" width="80%">
    </a>
</p>

[![License](https://img.shields.io/badge/License-MIT-9cf.svg)](https://choosealicense.com/licenses/mit/)
[![DOI](https://zenodo.org/badge/441025227.svg)](https://doi.org/10.5281/zenodo.14957711)
[![Inquiry](https://img.shields.io/badge/Inquiry-923DE2)](https://forms.gle/ME8EJZZHaRNgKZ979)


[日本語はこちら](https://github.com/akikuno/TSUMUGI-dev/blob/main/doc/README_JP.md)

**TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification)** is a tool that leverages comprehensive phenotype data from single-gene knockout (KO) mice, provided by the [International Mouse Phenotyping Consortium (IMPC)](https://www.mousephenotype.org/).  
It identifies and visualizes gene modules based on **phenotypic similarity**.

TSUMUGI is available as a web-tool that anyone can access from here👇️  

🔗 https://larc-tsukuba.github.io/tsumugi/

The name **TSUMUGI** is derived from the Japanese word **紡ぎ**, symbolizing the concept of *twisting various elements (genes) together to create a unified entity (phenotype)*.  

# 📖 How to Use TSUMUGI

## 💬 Top Page

TSUMUGI accepts the following three types of input:

### 1. Phenotype

When you input a phenotype of interest, TSUMUGI searches for a group of genes whose KO mice not only exhibit that phenotype, but also share **similar overall phenotype profiles**.  
Phenotype names are based on the [Mammalian Phenotype Ontology (MPO)](https://www.informatics.jax.org/vocab/mp_ontology).

You can view the list of phenotypes currently searchable with TSUMUGI here:  
👉 [Phenotype List](https://github.com/akikuno/TSUMUGI-dev/blob/main/TSUMUGI/data/available_mp_terms.txt)


### 2. Gene

When you specify a particular gene, TSUMUGI searches for **other genes whose KO mice share similar phenotype profiles** with the KO mouse of the specified gene.  
Gene symbols follow the official nomenclature from [MGI](http://www.informatics.jax.org/).

You can view the list of gene symbols currently searchable with TSUMUGI here:  
👉 [Gene Symbol List](https://github.com/akikuno/TSUMUGI-dev/blob/main/TSUMUGI/data/available_gene_symbols.txt)

### 3. Gene List

You can input multiple genes (one per line).  
TSUMUGI calculates phenotypic similarity **between genes within the list only**.

> [!Note]
> Unlike a single gene search, the Gene List input compares phenotypes **within the listed genes** only.

> [!CAUTION]
> If **no phenotype-similar genes** are found, an alert saying
> `No similar phenotypes were found among the entered genes.` will appear, and you will not be able to proceed.
>
> If the number of phenotype-similar genes **exceeds 200**, an alert saying
> `Too many genes submitted. Please limit the number to 200 or fewer.` will appear, and the process will be stopped to prevent browser overload.

### 📥 Download Data

You can download raw data of phenotype similarities between gene pairs (CSV format, gzip-compressed).

The file includes:

- Gene pair (Gene1, Gene2)
- Phenotypic similarity score (Jaccard Similarity)
- Number of shared phenotypes
- List of shared phenotypes

> [!CAUTION]
> The file size is approximately 100MB. Downloading may take some time.


## 🌐 Network Visualization

After input is submitted, the page automatically transitions to a network view.

> [!IMPORTANT]
> **Gene pairs that share three or more abnormal phenotypes** are visualized.

### Nodes

- Each node represents a single gene.  
- Clicking a node displays the list of abnormal phenotypes observed in its KO mouse.  
- Nodes can be repositioned freely by dragging.

### Edges

- Clicking an edge reveals detailed information about the shared phenotypes between the two connected genes.

### Control Panel

The left-hand control panel allows you to adjust the appearance and content of the network.

#### Change Network Layout

You can choose from the following layout options:

- Cose (default)  
- Circle  
- Random  
- Grid  
- Concentric

#### Filter by Phenotype Similarity

The `Phenotypes similarity` slider lets you filter **gene pairs** based on their phenotypic similarity (Jaccard index).  
The similarity scores are scaled to a range of 1 to 10, allowing filtering in 10 steps.

#### Filter by Phenotype Severity

The `Phenotypes severity` slider allows you to filter **nodes** based on phenotype severity in KO mice.  
Higher severity scores indicate stronger phenotypic effects.  
This score is also scaled from 1 to 10 for 10-step filtering.

> [!NOTE]
> The severity slider is not available if the phenotype data from IMPC is binary (e.g., [abnormal embryo development](https://larc-tsukuba.github.io/tsumugi/app/phenotype/abnormal_embryo_development.html)) or if the input consists of a single gene.

#### Adjust Network Appearance

The following visual properties can be adjusted:

- Font size  
- Edge thickness  
- Node repulsion (distance between nodes; applicable to Cose layout only)

#### Search Gene

You can search for specific gene names within the network.

#### Specify Genotype

You can restrict results to phenotypes observed in KO mice with a specific genotype:

- `Homo`: Homozygous  
- `Hetero`: Heterozygous  
- `Hemi`: Hemizygous

#### Specify Sex

You can extract phenotypes specific to sex:

- `Female`  
- `Male`

#### Export

You can export the current network as PNG and CSV files.  
The CSV file includes cluster (connected component) information and a list of phenotypes observed for each gene's KO mouse.

---

# 🔍 Method for Identifying Phenotypically Similar Gene Groups

## Data Source

The dataset used is [IMPC Release-22.1](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-22.1/results), specifically the `statistical-results-ALL.csv.gz` file.  
Detailed information about the data fields can be found here:  
👉 [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)

## Preprocessing

Gene–phenotype pairs were extracted where the KO mouse exhibited a phenotype with a p-value ≤ 0.0001  
(`p_value`, `female_ko_effect_p_value`, or `male_ko_effect_p_value`).

- Genotype-specific phenotypes are annotated with `homo`, `hetero`, or `hemi`.  
- Sex-specific phenotypes are annotated with `female` or `male`.

## Phenotype Similarity Calculation

Phenotypic similarity is quantified using the **Jaccard index**,  
which measures the proportion of shared phenotypes between two gene knockouts as a value between 0 and 1.

```
Jaccard(A, B) = |A ∩ B| / |A ∪ B|
```

For example, suppose KO mice of gene A and gene B exhibit the following abnormal phenotypes:

```
A: {abnormal embryo development, abnormal heart morphology, abnormal kidney morphology}
B: {abnormal embryo development, abnormal heart morphology, abnormal lung morphology}
```

In this case, there are 2 shared phenotypes and 4 unique phenotypes in total.  
The Jaccard index is calculated as follows:

```
Jaccard(A, B) = 2 / 4 = 0.5
```

# ✉️ Contact

If you have any questions or requests, feel free to contact us using one of the methods below (inquiries in Japanese are welcome):

- **Google Form**  
  👉 [Contact Form](https://forms.gle/ME8EJZZHaRNgKZ979)

- If you have a **GitHub account**  
  👉 [GitHub Issue](https://github.com/akikuno/TSUMUGI-dev/issues/new/choose)
