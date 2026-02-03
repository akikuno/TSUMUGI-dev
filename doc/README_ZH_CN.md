> ⚠️ 本文为生成式AI翻译，若有疑问请参考原文（README.md）。  
> 原文: https://github.com/akikuno/TSUMUGI-dev/blob/main/README.md

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

**TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification)** 是利用 [IMPC](https://www.mousephenotype.org/) 的 KO 小鼠表型数据，**按表型相似性提取并可视化基因模块**的 Web 工具。  
该工具面向所有人公开使用👇️  
🔗https://larc-tsukuba.github.io/tsumugi/

**TSUMUGI(紡ぎ)** 意为“把形成表型的基因群像纺丝一样编织起来”。

# 📖 TSUMUGI 的使用方法

TSUMUGI 支持三种输入。

### 表型（Phenotype）
输入关注的表型，在该表型的 KO 小鼠基因中寻找**整体表型也相似的基因群**。  
表型名称基于 [Mammalian Phenotype Ontology (MPO)](https://www.informatics.jax.org/vocab/mp_ontology)。  
👉 [表型列表](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### 基因名（Gene）
指定一个基因，寻找**KO 小鼠表型相似的其他基因群**。  
基因符号遵循 [MGI](http://www.informatics.jax.org/)。  
👉 [基因列表](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)

### 基因列表（Gene List）
支持多个基因（每行一个），在列表内部提取**表型相似的基因**。  
> [!CAUTION]  
> 若找不到相似基因：`No similar phenotypes were found among the entered genes.`  
> 若超过 200 个：`Too many genes submitted. Please limit the number to 200 or fewer.`

### 📥 下载原始数据
TSUMUGI 发布 gzip 压缩的 JSONL 文件。

#### `genewise_phenotype_annotations.jsonl.gz`
- 基因符号（如 "1110059G10Rik"）  
- Marker accession ID（如 "MGI:1913452"）  
- 表型名/ID（如 "fused joints", "MP:0000137"）  
- Effect size（如 0.0, 1.324）  
- 显著性（True/false）  
- 接合型（"Homo", "Hetero", "Hemi"）  
- 生命阶段（"Embryo", "Early", "Interval", "Late"）  
- 性别差异（"", "Male", "Female"）  
- 疾病注释（如 [] 或 "Premature Ovarian Failure 18"）

示例：
```
{"significant": true, "sexual_dimorphism": "Female", "effect_size": 0.0119677350763567, "marker_symbol": "4930447C04Rik", "zygosity": "Homo", "marker_accession_id": "MGI:1923051", "mp_term_id": "MP:0000063", "disease_annotation": ["Male Infertility With Azoospermia Or Oligozoospermia Due To Single Gene Mutation", "Premature Ovarian Failure 18", "Spermatogenic Failure 52"], "life_stage": "Early", "mp_term_name": "decreased bone mineral density"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- 基因对（`gene1_symbol`, `gene2_symbol`）  
- `phenotype_shared_annotations`：共享表型的元数据（生命阶段、接合型、性别差异）  
- `phenotype_similarity_score`：基于 Resnik 的 Phenodigm 分数（0–100）

示例：
```
{"gene1_symbol": "1500009L16Rik", "gene2_symbol": "Aak1", "phenotype_shared_annotations": [{"mp_term_name": "increased circulating enzyme level", "life_stage": "Early", "zygosity": "Homo", "sexual_dimorphism": "None"}], "phenotype_similarity_score": 47}
```

# 🌐 网络

根据输入自动生成网络。

> [!IMPORTANT]  
> **共享异常表型≥3 且 表型相似度>0.0** 的基因对会被可视化。

### 网络面板
**节点**代表基因。点击可查看该 KO 小鼠的异常表型列表，拖拽可调整位置。  
**边**点击可查看共享表型的详情。  
**模块**以多边形圈出基因子网络。点击模块可列出其中基因涉及的表型；可拖拽模块以重新摆放并避免重叠。

### 控制面板
在左侧面板调整网络显示。

#### 按表型相似度过滤
`Phenotypes similarity` 滑块按 Resnik→Phenodigm 分数为边设定阈值。  
> 计算详情：👉 [🔍 表型相似基因群的计算方法](#-表型相似基因群的计算方法)

#### 按表型严重程度过滤
`Phenotype severity` 滑块按 KO 小鼠的 effect size 过滤节点，值越大影响越强。  
> 对于二值表型（如 [abnormal embryo development](https://larc-tsukuba.github.io/tsumugi/app/phenotype/abnormal_embryo_development.html); 二值列表见[此处](https://github.com/larc-tsukuba/tsumugi/blob/main/data/binary_phenotypes.txt)）或单基因输入，此控件隐藏。

#### 指定接合型
- `Homo`（纯合）
- `Hetero`（杂合）
- `Hemi`（半合）

#### 指定性别
- `Female`
- `Male`

#### 指定生命阶段
- `Embryo`
- `Early`（0–16 周）
- `Interval`（17–48 周）
- `Late`（49 周以上）

### 标记面板
#### Highlight: Human Disease
基于 IMPC Disease Models Portal 数据，高亮与人类疾病相关的基因。

#### Search: Specific Gene
在网络中搜索基因名。

#### Layout & Display
调整布局、字体大小、边宽、节点斥力（Cose 布局）。

#### Export
导出 PNG/CSV/GraphML。  
CSV 含模块ID及每个基因的表型列表；GraphML 与 Cytoscape 兼容。

# 🛠 命令行版

TSUMUGI CLI 允许使用本地下载的最新IMPC数据，并提供比网页版更细粒度的过滤与输出。

## 功能

- 使用IMPC的`statistical-results-ALL.csv.gz`重新计算（可选`mp.obo`、`impc_phenodigm.csv`）。  
- 按MP术语的包含/排除进行过滤。  
- 按基因列表过滤（逗号分隔或文本文件）。  
- 输出：GraphML（`tsumugi build-graphml`）、离线Web应用包（`tsumugi build-webapp`）。

## 安装

BioConda:
```bash
conda install -c conda-forge -c bioconda tsumugi
```

PyPI:
```bash
pip install tsumugi
```

`tsumugi --version`正常输出即表示可用。

## 可用命令

- `tsumugi run`: 从IMPC数据重新计算网络  
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: 按MP术语包含/排除基因对或基因  
- `tsumugi count --pairwise/--genewise (--min/--max)`: 按表型数量过滤（基因对/基因）  
- `tsumugi score (--min/--max)`: 按表型相似性得分过滤（基因对）  
- `tsumugi genes --keep/--drop`: 基因列表保留/剔除（逗号或文本文件）  
- `tsumugi life-stage --keep/--drop`: 按生命阶段过滤（Embryo/Early/Interval/Late）  
- `tsumugi sex --keep/--drop`: 按性别过滤（Male/Female/None）  
- `tsumugi zygosity --keep/--drop`: 按接合型过滤（Homo/Hetero/Hemi）  
- `tsumugi build-graphml`: 生成GraphML（Cytoscape等）  
- `tsumugi build-webapp`: 生成TSUMUGI Web应用资源（本地HTML/CSS/JS）

> [!NOTE]
> 所有过滤类子命令都会将JSONL输出到STDOUT。  
> 如需保存到文件，请使用`>`重定向。

> [!IMPORTANT]
> 除`tsumugi run`外，所有命令都需要`pairwise_similarity_annotation.jsonl.gz`或`genewise_phenotype_annotation.jsonl.gz`。
> 两个文件都可以从[TSUMUGI首页](https://larc-tsukuba.github.io/tsumugi/)下载。

## 使用方法

### 从IMPC数据重新计算（`tsumugi run`）
若省略`--mp_obo`，TSUMUGI使用内置`data-version: releases/2025-08-27/mp.obo`。  
若省略`--impc_phenodigm`，使用2025-10-01从[IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/)获取的文件。
```bash
tsumugi run   --output_dir ./tsumugi-output   --statistical_results ./statistical-results-ALL.csv.gz   --threads 8
```
输出：`./tsumugi-output`包含genewise注释（genewise_phenotype_annotations.jsonl.gz）、pairwise相似度数据（pairwise_similarity_annotations.jsonl.gz）和可视化资源（`TSUMUGI-webapp`）。

> [!IMPORTANT]  
> `TSUMUGI-webapp`目录包含各操作系统的启动脚本；双击即可打开本地Web应用：  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### 按MP术语过滤（`tsumugi mp --include/--exclude`）
提取包含目标表型的基因对（或基因），或提取已测量但未出现显著异常的基因对。

```bash
tsumugi mp [-h] (-i MP_ID | -e MP_ID) [-g | -p] [-m PATH_MP_OBO] [-a PATH_GENEWISE_ANNOTATIONS] [--in PATH_PAIRWISE_ANNOTATIONS]
                  [--life_stage LIFE_STAGE] [--sex SEX] [--zygosity ZYGOSITY]
```

#### `-i MP_ID`, `--include MP_ID`
包含具有指定MP术语的基因/基因对（包含下位术语）。

#### `-e MP_ID`, `--exclude MP_ID`
返回已测量该MP术语（包含下位术语）但未出现显著表型的基因/基因对。需要`-a/--genewise_annotations`。

#### `-g`, `--genewise`
按基因级别过滤。读取`genewise_phenotype_annotations.jsonl(.gz)`。使用`--genewise`时请指定`-a/--genewise_annotations`。

#### `-p`, `--pairwise`
按基因对级别过滤。目标为`pairwise_similarity_annotations.jsonl(.gz)`。若省略`--in`，从STDIN读取。

#### `-m PATH_MP_OBO`, `--mp_obo PATH_MP_OBO`
哺乳动物表型本体（mp.obo）的路径。省略时使用内置`data/mp.obo`。

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
genewise注释文件（JSONL/.gz）路径。`--exclude`必需，`--genewise`时也需指定。

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise注释文件（JSONL/.gz）路径。省略时从STDIN读取。

#### `--life_stage LIFE_STAGE`
按生命阶段追加过滤。可选值：`Embryo`, `Early`, `Interval`, `Late`。

#### `--sex SEX`
按性别差异追加过滤。使用注释中的值（如`Male`, `Female`, `None`）。

#### `--zygosity ZYGOSITY`
按接合型追加过滤。可选值：`Homo`, `Hetero`, `Hemi`。

```bash
# 仅提取包含MP:0001146（abnormal testis morphology）或其下位术语（如MP:0004849 abnormal testis size）的基因对
tsumugi mp --include MP:0001146   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_filtered.jsonl

# 提取已测量MP:0001146及其下位术语但未出现显著异常的基因对
tsumugi mp --exclude MP:0001146   --genewise genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_filtered.jsonl

# 按基因提取包含MP:0001146的显著表型（含下位术语）
tsumugi mp --include MP:0001146   --genewise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > genewise_filtered.jsonl

# 按基因提取已测量MP:0001146（含下位术语）但不显著的基因
tsumugi mp --exclude MP:0001146   --genewise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > genewise_no_phenotype.jsonl
```

> [!IMPORTANT]
> **指定MP ID的下位术语同样会被处理。**  
> 例如，指定`MP:0001146 (abnormal testis morphology)`时，也会包含`MP:0004849 (abnormal testis size)`等下位术语。

### 按表型数量过滤（`tsumugi count`）
```bash
tsumugi count [-h] (-g | -p) [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS] [-a PATH_GENEWISE_ANNOTATIONS]
```

按表型数量过滤基因或基因对。至少需要`--min`或`--max`之一。

#### `-g`, `--genewise`
按每个基因的显著表型数量过滤。需要`-a/--genewise_annotations`与`genewise_phenotype_annotations.jsonl(.gz)`。

#### `-p`, `--pairwise`
按每个基因对的共享表型数量过滤。若省略`--in`，从STDIN读取。

#### `--min MIN`, `--max MAX`
表型数量的下限/上限。只指定一个也可进行单侧过滤。

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise注释文件（JSONL/.gz）路径。省略时从STDIN读取。

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
genewise注释文件（JSONL/.gz）路径。`--genewise`时必需。

- 基因对共享表型数量：
```bash
tsumugi count --pairwise --min 3 --max 20   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_min3_max20.jsonl
```

- 每个基因的表型数量（需要genewise）：
```bash
tsumugi count --genewise --min 5 --max 50   --genewise genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > genewise_min5_max50.jsonl
```

只用`--min`或`--max`也可以。

### 按相似度得分过滤（`tsumugi score`）
```bash
tsumugi score [-h] [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS]
```

按`phenotype_similarity_score`（0–100）过滤基因对。至少需要`--min`或`--max`之一。

#### `--min MIN`, `--max MAX`
得分下限/上限。只指定一个也可进行单侧过滤。

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise注释文件（JSONL/.gz）路径。省略时从STDIN读取。

```bash
tsumugi score --min 50 --max 80   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_score50_80.jsonl
```

只用`--min`或`--max`也可以。

### 按基因列表过滤（`tsumugi genes --keep/--drop`）
```bash
tsumugi genes [-h] (-k GENE_SYMBOL | -d GENE_SYMBOL) [-g | -p] [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k GENE_SYMBOL`, `--keep GENE_SYMBOL`
仅保留包含指定基因的基因对（通过文本文件提供）。

#### `-d GENE_SYMBOL`, `--drop GENE_SYMBOL`
移除包含指定基因的基因对（通过文本文件提供）。

#### `-g`, `--genewise`
按用户提供的基因符号过滤。

#### `-p`, `--pairwise`
按用户提供的基因对过滤。

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise注释文件（JSONL/.gz）路径。省略时从STDIN读取。

```bash
cat << EOF > genes.txt
Maf
Aamp
Cacna1c
EOF

tsumugi genes --genewise --keep genes.txt   --in "$directory"/pairwise_similarity_annotations.jsonl.gz   > pairwise_keep_genes.jsonl

cat << EOF > gene_pairs.csv
Maf,Aamp
Maf,Cacna1c
EOF

tsumugi genes --pairwise --drop gene_pairs.csv   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_drop_genes.jsonl

```

### 按生命阶段过滤（`tsumugi life-stage --keep/--drop`）
```bash
tsumugi life-stage [-h] (-k LIFE_STAGE | -d LIFE_STAGE) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k LIFE_STAGE`, `--keep LIFE_STAGE`
仅保留指定生命阶段（`Embryo`, `Early`, `Interval`, `Late`）。

#### `-d LIFE_STAGE`, `--drop LIFE_STAGE`
移除指定生命阶段。

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise注释文件（JSONL/.gz）路径。省略时从STDIN读取。

```bash
tsumugi life-stage --keep Early   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_lifestage_early.jsonl
```

### 按性别过滤（`tsumugi sex --keep/--drop`）
```bash
tsumugi sex [-h] (-k SEX | -d SEX) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k SEX`, `--keep SEX`
仅保留指定性别（`Male`, `Female`, `None`）。

#### `-d SEX`, `--drop SEX`
移除指定性别。

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise注释文件（JSONL/.gz）路径。省略时从STDIN读取。

```bash
tsumugi sex --drop Male   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_no_male.jsonl
```

### 按接合型过滤（`tsumugi zygosity --keep/--drop`）
```bash
tsumugi zygosity [-h] (-k ZYGOSITY | -d ZYGOSITY) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k ZYGOSITY`, `--keep ZYGOSITY`
仅保留指定接合型（`Homo`, `Hetero`, `Hemi`）。

#### `-d ZYGOSITY`, `--drop ZYGOSITY`
移除指定接合型。

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise注释文件（JSONL/.gz）路径。省略时从STDIN读取。

```bash
tsumugi zygosity --keep Homo   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_homo.jsonl
```

### 导出GraphML / webapp
```bash
tsumugi build-graphml [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise注释文件（JSONL/.gz）路径。省略时从STDIN读取。

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
genewise注释文件（JSONL/.gz）路径。必需。

```bash
tsumugi build-graphml   --in pairwise_similarity_annotations.jsonl.gz   --genewise genewise_phenotype_annotations.jsonl.gz   > network.graphml
```

```bash
tsumugi build-webapp [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS -o OUT
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise注释文件（JSONL/.gz）路径。省略时从STDIN读取。

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
genewise注释文件（JSONL/.gz）路径。必需。

#### `-o OUT`, `--out OUT`
Webapp输出目录（HTML/CSS/JS + 网络数据）。不要指定带扩展名的文件名。

```bash
tsumugi build-webapp   --in pairwise_similarity_annotations.jsonl.gz   --genewise genewise_phenotype_annotations.jsonl.gz   --output_dir ./webapp_output
```

CLI支持STDIN/STDOUT，可串联命令:  
`zcat pairwise_similarity_annotations.jsonl.gz | tsumugi mp ... | tsumugi genes ... > out.jsonl`

# 🔍 表型相似基因群的计算方法

## 数据源
[IMPC Release-23.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-23.0/results) 的 `statistical-results-ALL.csv.gz`  
字段说明: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)

## 预处理
提取 KO 小鼠 P 值(`p_value`, `female_ko_effect_p_value`, `male_ko_effect_p_value`) ≤ 0.0001 的基因–表型。  
- Zygosity: `homo`, `hetero`, `hemi`  
- 性别: `female`, `male`

## 表型相似度
TSUMUGI目前采用类似Phenodigm的方法。我们计算MP术语之间的**Resnik相似度**与祖先集合的**Jaccard相似度**，并用**几何平均**进行合并。与原始Phenodigm的主要差异是加入元数据加权（zygosity、life stage、sexual dimorphism）来汇总相似度。

1. 构建MP本体并计算信息量(IC)：  
   `IC(term) = -log((|Descendants(term)| + 1) / |All MP terms|)`  
   IC低于第5百分位的术语设为0。
2. 对每个MP术语对，找到最具体的公共祖先(MICA)并用其IC作为Resnik。  
   计算祖先集合的Jaccard指数。  
   术语对相似度 = `sqrt(Resnik * Jaccard)`。
3. 对每个基因对构建术语×术语相似度矩阵并应用元数据加权。  
   zygosity/生命阶段/性别二态性的匹配数为0/1/2/3时，权重分别为0.25/0.5/0.75/1.0。
4. 采用Phenodigm式缩放到0–100：  
   使用行/列最大值获得实际max/mean。  
   用IC得到的理论max/mean进行归一化并计算  
   `Score = 100 * (normalized_max + normalized_mean) / 2`。  
   若理论分母为0，则设为0。

# ✉️ 联系
- Google 表单: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose
