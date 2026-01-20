> ⚠️ 本文件為生成式AI翻譯，若有疑問請參考原文（README.md）。  
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

**TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification)** 使用 [IMPC](https://www.mousephenotype.org/) KO 小鼠的表型資料，**依表型相似性萃取並視覺化基因模組**的網路工具。  
此工具開放給所有人使用👇️  
🔗https://larc-tsukuba.github.io/tsumugi/

**TSUMUGI(紡ぎ)** 源自「將形成表型的基因群像紡線一樣編織」的概念。

# 📖 TSUMUGI 的使用方式

TSUMUGI 支援三種輸入。

### 表現型（Phenotype）
輸入關注的表現型，在該表現型之 KO 小鼠基因中尋找**整體表型也相似的基因群**。  
表現型名稱依據 [Mammalian Phenotype Ontology (MPO)](https://www.informatics.jax.org/vocab/mp_ontology)。  
👉 [表現型清單](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### 基因名（Gene）
指定一個基因，尋找**KO 表現型相似的其他基因群**。  
基因符號遵循 [MGI](http://www.informatics.jax.org/)。  
👉 [基因清單](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)

### 基因列表（Gene List）
可輸入多個基因（每行一個），在列表內提取**表型相似的基因**。  
> [!CAUTION]  
> 找不到相似基因時：`No similar phenotypes were found among the entered genes.`  
> 超過 200 個時：`Too many genes submitted. Please limit the number to 200 or fewer.`

### 📥 下載原始資料
TSUMUGI 發佈 gzip 壓縮的 JSONL 檔。

#### `genewise_phenotype_annotations.jsonl.gz`
- 基因符號（例："1110059G10Rik"）  
- Marker accession ID（例："MGI:1913452"）  
- 表現型名稱/ID（例："fused joints", "MP:0000137"）  
- Effect size（例：0.0, 1.324）  
- 顯著性（True/false）  
- 接合型（"Homo", "Hetero", "Hemi"）  
- 生命階段（"Embryo", "Early", "Interval", "Late"）  
- 性別差異（"", "Male", "Female"）  
- 疾病註解（例：[] 或 "Premature Ovarian Failure 18"）

範例：
```
{"life_stage": "Early", "marker_symbol": "1110059G10Rik", "marker_accession_id": "MGI:1913452", "effect_size": 0.0, "mp_term_name": "fused joints", "disease_annotation": [], "significant": false, "zygosity": "Homo", "sexual_dimorphism": "", "mp_term_id": "MP:0000137"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- 基因對 (`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations`：共享表現型的中介資料（生命階段、接合型、性別差異）  
- `phenotype_similarity_score`：Resnik→Phenodigm 分數（0–100）

範例：
```
{"gene1_symbol": "1110059G10Rik", "gene2_symbol": "Cog6", "phenotype_shared_annotations": {"vertebral transformation": {"zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "Male"}}, "phenotype_similarity_score": 42}
```

# 🌐 網路

系統會依輸入自動繪製網路。

> [!IMPORTANT]  
> **共享異常表現型≥3 且 表現型相似度 > 0.0** 的基因對會被視覺化。

### 網路面板
**節點**代表基因。點擊可查看該 KO 小鼠的異常表現型清單，拖曳可調整位置。  
**邊**點擊可查看共享表現型的詳細。  
**模組**以多邊形圈出基因子網絡。點擊模組可列出其中基因涉及的表現型；可拖曳模組重新擺放並避免重疊。

### 控制面板
可於左側調整網路顯示。

#### 依表現型相似度過濾
`Phenotypes similarity` 滑桿依 Resnik→Phenodigm 分數設定邊的門檻。  
> 計算詳情：👉 [🔍 表現型相似基因群的計算方法](#-表現型相似基因群的計算方法)

#### 依表現型嚴重度過濾
`Phenotype severity` 滑桿依 effect size（KO 小鼠中的嚴重度）過濾節點，值越大影響越強。  
> 對二值表現型（如 [abnormal embryo development](https://larc-tsukuba.github.io/tsumugi/app/phenotype/abnormal_embryo_development.html); 二值列表見[此處](https://github.com/larc-tsukuba/tsumugi/blob/main/data/binary_phenotypes.txt)）或單一基因輸入時，此控制隱藏。

#### 指定接合型
- `Homo`（純合）
- `Hetero`（雜合）
- `Hemi`（半合）

#### 指定性別
- `Female`
- `Male`

#### 指定生命階段
- `Embryo`
- `Early`（0–16 週）
- `Interval`（17–48 週）
- `Late`（49 週以上）

### 標記面板
#### Highlight: Human Disease
使用 IMPC Disease Models Portal 資料，高亮與人類疾病相關的基因。

#### Search: Specific Gene
於網路中搜尋基因名。

#### Layout & Display
調整布局、字體大小、邊線粗細、節點斥力（Cose 布局）。

#### Export
可匯出 PNG/CSV/GraphML。  
CSV 含模組ID與每個基因的表現型列表；GraphML 與 Cytoscape 相容。

# 🛠 命令列版本

本次發佈加入 **CLI**。可自行下載最新 IMPC 資料，執行管線，並以比網頁更彈性的方式過濾與輸出。

- 使用 IMPC `statistical-results-ALL.csv.gz`（可選 `mp.obo`、`impc_phenodigm.csv`）重算  
- MP 術語包含/排除過濾  
- 依基因列表過濾（逗號或文字檔）  
- 輸出：GraphML(`tsumugi build-graphml`)、離線 Web 應用(`tsumugi build-webapp`)

## 可用指令
- `tsumugi run`: 由 IMPC 資料重算網路  
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: 依 MP 術語包含/排除基因對或單個基因  
- `tsumugi count --pairwise/--genewise (--min/--max)`: 依表現型數量過濾（基因對/基因）  
- `tsumugi score (--min/--max)`: 依表型相似度分數篩選（基因配對）
- `tsumugi genes --keep/--drop`: 基因列表保留/移除  
- `tsumugi life-stage --keep/--drop`: 生命階段過濾  
- `tsumugi sex --keep/--drop`: 性別過濾  
- `tsumugi zygosity --keep/--drop`: 接合型過濾  
- `tsumugi build-graphml`: 產生 GraphML  
- `tsumugi build-webapp`: 產生 TSUMUGI Web 應用資源

## 安裝
BioConda:
```bash
conda install -c conda-forge -c bioconda tsumugi
```
PyPI:
```bash
pip install tsumugi
```
`tsumugi --version` 正常顯示即表示可用。

## 常見示例（依指令）

### 使用 IMPC 資料重算 (`tsumugi run`)
省略 `--mp_obo` 時，使用內建 `data-version: releases/2025-08-27/mp.obo`。  
省略 `--impc_phenodigm` 時，使用 2025-10-01 從 [IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/) 取得的檔案。
```bash
tsumugi run \
  --statistical_results ./statistical-results-ALL.csv.gz \
  --threads 8
```
輸出：`./tsumugi-output` 下的 genewise/pairwise JSONL 與 `TSUMUGI-webapp`。

> [!IMPORTANT]  
> `TSUMUGI-webapp` 內含各作業系統啟動腳本，雙擊即可本地開啟：  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### 依 MP 術語過濾 (`tsumugi mp --include/--exclude`)
僅提取包含目標表型的基因對，或提取已測量該表型但未出現顯著異常的基因對。

- `--pairwise`（預設）: 以基因對輸出。使用 `--in pairwise_similarity_annotations.jsonl(.gz)`。
- `--genewise`: 以單個基因輸出。使用 `--genewise_annotations genewise_phenotype_annotations.jsonl(.gz)`（`--exclude` 必填，`--include` 建議）。

```bash
# 只提取包含 MP:0001146 (abnormal testis morphology) 或其子術語（例如 MP:0004849 (abnormal testis size)）的基因對
tsumugi mp --include MP:0001146 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

# 提取已測量 MP:0001146 及其子術語但未出現顯著異常的基因對
tsumugi mp --exclude MP:0001146 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

# 提取包含 MP:0001146（含子術語）的顯著基因級註解
tsumugi mp --include MP:0001146 \
  --genewise \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  > genewise_filtered.jsonl

# 提取已測量 MP:0001146（含子術語）但未顯著異常的基因
tsumugi mp --exclude MP:0001146 \
  --genewise \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  > genewise_no_phenotype.jsonl
```

> [!IMPORTANT]
> **也會處理指定 MP 術語的子術語。**  
> 例如指定 `MP:0001146 (abnormal testis morphology)` 時，也會考慮 `MP:0004849 (abnormal testis size)` 等子術語。

### 依表現型數量過濾 (`tsumugi count`)
At least one of `--min` or `--max` is required. Use either alone for one-sided filtering.
- 基因對共享表現型數:
```bash
tsumugi count --pairwise --min 3 --max 20 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_min3_max20.jsonl
```
- 每基因表現型數（需 genewise）:
```bash
tsumugi count --genewise --min 5 --max 50 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > genewise_min5_max50.jsonl
```
`--min` 或 `--max` 可單獨指定。


### 按相似度分數篩選 (`tsumugi score`)
```txt
tsumugi score [-h] [--min MIN] [--max MAX] [--in IN]
```

依 `phenotype_similarity_score`（0–100）過濾基因配對。`--min` 或 `--max` 至少要指定一個。

#### `--min MIN`, `--max MAX`
相似度分數的下/上限，可單獨使用其中一個做單邊過濾。

#### `--in IN`
成對註釋檔（JSONL/.gz）的路徑；省略時從 STDIN 讀取。

```bash
tsumugi score --min 50 --max 80 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_score50_80.jsonl
```

`--min` 或 `--max` 單獨指定也可以。

### 基因列表過濾 (`tsumugi genes --keep/--drop`)
```bash
tsumugi genes --keep genes.txt \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_keep_genes.jsonl

tsumugi genes --drop geneA,geneB \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_drop_genes.jsonl
```

### 生命階段 / 性別 / 接合型
```bash
tsumugi life-stage --keep Early --in pairwise_similarity_annotations.jsonl.gz > pairwise_lifestage_early.jsonl
tsumugi sex --drop Male --in pairwise_similarity_annotations.jsonl.gz > pairwise_no_male.jsonl
tsumugi zygosity --keep Homo --in pairwise_similarity_annotations.jsonl.gz > pairwise_homo.jsonl
```

### 產生 GraphML / Web 應用
```bash
tsumugi build-graphml \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  > network.graphml

tsumugi build-webapp \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise genewise_phenotype_annotations.jsonl.gz \
```

管線示例：`zcat ... | tsumugi mp ... | tsumugi genes ... > out.jsonl`

# 🔍 表現型相似基因群的計算方法

## 資料來源
[IMPC Release-23.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-23.0/results) `statistical-results-ALL.csv.gz`  
欄位: [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)

## 前處理
擷取 KO 小鼠 P 值 (`p_value`, `female_ko_effect_p_value`, `male_ko_effect_p_value`) ≤ 0.0001 的基因–表現型。  
- Zygosity: `homo`, `hetero`, `hemi`  
- 性別: `female`, `male`

## 表現型相似度
TSUMUGI目前採用類似Phenodigm的方法。我們計算MP術語之間的**Resnik相似度**與祖先集合的**Jaccard相似度**，並以**幾何平均**合併。與原始Phenodigm的主要差異在於加入元資料加權（zygosity、life stage、sexual dimorphism）來彙總相似度。

1. 建立MP本體並計算資訊量(IC)：  
   `IC(term) = -log((|Descendants(term)| + 1) / |All MP terms|)`  
   IC低於第5百分位的術語設為0。
2. 對每個MP術語對，找出最具體的共同祖先(MICA)並以其IC作為Resnik。  
   計算祖先集合的Jaccard指數。  
   術語對相似度 = `sqrt(Resnik * Jaccard)`。
3. 對每個基因對建立術語×術語相似度矩陣並套用元資料加權。  
   zygosity/生命階段/性別二態性匹配數為0/1/2/3時，權重分別為0.25/0.5/0.75/1.0。
4. 以Phenodigm方式縮放到0–100：  
   使用行/列最大值得到實際max/mean。  
   以IC推得的理論max/mean正規化後計算  
   `Score = 100 * (normalized_max + normalized_mean) / 2`。  
   理論分母為0則設為0。

# ✉️ 聯絡
- Google 表單: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose
