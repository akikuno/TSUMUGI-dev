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
{"significant": true, "sexual_dimorphism": "Female", "effect_size": 0.0119677350763567, "marker_symbol": "4930447C04Rik", "zygosity": "Homo", "marker_accession_id": "MGI:1923051", "mp_term_id": "MP:0000063", "disease_annotation": ["Male Infertility With Azoospermia Or Oligozoospermia Due To Single Gene Mutation", "Premature Ovarian Failure 18", "Spermatogenic Failure 52"], "life_stage": "Early", "mp_term_name": "decreased bone mineral density"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- 基因對 (`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations`：共享表現型的中介資料（生命階段、接合型、性別差異）  
- `phenotype_similarity_score`：Resnik→Phenodigm 分數（0–100）

範例：
```
{"gene1_symbol": "1500009L16Rik", "gene2_symbol": "Aak1", "phenotype_shared_annotations": [{"mp_term_name": "increased circulating enzyme level", "life_stage": "Early", "zygosity": "Homo", "sexual_dimorphism": "None"}], "phenotype_similarity_score": 47}
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

# 🛠 命令列版

TSUMUGI CLI 允許使用本地下載的最新IMPC資料，並提供比網頁版更細緻的過濾與輸出。

## 功能

- 使用IMPC的`statistical-results-ALL.csv.gz`重新計算（可選`mp.obo`、`impc_phenodigm.csv`）。  
- 依MP術語包含/排除進行過濾。  
- 依基因清單過濾（逗號分隔或文字檔）。  
- 輸出：GraphML（`tsumugi build-graphml`）、離線Web應用包（`tsumugi build-webapp`）。

## 安裝

BioConda:
```bash
conda install -c conda-forge -c bioconda tsumugi
```

PyPI:
```bash
pip install tsumugi
```

`tsumugi --version`正常輸出即表示可用。

## 可用命令

- `tsumugi run`: 從IMPC資料重新計算網路  
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: 依MP術語包含/排除基因對或基因  
- `tsumugi count --pairwise/--genewise (--min/--max)`: 依表型數量過濾（基因對/基因）  
- `tsumugi score (--min/--max)`: 依表型相似度得分過濾（基因對）  
- `tsumugi genes --keep/--drop`: 基因清單保留/剔除（逗號或文字檔）  
- `tsumugi life-stage --keep/--drop`: 依生命階段過濾（Embryo/Early/Interval/Late）  
- `tsumugi sex --keep/--drop`: 依性別過濾（Male/Female/None）  
- `tsumugi zygosity --keep/--drop`: 依接合型過濾（Homo/Hetero/Hemi）  
- `tsumugi build-graphml`: 產生GraphML（Cytoscape等）  
- `tsumugi build-webapp`: 產生TSUMUGI Web應用資源（本地HTML/CSS/JS）

> [!NOTE]
> 所有過濾類子命令都會將JSONL輸出到STDOUT。  
> 如需存檔，請使用`>`重導向。

> [!IMPORTANT]
> 除`tsumugi run`外，所有命令都需要`pairwise_similarity_annotation.jsonl.gz`或`genewise_phenotype_annotation.jsonl.gz`。
> 兩個檔案都可以從[TSUMUGI首頁](https://larc-tsukuba.github.io/tsumugi/)下載。

## 使用方法

### 從IMPC資料重新計算（`tsumugi run`）
若省略`--mp_obo`，TSUMUGI使用內建`data-version: releases/2025-08-27/mp.obo`。  
若省略`--impc_phenodigm`，使用2025-10-01從[IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/)取得的檔案。
```bash
tsumugi run   --output_dir ./tsumugi-output   --statistical_results ./statistical-results-ALL.csv.gz   --threads 8
```
輸出：`./tsumugi-output`包含genewise註解（genewise_phenotype_annotations.jsonl.gz）、pairwise相似度資料（pairwise_similarity_annotations.jsonl.gz）與視覺化資源（`TSUMUGI-webapp`）。

> [!IMPORTANT]  
> `TSUMUGI-webapp`目錄包含各作業系統的啟動腳本；雙擊即可開啟本地Web應用：  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### 依MP術語過濾（`tsumugi mp --include/--exclude`）
擷取包含目標表型的基因對（或基因），或擷取已量測但未出現顯著異常的基因對。

```bash
tsumugi mp [-h] (-i MP_ID | -e MP_ID) [-g | -p] [-m PATH_MP_OBO] [-a PATH_GENEWISE_ANNOTATIONS] [--in PATH_PAIRWISE_ANNOTATIONS]
                  [--life_stage LIFE_STAGE] [--sex SEX] [--zygosity ZYGOSITY]
```

#### `-i MP_ID`, `--include MP_ID`
包含具有指定MP術語的基因/基因對（包含下位術語）。

#### `-e MP_ID`, `--exclude MP_ID`
回傳已量測該MP術語（包含下位術語）但未出現顯著表型的基因/基因對。需要`-a/--genewise_annotations`。

#### `-g`, `--genewise`
以基因層級過濾。讀取`genewise_phenotype_annotations.jsonl(.gz)`。使用`--genewise`時請指定`-a/--genewise_annotations`。

#### `-p`, `--pairwise`
以基因對層級過濾。目標為`pairwise_similarity_annotations.jsonl(.gz)`。若省略`--in`，從STDIN讀取。

#### `-m PATH_MP_OBO`, `--mp_obo PATH_MP_OBO`
哺乳類表型本體（mp.obo）路徑。省略時使用內建`data/mp.obo`。

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
genewise註解檔（JSONL/.gz）路徑。`--exclude`必需，`--genewise`時也需指定。

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise註解檔（JSONL/.gz）路徑。省略時從STDIN讀取。

#### `--life_stage LIFE_STAGE`
依生命階段追加過濾。可選值：`Embryo`, `Early`, `Interval`, `Late`。

#### `--sex SEX`
依性別差異追加過濾。使用註解中的值（如`Male`, `Female`, `None`）。

#### `--zygosity ZYGOSITY`
依接合型追加過濾。可選值：`Homo`, `Hetero`, `Hemi`。

```bash
# 僅擷取包含MP:0001146（abnormal testis morphology）或其下位術語（如MP:0004849 abnormal testis size）的基因對
tsumugi mp --include MP:0001146   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_filtered.jsonl

# 擷取已量測MP:0001146及其下位術語但未出現顯著異常的基因對
tsumugi mp --exclude MP:0001146   --genewise genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_filtered.jsonl

# 以基因擷取包含MP:0001146的顯著表型（含下位術語）
tsumugi mp --include MP:0001146   --genewise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > genewise_filtered.jsonl

# 以基因擷取已量測MP:0001146（含下位術語）但不顯著的基因
tsumugi mp --exclude MP:0001146   --genewise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > genewise_no_phenotype.jsonl
```

> [!IMPORTANT]
> **指定MP ID的下位術語也會被處理。**  
> 例如，指定`MP:0001146 (abnormal testis morphology)`時，也會包含`MP:0004849 (abnormal testis size)`等下位術語。

### 依表型數量過濾（`tsumugi count`）
```bash
tsumugi count [-h] (-g | -p) [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS] [-a PATH_GENEWISE_ANNOTATIONS]
```

依表型數量過濾基因或基因對。至少需要`--min`或`--max`之一。

#### `-g`, `--genewise`
依每個基因的顯著表型數量過濾。需要`-a/--genewise_annotations`與`genewise_phenotype_annotations.jsonl(.gz)`。

#### `-p`, `--pairwise`
依每個基因對的共享表型數量過濾。若省略`--in`，從STDIN讀取。

#### `--min MIN`, `--max MAX`
表型數量下限/上限。只指定一個也可進行單側過濾。

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise註解檔（JSONL/.gz）路徑。省略時從STDIN讀取。

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
genewise註解檔（JSONL/.gz）路徑。`--genewise`時必需。

- 基因對共享表型數量：
```bash
tsumugi count --pairwise --min 3 --max 20   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_min3_max20.jsonl
```

- 每個基因的表型數量（需genewise）：
```bash
tsumugi count --genewise --min 5 --max 50   --genewise genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > genewise_min5_max50.jsonl
```

只用`--min`或`--max`也可以。

### 依相似度得分過濾（`tsumugi score`）
```bash
tsumugi score [-h] [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS]
```

依`phenotype_similarity_score`（0–100）過濾基因對。至少需要`--min`或`--max`之一。

#### `--min MIN`, `--max MAX`
得分下限/上限。只指定一個也可進行單側過濾。

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise註解檔（JSONL/.gz）路徑。省略時從STDIN讀取。

```bash
tsumugi score --min 50 --max 80   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_score50_80.jsonl
```

只用`--min`或`--max`也可以。

### 依基因清單過濾（`tsumugi genes --keep/--drop`）
```bash
tsumugi genes [-h] (-k GENE_SYMBOL | -d GENE_SYMBOL) [-g | -p] [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k GENE_SYMBOL`, `--keep GENE_SYMBOL`
僅保留包含指定基因的基因對（以文字檔提供）。

#### `-d GENE_SYMBOL`, `--drop GENE_SYMBOL`
移除包含指定基因的基因對（以文字檔提供）。

#### `-g`, `--genewise`
依使用者提供的基因符號過濾。

#### `-p`, `--pairwise`
依使用者提供的基因對過濾。

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise註解檔（JSONL/.gz）路徑。省略時從STDIN讀取。

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

### 依生命階段過濾（`tsumugi life-stage --keep/--drop`）
```bash
tsumugi life-stage [-h] (-k LIFE_STAGE | -d LIFE_STAGE) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k LIFE_STAGE`, `--keep LIFE_STAGE`
僅保留指定生命階段（`Embryo`, `Early`, `Interval`, `Late`）。

#### `-d LIFE_STAGE`, `--drop LIFE_STAGE`
移除指定生命階段。

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise註解檔（JSONL/.gz）路徑。省略時從STDIN讀取。

```bash
tsumugi life-stage --keep Early   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_lifestage_early.jsonl
```

### 依性別過濾（`tsumugi sex --keep/--drop`）
```bash
tsumugi sex [-h] (-k SEX | -d SEX) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k SEX`, `--keep SEX`
僅保留指定性別（`Male`, `Female`, `None`）。

#### `-d SEX`, `--drop SEX`
移除指定性別。

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise註解檔（JSONL/.gz）路徑。省略時從STDIN讀取。

```bash
tsumugi sex --drop Male   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_no_male.jsonl
```

### 依接合型過濾（`tsumugi zygosity --keep/--drop`）
```bash
tsumugi zygosity [-h] (-k ZYGOSITY | -d ZYGOSITY) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k ZYGOSITY`, `--keep ZYGOSITY`
僅保留指定接合型（`Homo`, `Hetero`, `Hemi`）。

#### `-d ZYGOSITY`, `--drop ZYGOSITY`
移除指定接合型。

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise註解檔（JSONL/.gz）路徑。省略時從STDIN讀取。

```bash
tsumugi zygosity --keep Homo   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_homo.jsonl
```

### 匯出GraphML / webapp
```bash
tsumugi build-graphml [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise註解檔（JSONL/.gz）路徑。省略時從STDIN讀取。

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
genewise註解檔（JSONL/.gz）路徑。必需。

```bash
tsumugi build-graphml   --in pairwise_similarity_annotations.jsonl.gz   --genewise genewise_phenotype_annotations.jsonl.gz   > network.graphml
```

```bash
tsumugi build-webapp [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS -o OUT
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise註解檔（JSONL/.gz）路徑。省略時從STDIN讀取。

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
genewise註解檔（JSONL/.gz）路徑。必需。

#### `-o OUT`, `--out OUT`
Webapp輸出目錄（HTML/CSS/JS + 網路資料）。不要指定帶副檔名的檔名。

```bash
tsumugi build-webapp   --in pairwise_similarity_annotations.jsonl.gz   --genewise genewise_phenotype_annotations.jsonl.gz   --output_dir ./webapp_output
```

CLI支援STDIN/STDOUT，可串聯命令：  
`zcat pairwise_similarity_annotations.jsonl.gz | tsumugi mp ... | tsumugi genes ... > out.jsonl`

# 🔍 表現型相似基因群的計算方法

## 資料來源

使用IMPC資料集[Release-23.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-23.0/results) `statistical-results-ALL.csv.gz`。  
資料欄位資訊：[Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)  

## 前處理

擷取KO小鼠P-value（`p_value`、`female_ko_effect_p_value`或`male_ko_effect_p_value`）≤ 0.0001的基因–表現型配對。  
- 基因型特異表現型標註為`homo`、`hetero`或`hemi`。  
- 性別特異表現型標註為`female`或`male`。

## 表現型相似度

TSUMUGI採用類Phenodigm方法（[Smedley D, et al. (2013)](https://doi.org/10.1093/database/bat025)）。  

> [!NOTE]
> 與原始Phenodigm的差異如下。  
> 1. **IC低於第5百分位的術語設定為IC=0，以避免評估過於一般的表現型（例如embryo phenotype）。**
> 2. **根據基因型、生命階段與性別的中繼資料匹配進行加權。**

### 1. MP術語對相似度定義

* 建立MP本體並計算每個術語的資訊量（IC）：  
   `IC(term) = -log((|Descendants(term)| + 1) / |All MP terms|)`  
   IC低於第5百分位的術語設定為IC=0。

* 對每個MP術語對，找出最特異的共同祖先（MICA），並以其IC作為Resnik相似度。  

* 對兩個MP術語，計算其祖先集合的Jaccard指數。  

* 將MP術語對相似度定義為`sqrt(Resnik * Jaccard)`。

### 2. 依表現型中繼資料一致性加權

* 根據表現型中繼資料（基因型、生命階段、性別）進行加權。

* 對每個基因對建立MP術語×MP術語相似度矩陣。  

* 對基因型/生命階段/性別匹配數為0、1、2、3時，分別乘以0.2、0.5、0.75、1.0的權重。

### 3. Phenodigm縮放

* 使用Phenodigm式縮放，將每個KO小鼠的表現型相似度正規化為0–100：  
   計算觀測的最大值/平均值，並用理論最大值/平均值正規化。  
   `Score = 100 * (normalized_max + normalized_mean) / 2`  
   若分母為0，分數為0。

---

# ✉️ 聯絡
- Google 表單: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose
