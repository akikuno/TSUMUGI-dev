<p align="center">
    <a href="https://larc-tsukuba.github.io/tsumugi/" target="_blank">
        <img src="../image/tsumugi-logo.jpg" alt="Tsumugi Logo" width="90%">
    </a>
</p>

[![License](https://img.shields.io/badge/License-MIT-9cf.svg)](https://choosealicense.com/licenses/mit/)
[![DOI](https://zenodo.org/badge/441025227.svg)](https://doi.org/10.5281/zenodo.14957711)

TSUMUGI（Trait-driven Surveillance for Mutation-based Gene module Identification）は、[国際マウス表現型解析コンソーシアム（International Mouse Phenotyping Consortium: IMPC）](https://www.mousephenotype.org/) によって得られた単一遺伝子ノックアウト（KO）マウスの表現型データをもとに、表現型の類似性を指標として遺伝子モジュールを抽出・可視化するツールです。  

Web上で誰でも利用できる公開ツールとして提供されています👇️  

https://larc-tsukuba.github.io/tsumugi/

TSUMUGIは、**表現型を織りなす遺伝子群を紡ぎ出す**という動機に由来しています。


# 🧭 Webツールの使い方

## トップページ

### 種類

TSUMUGIは以下の3つの入力に対応しています

- 表現型 Phenotype
- 遺伝子シンボル Gene
- 遺伝子リスト Gene List

### 1. 表現型 Phenotype

興味の表現型を入力することができます

表現型は[Mammalian Phenotype Ontology（MPO）](https://www.informatics.jax.org/vocab/mp_ontology)に基づいています  

<!-- 現在、TSUMUGIで検索可能な表現型のリストはこちらです  

[表現型リスト](https://larc-tsukuba.github.io/tsumugi/app/phenotype_list.html) # TODO -->

### 2. 遺伝子シンボル

遺伝子シンボルでは特定の遺伝子に対してその他の遺伝子すべての類似度を計算します

遺伝子シンボルは、[MGI](http://www.informatics.jax.org/)に基づいています

<!-- 現在、TSUMUGIで検索可能な遺伝子シンボルのリストはこちらです  

[遺伝子シンボルリスト](https://larc-tsukuba.github.io/tsumugi/app/phenotype_list.html) # TODO -->


### 3. 遺伝子リスト

複数遺伝子の入力が可能です  
遺伝子リストは、改行区切りで入力してください  

遺伝子シンボルとの違いは、遺伝子シンボルでは1つの遺伝子に対してその他の遺伝子すべての類似度を計算する一方で、遺伝子リストでは**リスト内の遺伝子同士の類似度**を計算します  

入力された遺伝子リストにおいて、３つ以上表現型が類似する遺伝子ペアがまったく見つからなかった場合、`Gene not found`と警告が表示されます  

また、類似する遺伝子ペアが200以上見つかった場合、ネットワークを描画するとブラウザが固まってしまうため、こちらも警告が表示されます  

### データのダウンロード

類似度の生データをダウンロードすることができます

生データには以下の情報が含まれます  

- ペアとなる遺伝子シンボル （Gene1, Gene2）
- ペアとなる遺伝子シンボルに共通する表現型の類似度 （Jaccard Similarity）
- ペアとなる遺伝子シンボルに共通する表現型の数（Number of shared phenotype）
- ペアとなる遺伝子シンボルに共通する表現型のリスト（List of shared phenotype）

> [!CAUTION]
> 約100MBのGZip圧縮CSVファイルです。ダウンロードには時間がかかる場合があります。

## ネットワーク描出

入力を受け付けるとページが遷移し、ネットワークが描出されます  

### ノード（点）

ネットワークのノードをクリックすると、そのノードに対応した遺伝子のKOマウスが示す異常表現型の一覧が表示されます  

ノードをドラッグして、移動することができます

### エッジ（線）

ノードとノードをつなぐエッジ（線）をクリックすると、その２つの遺伝子のKOマウスに共通する異常表現型の一覧が表示されます  

### コントロールパネル

左側のコントロールパネルでは、ネットワークの表示を調整することができます

#### ネットワークレイアウトの変更

以下のレイアウトから選択できます

- Cose (推奨)
- Circle
- Random
- Grid
- Concentric

#### 表現型類似度によるフィルター

`Phenotypes similarity`のスライダーで、表現型類似度に基づいてネットワーク図に表示する閾値を設定することができます

#### 効果量によるフィルター

`Phenotypes severity`のスライダーで、効果量に基づいてネットワーク図に表示する閾値を設定することができます

> [!NOTE]
> IMPCによる表現型の評価が二値（あり・なし）の場合（例: [abnormal embryo development](https://larc-tsukuba.github.io/tsumugi/app/phenotype/abnormal_embryo_development.html)）や、入力が遺伝子シンボルの場合には、効果量のスライドバーはありません


# 🔍 表現型類似遺伝子群の抽出法

## データ

- IMPCのデータセットは[Release-22.1 (2024-12-11)](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-22.1/results)の`statistical-results-ALL.csv.gz`を使用しています  

## 前処理

- KOマウスの表現型のP値が0.0001以下を抽出
  - 性差がある表現型は、`male` または `female`を注釈
  - 遺伝型特異性が表現型は、`homo`, `hetero` または `hemi`を注釈

## 類似度の計算

- 類似度の指標には、Jaccard係数を使用

## 可視化

- ネットワークの[cytoscape.js](https://academic.oup.com/bioinformatics/article/32/2/309/1744007)を使用

# ✉️ お問い合わせ

ご質問やご要望は、以下の方法でお問い合わせいただけます（日本語可）：

- **Googleフォーム**から送信  
  [お問い合わせフォーム](https://forms.gle/ME8EJZZHaRNgKZ979)

- **GitHubアカウント**をお持ちの方は、**GitHub Issue**をご利用いただけます  
  [GitHub Issue](https://github.com/akikuno/TSUMUGI-dev/issues/new/choose)
