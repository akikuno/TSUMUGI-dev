<p align="center">
    <a href="https://larc-tsukuba.github.io/tsumugi/" target="_blank">
        <img src="../image/tsumugi-logo.jpg" alt="Tsumugi Logo" width="80%">
    </a>
</p>

[![License](https://img.shields.io/badge/License-MIT-9cf.svg)](https://choosealicense.com/licenses/mit/)
[![DOI](https://zenodo.org/badge/441025227.svg)](https://doi.org/10.5281/zenodo.14957711)
[![お問い合わせ](https://img.shields.io/badge/%E3%81%8A%E5%95%8F%E3%81%84%E5%90%88%E3%82%8F%E3%81%9B-923DE2)](https://forms.gle/ME8EJZZHaRNgKZ979)

**TSUMUGI（Trait-driven Surveillance for Mutation-based Gene module Identification）** は、[国際マウス表現型解析コンソーシアム（IMPC）](https://www.mousephenotype.org/) によるノックアウト(KO)マウスの表現型データを活用し、**表現型の類似性に基づいて遺伝子モジュールを抽出・可視化するWebツール**です。

Web上で誰でも利用できる公開ツールとして提供されています👇️  

🔗 https://larc-tsukuba.github.io/tsumugi/

**TSUMUGI**は「表現型を織りなす遺伝子群を紡ぎ出す」という動機に由来します。  


# 📖 TSUMUGIの使い方

## 💬 トップページ

TSUMUGIは、以下の3種類の入力に対応しています。

### 1. 表現型（Phenotype）

関心のある表現型を入力すると、それを示すKOマウスをもつ遺伝子の中から、**他の表現型も類似している遺伝子群**を探索します。  
表現型名は [Mammalian Phenotype Ontology（MPO）](https://www.informatics.jax.org/vocab/mp_ontology) に基づいています。

TSUMUGIで現在検索可能な表現型の一覧はこちら：  
👉 [表現型リスト](https://github.com/akikuno/TSUMUGI-dev/blob/main/TSUMUGI/data/available_mp_terms.txt)

### 2. 遺伝子名（Gene）

特定の遺伝子を1つ指定すると、**そのKOマウスと類似した表現型をもつ他の遺伝子群**を探索します。  
遺伝子名は [MGI](http://www.informatics.jax.org/) に登録された遺伝子シンボルに準拠しています。

TSUMUGIで現在検索可能な遺伝子名の一覧はこちら：  
👉 [遺伝子名リスト](https://github.com/akikuno/TSUMUGI-dev/blob/main/TSUMUGI/data/available_gene_symbols.txt)


### 3. 遺伝子リスト (Gene List)

複数遺伝子の入力を受け付けます。  
遺伝子リストは、改行区切りで入力してください。  

> [!NOTE]
> 遺伝子リストは遺伝子名（Gene）とは異なり、**リスト内の遺伝子同士**の表現型類似遺伝子を抽出します。

> [!CAUTION]
> **表現型類似遺伝子がひとつも見つからない**場合、
> `No similar phenotypes were found among the entered genes.` というアラートが表示され、処理が停止されます。
>
> **表現型類似遺伝子が200を超える**場合、
> `Too many genes submitted. Please limit the number to 200 or fewer.` というアラートが表示され、ブラウザの負荷を防ぐため処理が停止されます。


### 📥 生データ(`TSUMUGI_{version}_raw_data`)のダウンロード

遺伝子ペアにおける表現型類似度の生データ（Gzip圧縮CSV形式、またはParquet形式）をダウンロードすることができます。  

内容は以下のとおりです：  

- ペアとなる遺伝子名（Gene1, Gene2）
- ペアに共通する表現型の類似度（Phenodigm Score）
- ペアに共通する表現型の類似度（Jaccard Similarity）
- ペアに共通する表現型の数（Number of shared phenotype）
- ペアに共通する表現型のリスト（List of shared phenotype）

> [!CAUTION]
> ファイルサイズは約50-100MBあります。ダウンロードに時間がかかる場合があります。

`Polars` または `Pandas` を用いる場合には、Parquet形式のご利用を推奨します。  
次のようにデータを読み込むことができます：  

#### Polars

```bash
# condaを使用してPolarsとPyArrowをインストールします
conda create -y -n env-tsumugi polars pyarrow
conda activate env-tsumugi
```

```python
# Polarsを使用してParquetファイルを読み込みます
import polars as pl
df_tsumugi = pl.read_parquet("TSUMUGI_{version}_raw_data.parquet")
```

#### Pandas

```bash
# condaを使用してPandasとPyArrowをインストールします
conda create -y -n env-tsumugi pandas pyarrow
conda activate env-tsumugi
```

```python
# Pandasを使用してParquetファイルを読み込みます
import pandas as pd
df_tsumugi = pd.read_parquet("TSUMUGI_{version}_raw_data.parquet")
```

## 🌐 ネットワーク描出

入力内容に基づいてページが遷移し、ネットワークが自動的に描画されます。  

> [!IMPORTANT]
> **共通する異常表現型が2つ以上 かつ Phenodigmスコアが25以上**の遺伝子ペアが、可視化の対象となります。  

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

`Phenotypes similarity`のスライダーでは、**エッジの表現型類似度**（Phenodigmスコア）に基づいて、ネットワークに表示する遺伝子ペアの閾値を設定できます。  
類似度の最小値と最大値を 1〜10 のスケールに変換し、10段階でフィルタリングが可能です。  
なお、10段階で表記されたPhenodigmスコアの値は、分布の偏りを是正するため、対数変換されています。  

> [!NOTE]
> 表現型類似度についての詳細は、以下を御覧ください  
> 👉 [🔍 表現型類似遺伝子群の算出方法](https://github.com/akikuno/TSUMUGI-dev/blob/main/doc/README_JP.md#-%E8%A1%A8%E7%8F%BE%E5%9E%8B%E9%A1%9E%E4%BC%BC%E9%81%BA%E4%BC%9D%E5%AD%90%E7%BE%A4%E3%81%AE%E7%AE%97%E5%87%BA%E6%96%B9%E6%B3%95)

#### 表現型重症度によるフィルター

`Phenotype severity`のスライダーでは、**KOマウスにおける表現型の重症度**（効果量）に基づいて、ノードの表示を調整できます。  
効果量が高いほど、表現型の影響が強く現れていることを示します。  
こちらも、効果量の範囲を 1〜10 にスケールしており、10段階のフィルタリングが可能です。  
なお、バイナリ表現型以外では、10段階で表記された効果量の値は、分布の偏りを是正するため、対数変換されています。  

> [!NOTE]
> IMPCによる表現型の評価が二値（あり・なし）の場合（例: [abnormal embryo development](https://larc-tsukuba.github.io/tsumugi/app/phenotype/abnormal_embryo_development.html)：二値遺伝子のリストは[こちら](https://github.com/akikuno/TSUMUGI-dev/blob/main/TSUMUGI/data/binary_phenotypes.txt)）や、遺伝子名が入力の場合には、`Phenotypes severity`のスライダーはありません。

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

#### ヒト疾患関連遺伝子のハイライト (Highlight: Human Disease)

ヒト疾患に関連する遺伝子をハイライト表示できます。  
KOマウスとヒト疾患の関連は、[IMPC Disease Models Portal](https://diseasemodels.research.its.qmul.ac.uk/)の公開データを使用しています。  

#### 遺伝子名の検索 (Search: Specific Gene)

ネットワークに含まれる遺伝子名を検索できます。

#### ネットワーク図の表示スタイル調整 （Layout ＆ Display）

以下の要素を調整できます：

- ネットワークレイアウト (layout)
- フォントサイズ (Font size)
- エッジ（線）の太さ (Edge width)
- ノード（点）間の距離（＊Coseレイアウト限定） (Node repulsion)

#### エクスポート (Export)

現在のネットワークの画像およびデータを、PNG、CSVおよびGraphML形式でエクスポートできます。  
CSVには、連結成分（モジュール）のIDと、各遺伝子のKOマウスが示す表現型の一覧が含まれます。  
GraphMLは、デスクトップ版Cytoscapeと互換性のある形式で、Cytoscapeにネットワークをインポートして分析することができます。  

# 🔍 表現型類似遺伝子群の算出方法

## データソース

IMPCのデータセットは[Release-23.0](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-23.0/results)の`statistical-results-ALL.csv.gz`を使用しています。  
データセットに含まれる列の情報はこちらです： [Data fields](https://www.mousephenotype.org/help/programmatic-data-access/data-fields/)  

## 前処理

KOマウスの示す表現型のP値（`p_value` `female_ko_effect_p_value` `male_ko_effect_p_value` のいずれか）が0.0001以下の遺伝子-表現型を抽出します。  
- 遺伝型特異的な表現型には、`homo`, `hetero` または `hemi`を注釈します
- 性特異的な表現型には、`female` または `male`を注釈します

## 表現型類似度の計算

TSUMUGIでは、遺伝子ペア間の表現型類似度を計算するために2つの相補的な指標を使用しています：

### 1. Phenodigmスコア

**[Phenodigm](https://pmc.ncbi.nlm.nih.gov/articles/PMC3649640/)**は、Mammalian Phenotype (MP)オントロジーの構造に基づいて表現型用語間の意味的類似性を考慮した、表現型類似度計算手法です。このアルゴリズムは元々異種間の表現型比較のために開発され、KOマウス表現型の比較に適応されています。

#### 主な特徴：

- **意味的類似性**: 情報量（IC）に基づくResnik類似度を使用して、表現型用語の関連性を測定
- **アノテーション重み付け**: 実験条件（遺伝型、性別、ライフステージ）を類似度計算に考慮
- **非対称スコアリング**: 遺伝子間の表現型セットサイズの違いを考慮

#### アルゴリズムの概要：

1. **情報量の計算**: 各MP用語について、オントロジー内での頻度に基づいてICを計算：
   ```
   IC(term) = -log(P(term))
   ```
   ここで、P(term)はその用語またはその子孫を観察する確率

2. **表現型ペアごとの類似度**: 各表現型ペアについて、重み付きResnik類似度を計算：
   - 基本類似度: 最も情報量の多い共通祖先（MICA）のIC
   - 実験条件の一致に基づいてアノテーション重みを適用：
     - 3つのアノテーションすべて一致（遺伝型、性別、ライフステージ）: 1.0倍
     - 2つのアノテーションが一致: 0.75倍
     - 1つのアノテーションが一致: 0.5倍
     - アノテーションが一致しない: 0.25倍

3. **遺伝子間類似度**: 遺伝子AとB間のPhenodigmスコアを計算：
   ```
   Phenodigm(A,B) = 100 × (maxSim/maxIC) × ((avgSimA/avgICA + avgSimB/avgICB)/2)
   ```
   ここで：
   - maxSim: すべての表現型ペア間の最大類似度
   - maxIC: すべての表現型の中の最大IC
   - avgSimA/B: 遺伝子A/Bの表現型の平均類似度
   - avgICA/B: 遺伝子A/Bの表現型の平均IC

Phenodigmスコアは0から100の範囲で、値が高いほど表現型の類似性が高いことを示します。

### 2. Jaccard係数

相補的な指標として、TSUMUGIではよりシンプルな集合ベースの類似度尺度である**Jaccard係数**も使用しています。  
こちらは、共通する表現型の割合を0-1の数値で表す類似度指標です。

```
Jaccard(A, B) = |A ∩ B| / |A ∪ B|
```

例えば、遺伝子Aと遺伝子BのKOマウスが、以下のような異常表現型を持つとします：  

```
A: {abnormal embryo development, abnormal heart morphology, abnormal kidney morphology}
B: {abnormal embryo development, abnormal heart morphology, abnormal lung morphology}
```

このとき、共通する表現型は2つ、全体のユニークな表現型は4つなので、Jaccard係数は次のように計算されます：

```
Jaccard(A, B) = 2 / 4 = 0.5
```

## 可視化の閾値

ネットワークの可視化において、TSUMUGIは以下の基準を適用します：
- 遺伝子ペア間で最低2つの異常表現型を共有
- Phenodigmスコア ≥ 25（意味のある表現型類似性を示す）

この二重閾値アプローチにより、可視化される遺伝子関係が統計的に有意かつ生物学的に意味のあるものであることを保証します。

# ✉️ お問い合わせ

ご質問やご要望は、以下にお気軽にお問い合わせください（日本語可）：

- **Googleフォーム**  
  👉 [お問い合わせフォーム](https://forms.gle/ME8EJZZHaRNgKZ979)

- **GitHubアカウント**をお持ちの方  
  👉 [GitHub Issue](https://github.com/akikuno/TSUMUGI-dev/issues/new/choose)
