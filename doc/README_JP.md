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

**TSUMUGI** (Trait-driven Surveillance for Mutation-based Gene module Identification)は、[国際マウス表現型解析コンソーシアム（IMPC）](https://www.mousephenotype.org/)によるノックアウト(KO)マウスの表現型データを活用し、**表現型の類似性に基づいて遺伝子モジュールを抽出・可視化するWebツール**です。

Web上で誰でも利用できる公開ツールとして提供されています👇️  

🔗https://larc-tsukuba.github.io/tsumugi/

TSUMUGI(**紡ぎ**)は「表現型を織りなす遺伝子群を紡ぎ出す」という動機に由来します。  

# 📖[TSUMUGI](https://larc-tsukuba.github.io/tsumugi/)の使い方

## 💬 トップページ

TSUMUGIは、以下の3種類の入力に対応しています。

### 1. 表現型（Phenotype）

関心のある表現型を入力すると、それを示すKOマウスをもつ遺伝子の中から、**他の表現型も類似している遺伝子群**を探索します。  
表現型名は[Mammalian Phenotype Ontology（MPO）](https://www.informatics.jax.org/vocab/mp_ontology)に基づいています。

TSUMUGIで現在検索可能な表現型の一覧はこちら：  
👉 [表現型リスト](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_mp_terms.txt)

### 2. 遺伝子名（Gene）

特定の遺伝子を1つ指定すると、**そのKOマウスと類似した表現型をもつ他の遺伝子群**を探索します。  
遺伝子名は[MGI](http://www.informatics.jax.org/)に登録された遺伝子シンボルに準拠しています。

TSUMUGIで現在検索可能な遺伝子名の一覧はこちら：  
👉 [遺伝子名リスト](https://github.com/larc-tsukuba/tsumugi/blob/main/data/available_gene_symbols.txt)


### 3. 遺伝子リスト(Gene List)

複数遺伝子の入力を受け付けます。  
遺伝子リストは、改行区切りで入力してください。  

> [!NOTE]
> 遺伝子リストは遺伝子名（Gene）とは異なり、**リスト内の遺伝子同士**の表現型類似遺伝子を抽出します。

> [!CAUTION]
> **表現型類似遺伝子がひとつも見つからない**場合、
> `No similar phenotypes were found among the entered genes.`というアラートが表示され、処理が停止されます。
>
> **表現型類似遺伝子が200を超える**場合、
> `Too many genes submitted. Please limit the number to 200 or fewer.`というアラートが表示され、ブラウザの負荷を防ぐため処理が停止されます。


### 📥 生データのダウンロード

TSUMUGIにおける表現型情報（Gzip圧縮JSONL形式）をダウンロードできます。  

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

```
{"life_stage": "Early", "marker_symbol": "1110059G10Rik", "marker_accession_id": "MGI:1913452", "effect_size": 0.0, "mp_term_name": "fused joints", "disease_annotation": [], "significant": false, "zygosity": "Homo", "sexual_dimorphism": "None", "mp_term_id": "MP:0000137"}
```

#### `pairwise_similarity_annotations.jsonl.gz`

遺伝子ペアにおける表現型類似度情報がまとまっています。  
各レコードの内容は以下のとおりです：  

- 遺伝子ペアの名称（Gene1_symbol, Gene2_symbol）  
- 共通する表現型の注釈情報（Phenotype shared annotations；各表現型ごとに発達段階、接合型、性差情報などを保持）  
- ペア間の表現型類似度（Phenotype similarity score；Resnik類似度に基づくPhenodigmスコア；0–100スケール）  

```
{"gene1_symbol": "1110059G10Rik", "gene2_symbol": "Cog6", "phenotype_shared_annotations": {"vertebral transformation": {"zygosity": "Homo", "life_stage": "Early", "sexual_dimorphism": "Male"}}, "phenotype_similarity_score": 42}
```

## 🌐 ネットワーク描出

入力内容に基づいてページが遷移し、ネットワークが自動的に描画されます。  

> [!IMPORTANT]
> **共通する異常表現型が3つ以上 かつ 表現型類似度が0.0よりも大きい**遺伝子ペアが、可視化の対象となります。  

### ネットワークパネル

#### ノード（点）

各ノードは1つの遺伝子を表します。  
クリックすると、そのKOマウスに観察された異常表現型のリストが表示されます。  
ドラッグで自由に位置を調整できます。  

#### エッジ（線）

エッジをクリックすると、共通表現型の詳細が確認できます。  

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

#### ヒト疾患関連遺伝子のハイライト(Highlight: Human Disease)

ヒト疾患に関連する遺伝子をハイライト表示できます。  
KOマウスとヒト疾患の関連は、[IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/)の公開データを使用しています。  

#### 遺伝子名の検索(Search: Specific Gene)

ネットワークに含まれる遺伝子名を検索できます。

#### ネットワーク図の表示スタイル調整 （Layout ＆Display）

以下の要素を調整できます：

- ネットワークレイアウト(layout)
- フォントサイズ(Font size)
- エッジ（線）の太さ(Edge width)
- ノード（点）間の距離（＊Coseレイアウト限定） (Node repulsion)

#### エクスポート(Export)

現在のネットワークの画像およびデータを、PNG、CSVおよびGraphML形式でエクスポートできます。  
CSVには、連結成分（モジュール）のIDと、各遺伝子のKOマウスが示す表現型の一覧が含まれます。  
GraphMLは、デスクトップ版Cytoscapeと互換性のある形式で、Cytoscapeにネットワークをインポートして分析することができます。  

# 🛠 コマンドライン版

今回のリリースでは**コマンドラインインターフェース（CLI）**を追加しました。IMPCのデータが更新された際に、ユーザー自身で最新データをダウンロードしてTSUMUGIのパイプラインを実行できます。Web版より柔軟にフィルタリングや出力形式を選べます。

- 自前データで最新版を再計算: IMPC `statistical-results-ALL.csv.gz`（任意で`mp.obo`と`impc_phenodigm.csv`）を渡してネットワークを一括生成できます。
- 興味のあるMP用語の有無でフィルター: `tsumugi mp --include MP:xxxx`で含める、`--exclude MP:xxxx`で除外するなど、Web版より細かい操作ができます。
- 遺伝子リストでの絞り込み・除外: Webツールよりも自由に入力形式を選び、複数ファイルやカンマ区切りを受け付けます。
- 出力の拡張: GraphMLを直接生成(`tsumugi build-graphml`)したり、TSUMUGI用のWebアプリケーション一式をオフライン向けに出力(`tsumugi build-webapp`)できます。

## 利用可能なコマンド一覧
- `tsumugi run`: IMPCデータからネットワークを再計算
- `tsumugi mp --include/--exclude`: 指定MP用語を含む/示さない遺伝子ペアでフィルター
- `tsumugi n-phenos --pairwise/--genewise (--min/--max)`: 表現型の数でフィルター（遺伝子ペア/遺伝子単位）
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

### 1. IMPCデータからネットワークを再計算する(`tsumugi run`)
最新のIMPCからダウンロードした`statistical-results-ALL.csv.gz`を渡して計算できます。  
`--mp_obo`を指定しない場合、TSUMUGIは同梱の`data-version: releases/2025-08-27/mp.obo`を内部利用します。  
`--impc_phenodigm`を指定しない場合、2025-10-01に[IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/)から取得したファイルを内部利用します。
```bash
tsumugi run \
  --output_dir ./tsumugi-output \
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


### 2. MP用語でフィルターする(`tsumugi mp --include/--exclude`)
興味のある表現型を持つ遺伝子ペアのみ抽出、または該当表現型を測定済みだが有意な異常を示さなかった遺伝子ペアを除外できます。

```bash
# MP:0001146(abnormal testis morphology)とその下層の表現型（MP:0004849 (abnormal testis size)など）を含む遺伝子ペアだけ残す
tsumugi mp --include MP:0001146 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl

# MP:0001146(abnormal testis morphology)とその下層の表現型（MP:0004849 (abnormal testis size)など）を測定しており、かつ有意な示さなかった遺伝子を除外
tsumugi mp --exclude MP:0001146 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_filtered.jsonl
```

> [!IMPORTANT]
> 指定されたMP用語の下層にある用語も含めてフィルターされます。
> 例えば`MP:0001146 (abnormal testis morphology)`を指定した場合、`MP:0004849 (abnormal testis size)`などの下層用語も考慮されます。

### 3. 表現型数でフィルターする(`tsumugi n-phenos`)
- 遺伝子ペア内で共有する表現型の数でフィルター:  
```bash
tsumugi n-phenos --pairwise --min 3 --max 20 \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_min3_max20.jsonl
```
- 遺伝子ごとの表現型数でフィルター（genewiseが必要）:  
```bash
tsumugi n-phenos --genewise --min 5 --max 50 \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --in pairwise_similarity_annotations.jsonl.gz \
  > genewise_min5_max50.jsonl
```
`--min`または`--max`を単独で指定しても使えます。

### 4. 遺伝子リストで絞り込み・除外する(`tsumugi genes --keep/--drop`)
```bash
# keep: リストに含まれる遺伝子が絡むペアのみ残す
tsumugi genes --keep genes.txt \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_keep_genes.jsonl

# drop: リストに含まれる遺伝子が絡むペアを除外
tsumugi genes --drop geneA,geneB \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_drop_genes.jsonl
```

### 5. ライフステージでフィルターする(`tsumugi life-stage --keep/--drop`)
```bash
tsumugi life-stage --keep Early \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_lifestage_early.jsonl
```

### 6. 性差でフィルターする(`tsumugi sex --keep/--drop`)
```bash
tsumugi sex --drop Male \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_no_male.jsonl
```

### 7. 接合型でフィルターする(`tsumugi zygosity --keep/--drop`)
```bash
tsumugi zygosity --keep Homo \
  --in pairwise_similarity_annotations.jsonl.gz \
  > pairwise_homo.jsonl
```

### 8. 出力をGraphML／Webアプリに変換する
```bash
# GraphMLを生成（Cytoscape等で利用可能）
tsumugi build-graphml \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  > network.graphml

# TSUMUGIのWebアプリ素材を生成（ローカルで開けるHTML/CSS/JS一式）
tsumugi build-webapp \
  --in pairwise_similarity_annotations.jsonl.gz \
  --genewise genewise_phenotype_annotations.jsonl.gz \
  --output_dir ./webapp_output
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

### 1. 表現型用語間のResnik類似度

MPオントロジーの階層構造を構築し、各用語の子孫（自身を含む）との割合から情報量（Information Content; IC）を計算します：

```
IC(term) = -log((|Descendants(term)| + 1) / |MP用語総数|)
```

任意の2用語に対して共通祖先を列挙し、そのうち**最も情報量が大きい共通祖先（MICA）**のICをResnik類似度とします：

```
Resnik(term_1, term_2) = max_{c∈Anc(term_1) ∩Anc(term_2)} IC(c)
```

共通祖先が存在しない場合、類似度は0になります。

### 2. 遺伝子ペアへのPhenodigmスケーリング

1. 各遺伝子ペアについて、有意なMP用語同士のResnik類似度をマトリクス化し、遺伝型（zygosity）、ライフステージ、性差の一致度に応じて 1.0 / 0.75 / 0.5 / 0.25 の重みを掛けます。  
2. 行・列ごとの最大値から、その遺伝子ペアで実際に観測された類似度の最大値・平均値を求めます。  
3. 個々のMP用語のICから、理論上達成しうる最大値・平均値を算出します。  
4. 実測値を理論値で正規化し、最大値と平均値の2つを平均してPhenodigmスコアを得ます：

```
Phenodigm = 100 * 0.5 * ( actual_max / theoretical_max + actual_mean / theoretical_mean )
```

この正規化によって得られる0〜100のスコアを生データおよびWeb UIの`Phenotypes similarity`スライダーで用いています。


# ✉️ お問い合わせ

ご質問やご要望は、以下にお気軽にお問い合わせください（日本語可）：

- **Googleフォーム**  
  👉 [お問い合わせフォーム](https://forms.gle/ME8EJZZHaRNgKZ979)

- **GitHubアカウント**をお持ちの方  
  👉 [GitHub Issue](https://github.com/akikuno/TSUMUGI-dev/issues/new/choose)
