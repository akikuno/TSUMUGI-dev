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
[![Preprint](https://img.shields.io/badge/bioRxiv-10.64898/2026.02.18.706720-red)](https://doi.org/10.64898/2026.02.18.706720)
[![DOI](https://zenodo.org/badge/441025227.svg)](https://doi.org/10.5281/zenodo.14957711)
[![Contact](https://img.shields.io/badge/Contact-923DE2)](https://forms.gle/ME8EJZZHaRNgKZ979)

**TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification)** 是利用 [IMPC](https://www.mousephenotype.org/) 的 KO 小鼠表型数据，**按表型相似性提取并可视化基因模块**的 Web 工具。  
该工具面向所有人公开使用👇️  
🔗https://larc-tsukuba.github.io/tsumugi/

本文档说明**TSUMUGI v1.2.0**的当前功能。公开Web应用使用IMPC **Release 24.0**数据。

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
> 如果没有找到相似基因：`No similar phenotypes were found among the entered genes.`
> Gene List最多接受200个不同且可用的基因。计数前会删除重复符号和空行；不可用符号会被报告并排除。包含201个或更多可用基因的列表会在加载网络数据前被拒绝。

### 📥 下载原始数据
TSUMUGI 发布 gzip 压缩的 JSONL 文件。

#### `genewise_phenotype_annotations.jsonl.gz`
- 基因符号（如 "1110059G10Rik"）  
- Marker accession ID（如 "MGI:1913452"）  
- 表型名/ID（如 "fused joints", "MP:0000137"）  
- Effect size（`number`或`null`；如 0.0, 1.324）
- 显著性标志（IMPC异常表型注释为`true`；已映射但没有显著异常的测量为`false`）
- 接合型（"Homo", "Hetero", "Hemi"）  
- 生命阶段（"Embryo", "Early", "Interval", "Late"）  
- 性别差异（`None`、`Male`、`Female`）
- 疾病注释（如 [] 或 "Premature Ovarian Failure 18"）

示例：
```
{"significant": true, "sexual_dimorphism": "Female", "effect_size": 0.0119677350763567, "marker_symbol": "4930447C04Rik", "zygosity": "Homo", "marker_accession_id": "MGI:1923051", "mp_term_id": "MP:0000063", "disease_annotation": ["Male Infertility With Azoospermia Or Oligozoospermia Due To Single Gene Mutation", "Premature Ovarian Failure 18", "Spermatogenic Failure 52"], "life_stage": "Early", "mp_term_name": "decreased bone mineral density"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- 基因对（`gene1_symbol`, `gene2_symbol`）  
- `phenotype_shared_annotations`（元数据一致的MICA上下文：MP术语、生命阶段、接合型和性别标签）
- `phenotype_similarity_score`（Phenodigm分数，0–100）

示例：
```
{"gene1_symbol": "1500009L16Rik", "gene2_symbol": "Aak1", "phenotype_shared_annotations": [{"mp_term_name": "increased circulating enzyme level", "life_stage": "Early", "zygosity": "Homo", "sexual_dimorphism": "None"}], "phenotype_similarity_score": 47}
```

## 解读注意事项

- **共享上下文：** `phenotype_shared_annotations`中的每个条目，都是两条显著MP注释在接合型、生命阶段和性别标签一致时得到的信息量最大共同祖先（MICA）。这不一定表示两个基因都直接注释了同一个叶节点MP术语。同一个MICA在元数据不同时可作为不同上下文出现。
- **显示规则：** Gene和Phenotype页面显示共享异常表型上下文不少于3个且相似度分数大于0的基因对。Gene List要求输入基因之间至少有1个共享上下文。这些是显示规则，不是统计显著性标准。
- **相似度显示：** 发布的`phenotype_similarity_score`是0–100的Phenodigm分数。Web应用会把每个当前网络中的可用值重新缩放到1–100，因此不同页面的滑块值和提示值不能作为统一的绝对尺度比较。
- **效应量显示：** TSUMUGI取IMPC效应量的绝对值，进行`log1p`转换，并在目标表型内重新缩放到1–100。该值仅用于页面内排序，不是原始效应量，也不能在不同表型页面之间直接比较。缺失值保持为JSON `null`，对应节点显示为白色。
- **模块：** 模块只是视觉分组，并不是分子通路或蛋白质复合物的证据。`Similarity`表示连通分量，`Top-level MP`表示基于本体的分组；Gene页面的soft/fuzzy模块允许一个基因属于多个模块。模块节点数过滤器只限制当前显示的模块。
- **性别标签：** `Female`表示只有雌性KO效应P-value≤0.0001；`Male`表示只有雄性KO效应P-value≤0.0001。两个选项在Web界面中互斥，不能替代正式的性别×基因型交互检验。
- **表型高亮：** 同一表型的不同元数据变体会合并为一个选项。当Human Disease与一个或多个表型在同一基因上重叠时，各类别以同心圆显示。
- **疾病高亮：** IMPC Disease Models Portal的注释只提供疾病模型相似性证据，不能单独确立人类基因–疾病因果关系。
- **非显著记录：** 这表示在对应条件下已完成映射测量，但没有显著异常注释。它不能证明动物正常或表型不存在；`disease_annotation`保持为空。
- **分数含义：** TSUMUGI分数不是P-value、效应量、结合亲和力，也不是基因间因果相互作用的证据。

# 🌐 网络

根据输入自动生成网络。

> [!IMPORTANT]
> Gene和Phenotype页面显示共享异常表型上下文不少于3个且相似度分数大于0的基因对；Gene List要求输入基因之间至少有1个共享上下文。这些是显示规则，不是统计显著性标准。

### 网络面板
**节点**代表基因。点击可查看该 KO 小鼠的异常表型列表，拖拽可调整位置。  
**边**点击可查看共享表型的详情。  
**模块**以多边形圈出基因子网络。点击模块可列出其中基因涉及的表型；可拖拽模块以重新摆放并避免重叠。
Gene页面使用soft/fuzzy Top-level MP模块，因此一个基因可以属于多个模块。Phenotype和Gene List页面可在基于连通分量的`Similarity`模块与`Top-level MP`模块之间切换。

### 控制面板
在左侧面板调整网络显示。

#### 按表型相似度过滤
`Phenotypes similarity`按显示用相似度值过滤边。发布的`phenotype_similarity_score`范围为0–100，但每个显示网络都会重新缩放到1–100，因此不同页面的值不能直接比较。
> 计算详情：👉 [🔍 表型相似基因群的计算方法](#-表型相似基因群的计算方法)

#### 按 effect size 过滤
`Effect size`按页面特定的显示值过滤节点。TSUMUGI取IMPC效应量的绝对值，进行`log1p`转换，并在目标表型内重新缩放到1–100。该值只用于页面内排序，不是原始效应量，也不能在不同表型页面之间比较。
缺失的`effect_size`在JSONL中序列化为标准JSON的`null`，其语义仍为缺失值而不会转换为0；相应节点显示为白色。
> 对于二值表型（如 abnormal embryo development; 二值列表见[此处](https://github.com/larc-tsukuba/tsumugi/blob/main/data/binary_phenotypes.txt)）或单基因输入，此控件隐藏。

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
#### 模块显示
可在右侧面板选择模块定义和当前显示的模块。隐藏模块边框不会从网络中移除基因或边。

#### Highlight: Phenotype
根据表型注释高亮基因。同一表型的不同元数据变体会合并为一个选项。当Human Disease与至少一个表型在同一基因上重叠时，各类别以同心圆显示。

#### Highlight: Human Disease
高亮在IMPC Disease Models Portal中具有疾病模型注释的KO基因。该注释表示模型相似性，不能单独确立人类基因–疾病因果关系。

#### Search: Specific Gene
在网络中搜索基因名。

#### Layout & Display
调整布局、字体大小、边宽、节点斥力（Cose 布局）。

#### Export
可导出PNG、JPG、SVG、CSV或GraphML。PNG、JPG和SVG可选择包含模块边框。CSV记录当前Similarity或Top-level MP模块分配及表型列表；GraphML与Cytoscape兼容。

# 🛠 命令行版

TSUMUGI CLI 允许使用本地下载的最新IMPC数据，并提供比网页版更细粒度的过滤与输出。

## 功能

- 使用IMPC的`statistical-results-ALL.csv.gz`重新计算（可选`mp.obo`、`impc_phenodigm.csv`）。  
- 按显著MP注释或已映射的非显著测量记录进行过滤。
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
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: 按显著MP注释或已映射的非显著测量记录过滤基因对或基因
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
> 除`tsumugi run`外，所有命令都需要`pairwise_similarity_annotations.jsonl.gz`或`genewise_phenotype_annotations.jsonl.gz`。
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
tsumugi mp [-h] (-i MP_ID | -e MP_ID) (-g | -p) [-m PATH_MP_OBO] [-a PATH_GENEWISE_ANNOTATIONS] [--in PATH_PAIRWISE_ANNOTATIONS]
                  [--life_stage LIFE_STAGE] [--sex SEX] [--zygosity ZYGOSITY]
```

#### `-i MP_ID`, `--include MP_ID`
包含具有指定MP术语的基因/基因对（包含下位术语）。

#### `-e MP_ID`, `--exclude MP_ID`
返回已测量该MP术语（包含下位术语）但未出现显著表型的基因/基因对。需要`-a/--genewise_annotations`。

> [!CAUTION]
> 非显著记录不能证明动物正常或表型不存在。它只表示映射测量在该条件下没有产生显著异常注释。

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
tsumugi mp --include MP:0001146   --pairwise   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_filtered.jsonl

# 提取已测量MP:0001146及其下位术语但未出现显著异常的基因对
tsumugi mp --exclude MP:0001146   --pairwise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_without_significant_testis_phenotype.jsonl

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
tsumugi count --genewise --min 5 --max 50   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_genes_with_5_to_50_phenotypes.jsonl
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
tsumugi genes [-h] (-k GENE_SYMBOL | -d GENE_SYMBOL) (-g | -p) [--in PATH_PAIRWISE_ANNOTATIONS]
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

tsumugi genes --genewise --keep genes.txt   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_keep_genes.jsonl

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
tsumugi build-graphml   --in pairwise_similarity_annotations.jsonl.gz   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > network.graphml
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
tsumugi build-webapp   --in pairwise_similarity_annotations.jsonl.gz   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   --out ./webapp_output
```

CLI支持STDIN/STDOUT，可串联命令:  
`tsumugi score --min 50 --in pairwise_similarity_annotations.jsonl.gz | tsumugi sex --drop Male > pairwise_score50_no_male.jsonl`

# 🔍 表型相似基因群的计算方法

## 数据来源

使用IMPC数据集[Release 24.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-24.0/results) `statistical-results-ALL.csv.gz`。
数据列信息：[Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)  

## 预处理

TSUMUGI将IMPC `mp_term_id`非空的记录视为IMPC异常表型注释。同时保留已映射但没有显著异常注释的测量记录，用于考虑是否完成测量的排除查询。
对于非显著测量，`intermediate_mp_term_id`中ontology上互不可比的最具体非根术语会分别输出为独立记录。仅映射到`MP:0000001`或未映射到有效MP术语的测量无法支持表型特异查询，因此不予输出。

- 将接合型转换为`Homo`、`Hetero`或`Hemi`。
- 仅`female_ko_effect_p_value`≤0.0001时标记为`Female`，仅`male_ko_effect_p_value`≤0.0001时标记为`Male`，其他情况标记为`None`。
- 使用效应量的绝对值。缺失值保持缺失，并在JSON中序列化为`null`。

## 表型相似度

TSUMUGI使用PhenoDigm原始评分公式（[Smedley D, et al. (2013)](https://doi.org/10.1093/database/bat025)），在Mammalian Phenotype Ontology内比较IMPC KO小鼠基因的表型谱。

> [!NOTE]
> TSUMUGI使用PhenoDigm评分公式，但不运行原始的跨物种HPO-MP/ZP OWLSim pipeline。它比较IMPC KO小鼠基因的MP annotation。

### 1. MP术语对相似度定义

* 构建MP本体，并根据显著IMPC annotation计算Information Content（IC）：
   `IC(term) = -log2(|传播到该术语的annotation| / |全部显著annotation|)`
   每个直接annotation都会传播到被注释的MP术语及其全部ancestor。

* 对每个MP术语对，查找annotation-derived IC最高的共同ancestor。若候选同分，则依次确定性选择MP本体中transitive descendant较少的候选，以及字典序较小的MP term ID。所选MICA的IC作为Resnik相似度。该tie-break不改变相似度得分或输出schema。
   并列候选的术语对数值分数相同，但所选MICA标签可能改变共享上下文数量，进而影响是否满足显示条件。

* 对两个MP术语，计算其inferred attribute集合的Jaccard指数；该集合定义为术语本身及其全部ancestor。

* 将MP术语对相似度定义为`sqrt(Resnik * Jaccard)`。

### 2. 基因对相似度矩阵

* 对每个基因对，根据术语对得分构建MP术语×MP术语相似度矩阵。

* 只有在接合型、生命阶段和性别标签一致时，才把MICA记录到`phenotype_shared_annotations`中。这些元数据不会对PhenoDigm分数加权。

### 3. Phenodigm缩放

* 使用PhenoDigm maximum/average scaling，将每个KO小鼠基因对的相似度归一化到0–100：
   计算观测best match的maximum/mean，然后使用两个基因对称的optimal self-match score进行归一化。
   `Score = 100 * (normalized_max + normalized_mean) / 2`  
   若分母为0，则得分为0。

最终分数衡量表型谱相似度。它不是P-value、效应量、结合亲和力，也不是基因间因果相互作用的证据。

---

# ✉️ 联系
- Google 表单: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose


---

# 📄 引用

Kuno A, Matsumoto K, Taki T, Takahashi S, and Mizuno S  
**TSUMUGI: a platform for phenotype-driven gene network identification from comprehensive knockout mouse phenotyping data**  
*bioRxiv*. (2026) https://doi.org/10.64898/2026.02.18.706720  
