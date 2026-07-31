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
[![Preprint](https://img.shields.io/badge/bioRxiv-10.64898/2026.02.18.706720-red)](https://doi.org/10.64898/2026.02.18.706720)
[![DOI](https://zenodo.org/badge/441025227.svg)](https://doi.org/10.5281/zenodo.14957711)
[![Contact](https://img.shields.io/badge/Contact-923DE2)](https://forms.gle/ME8EJZZHaRNgKZ979)

**TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification)** 使用 [IMPC](https://www.mousephenotype.org/) KO 小鼠的表型資料，**依表型相似性萃取並視覺化基因模組**的網路工具。  
此工具開放給所有人使用👇️  
🔗https://larc-tsukuba.github.io/tsumugi/

本文件說明**TSUMUGI v1.1.1**的現行功能。公開Web應用程式使用IMPC **Release 24.0**資料。

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
> 如果沒有找到相似基因：`No similar phenotypes were found among the entered genes.`
> Gene List最多接受200個不同且可用的基因。計數前會移除重複符號與空行；不可用符號會被報告並排除。包含201個或更多可用基因的清單會在載入網路資料前被拒絕。

### 📥 下載原始資料
TSUMUGI 發佈 gzip 壓縮的 JSONL 檔。

#### `genewise_phenotype_annotations.jsonl.gz`
- 基因符號（例："1110059G10Rik"）  
- Marker accession ID（例："MGI:1913452"）  
- 表現型名稱/ID（例："fused joints", "MP:0000137"）  
- Effect size（`number`或`null`；例：0.0, 1.324）
- 顯著性標記（IMPC異常表現型註釋為`true`；已映射但沒有顯著異常的測量為`false`）
- 接合型（"Homo", "Hetero", "Hemi"）  
- 生命階段（"Embryo", "Early", "Interval", "Late"）  
- 性別差異（`None`、`Male`、`Female`）
- 疾病註解（例：[] 或 "Premature Ovarian Failure 18"）

範例：
```
{"significant": true, "sexual_dimorphism": "Female", "effect_size": 0.0119677350763567, "marker_symbol": "4930447C04Rik", "zygosity": "Homo", "marker_accession_id": "MGI:1923051", "mp_term_id": "MP:0000063", "disease_annotation": ["Male Infertility With Azoospermia Or Oligozoospermia Due To Single Gene Mutation", "Premature Ovarian Failure 18", "Spermatogenic Failure 52"], "life_stage": "Early", "mp_term_name": "decreased bone mineral density"}
```

#### `pairwise_similarity_annotations.jsonl.gz`
- 基因對 (`gene1_symbol`, `gene2_symbol`)  
- `phenotype_shared_annotations`（元資料一致的MICA脈絡：MP術語、生命階段、接合型與性別標籤）
- `phenotype_similarity_score`（Phenodigm分數，0–100）

範例：
```
{"gene1_symbol": "1500009L16Rik", "gene2_symbol": "Aak1", "phenotype_shared_annotations": [{"mp_term_name": "increased circulating enzyme level", "life_stage": "Early", "zygosity": "Homo", "sexual_dimorphism": "None"}], "phenotype_similarity_score": 47}
```

## 解讀注意事項

- **共享脈絡：** `phenotype_shared_annotations`中的每個項目，都是兩條顯著MP註釋在接合型、生命階段與性別標籤一致時得到的資訊量最大共同祖先（MICA）。這不一定表示兩個基因都直接註釋了同一個葉節點MP術語。同一個MICA在元資料不同時可作為不同脈絡出現。
- **顯示規則：** Gene與Phenotype頁面顯示共享異常表現型脈絡不少於3個且相似度分數大於0的基因配對。Gene List要求輸入基因之間至少有1個共享脈絡。這些是顯示規則，不是統計顯著性標準。
- **相似度顯示：** 發布的`phenotype_similarity_score`是0–100的Phenodigm分數。Web應用會把每個目前網路中的可用值重新縮放到1–100，因此不同頁面的滑桿值與提示值不能當作統一的絕對尺度比較。
- **效應量顯示：** TSUMUGI取IMPC效應量的絕對值，進行`log1p`轉換，並在目標表現型內重新縮放到1–100。該值僅用於頁面內排序，不是原始效應量，也不能在不同表現型頁面之間直接比較。缺失值維持為JSON `null`，對應節點顯示為白色。
- **模組：** 模組只是視覺分組，並不是分子路徑或蛋白質複合體的證據。`Similarity`表示連通分量，`Top-level MP`表示基於本體的分組；Gene頁面的soft/fuzzy模組允許一個基因屬於多個模組。模組節點數篩選器只限制目前顯示的模組。
- **性別標籤：** `Female`表示只有雌性KO效應P-value≤0.0001；`Male`表示只有雄性KO效應P-value≤0.0001。兩個選項在Web介面中互斥，不能取代正式的性別×基因型交互作用檢定。
- **表現型醒目提示：** 同一表現型的不同元資料變體會合併為一個選項。當Human Disease與一個或多個表現型在同一基因上重疊時，各類別以同心圓顯示。
- **疾病醒目提示：** IMPC Disease Models Portal的註釋只提供疾病模型相似性證據，不能單獨確立人類基因–疾病因果關係。
- **非顯著記錄：** 這表示在對應條件下已完成映射測量，但沒有顯著異常註釋。它不能證明動物正常或表現型不存在；`disease_annotation`維持為空。
- **分數含義：** TSUMUGI分數不是P-value、效應量、結合親和力，也不是基因間因果交互作用的證據。

# 🌐 網路

系統會依輸入自動繪製網路。

> [!IMPORTANT]
> Gene與Phenotype頁面顯示共享異常表現型脈絡不少於3個且相似度分數大於0的基因配對；Gene List要求輸入基因之間至少有1個共享脈絡。這些是顯示規則，不是統計顯著性標準。

### 網路面板
**節點**代表基因。點擊可查看該 KO 小鼠的異常表現型清單，拖曳可調整位置。  
**邊**點擊可查看共享表現型的詳細。  
**模組**以多邊形圈出基因子網絡。點擊模組可列出其中基因涉及的表現型；可拖曳模組重新擺放並避免重疊。
Gene頁面使用soft/fuzzy Top-level MP模組，因此一個基因可以屬於多個模組。Phenotype與Gene List頁面可在基於連通分量的`Similarity`模組與`Top-level MP`模組之間切換。

### 控制面板
可於左側調整網路顯示。

#### 依表現型相似度過濾
`Phenotypes similarity`依顯示用相似度值過濾邊。發布的`phenotype_similarity_score`範圍為0–100，但每個顯示網路都會重新縮放到1–100，因此不同頁面的值不能直接比較。
> 計算詳情：👉 [🔍 表現型相似基因群的計算方法](#-表現型相似基因群的計算方法)

#### 依 effect size 過濾
`Effect size`依頁面特定的顯示值過濾節點。TSUMUGI取IMPC效應量的絕對值，進行`log1p`轉換，並在目標表現型內重新縮放到1–100。該值只用於頁面內排序，不是原始效應量，也不能在不同表現型頁面之間比較。
缺失的`effect_size`在JSONL中序列化為標準JSON的`null`，其語義仍為缺失值而不會轉換為0；相應節點顯示為白色。
> 對二值表現型（如 abnormal embryo development; 二值列表見[此處](https://github.com/larc-tsukuba/tsumugi/blob/main/data/binary_phenotypes.txt)）或單一基因輸入時，此控制隱藏。

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
#### 模組顯示
可在右側面板選擇模組定義與目前顯示的模組。隱藏模組邊框不會從網路中移除基因或邊。

#### Highlight: Phenotype
根據表現型註釋醒目提示基因。同一表現型的不同元資料變體會合併為一個選項。當Human Disease與至少一個表現型在同一基因上重疊時，各類別以同心圓顯示。

#### Highlight: Human Disease
醒目提示在IMPC Disease Models Portal中具有疾病模型註釋的KO基因。該註釋表示模型相似性，不能單獨確立人類基因–疾病因果關係。

#### Search: Specific Gene
於網路中搜尋基因名。

#### Layout & Display
調整布局、字體大小、邊線粗細、節點斥力（Cose 布局）。

#### Export
可匯出PNG、JPG、SVG、CSV或GraphML。PNG、JPG與SVG可選擇包含模組邊框。CSV記錄目前Similarity或Top-level MP模組分配與表現型列表；GraphML與Cytoscape相容。

# 🛠 命令列版

TSUMUGI CLI 允許使用本地下載的最新IMPC資料，並提供比網頁版更細緻的過濾與輸出。

## 功能

- 使用IMPC的`statistical-results-ALL.csv.gz`重新計算（可選`mp.obo`、`impc_phenodigm.csv`）。  
- 依顯著MP註釋或已映射的非顯著測量記錄進行過濾。
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
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: 依顯著MP註釋或已映射的非顯著測量記錄過濾基因配對或基因
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
> 除`tsumugi run`外，所有命令都需要`pairwise_similarity_annotations.jsonl.gz`或`genewise_phenotype_annotations.jsonl.gz`。
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
tsumugi mp [-h] (-i MP_ID | -e MP_ID) (-g | -p) [-m PATH_MP_OBO] [-a PATH_GENEWISE_ANNOTATIONS] [--in PATH_PAIRWISE_ANNOTATIONS]
                  [--life_stage LIFE_STAGE] [--sex SEX] [--zygosity ZYGOSITY]
```

#### `-i MP_ID`, `--include MP_ID`
包含具有指定MP術語的基因/基因對（包含下位術語）。

#### `-e MP_ID`, `--exclude MP_ID`
回傳已量測該MP術語（包含下位術語）但未出現顯著表型的基因/基因對。需要`-a/--genewise_annotations`。

> [!CAUTION]
> 非顯著記錄不能證明動物正常或表現型不存在。它只表示映射測量在該條件下沒有產生顯著異常註釋。

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
tsumugi mp --include MP:0001146   --pairwise   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_filtered.jsonl

# 擷取已量測MP:0001146及其下位術語但未出現顯著異常的基因對
tsumugi mp --exclude MP:0001146   --pairwise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_without_significant_testis_phenotype.jsonl

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
tsumugi count --genewise --min 5 --max 50   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_genes_with_5_to_50_phenotypes.jsonl
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
tsumugi genes [-h] (-k GENE_SYMBOL | -d GENE_SYMBOL) (-g | -p) [--in PATH_PAIRWISE_ANNOTATIONS]
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

tsumugi genes --genewise --keep genes.txt   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_keep_genes.jsonl

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
tsumugi build-graphml   --in pairwise_similarity_annotations.jsonl.gz   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > network.graphml
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
tsumugi build-webapp   --in pairwise_similarity_annotations.jsonl.gz   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   --out ./webapp_output
```

CLI支援STDIN/STDOUT，可串聯命令：  
`tsumugi score --min 50 --in pairwise_similarity_annotations.jsonl.gz | tsumugi sex --drop Male > pairwise_score50_no_male.jsonl`

# 🔍 表現型相似基因群的計算方法

## 資料來源

使用IMPC資料集[Release 24.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-24.0/results) `statistical-results-ALL.csv.gz`。
資料欄位資訊：[Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)  

## 前處理

TSUMUGI將IMPC `mp_term_id`非空的記錄視為IMPC異常表現型註釋。同時保留已映射但沒有顯著異常註釋的測量記錄，用於考量是否完成測量的排除查詢。
對於非顯著測量，`intermediate_mp_term_id`中ontology上互不可比的最具體非根術語會分別輸出為獨立記錄。僅映射至`MP:0000001`或未映射至有效MP術語的測量無法支援表現型特異查詢，因此不予輸出。

- 將接合型轉換為`Homo`、`Hetero`或`Hemi`。
- 僅`female_ko_effect_p_value`≤0.0001時標記為`Female`，僅`male_ko_effect_p_value`≤0.0001時標記為`Male`，其他情況標記為`None`。
- 使用效應量的絕對值。缺失值維持缺失，並在JSON中序列化為`null`。

## 表現型相似度

TSUMUGI使用PhenoDigm原始評分公式（[Smedley D, et al. (2013)](https://doi.org/10.1093/database/bat025)），在Mammalian Phenotype Ontology內比較IMPC KO小鼠基因的表現型譜。

> [!NOTE]
> TSUMUGI使用PhenoDigm評分公式，但不執行原始的跨物種HPO-MP/ZP OWLSim pipeline。它比較IMPC KO小鼠基因的MP annotation。

### 1. MP術語對相似度定義

* 建立MP本體，並依據顯著IMPC annotation計算Information Content（IC）：
   `IC(term) = -log2(|傳播到該術語的annotation| / |全部顯著annotation|)`
   每個直接annotation都會傳播到被註解的MP術語及其全部ancestor。

* 對每個MP術語對，尋找annotation-derived IC最高的共同ancestor。若候選同分，則依序確定性選擇MP本體中transitive descendant較少的候選，以及字典序較小的MP term ID。所選MICA的IC作為Resnik相似度。此tie-break不改變相似度分數或輸出schema。
   並列候選的術語配對數值分數相同，但所選MICA標籤可能改變共享脈絡數量，進而影響是否符合顯示條件。

* 對兩個MP術語，計算其inferred attribute集合的Jaccard指數；此集合定義為術語本身及其全部ancestor。

* 將MP術語對相似度定義為`sqrt(Resnik * Jaccard)`。

### 2. 基因對相似度矩陣

* 對每個基因對，依據術語對分數建立MP術語×MP術語相似度矩陣。

* 只有在接合型、生命階段與性別標籤一致時，才把MICA記錄到`phenotype_shared_annotations`中。這些元資料不會對PhenoDigm分數加權。

### 3. Phenodigm縮放

* 使用PhenoDigm maximum/average scaling，將每個KO小鼠基因對的相似度正規化為0–100：
   計算觀測best match的maximum/mean，再使用兩個基因對稱的optimal self-match score進行正規化。
   `Score = 100 * (normalized_max + normalized_mean) / 2`  
   若分母為0，分數為0。

最終分數衡量表現型譜相似度。它不是P-value、效應量、結合親和力，也不是基因間因果交互作用的證據。

---

# ✉️ 聯絡
- Google 表單: https://forms.gle/ME8EJZZHaRNgKZ979  
- GitHub Issues: https://github.com/akikuno/TSUMUGI-dev/issues/new/choose


---

# 📄 引用

Kuno A, Matsumoto K, Taki T, Takahashi S, and Mizuno S  
**TSUMUGI: a platform for phenotype-driven gene network identification from comprehensive knockout mouse phenotyping data**  
*bioRxiv*. (2026) https://doi.org/10.64898/2026.02.18.706720  
