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

**TSUMUGI** (Trait-driven Surveillance for Mutation-based Gene module Identification)は、[国際マウス表現型解析コンソーシアム（IMPC）](https://www.mousephenotype.org/)のノックアウト(KO)マウス表現型データを用いて、**KOマウスの表現型類似性を指標とした遺伝子ネットワークを抽出・可視化するWebツール**です。

ブラウザまたはコマンドラインからご利用いただけます👇️  

ブラウザはこちら： 🔗https://larc-tsukuba.github.io/tsumugi/  
コマンドラインの詳細はページ下部 (🛠 コマンドライン版) にございます。  

TSUMUGI(**紡ぎ**)には「表現型を織りなす遺伝子群を紡ぎ出す」という開発動機に即しています。  

# 📖[TSUMUGI](https://larc-tsukuba.github.io/tsumugi/)の使い方

## 💬 トップページ

TSUMUGIは、次の3種類の入力に対応しています。

### 表現型（Phenotype）

特定の表現型を1つ指定すると、KOマウスがその表現型を示す遺伝子の中から、**他の表現型も類似している遺伝子群**を探索します。  
表現型名は[Mammalian Phenotype Ontology（MPO）](https://www.informatics.jax.org/vocab/mp_ontology)に基づいています。

TSUMUGIで現在検索可能な表現型の一覧はこちら：  
👉 [表現型リスト](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### 遺伝子名（Gene）

特定の遺伝子を1つ指定すると、**そのKOマウスと類似する表現型をもつ他の遺伝子群**を探索します。  
遺伝子名は[MGI](http://www.informatics.jax.org/)に登録された遺伝子シンボルに準拠しています。

TSUMUGIで現在検索可能な遺伝子名の一覧はこちら：  
👉 [遺伝子名リスト](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)


### 遺伝子リスト(Gene List)

複数遺伝子をまとめて入力できます。  
遺伝子リストは改行区切りで入力してください。  

> [!NOTE]
> 遺伝子リストは遺伝子名（Gene）とは異なり、**リスト内の遺伝子同士**の表現型類似遺伝子を抽出します。

> [!CAUTION]
> **表現型類似遺伝子がひとつも見つからない**場合、
> `No similar phenotypes were found among the entered genes.`というアラートが表示され、処理が停止されます。
>
> **表現型類似遺伝子が200を超える**場合、
> `Too many genes submitted. Please limit the number to 200 or fewer.`というアラートが表示され、ブラウザの負荷を防ぐため処理が停止されます。


### 📥 生データのダウンロード

TSUMUGIで利用している表現型データを、Gzip圧縮JSONL形式でダウンロードできます。  

#### `genewise_phenotype_annotations.jsonl.gz`

遺伝子ごとの表現型情報がまとまっています。  
各レコードの内容は以下のとおりです：  

- 遺伝子シンボル（Gene symbol；例："1110059G10Rik"）  
- 遺伝子アクセッションID（Marker accession ID；例："MGI:1913452"）  
- 表現型名（Phenotype term name；例："fused joints"）  
- 表現型ID（Phenotype term ID；例："MP:0000137"）  
- 効果量（Effect size；例：0.0, 1.324）  
- 有意性（Statistical significance；True/false）  
- 接合型（Zygosity；"Homo", "Hetero", "Hemi"）  
- 発達段階（Life stage；"Embryo", "Early", "Interval", "Late"）  
- 性差情報（Sexual dimorphism；："None", "Male", "Female"）  
- 疾患注釈（Disease annotation；例：[]または "Premature Ovarian Failure 18" など）  

```json
{"life_stage": "Early", "marker_symbol": "1110059G10Rik", "marker_accession_id": "MGI:1913452", "effect_size": 0.0, "mp_term_name": "fused joints", "disease_annotation": [], "significant": false, "zygosity": "Homo", "sexual_dimorphism": "None", "mp_term_id": "MP:0000137"}
```

#### `pairwise_similarity_annotations.jsonl.gz`

遺伝子ペア間の表現型類似度をまとめたファイルです。  
各レコードの内容は以下のとおりです。  

- 遺伝子ペアの名称（gene1_symbol, gene2_symbol）  
- 共通する表現型の注釈情報（Phenotype shared annotations；各表現型ごとに発達段階、接合型、性差情報などを保持）  
- ペア間の表現型類似度（Phenotype similarity score；Resnik類似度に基づくPhenodigmスコア；0–100スケール）  

```json
{"gene1_symbol": "1110059G10Rik", "gene2_symbol": "Cog6", "phenotype_shared_annotations": {"vertebral transformation": {"zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "Male"}}, "phenotype_similarity_score": 42}
```

## 🌐 ネットワーク描出

入力内容に基づいてページが遷移し、ネットワークが自動的に描画されます。  

> [!IMPORTANT]
> **共通する異常表現型が3つ以上かつ表現型類似度が0.0よりも大きい**遺伝子ペアが、可視化の対象となります。  

### ネットワークパネル

#### ノード（点）

各ノードは1つの遺伝子を表します。  
クリックすると、そのKOマウスに観察された異常表現型のリストが表示されます。  
ドラッグで自由に位置を調整できます。  

#### エッジ（線）

エッジをクリックすると、共通表現型の詳細が確認できます。  

#### モジュール（囲み）

遺伝子群のサブネットワークは、ポリゴンで囲まれた「モジュール」として表示されます。  
モジュールをクリックすると、そのモジュールに含まれる遺伝子が関与する表現型がリストアップされます。  
モジュールはドラッグで移動でき、他のモジュールと重ならないように配置を調整できます。  

### コントロールパネル

左側のコントロールパネルでは、ネットワークの表示を調整することができます。  

#### 表現型類似度によるフィルター

`Phenotypes similarity`のスライダーでは、**エッジの表現型類似度**（Resnik類似度をPhenodigmスコアに変換した値）に基づいて、ネットワークに表示する遺伝子ペアの閾値を設定できます。  

> [!NOTE]
> 表現型類似度についての詳細は、以下を御覧ください  
> 👉 [🔍 表現型類似遺伝子群の算出方法](https://github.com/akikuno/TSUMUGI-dev/blob/main/doc/README_JP.md#-%E8%A1%A8%E7%8F%BE%E5%9E%8B%E9%A1%9E%E4%BC%BC%E9%81%BA%E4%BC%9D%E5%AD%90%E7%BE%A4%E3%81%AE%E7%AE%97%E5%87%BA%E6%96%B9%E6%B3%95)

#### 表現型重症度によるフィルター

`Phenotype severity`のスライダーでは、**KOマウスにおける表現型の重症度**（効果量）に基づいて、ノードの表示を調整できます。  
効果量が高いほど、表現型の影響が強く現れていることを示します。  

> [!NOTE]
> IMPCによる表現型の評価が二値（あり・なし）の場合（例: [abnormal embryo development](https://larc-tsukuba.github.io/tsumugi/app/phenotype/abnormal_embryo_development.html)：二値遺伝子のリストは[こちら](https://github.com/larc-tsukuba/tsumugi/blob/main/data/binary_phenotypes.txt)）や、遺伝子名が入力の場合には、`Phenotypes severity`のスライダーはありません。

#### 遺伝型を指定

表現型を呈するKOマウスの遺伝型を指定できます：

- `Homo`：ホモ接合型でみられる表現型
- `Hetero`: ヘテロ接合型でみられる表現型
- `Hemi`: ヘミ接合型でみられる表現型

#### 性差を指定

性特異的な表現型を抽出できます：

- `Female`: 雌特異的な表現型
- `Male`: 雄特異的な表現型

#### ライフステージを指定

表現型を呈するライフステージを指定できます：

- `Embryo`: 胎児期に現れる表現型
- `Early`: 0-16週齢に現れる表現型
- `Interval`: 17-48週齢に現れる表現型
- `Late`： 49週齢以上に現れる表現型

### マークアップパネル

#### ヒト疾患関連遺伝子のハイライト

ヒト疾患に関連する遺伝子をハイライト表示できます。  
KOマウスとヒト疾患の関連は、[IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/)の公開データを使用しています。  

#### 遺伝子名の検索

ネットワークに含まれる遺伝子名を検索できます。

#### ネットワーク図の表示スタイル調整

以下の要素を調整できます：

- ネットワークレイアウト(layout)
- フォントサイズ(Font size)
- エッジ（線）の太さ(Edge width)
- ノード（点）間の距離（＊Coseレイアウト限定） (Node repulsion)

#### エクスポート

現在のネットワークの画像およびデータを、PNG、JPEG、CSVおよびGraphML形式でエクスポートできます。  
CSVには、連結成分（モジュール）のIDと、各遺伝子のKOマウスが示す表現型の一覧が含まれます。  
GraphMLは、デスクトップ版Cytoscapeと互換性のある形式で、Cytoscapeにネットワークをインポートして分析することができます。  

# 🛠 コマンドライン版

TSUMUGIにはコマンドラインインターフェース（CLI）も付属しています。  
以下のように、Web版より柔軟なデータ操作が可能です。  

- 自前データで最新版を再計算: IMPC `statistical-results-ALL.csv.gz`（必要に応じて`mp.obo`と`impc_phenodigm.csv`も）を渡してネットワークを一括生成できます。
- MP用語の有無でフィルター: `tsumugi mp --include MP:xxxx`で含める、`--exclude MP:xxxx`で除外するなど、Web版より細かい指定が可能です。
- 遺伝子リストや生物学的アノテーションでの絞り込み・除外: 興味のある遺伝子リストやアノテーションに絞ってフィルターできます。
- 出力の拡張: Web版に比べてより大規模なネットワークに対して、GraphMLを直接生成(`tsumugi build-graphml`)したり、TSUMUGI用Webアプリ一式をオフライン向けに出力(`tsumugi build-webapp`)できます。

## 利用可能なコマンド一覧
- `tsumugi run`: IMPCデータからネットワークを再計算
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: 指定MP用語を含む/示さない遺伝子ペアまたは遺伝子単位でフィルター
- `tsumugi count --pairwise/--genewise (--min/--max)`: 表現型の数でフィルター（遺伝子ペア/遺伝子単位）
- `tsumugi score (--min/--max)`: 表現型類似度スコアでフィルター（遺伝子ペア）
- `tsumugi genes --keep/--drop`: 遺伝子リストで抽出または除外（カンマ区切りorテキストファイル）
- `tsumugi life-stage --keep/--drop`: ライフステージでフィルター (Embryo/Early/Interval/Late)
- `tsumugi sex --keep/--drop`: 性差でフィルター (Male/Female/None)
- `tsumugi zygosity --keep/--drop`: 接合型でフィルター (Homo/Hetero/Hemi)
- `tsumugi build-graphml`: GraphMLを生成（Cytoscape等で利用可能）
- `tsumugi build-webapp`: TSUMUGIのWebアプリ素材一式を生成（ローカルで閲覧可能）

## インストール

BioConda:

```bash
conda install -c conda-forge -c bioconda tsumugi
```

PyPI:

```bash
pip install tsumugi
```

`tsumugi --version`でバージョンが表示されれば利用可能です。

## 代表的な使い方（コマンド別）

### IMPCの統計データからTSUMUGIのWebアプリを生成する (`tsumugi run`)

```txt
tsumugi run [-h] -o OUTPUT_DIR -s STATISTICAL_RESULTS [-m MP_OBO] [-i IMPC_PHENODIGM] [-t THREADS]
```

**出力ディレクトリの指定 (必須)**  

TSUMUGIの解析結果を保存するディレクトリを指定します。  
途中経過ファイルおよび最終的な出力結果がすべてこのディレクトリに格納されます。

#### `-s STATISTICAL_RESULTS`, `--statistical_results STATISTICAL_RESULTS`
**IMPC表現型統計結果ファイルの指定 (必須)**

IMPCの`statistical_results_ALL.csv`へのパスを指定します。  
このファイルには、すべてのIMPC表現型実験における統計検定結果（効果量、p値など）が含まれています。

**取得先:**

```
https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/latest/TSUMUGI-results/
```

#### `-m MP_OBO`, `--mp_obo MP_OBO`
**哺乳類表現型オントロジーファイル(mp.obo)の指定（オプション）**

MP(Ontology)ファイルへのパスを指定します。  
TSUMUGIはこのファイルを用いて表現型用語間の階層関係を推論します。

`--mp_obo`を指定しない場合、TSUMUGIは同梱の`data-version: releases/2025-08-27/mp.obo`を利用します。  

**取得先:**
```
https://obofoundry.org/ontology/mp.html
```

#### `-i IMPC_PHENODIGM`, `--impc_phenodigm IMPC_PHENODIGM`
**Phenodigmアノテーションファイルの指定（オプション）**

IMPCの`impc_phenodigm.csv`へのパスを指定します。  
このファイルには、マウス表現型とヒト疾患をPhenodigm類似度に基づいて関連付けた情報が含まれています。

`--impc_phenodigm`を指定しない場合、2025-10-01に[IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/)から取得したファイルを利用します。

**取得先:**
```
https://diseasemodels.research.its.qmul.ac.uk/
```

#### `-t THREADS`, `--threads THREADS`
**並列処理スレッド数の指定（オプション）**

TSUMUGIパイプラインで使用するスレッド数を指定します。  
指定しない場合、デフォルトは`1`です。

#### 実行例

```bash
tsumugi run \
  --statistical_results ./statistical-results-ALL.csv.gz \
  --threads 8
```

上記の例では`./tsumugi-output`に遺伝子ごとの注釈（genewise_phenotype_annotations.jsonl.gz）、遺伝子ペアの類似度データ(pairwise_similarity_annotations.jsonl.gz)、可視化用素材(TSUMUGI-webapp)が生成されます。

>[!IMPORTANT]
> TSUMUGI-webappディレクトリにはOSごとの起動スクリプトが含まれています。  
> お使いのOSに合わせてダブルクリックするとローカルでTSUMUGIのWebアプリケーションを開けます。  
> - Windows: `open_webapp_windows.bat`
> - macOS: `open_webapp_mac.command`
> - Linux: `open_webapp_linux.sh`


### 表現型（MP term）でフィルター (`tsumugi mp --include/--exclude`)

興味のある表現型を持つ遺伝子ペアのみ抽出、または該当表現型を測定済みだが有意な異常を示さなかった遺伝子ペアを抽出できます。

```txt
tsumugi mp [-h] (-i MP_ID | -e MP_ID) [-g | -p] [-m MP_OBO] [-a GENEWISE_ANNOTATIONS] [--in IN]  [--life_stage LIFE_STAGE] [--sex SEX] [--zygosity ZYGOSITY]
```

#### `-i MP_ID`, `--include MP_ID`
**指定したMP表現型（下位語含む）を持つ遺伝子/遺伝子ペアを抽出（必須オプションの一つ）**  

#### `-e MP_ID`, `--exclude MP_ID`
**指定したMP表現型（下位語含む）を測定済みで「表現型が出なかった」遺伝子/遺伝子ペアを抽出（必須オプションの一つ）**  
`--exclude`を使う場合は`-a/--genewise_annotations`を指定してください。

#### `-g`, `--genewise`
**遺伝子単位でフィルター**  
`genewise_phenotype_annotations.jsonl(.gz)`を読み込み、有意な表現型の有無で抽出します。  
`--genewise`を使う場合は`-a/--genewise_annotations`を指定してください。

#### `-p`, `--pairwise`

**遺伝子ペア単位でフィルター (デフォルト)**  
`pairwise_similarity_annotations.jsonl(.gz)`を対象にします。`--in`未指定なら標準入力を読み込みます。

#### `-m MP_OBO`, `--mp_obo MP_OBO`
**哺乳類表現型オントロジーファイル(mp.obo)のパス（オプション）**  

`--mp_obo`を指定しない場合、TSUMUGIは同梱の`data-version: releases/2025-08-27/mp.obo`を利用します。  

#### `-a GENEWISE_ANNOTATIONS`, `--genewise_annotations GENEWISE_ANNOTATIONS`

**遺伝子注釈ファイルのパス（JSONL/.gz）**  
`--exclude`では必須です。`--genewise`での抽出時にも指定してください。

#### `--in IN`
**pairwise注釈ファイルのパス（JSONL/.gz）**  
未指定時は標準入力を読み込みます。

#### `--life_stage LIFE_STAGE`
**ライフステージで追加フィルター（オプション）**  
`Embryo`, `Early`, `Interval`, `Late`を指定可能。

#### `--sex SEX`
**性差で追加フィルター（オプション）**  
`Male`, `Female`, `None`など、注釈に記載された値を指定します。

#### `--zygosity ZYGOSITY`
**接合型で追加フィルター（オプション）**  
`Homo`, `Hetero`, `Hemi`を指定可能。

#### 実行例

```bash
# MP:0001146(abnormal testis morphology)とその下層の表現型（MP:0004849 (abnormal testis size)など）を含む遺伝子ペアだけを抽出
tsumugi mp --include MP:0001146 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

# MP:0001146(abnormal testis morphology)とその下層の表現型（MP:0004849 (abnormal testis size)など）を
# 測定しており、かつ有意な示さなかった遺伝子ペアを抽出
tsumugi mp --exclude MP:0001146 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

# 遺伝子単位でMP:0001146を含む有意な表現型のみを抽出
tsumugi mp --include MP:0001146 \
  --genewise \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  > genewise_filtered.jsonl

# 遺伝子単位でMP:0001146を測定済みかつ有意ではなかった遺伝子を抽出
tsumugi mp --exclude MP:0001146 \
  --genewise \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  > genewise_no_phenotype.jsonl
```

> [!IMPORTANT]
> **指定されたMP用語の下層にある用語も対処されます。**
> 例えば`MP:0001146 (abnormal testis morphology)`を指定した場合、`MP:0004849 (abnormal testis size)`などの下層用語も考慮されます。

### 表現型数でフィルターする(`tsumugi count`)
At least one of `--min` or `--max` is required. Use either alone for one-sided filtering.

```txt
tsumugi count [-h] (-g | -p) [--min MIN] [--max MAX] [--in IN]  [-a GENEWISE_ANNOTATIONS]
```

#### `-g`, `--genewise`
**遺伝子ごとの有意表現型数でフィルター**  
`-a/--genewise_annotations`で`genewise_phenotype_annotations.jsonl(.gz)`が必要です。

#### `-p`, `--pairwise`
**遺伝子ペアで共有する表現型数でフィルター**  
`--in`未指定なら標準入力から`pairwise_similarity_annotations.jsonl(.gz)`を読み込みます。

#### `--min MIN`, `--max MAX`
**最小/最大の閾値指定（少なくともどちらか一方が必須）**  
片方のみ指定して下限または上限フィルターとして利用できます。

#### `--in IN`
**pairwise注釈ファイルのパス（JSONL/.gz）**  
未指定時は標準入力を読み込みます。

#### `-a GENEWISE_ANNOTATIONS`, `--genewise_annotations GENEWISE_ANNOTATIONS`
**遺伝子注釈ファイルのパス（JSONL/.gz）**  
`--genewise`指定時は必須。

#### 実行例


- 遺伝子ペア内で共有する表現型の数でフィルター:  
```bash
tsumugi count --pairwise --min 3 --max 20 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_min3_max20.jsonl
```
- 遺伝子ごとの表現型数でフィルター（genewiseが必要）:  
```bash
tsumugi count --genewise --min 5 --max 50 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > genewise_min5_max50.jsonl
```
`--min`または`--max`を単独で指定しても使えます。


### 類似度スコアでフィルター (`tsumugi score`)
```txt
tsumugi score [-h] [--min MIN] [--max MAX] [--in IN]
```

表現型類似度スコア（0–100）で遺伝子ペアをフィルターします。`--min`または`--max`の少なくとも一方が必須です。

#### `--min MIN`, `--max MAX`
`phenotype_similarity_score`の下限/上限を指定します。片方だけでも指定できます。

#### `--in IN`
pairwise注釈ファイル（JSONL/.gz）のパス。未指定時は標準入力を読み込みます。

#### 実行例

```bash
tsumugi score --min 50 --max 80 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_score50_80.jsonl
```

`--min`または`--max`の片方だけでも利用できます。

### 遺伝子リストで絞り込み・除外する(`tsumugi genes --keep/--drop`)

```txt
tsumugi genes [-h] [-p | -g] (-k GENE_SYMBOLS | -d GENE_SYMBOLS) [--in IN] 
```

#### `-p`, `--pairwise`
**遺伝子ペア単位でフィルター (デフォルト)**  
`pairwise_similarity_annotations.jsonl(.gz)`を対象にします。`-p/--pairwise`を指定しない場合もこのモードになります。  
`-k/-d` に渡すのは遺伝子ペアを1行1レコードで書いたテキストファイル（CSV/TSV）です。
```text
Gene1,Gene2
Gene2,Gene3
```

#### `-g`, `--genewise`
**遺伝子単位でフィルター**  
`pairwise_similarity_annotations.jsonl(.gz)`を読み込み、指定した遺伝子リストを含む/含まないペアだけを残します。  
`-k/-d` はカンマ区切り（`GeneA,GeneB`）または1行1遺伝子のテキストファイルを指定できます。


#### `-k GENE_SYMBOLS`, `--keep GENE_SYMBOLS`
**指定条件に一致するものだけ残す（必須オプションの一つ）**  
pairwiseモードでは遺伝子ペアを並べたテキストファイルを指定します。  
genewiseモードではカンマ区切りまたは1行1遺伝子のテキストファイルを指定します。


#### `-d GENE_SYMBOLS`, `--drop GENE_SYMBOLS`
**指定条件に一致するものを除外（必須オプションの一つ）**  
pairwiseモードでは遺伝子ペアを並べたテキストファイルを指定します。  
genewiseモードではカンマ区切りまたは1行1遺伝子のテキストファイルを指定します。


#### `--in IN`
**pairwise注釈ファイルのパス（JSONL/.gz）**  
未指定時は標準入力を読み込みます（genewiseモードでも入力はpairwise JSONLです）。


#### 実行例

```bash
# pairwiseモード: リストに含まれる遺伝子ペアのみ残す
tsumugi genes --keep gene_pairs.txt \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_keep_gene_pairs.jsonl

# genewiseモード: 指定遺伝子を含むペアを除外
tsumugi genes --genewise --drop GeneA,GeneB \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_drop_genes.jsonl
```

### ライフステージでフィルターする(`tsumugi life-stage --keep/--drop`)

```txt
tsumugi life-stage [-h] (-k LIFE_STAGE | -d LIFE_STAGE) [--in IN] 
```

#### `-k LIFE_STAGE`, `--keep LIFE_STAGE`
**指定したライフステージのデータのみ残す（必須オプションの一つ）**  
指定可能: `Embryo`, `Early`, `Interval`, `Late`

#### `-d LIFE_STAGE`, `--drop LIFE_STAGE`
**指定したライフステージのデータを除外（必須オプションの一つ）**

#### `--in IN`
**pairwise注釈ファイルのパス（JSONL/.gz）**  
未指定時は標準入力を読み込みます。

#### 実行例

```bash
tsumugi life-stage --keep Early \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_lifestage_early.jsonl
```

### 性差でフィルターする(`tsumugi sex --keep/--drop`)

```txt
tsumugi sex [-h] (-k SEX | -d SEX) [--in IN] 
```

#### `-k SEX`, `--keep SEX`
**指定した性差のデータのみ残す（必須オプションの一つ）**  
指定可能: `Male`, `Female`, `None`

#### `-d SEX`, `--drop SEX`
**指定した性差のデータを除外（必須オプションの一つ）**

#### `--in IN`
**pairwise注釈ファイルのパス（JSONL/.gz）**  
未指定時は標準入力を読み込みます。

#### 実行例

```bash
tsumugi sex --drop Male \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_no_male.jsonl
```

### 接合型でフィルターする(`tsumugi zygosity --keep/--drop`)

```txt
tsumugi zygosity [-h] (-k ZYGOSITY | -d ZYGOSITY) [--in IN] 
```

#### `-k ZYGOSITY`, `--keep ZYGOSITY`
**指定した接合型のデータのみ残す（必須オプションの一つ）**  
指定可能: `Homo`, `Hetero`, `Hemi`

#### `-d ZYGOSITY`, `--drop ZYGOSITY`
**指定した接合型のデータを除外（必須オプションの一つ）**

#### `--in IN`
**pairwise注釈ファイルのパス（JSONL/.gz）**  
未指定時は標準入力を読み込みます。

#### 実行例


```bash
tsumugi zygosity --keep Homo \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_homo.jsonl
```

### 出力をGraphML／Webアプリに変換する

```txt
tsumugi build-graphml [-h] [--in IN] -a GENEWISE_ANNOTATIONS
```

#### `--in IN`
**pairwise注釈ファイルのパス（JSONL/.gz）**  
未指定時は標準入力を読み込みます。

#### `-a GENEWISE_ANNOTATIONS`, `--genewise_annotations GENEWISE_ANNOTATIONS`
**遺伝子注釈ファイルのパス（JSONL/.gz）**  
必須です。

#### 実行例

```bash
# GraphMLを生成（Cytoscape等で利用可能）
tsumugi build-graphml \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  > network.graphml
```

```txt
tsumugi build-webapp [-h] [--in IN] -a GENEWISE_ANNOTATIONS -o OUT
```

#### `--in IN`
**pairwise注釈ファイルのパス（JSONL/.gz）**  
未指定時は標準入力を読み込みます。

#### `-a GENEWISE_ANNOTATIONS`, `--genewise_annotations GENEWISE_ANNOTATIONS`
**遺伝子注釈ファイルのパス（JSONL/.gz）**  
必須です。

**出力ディレクトリの指定（必須）**  
指定先にWebアプリ用のHTML/CSS/JSとネットワークデータを生成します。

#### 実行例

```bash
# TSUMUGIのWebアプリ素材を生成（ローカルで開けるHTML/CSS/JS一式）
tsumugi build-webapp \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise genewise_phenotype_annotations.jsonl.gz \
```

CLIは標準入力・標準出力をサポートしているため、パイプでつなげて柔軟に処理できます。

```bash
zcat pairwise_similarity_annotations.jsonl.gz |
  tsumugi mp ... |
  tsumugi genes ... > out.jsonl
```

# 🔍 表現型類似遺伝子群の算出方法

## データソース

IMPCのデータセットは[Release-23.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-23.0/results)の`statistical-results-ALL.csv.gz`を使用しています。  
データセットに含まれる列の情報はこちらです：[Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)  

## 前処理

KOマウスの示す表現型のP値（`p_value` `female_ko_effect_p_value` `male_ko_effect_p_value`のいずれか）が0.0001以下の遺伝子-表現型を抽出します。  
- 遺伝型特異的な表現型には、`homo`, `hetero`または`hemi`を注釈します
- 性特異的な表現型には、`female`または`male`を注釈します

## 表現型類似度の計算

TSUMUGIではMammalian Phenotype (MP)用語間の**Resnik類似度**を算出し、その結果を基に遺伝子ペアのスコアを**Phenodigmスケール（0-100）**へ変換して表現型類似度を定義しています。

### 表現型用語間のResnik類似度

MPオントロジーの階層構造を構築し、各用語の子孫（自身を含む）との割合から情報量（Information Content; IC）を計算します：

```math
IC(term) = -log((子termの数 + 1) / MP用語総数)
```

任意の2用語に対して共通祖先を列挙し、そのうち**最も情報量が大きい共通祖先**(MICA)のICをResnik類似度とします：

```math
Resnik(term_1, term_2)=IC(MICA(term_1, term_2))
```

共通祖先が存在しない場合、類似度は0になります。

### 遺伝子ペアへのPhenodigmスケーリング

1. 各遺伝子ペアについて、有意なMP用語同士のResnik類似度をマトリクス化し、遺伝型（zygosity）、ライフステージ、性差の一致度に応じて 1.0 / 0.75 / 0.5 / 0.25 の重みを掛けます。  
2. 行・列ごとの最大値から、その遺伝子ペアで実際に観測された類似度の最大値・平均値を求めます。  
3. 個々のMP用語のICから、理論上達成しうる最大値・平均値を算出します。  
4. 実測値を理論値で正規化し、最大値と平均値の2つを平均してPhenodigmスコアを得ます：

```math
\mathrm{Phenodigm} = 100 \times \frac{1}{2} \left( 
\frac{\mathrm{actual_{max}}}{\mathrm{theoretical_{max}}} + 
\frac{\mathrm{actual_{mean}}}{\mathrm{theoretical_{mean}}}
\right)
```

この正規化によって得られる0〜100のスコアを生データおよびWeb UIの`Phenotypes similarity`スライダーで用いています。


# ✉️ お問い合わせ

ご質問やご要望は、以下にお気軽にお問い合わせください（日本語可）：

- **Googleフォーム**  
  👉 [お問い合わせフォーム](https://forms.gle/ME8EJZZHaRNgKZ979)

- **GitHubアカウント**をお持ちの方  
  👉 [GitHub Issue](https://github.com/akikuno/TSUMUGI-dev/issues/new/choose)
