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

### 1. 表型（Phenotype）
输入关注的表型，在该表型的 KO 小鼠基因中寻找**整体表型也相似的基因群**。  
表型名称基于 [Mammalian Phenotype Ontology (MPO)](https://www.informatics.jax.org/vocab/mp_ontology)。  
👉 [表型列表](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### 2. 基因名（Gene）
指定一个基因，寻找**KO 小鼠表型相似的其他基因群**。  
基因符号遵循 [MGI](http://www.informatics.jax.org/)。  
👉 [基因列表](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)

### 3. 基因列表（Gene List）
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
{"life_stage": "Early", "marker_symbol": "1110059G10Rik", "marker_accession_id": "MGI:1913452", "effect_size": 0.0, "mp_term_name": "fused joints", "disease_annotation": [], "significant": false, "zygosity": "Homo", "sexual_dimorphism": "", "mp_term_id": "MP:0000137"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- 基因对（`gene1_symbol`, `gene2_symbol`）  
- `phenotype_shared_annotations`：共享表型的元数据（生命阶段、接合型、性别差异）  
- `phenotype_similarity_score`：基于 Resnik 的 Phenodigm 分数（0–100）

示例：
```
{"gene1_symbol": "1110059G10Rik", "gene2_symbol": "Cog6", "phenotype_shared_annotations": {"vertebral transformation": {"zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "Male"}}, "phenotype_similarity_score": 42}
```

# 🌐 网络

根据输入自动生成网络。

> [!IMPORTANT]  
> **共享异常表型≥3 且 表型相似度>0.0** 的基因对会被可视化。

### 网络面板
**节点**代表基因。点击可查看该 KO 小鼠的异常表型列表，拖拽可调整位置。  
**边**点击可查看共享表型的详情。

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

本次发布新增 **CLI**。可自行下载最新 IMPC 数据运行管线，比网页版更灵活过滤与输出。

- 用 IMPC `statistical-results-ALL.csv.gz`（可选 `mp.obo`、`impc_phenodigm.csv`）重算  
- MP 术语的包含/排除过滤  
- 按基因列表过滤（逗号或文本文件）  
- 输出：GraphML(`tsumugi build-graphml`)、离线 Web 应用(`tsumugi build-webapp`)

## 可用命令
- `tsumugi run`: 由 IMPC 数据重算网络  
- `tsumugi mp --include/--exclude`: 按 MP 术语包含/排除基因对  
- `tsumugi n-phenos --pairwise/--genewise (--min/--max)`: 按表型数过滤（基因对/基因）  
- `tsumugi genes --keep/--drop`: 基因列表保留/剔除  
- `tsumugi life-stage --keep/--drop`: 按生命阶段过滤  
- `tsumugi sex --keep/--drop`: 按性别过滤  
- `tsumugi zygosity --keep/--drop`: 按接合型过滤  
- `tsumugi build-graphml`: 生成 GraphML  
- `tsumugi build-webapp`: 生成 TSUMUGI Web 应用资源

## 安装
BioConda:
```bash
conda install -c conda-forge -c bioconda tsumugi
```
PyPI:
```bash
pip install tsumugi
```
`tsumugi --version` 正常输出即表示可用。

## 常用示例（按命令）

### 1. 用 IMPC 数据重算(`tsumugi run`)
若省略 `--mp_obo`，使用内置 `data-version: releases/2025-08-27/mp.obo`。  
若省略 `--impc_phenodigm`，使用 2025-10-01 从 [IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/) 获取的文件。
```bash
tsumugi run \
  --output_dir ./tsumugi-output \
  --statistical_results ./statistical-results-ALL.csv.gz \
  --threads 8
```
输出：`./tsumugi-output` 中包含 genewise/pairwise JSONL 和可视化资源(`TSUMUGI-webapp`)。

> [!IMPORTANT]  
> `TSUMUGI-webapp` 内含各操作系统的启动脚本，双击即可本地打开：  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### 2. 按 MP 术语过滤(`tsumugi mp --include/--exclude`)
仅提取包含目标表型的基因对，或提取已测量该表型但未出现显著异常的基因对。

```bash
# 仅提取包含 MP:0001146 (abnormal testis morphology) 或其子术语（如 MP:0004849 (abnormal testis size)）的基因对
tsumugi mp --include MP:0001146 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

# 提取已测量 MP:0001146 及其子术语，但未出现显著异常的基因对
tsumugi mp --exclude MP:0001146 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl
```

> [!IMPORTANT]
> **会同时处理指定 MP 术语的子术语。**  
> 例如指定 `MP:0001146 (abnormal testis morphology)` 时，也会考虑 `MP:0004849 (abnormal testis size)` 等子术语。

### 3. 按表型数量过滤(`tsumugi n-phenos`)
- 每对共享表型数:
```bash
tsumugi n-phenos --pairwise --min 3 --max 20 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_min3_max20.jsonl
```
- 每基因表型数（需 genewise）:
```bash
tsumugi n-phenos --genewise --min 5 --max 50 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > genewise_min5_max50.jsonl
```
`--min` 或 `--max` 可单独指定。

### 4. 基因列表过滤(`tsumugi genes --keep/--drop`)
```bash
tsumugi genes --keep genes.txt \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_keep_genes.jsonl

tsumugi genes --drop geneA,geneB \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_drop_genes.jsonl
```

### 5. 按生命阶段过滤(`tsumugi life-stage --keep/--drop`)
```bash
tsumugi life-stage --keep Early \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_lifestage_early.jsonl
```

### 6. 按性别过滤(`tsumugi sex --keep/--drop`)
```bash
tsumugi sex --drop Male \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_no_male.jsonl
```

### 7. 按接合型过滤(`tsumugi zygosity --keep/--drop`)
```bash
tsumugi zygosity --keep Homo \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_homo.jsonl
```

### 8. 导出 GraphML / Web 应用
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

CLI 支持标准输入/输出，可串联：`zcat ... | tsumugi mp ... | tsumugi genes ... > out.jsonl`

# 🔍 表型相似基因群的计算方法

## 数据源
[IMPC Release-23.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-23.0/results) 的 `statistical-results-ALL.csv.gz`  
字段说明: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)

## 预处理
提取 KO 小鼠 P 值(`p_value`, `female_ko_effect_p_value`, `male_ko_effect_p_value`) ≤ 0.0001 的基因–表型。  
- Zygosity: `homo`, `hetero`, `hemi`  
- 性别: `female`, `male`

## 表型相似度
计算 MP 术语间的 **Resnik 相似度**，并将基因对得分缩放到 **Phenodigm(0–100)**。

1. 构建 MP 本体并计算信息量(IC)：  
   `IC(term) = -log((|Descendants(term)| + 1) / |All MP terms|)`  
2. Resnik(t1, t2) = 最信息丰富公共祖先(MICA)的 IC（无公共祖先则为0）。  
3. 基因对：将有意义的 MP 术语 Resnik 分数按 zygosity/生命阶段/性别匹配度(1.0/0.75/0.5/0.25)加权。  
4. 实际最大值/平均值除以理论最大/平均并取平均：  
   `Phenodigm = 100 * 0.5 * ( actual_max / theoretical_max + actual_mean / theoretical_mean )`  
   若理论分母为0，则设为0。0–100 分用于下载和 `Phenotypes similarity` 滑块。

# ✉️ 联系
- Google 表单: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose
