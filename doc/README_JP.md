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

**TSUMUGI** (Trait-driven Surveillance for Mutation-based Gene module Identification)は、[国際マウス表現型解析コンソーシアム（IMPC）](https://www.mousephenotype.org/)のノックアウト(KO)マウス表現型データを用いて、**KOマウスの表現型類似性を指標とした遺伝子ネットワークを抽出・可視化するWebツール**です。

ブラウザまたはコマンドラインからご利用いただけます👇️  

ブラウザはこちら： 🔗https://larc-tsukuba.github.io/tsumugi/  
コマンドラインの詳細はページ下部 (🛠 コマンドライン版) にございます。  


TSUMUGI(**紡ぎ**)の由来は、「表現型を織りなす遺伝子群を紡ぎ出す」という開発動機に即しています。  

この文書は**TSUMUGI v1.1.1**を説明しています。

| 対象 | ソフトウェア版またはデータ版 |
| --- | --- |
| この文書で説明するソースコードとCLI | TSUMUGI v1.1.1 |
| 公開Web版 | TSUMUGI v1.1.0（2026-07-31確認、v1.1.1は未配備） |
| 公開Web版が使用するデータ | IMPC Release 24.0 |

過去のソフトウェア版は[Zenodo](https://zenodo.org/records/21480711)から取得できます。

---

# 📖[TSUMUGI](https://larc-tsukuba.github.io/tsumugi/)の使い方

## 💬 トップページ

トップページでは、データの入力と、生データのダウンロードが可能です。  

TSUMUGIは、次の3種類の入力に対応しています。

### 1. 表現型（Phenotype）

特定の表現型を1つ指定すると、KOマウスがその表現型を示す遺伝子の中から、**他の表現型も類似している遺伝子群**を探索します。  
表現型名は[Mammalian Phenotype（MP）ontology](https://www.informatics.jax.org/vocab/mp_ontology)に基づいています。

TSUMUGIで現在検索可能な表現型の一覧はこちら：  
👉 [表現型リスト](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### 2. 遺伝子名（Gene）

特定の遺伝子を1つ指定すると、**そのKOマウスと類似する表現型をもつ他の遺伝子群**を探索します。  
遺伝子名は[MGI](http://www.informatics.jax.org/)に登録された遺伝子シンボルに準拠しています。

TSUMUGIで現在検索可能な遺伝子名の一覧はこちら：  
👉 [遺伝子名リスト](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)


### 3. 遺伝子リスト(Gene List)

複数遺伝子をまとめて入力できます。  
遺伝子リストは改行区切りで入力してください。  

> [!NOTE]
> 遺伝子リストは遺伝子名（Gene）とは異なり、**リスト内の遺伝子同士**の表現型類似遺伝子を抽出します。

> [!CAUTION]
> **表現型類似遺伝子がひとつも見つからない**場合、
> `No similar phenotypes were found among the entered genes.`というアラートが表示され、処理が停止されます。
>
> 空行と重複を除き、利用可能な遺伝子を最大200件まで入力できます。利用できない遺伝子は警告後に除外されます。
> 利用可能な遺伝子が201件以上入力された場合、
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
- 効果量の絶対値（Effect size；`number`または`null`、例：1.324）
- 有意性（`true`はIMPCの異常表現型注釈、`false`は有意な異常注釈が得られなかった対応測定）
- 接合型（Zygosity；"Homo", "Hetero", "Hemi"）  
- 発達段階（Life stage；"Embryo", "Early", "Interval", "Late"）  
- 性差情報（Sexual dimorphism；："None", "Male", "Female"）  
- 疾患注釈（Disease annotation；例：[]または "Premature Ovarian Failure 18" など）  

```json
{"significant": true, "sexual_dimorphism": "Female", "effect_size": 0.0119677350763567, "marker_symbol": "4930447C04Rik", "zygosity": "Homo", "marker_accession_id": "MGI:1923051", "mp_term_id": "MP:0000063", "disease_annotation": ["Male Infertility With Azoospermia Or Oligozoospermia Due To Single Gene Mutation", "Premature Ovarian Failure 18", "Spermatogenic Failure 52"], "life_stage": "Early", "mp_term_name": "decreased bone mineral density"}
```

#### `pairwise_similarity_annotations.jsonl.gz`

遺伝子ペア間の表現型類似度をまとめたファイルです。  
各レコードの内容は以下のとおりです。  

- 遺伝子ペアの名称（gene1_symbol, gene2_symbol）  
- メタデータが一致するMICAの注釈情報（Phenotype shared annotations；MP用語、発達段階、接合型、性差情報を保持）
- ペア間の表現型類似度（Phenotype similarity score；Resnik類似度に基づくPhenodigmスコア；0–100スケール）  

各共有contextは、接合型、ライフステージ、性差ラベルが一致する2つの有意MP注釈から得た、最も情報量の高い共通祖先（MICA）です。両遺伝子に同じ末端MP用語が直接注釈されたことを意味しません。同じMICAでもメタデータが異なれば、別のcontextとして扱います。

```json
{"gene1_symbol": "1500009L16Rik", "gene2_symbol": "Aak1", "phenotype_shared_annotations": [{"mp_term_name": "increased circulating enzyme level", "life_stage": "Early", "zygosity": "Homo", "sexual_dimorphism": "None"}], "phenotype_similarity_score": 47}
```

## 🌐 ネットワーク描出

入力内容に基づいてページが遷移し、ネットワークが自動的に描画されます。  

> [!IMPORTANT]
> GeneページとPhenotypeページでは、**共通する異常表現型contextが3件以上かつ表現型類似度が0.0よりも大きい**遺伝子ペアが可視化の対象となります。
> Gene Listでは、入力遺伝子間で共通する異常表現型contextが1件以上ある遺伝子ペアを可視化します。
> これらは表示条件であり、統計的有意性の基準ではありません。

ネットワーク図には、中央のネットワークパネルと、左右のコントロールパネルおよびマークアップパネル、そして下部のエクスポートパネルがあります。

### 1. ネットワークパネル

#### ノード（点）

各ノードは1つの遺伝子を表します。  
クリックすると、そのKOマウスに観察された異常表現型のリストが表示されます。  
ドラッグで自由に位置を調整できます。  

#### エッジ（線）

エッジをクリックすると、共通表現型の詳細が確認できます。  

#### モジュール（囲み）

モジュールは表示上のグループであり、分子経路やタンパク質複合体の証拠ではありません。遺伝子ページではTop-level MPに基づくsoft/fuzzy moduleを使用するため、1つの遺伝子が複数のモジュールに所属することがあります。表現型ページとGene Listページでは、連結成分に基づく`Similarity`モジュールと、ontologyに基づく`Top-level MP`モジュールを切り替えられます。モジュールのノード数フィルターにより、構成遺伝子数の範囲で表示対象を絞り込めます。
モジュールをクリックすると、そのモジュールに含まれる遺伝子が関与する表現型がリストアップされます。  
モジュールはドラッグで移動でき、他のモジュールと重ならないように配置を調整できます。  

### 2. コントロールパネル

左側のコントロールパネルでは、ネットワークの表示を調整することができます。  

#### 表現型類似度によるフィルター

`Phenotypes similarity`のスライダーでは、表示用の表現型類似度に基づいてエッジを絞り込めます。配布データの`phenotype_similarity_score`は0–100のPhenodigmスコアですが、Web版は各ネットワーク内の値を1–100へ再尺度化します。異なるページのスライダー値やツールチップ値を共通の絶対尺度として比較できません。

> [!NOTE]
> 表現型類似度についての詳細は、以下を御覧ください  
> 👉 [🔍 表現型類似遺伝子群の算出方法](https://github.com/akikuno/TSUMUGI-dev/blob/main/doc/README_JP.md#-%E8%A1%A8%E7%8F%BE%E5%9E%8B%E9%A1%9E%E4%BC%BC%E9%81%BA%E4%BC%9D%E5%AD%90%E7%BE%A4%E3%81%AE%E7%AE%97%E5%87%BA%E6%96%B9%E6%B3%95)

#### 効果量によるフィルター

`Effect size`のスライダーでは、ページ内で再尺度化した表示値に基づいてノードを絞り込めます。TSUMUGIはIMPC由来の効果量の絶対値を`log1p`変換し、対象表現型内で1–100へ再尺度化します。この値はページ内の順位を確認するための指標であり、生の効果量ではありません。異なる表現型ページ間で直接比較できません。

欠損した`effect_size`はJSONLで標準JSONの`null`として出力します。0ではなく欠損値として扱い、該当するノードは白色で表示します。

> [!NOTE]
> IMPCによる表現型の評価が二値（あり・なし）の場合（例: [abnormal embryo development](https://larc-tsukuba.github.io/tsumugi/app/phenotype/abnormal_embryo_development.html)：二値遺伝子のリストは[こちら](https://github.com/larc-tsukuba/tsumugi/blob/main/data/binary_phenotypes.txt)）や、遺伝子名が入力の場合には、`Effect size`のスライダーはありません。

#### 遺伝型を指定

表現型を呈するKOマウスの遺伝型を指定できます：

- `Homo`：ホモ接合型でみられる表現型
- `Hetero`: ヘテロ接合型でみられる表現型
- `Hemi`: ヘミ接合型でみられる表現型

#### 性差を指定

性別ごとの証拠ラベルで絞り込めます：

- `Female`: 雌KOの効果のP値だけが0.0001以下
- `Male`: 雄KOの効果のP値だけが0.0001以下

Web版では両者を同時に選択できません。このラベルは、性別と遺伝型の正式な交互作用検定を表すものではありません。

#### ライフステージを指定

表現型を呈するライフステージを指定できます：

- `Embryo`: 胎児期に現れる表現型
- `Early`: 0-16週齢に現れる表現型
- `Interval`: 17-48週齢に現れる表現型
- `Late`： 49週齢以上に現れる表現型

### 3. マークアップパネル

#### モジュール表示

右側のパネルでモジュールの定義と表示対象を選択できます。モジュールの境界線を非表示にしても、ネットワーク内の遺伝子やエッジは削除されません。

#### 表現型のハイライト

表現型注釈に基づいて遺伝子をハイライト表示できます。同じ表現型の接合型、ライフステージ、性差の違いは1つの選択肢へ統合されます。ヒト疾患と1つ以上の表現型が同じ遺伝子で重なる場合は、各分類を同心円で表示します。

#### ヒト疾患関連遺伝子のハイライト

[IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/)で疾患モデル注釈を持つKO遺伝子をハイライト表示できます。この注釈は疾患モデルの類似性を示す情報であり、ヒトにおける遺伝子と疾患の因果関係を単独で確立するものではありません。

#### 遺伝子名の検索

ネットワークに含まれる遺伝子名を検索できます。

#### ネットワーク図の表示スタイル調整

以下の要素を調整できます：

- ネットワークレイアウト (layout)
- フォントサイズ (Font size)
- エッジ（線）の太さ (Edge width)
- ノード（点）間の距離（＊Coseレイアウト限定） (Node repulsion)

#### 4. エクスポートパネル

現在のネットワークの画像およびデータを、PNG、JPG、SVG、CSVおよびGraphML形式でエクスポートできます。PNG、JPG、SVGではモジュールの枠を含めるか選択できます。
CSVには、現在選択しているSimilarityモジュールまたはTop-level MPモジュールの割り当てと、各遺伝子のKOマウスが示す表現型の一覧が含まれます。
GraphMLは、デスクトップ版Cytoscapeと互換性のある形式で、Cytoscapeにネットワークをインポートして分析することができます。  

---

# 🛠 コマンドライン版

TSUMUGIのCLIでは、ローカルにダウンロードしたIMPC Release 24.0の統計結果ファイルから再計算でき、Web版より細かなフィルターや出力が可能です。

## 特徴

- IMPCの`statistical-results-ALL.csv.gz`を用いて再計算（必要に応じて`mp.obo`、`impc_phenodigm.csv`）
- MP用語の有無でフィルター
- 遺伝子シンボルファイルまたはCSV/TSV形式の遺伝子ペアファイルでフィルター
- GraphML(`tsumugi build-graphml`)とローカル配信用Webアプリバンドル(`tsumugi build-webapp`)の出力

## インストール

TSUMUGIにはPython 3.10以降が必要です。

BioConda:
```bash
conda install -c conda-forge -c bioconda tsumugi
```

PyPI:
```bash
pip install tsumugi
```

`tsumugi --version`でバージョンが表示されれば利用可能です。

## 利用可能なコマンド

- `tsumugi run`: IMPCデータからネットワークを再計算  
- `tsumugi mp --include/--exclude (--pairwise/--genewise)`: 指定MP用語を含む/示さない遺伝子ペアまたは遺伝子単位でフィルター  
- `tsumugi count --pairwise/--genewise (--min/--max)`: 表現型の数でフィルター（遺伝子ペア/遺伝子単位）  
- `tsumugi score (--min/--max)`: 表現型類似度スコアでフィルター（遺伝子ペア）  
- `tsumugi genes --keep/--drop`: 遺伝子シンボルファイルまたはCSV/TSV形式の遺伝子ペアファイルで抽出/除外
- `tsumugi life-stage --keep/--drop`: ライフステージでフィルター (Embryo/Early/Interval/Late)  
- `tsumugi sex --keep/--drop`: 性差でフィルター (Male/Female/None)  
- `tsumugi zygosity --keep/--drop`: 接合型でフィルター (Homo/Hetero/Hemi)  
- `tsumugi build-graphml`: GraphMLを生成（Cytoscape等で利用可能）  
- `tsumugi build-webapp`: TSUMUGIのWebアプリ素材一式を生成（ローカルで閲覧可能なHTML/CSS/JS）

> [!NOTE]
> すべてのフィルター系サブコマンドはJSONLをSTDOUTに出力します。  
> ファイルに保存する場合は`>`でリダイレクトしてください。

> [!IMPORTANT]
> フィルターと出力の各コマンドは、用途に応じて`pairwise_similarity_annotations.jsonl.gz`、`genewise_phenotype_annotations.jsonl.gz`、または両方を使用します。
> どちらのファイルも[TSUMUGIトップページ](https://larc-tsukuba.github.io/tsumugi/)からダウンロードできます。正確な入力は`tsumugi COMMAND --help`で確認してください。


## 使い方

### IMPCデータから再計算する(`tsumugi run`)

`--mp_obo`を省略すると、同梱の`data-version: releases/2025-08-27/mp.obo`を使います。  
`--impc_phenodigm`を省略すると、2025-10-01に[IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/)から取得したファイルを使います。
```bash
tsumugi run   --output_dir ./tsumugi-output   --statistical_results ./statistical-results-ALL.csv.gz   --threads 8
```
出力: `./tsumugi-output`にgenewise注釈（genewise_phenotype_annotations.jsonl.gz）、ペアの類似度データ（pairwise_similarity_annotations.jsonl.gz）、可視化用素材（`TSUMUGI-webapp`）が生成されます。

> [!IMPORTANT]  
> `TSUMUGI-webapp`ディレクトリにはOS別の起動スクリプトが含まれています。ダブルクリックでローカルWebアプリを開けます:  
> - Windows: `open_webapp_windows.bat`  
> - macOS: `open_webapp_mac.command`  
> - Linux: `open_webapp_linux.sh`

### MP用語でフィルターする(`tsumugi mp --include/--exclude`)

興味のある表現型を含む遺伝子ペア（または遺伝子）を抽出できます。また、指定条件で有意な異常注釈が得られなかった対応測定を検索できます。

```bash
tsumugi mp [-h] (-i MP_ID | -e MP_ID) [-g | -p] [-m PATH_MP_OBO] [-a PATH_GENEWISE_ANNOTATIONS] [--in PATH_PAIRWISE_ANNOTATIONS]
                  [--life_stage LIFE_STAGE] [--sex SEX] [--zygosity ZYGOSITY]
```

#### `-i MP_ID`, `--include MP_ID`
指定したMP用語（下位語含む）を持つ遺伝子/遺伝子ペアを含めます。

#### `-e MP_ID`, `--exclude MP_ID`
指定したMP用語に対応する測定があり、選択したメタデータ条件で有意な異常注釈がなかった遺伝子または遺伝子ペアを返します。関連する上位語と下位語も判定に用います。`-a/--genewise_annotations`が必須です。

> [!CAUTION]
> 非有意レコードは、動物が正常であることや、表現型が存在しないことを証明しません。対応する測定条件で有意な異常注釈が得られなかったことを示します。

#### `-g`, `--genewise`
遺伝子単位でフィルターします。`genewise_phenotype_annotations.jsonl(.gz)`を読み込み、`--genewise`使用時は`-a/--genewise_annotations`を指定します。

#### `-p`, `--pairwise`
遺伝子ペア単位でフィルターします。`pairwise_similarity_annotations.jsonl(.gz)`を対象にし、`--in`未指定時はSTDINを読み込みます。

#### `-m PATH_MP_OBO`, `--mp_obo PATH_MP_OBO`
哺乳類表現型オントロジー(mp.obo)のパス。省略時は同梱の`data/mp.obo`を使います。

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
genewise_phenotype_annotations（JSONL/.gz）のパス。`--exclude`では必須で、`--genewise`使用時にも指定してください。

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise_similarity_annotations（JSONL/.gz）のパス。未指定時はSTDINを読み込みます。

#### `--life_stage LIFE_STAGE`
ライフステージで追加フィルターします。指定可能: `Embryo`, `Early`, `Interval`, `Late`。

#### `--sex SEX`
性差で追加フィルターします。指定可能: `Male`, `Female`, `None`。

#### `--zygosity ZYGOSITY`
接合型で追加フィルターします。指定可能: `Homo`, `Hetero`, `Hemi`。

```bash
# MP:0001146(abnormal testis morphology)を含む遺伝子ペアのみ抽出（下位語も対象）
tsumugi mp --include MP:0001146   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_filtered.jsonl

# MP:0001146に対応する測定があり、有意な異常注釈がなかった遺伝子ペアを抽出
tsumugi mp --exclude MP:0001146 \
  --pairwise \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_without_significant_testis_phenotype.jsonl

# 遺伝子単位でMP:0001146を含む有意な表現型のみを抽出
tsumugi mp --include MP:0001146   --genewise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > genewise_filtered.jsonl

# 遺伝子単位でMP:0001146を測定済みかつ有意ではなかった遺伝子を抽出
tsumugi mp --exclude MP:0001146   --genewise   --genewise_annotations genewise_phenotype_annotations.jsonl.gz   > genewise_no_phenotype.jsonl
```

> [!IMPORTANT]
> **指定したMP用語の下位語もフィルターの対象です。**  
> 例: `MP:0001146 (abnormal testis morphology)`を指定すると、`MP:0004849 (abnormal testis size)`などの下位語も含まれます。

### 表現型数でフィルターする(`tsumugi count`)

```bash
tsumugi count [-h] (-g | -p) [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS] [-a PATH_GENEWISE_ANNOTATIONS]
```

表現型数の条件で遺伝子ペアをフィルターします。
`--min`または`--max`の少なくとも一方が必須です。  

#### `-g`, `--genewise`
両方の遺伝子について、有意表現型数が指定範囲内にある遺伝子ペアだけを残します。`-a/--genewise_annotations`で`genewise_phenotype_annotations.jsonl(.gz)`を指定する必要があります。

#### `-p`, `--pairwise`
遺伝子ペアで共有する表現型数でフィルターします。`--in`未指定ならSTDINから`pairwise_similarity_annotations.jsonl(.gz)`を読み込みます。

#### `--min MIN`, `--max MAX`
表現型数の下限/上限を指定します。片方のみ指定して片側フィルターとして使えます。

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise_similarity_annotations（JSONL/.gz）のパス。未指定時はSTDINを読み込みます。

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
genewise_phenotype_annotations（JSONL/.gz）のパス。`--genewise`指定時は必須です。

- 遺伝子ペア内で共有する表現型の数でフィルター:

```bash
tsumugi count --pairwise --min 3 --max 20   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_min3_max20.jsonl
```

- 遺伝子ごとの表現型数をペア出力へ適用:

```bash
tsumugi count --genewise --min 5 --max 50 \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_genes_with_5_to_50_phenotypes.jsonl
```

> [!NOTE]
> `--min`または`--max`の片方だけでも利用できます。

### 類似度スコアでフィルターする(`tsumugi score`)

```bash
tsumugi score [-h] [--min MIN] [--max MAX] [--in PATH_PAIRWISE_ANNOTATIONS]
```

表現型類似度スコア（0–100）で遺伝子ペアをフィルターします。  
`--min`または`--max`の少なくとも一方が必須です。

#### `--min MIN`, `--max MAX`
`phenotype_similarity_score`の下限/上限を指定します。片方だけでも指定できます。

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise_similarity_annotations（JSONL/.gz）のパス。未指定時はSTDINを読み込みます。

```bash
tsumugi score --min 50 --max 80   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_score50_80.jsonl
```

> [!NOTE]
> `--min`または`--max`の片方だけでも利用できます。

### 遺伝子リストでフィルターする(`tsumugi genes --keep/--drop`)

```bash
tsumugi genes [-h] (-k GENE_SYMBOL | -d GENE_SYMBOL) [-g | -p] [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k GENE_SYMBOL`, `--keep GENE_SYMBOL`
指定した遺伝子を含むペアのみ残します（テキストファイルで指定）。

#### `-d GENE_SYMBOL`, `--drop GENE_SYMBOL`
指定した遺伝子を含むペアを除外します（テキストファイルで指定）。

#### `-g`, `--genewise`
空行を除き、1行に1つの遺伝子シンボルを記載したファイルを読み込みます。

#### `-p`, `--pairwise`
空行を除き、1行に1組の遺伝子ペアをカンマまたはタブで区切ったファイルを読み込みます。

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise_similarity_annotations（JSONL/.gz）のパス。未指定時はSTDINを読み込みます。

```bash
cat << EOF > genes.txt
Maf
Aamp
Cacna1c
EOF

tsumugi genes --genewise --keep genes.txt \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_keep_genes.jsonl

cat << EOF > gene_pairs.csv
Maf,Aamp
Maf,Cacna1c
EOF

tsumugi genes --pairwise --drop gene_pairs.csv   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_drop_genes.jsonl

```

### ライフステージでフィルターする(`tsumugi life-stage --keep/--drop`)
```bash
tsumugi life-stage [-h] (-k LIFE_STAGE | -d LIFE_STAGE) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k LIFE_STAGE`, `--keep LIFE_STAGE`
指定したライフステージ（`Embryo`, `Early`, `Interval`, `Late`）のみ残します。

#### `-d LIFE_STAGE`, `--drop LIFE_STAGE`
指定したライフステージ（`Embryo`, `Early`, `Interval`, `Late`）を除外します。

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise_similarity_annotations（JSONL/.gz）のパス。未指定時はSTDINを読み込みます。

```bash
tsumugi life-stage --keep Early   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_lifestage_early.jsonl
```

### 性差でフィルターする(`tsumugi sex --keep/--drop`)
```bash
tsumugi sex [-h] (-k SEX | -d SEX) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k SEX`, `--keep SEX`
指定した性差（`Male`, `Female`, `None`）のみ残します。

#### `-d SEX`, `--drop SEX`
指定した性差（`Male`, `Female`, `None`）を除外します。

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise_similarity_annotations（JSONL/.gz）のパス。未指定時はSTDINを読み込みます。

```bash
tsumugi sex --drop Male   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_no_male.jsonl
```

### 接合型でフィルターする(`tsumugi zygosity --keep/--drop`)
```bash
tsumugi zygosity [-h] (-k ZYGOSITY | -d ZYGOSITY) [--in PATH_PAIRWISE_ANNOTATIONS]
```

#### `-k ZYGOSITY`, `--keep ZYGOSITY`
指定した接合型（`Homo`, `Hetero`, `Hemi`）のみ残します。

#### `-d ZYGOSITY`, `--drop ZYGOSITY`
指定した接合型（`Homo`, `Hetero`, `Hemi`）を除外します。

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise_similarity_annotations（JSONL/.gz）のパス。未指定時はSTDINを読み込みます。

```bash
tsumugi zygosity --keep Homo   --in pairwise_similarity_annotations.jsonl.gz   > pairwise_homo.jsonl
```

### GraphML / Webアプリに出力する
```bash
tsumugi build-graphml [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise_similarity_annotations（JSONL/.gz）のパス。未指定時はSTDINを読み込みます。

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
genewise_phenotype_annotations（JSONL/.gz）のパス。必須です。

```bash
tsumugi build-graphml \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  > network.graphml
```

```bash
tsumugi build-webapp [-h] [--in PATH_PAIRWISE_ANNOTATIONS] -a PATH_GENEWISE_ANNOTATIONS -o OUT
```

#### `--in PATH_PAIRWISE_ANNOTATIONS`
pairwise_similarity_annotations（JSONL/.gz）のパス。未指定時はSTDINを読み込みます。

#### `-a PATH_GENEWISE_ANNOTATIONS`, `--genewise_annotations PATH_GENEWISE_ANNOTATIONS`
genewise_phenotype_annotations（JSONL/.gz）のパス。必須です。

#### `-o OUT`, `--out OUT`
Webアプリバンドル（HTML/CSS/JS +ネットワークデータ）の出力先ディレクトリ。  
拡張子付きのファイル名は指定しないでください。

```bash
tsumugi build-webapp \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise_annotations genewise_phenotype_annotations.jsonl.gz \
  --out ./webapp_output
```

`build-webapp`が受け付けるノード数は最大150です。より大きなネットワークには`build-graphml`を使用してください。生成物は同梱の起動スクリプトでローカル配信できますが、Cytoscape.js、noUiSlider、pako、フォント、アイコンを外部CDNから読み込むため、これらを別途同梱またはキャッシュしていない環境ではインターネット接続が必要です。

>[!TIP]
> CLIはSTDIN/STDOUTをサポートしているため、パイプでつなげて柔軟に処理できます:  
> `zcat pairwise_similarity_annotations.jsonl.gz | tsumugi mp ... | tsumugi genes ... > out.jsonl`

---

# 🔍 表現型類似遺伝子群の算出方法

## データソース

IMPCのデータセットは[Release 24.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-24.0/results)の`statistical-results-ALL.csv.gz`を使用しています。
データセットに含まれる列の情報はこちらです：[Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)  

## 前処理

TSUMUGIは、IMPCの`mp_term_id`が空でないレコードを異常表現型注釈として扱います。また、測定済みの非有意レコードを保持し、測定の有無を考慮した除外検索に使用します。

- 接合型を`Homo`、`Hetero`、`Hemi`へ変換します。
- 雌KOの効果のP値だけが0.0001以下の場合は`Female`、雄KOの効果のP値だけが0.0001以下の場合は`Male`、それ以外は`None`を付与します。
- 効果量の絶対値を使用します。欠損値は欠損のまま保持し、JSONでは`null`として出力します。

## 表現型類似度の計算

TSUMUGIは、Phenodigm ([Smedley D, et al. (2013)](https://doi.org/10.1093/database/bat025))のスコア計算式を用いて、Mammalian Phenotype Ontology内でIMPC KOマウス遺伝子の表現型プロファイルを比較します。

>[!NOTE]
> Phenodigmのスコア計算式を使用しますが、原著の種間比較用HPO-MP/ZP OWLSimパイプラインは実行しません。IMPC KOマウス遺伝子に付与されたMP注釈同士を比較します。

### 1. MP用語ペア類似度の定義

* MPオントロジーを構築し、有意なIMPC注釈から各用語の情報量(Information Content; IC)を計算します：
   `IC(term) = -log2(|用語へ伝播した注釈数| / |全有意注釈数|)`
   各直接注釈を、付与されたMP用語とその全祖先用語へ伝播させます。

* 各MP用語ペアについて、注釈由来ICが最大となる共通祖先を求めます。候補が同率の場合は、MPオントロジー上の推移的な子孫用語が少ない候補、次いでMP用語IDの辞書順が小さい候補を決定的に選択します。選択したMICAのICをResnik類似度とします。同率候補の数値スコアは同じですが、選ばれるMICA名が変わると共有context数と表示対象が変わる場合があります。

* 2つのMP用語について、各用語自身と全祖先用語からなる推論属性集合のJaccard指数を計算します。

* MP用語ペア類似度を`sqrt(Resnik * Jaccard)`と定義します。

### 2. 遺伝子ペアの類似度行列

* 各遺伝子ペアについて、MP用語ペアの類似度からMP用語×MP用語の類似度行列を作成します。

* 接合型、ライフステージ、性差のメタデータが一致する場合に限り、MICAを`phenotype_shared_annotations`へ記録します。これらのメタデータはPhenodigmスコア自体の重み付けには使用しません。

### 3. Phenodigmスケーリング

* Phenodigmの最大値・平均値スケーリングにより、KOマウス遺伝子ペアの表現型類似度を0–100に正規化します：
   観測された最良対応の最大値と平均値を求め、2遺伝子の対称な最適自己一致スコアで正規化します。
   `Score = 100 * (normalized_max + normalized_mean) / 2`  
   分母が0の場合は0とします。

このスコアは表現型プロファイルの類似度です。P値、効果量、結合親和性、遺伝子間の因果的相互作用を示す値ではありません。

---

# ✉️ お問い合わせ

ご質問やご要望は、以下にお気軽にお問い合わせください（日本語可）：

- **Googleフォーム**  
  👉 [お問い合わせフォーム](https://forms.gle/ME8EJZZHaRNgKZ979)

- **GitHubアカウント**をお持ちの方  
  👉 [GitHub Issue](https://github.com/akikuno/TSUMUGI-dev/issues/new/choose)

---

# 📄 論文

Kuno A, Matsumoto K, Taki T, Takahashi S, and Mizuno S.  
**TSUMUGI: a platform for phenotype-driven gene network identification from comprehensive knockout mouse phenotyping data**  
*bioRxiv*. (2026) https://doi.org/10.64898/2026.02.18.706720
