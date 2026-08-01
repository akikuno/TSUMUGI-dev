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

Translations: [日本語](doc/README_JP.md) | [한국어](doc/README_KR.md) | [简体中文](doc/README_ZH_CN.md) | [繁體中文](doc/README_ZH_TW.md) | [हिन्दी](doc/README_HI.md) | [Bahasa Indonesia](doc/README_ID.md) | [Tiếng Việt](doc/README_VN.md) | [Español](doc/README_ES.md) | [Français](doc/README_FR.md) | [Deutsch](doc/README_DE.md) | [Português](doc/README_PT.md)

**TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification)** is a web tool that uses knockout (KO) mouse phenotype data from the [International Mouse Phenotyping Consortium (IMPC)](https://www.mousephenotype.org/) to **extract and visualize gene modules based on phenotypic similarity**.  

**TSUMUGI (紡ぎ in Japanese)** comes from the idea of “weaving together gene groups that form phenotypes.”

This web app is available to everyone online👇️  

🔗 https://larc-tsukuba.github.io/tsumugi/

This repository documents **TSUMUGI v1.2.0**.

| Component                          | Version or data release                                         |
| ---------------------------------- | --------------------------------------------------------------- |
| Source code and CLI described here | TSUMUGI v1.2.0                                                  |
| Public web app                     | TSUMUGI v1.1.0 (verified 2026-07-31; v1.2.0 deployment pending) |
| Data used by the public web app    | IMPC Release 24.0                                               |

Archived software releases are available from [Zenodo](https://zenodo.org/records/21480711).

# 📖 How to Use TSUMUGI

TSUMUGI supports three kinds of input.

### Phenotype
Enter a phenotype of interest to search for **genes whose KO mice have similar overall phenotype profiles**.  
Phenotype names follow the [Mammalian Phenotype (MP) ontology](https://www.informatics.jax.org/vocab/mp_ontology).

👉 [Phenotype list](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### Gene
Specify one gene to search for **other genes whose KO mice show similar phenotypes**.  
Gene symbols follow [MGI](http://www.informatics.jax.org/).

👉 [Gene list](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)

### Gene List
Paste multiple genes (one per line). This extracts phenotypically similar genes **among the genes in the list**.

> [!CAUTION]  
> If no similar genes are found: `No similar phenotypes were found among the entered genes.`  
> Gene List accepts up to 200 distinct available genes. Duplicate symbols and blank lines are removed before counting.
> Unavailable symbols are reported and excluded. A list with 201 or more available genes is rejected before network data are loaded.

### 📥 Download data

TSUMUGI reports gzipped JSONL files.

#### `genewise_phenotype_annotations.jsonl.gz`

- Gene symbol (e.g., "1110059G10Rik")  
- Marker accession ID (e.g., "MGI:1913452")  
- Phenotype term name/ID (e.g., "fused joints", "MP:0000137")  
- Absolute effect size (`number` or `null`; e.g., 0.0, 1.324)
- Significance flag (`true` for an IMPC phenodeviant annotation; `false` for a mapped measurement without a significant abnormality)
- Zygosity ("Homo", "Hetero", "Hemi")  
- Life stage ("Embryo", "Early", "Interval", "Late")  
- Sexual dimorphism ("None", "Male", "Female")  
- Disease annotation (e.g., [] or "Premature Ovarian Failure 18")

Example:  
```json
{"significant": true, "sexual_dimorphism": "Female", "effect_size": 0.0119677350763567, "marker_symbol": "4930447C04Rik", "zygosity": "Homo", "marker_accession_id": "MGI:1923051", "mp_term_id": "MP:0000063", "disease_annotation": ["Male Infertility With Azoospermia Or Oligozoospermia Due To Single Gene Mutation", "Premature Ovarian Failure 18", "Spermatogenic Failure 52"], "life_stage": "Early", "mp_term_name": "decreased bone mineral density"}
```

#### `pairwise_similarity_annotations.jsonl.gz`

- Gene pair (`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations` (metadata-matched MICA contexts: MP term, life stage, zygosity, sexual dimorphism)
- `phenotype_similarity_score` (Phenodigm score, 0–100)

Each shared context is the most informative common ancestor (MICA) of two significant MP annotations whose zygosity, life stage, and sexual-dimorphism labels match. It does not necessarily mean that both genes have the same directly annotated leaf MP term. The same MICA can appear as separate contexts when its metadata differ.

Example:  
```json
{"gene1_symbol": "1500009L16Rik", "gene2_symbol": "Aak1", "phenotype_shared_annotations": [{"mp_term_name": "increased circulating enzyme level", "life_stage": "Early", "zygosity": "Homo", "sexual_dimorphism": "None"}], "phenotype_similarity_score": 47}
```

# 🌐 Network

The page transitions and draws the network automatically.

> [!IMPORTANT]  
> Gene and Phenotype pages visualize gene pairs with **3 or more shared abnormal phenotype contexts** and
> **phenotypic similarity > 0.0**. Gene List retains pairs with **1 or more shared abnormal phenotype contexts**
> among the submitted genes. These are display rules, not thresholds for statistical significance.

### Network panel
**Nodes** represent genes. Click to see the list of abnormal phenotypes observed in that KO mouse; drag to rearrange positions.  
**Edges** show shared phenotypes; click to view details.
**Modules** are visual groupings, not evidence of a molecular pathway or protein complex. Gene pages use soft/fuzzy Top-level MP modules, so one gene can belong to multiple modules. Phenotype and Gene List pages can switch between connected-component-based `Similarity` modules and ontology-based `Top-level MP` modules. Click a module to list phenotypes involving its member genes; drag modules to reposition them and avoid overlap. The module node-count filter limits the displayed modules by their number of member genes.

### Control panel
Adjust network display from the left panel.

#### Filter by phenotypic similarity
`Phenotypes similarity` filters edges by the displayed similarity value. The distributed `phenotype_similarity_score` is a 0–100 Phenodigm score. For each displayed network, the web app rescales the available scores to 1–100, so slider and tooltip values must not be compared across different pages as a common absolute scale.

> [!NOTE]
> For how we compute similarity, see: 👉 [🔍 How We Calculate Phenotypically Similar Genes](#-how-we-calculate-phenotypically-similar-genes)

#### Filter by effect size
`Effect size` filters nodes by a page-specific display value. TSUMUGI takes the absolute IMPC-derived effect size, applies `log1p`, and rescales the values for the target phenotype to 1–100. This display value is a within-page ranking aid, not the raw effect size, and values from different phenotype pages are not directly comparable.

Missing effect sizes are serialized as standard JSON `null`, remain semantically missing rather than being converted to zero, and those nodes are shown in white.

> [!NOTE]
> Hidden for binary phenotypes  
> binary list: 👉 [here](https://github.com/larc-tsukuba/tsumugi/blob/main/data/binary_phenotypes.txt)) or gene(s) input.

#### Specify genotype
Choose the genotype in which phenotypes appear:
- `Homo`: homozygous
- `Hetero`: heterozygous
- `Hemi`: hemizygous

#### Specify sex
Filter by the sex-specific evidence label:
- `Female`: only the female KO effect P-value is ≤ 0.0001
- `Male`: only the male KO effect P-value is ≤ 0.0001

The two options are mutually exclusive in the web interface. This label is not a formal sex-by-genotype interaction test.

#### Specify life stage
Filter by life stage in which phenotypes appear:
- `Embryo`
- `Early` (0–16 weeks)
- `Interval` (17–48 weeks)
- `Late` (49+ weeks)

### Markup panel

#### Module display
Select the module definition and visible module from the right panel. Module borders can be shown or hidden without removing genes or edges from the network.

#### Highlight: Phenotype
Highlight genes by phenotype annotation. Metadata variants of the same phenotype are consolidated into one option. When Human Disease and one or more Phenotype highlights overlap on a gene, the categories are shown as concentric rings.

#### Highlight: Human Disease
Highlight KO genes with disease-model annotations in the IMPC Disease Models Portal. This annotation is model-similarity evidence and does not by itself establish a causal human gene–disease relationship.

#### Search: Specific Gene
Search gene names within the network.

#### Layout & Display
Adjust layout, font size, edge width, and node repulsion (Cose layout).

#### Export
Export the current network as PNG, JPG, SVG, CSV, or GraphML. Module frames can be included in PNG, JPG, and SVG files. CSV records the active similarity-module or Top-level MP-module assignments together with phenotype lists; GraphML is Cytoscape-compatible.

# 🛠 Command-Line Interface (CLI)

The TSUMUGI v1.2.0 CLI can recompute results from a locally downloaded IMPC Release 24.0 statistical-results file, filter the generated annotations, and export GraphML or a local webapp bundle. TSUMUGI requires Python 3.10 or later.

## Installation

BioConda:

```bash
conda install -c conda-forge -c bioconda tsumugi
```

PyPI:

```bash
pip install tsumugi
```

The installation is ready when `tsumugi --version` prints the installed version.

## Quick start

```bash
tsumugi run \
  --output_dir ./tsumugi-output \
  --statistical_results ./statistical-results-ALL.csv.gz \
  --threads 8
```

The output directory contains `genewise_phenotype_annotations.jsonl.gz`, `pairwise_similarity_annotations.jsonl.gz`, and the `TSUMUGI-webapp` visualization bundle.

A pairwise result can then be filtered, for example:

```bash
tsumugi mp --include MP:0001146 \
  --pairwise \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl
```

## Main commands

| Command                 | Purpose                                                           |
| ----------------------- | ----------------------------------------------------------------- |
| `tsumugi run`           | Recompute annotations and the similarity network from IMPC data   |
| `tsumugi mp`            | Filter by the presence or measured non-significance of an MP term |
| `tsumugi count`         | Filter by phenotype counts per pair or per gene                   |
| `tsumugi score`         | Filter by pairwise phenotype similarity score                     |
| `tsumugi genes`         | Keep or drop gene symbols or gene pairs listed in a file          |
| `tsumugi life-stage`    | Keep or drop a life stage                                         |
| `tsumugi sex`           | Keep or drop a sex label                                          |
| `tsumugi zygosity`      | Keep or drop a zygosity                                           |
| `tsumugi build-graphml` | Export GraphML                                                    |
| `tsumugi build-webapp`  | Build a locally served webapp bundle                              |

Filtering and export commands use `pairwise_similarity_annotations.jsonl.gz`, `genewise_phenotype_annotations.jsonl.gz`, or both. The files are available from the [TSUMUGI top page](https://larc-tsukuba.github.io/tsumugi/). Filtering commands write JSONL to STDOUT and can be chained with pipes.

See the [complete CLI reference](doc/CLI.md) for all options, input requirements, examples, output details, and interpretation cautions.

# 🔍 How We Calculate Phenotypically Similar Genes

## Data source

We use the IMPC dataset [Release 24.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-24.0/results) `statistical-results-ALL.csv.gz`.
See dataset columns: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)  

## Preprocessing

TSUMUGI treats a non-empty IMPC `mp_term_id` as an IMPC phenodeviant annotation. It also retains mapped measurement records without a significant abnormal annotation for measurement-aware exclusion queries.
For non-significant measurements, every ontology-incomparable, most-specific non-root term in `intermediate_mp_term_id` is emitted as a separate record. Measurements mapped only to `MP:0000001`, or to no valid MP term, are omitted because they do not support phenotype-specific queries.

- Convert zygosity to `Homo`, `Hetero`, or `Hemi`.
- Assign `Female` when only `female_ko_effect_p_value` is ≤ 0.0001 and `Male` when only `male_ko_effect_p_value` is ≤ 0.0001; otherwise assign `None`.
- Use the absolute effect size. Missing values remain missing and are serialized as JSON `null`.

## Phenotypic similarity

TSUMUGI adapts the original PhenoDigm scoring formula ([Smedley D, et al. (2013)](https://doi.org/10.1093/database/bat025)) to compare KO mouse gene phenotype profiles within the Mammalian Phenotype Ontology.

> [!NOTE]
> TSUMUGI keeps the PhenoDigm scoring formula but does not run the original cross-species HPO-MP/ZP OWLSim pipeline.
> It compares MP annotations from IMPC KO mouse genes.

### 1. Definition of MP term-pair similarity

* Build the MP ontology and compute Information Content (IC) from significant IMPC annotations:
   `IC(term) = -log2(|annotations propagated to term| / |all significant annotations|)`
   Each direct annotation is propagated to the annotated MP term and all of its ancestors.

* For each MP term pair, find the common ancestors with the highest annotation-derived IC. If multiple candidates tie, select one deterministically by the fewest transitive descendants in the MP ontology (not only direct children), then by the lexicographically smallest MP term ID. Use the selected MICA's IC as Resnik similarity. The tied candidates have the same numeric term-pair score, but the selected MICA label can change shared-context counts and therefore display eligibility.

* For two MP terms, compute the Jaccard index of their inferred attribute sets, defined as each term itself plus all ancestors.

* Define MP term-pair similarity as `sqrt(Resnik * Jaccard)`.

### 2. Gene-pair similarity matrix

* For each gene pair, build an MP-term × MP-term similarity matrix from the term-pair scores.

* Genotype, life stage, and sexual-dimorphism metadata must match when a MICA is recorded in `phenotype_shared_annotations`. These metadata do not weight the PhenoDigm score itself.

### 3. PhenoDigm scaling

* Apply PhenoDigm max/average scaling to normalize each KO mouse gene-pair similarity to 0–100:
   Compute observed best-match max/mean, then normalize by the symmetric optimal self-match score for the two genes.
   `Score = 100 * (normalized_max + normalized_mean) / 2`
   If the denominator is 0, the score is set to 0.

The resulting score is a phenotype-profile similarity measure. It is not a P-value, effect size, binding affinity, or evidence of a causal interaction between the genes.

---

# ✉️ Contact

If you have any questions or requests, please feel free to contact us using one of the following methods:  

👉 [Google Form](https://forms.gle/ME8EJZZHaRNgKZ979)

If you have a GitHub account:  
👉 [GitHub Issue](https://github.com/akikuno/TSUMUGI-dev/issues/new/choose)  

---

# 📄 Citation

Kuno A, Matsumoto K, Taki T, Takahashi S, and Mizuno S  
**TSUMUGI: a platform for phenotype-driven gene network identification from comprehensive knockout mouse phenotyping data**  
*bioRxiv*. (2026) https://doi.org/10.64898/2026.02.18.706720  
