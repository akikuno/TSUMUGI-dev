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

類似度の生データをダウンロードすることができます

> [!NOTE]
> 100MBのCSVファイルです。ダウンロードには時間がかかる場合があります。



## 表現型



> [!NOTE]
> IMPCによる表現型の評価が二値（あり・なし）の場合（例: [abnormal embryo development](https://larc-tsukuba.github.io/tsumugi/app/phenotype/abnormal_embryo_development.html)）には、効果量のスライドバーはありません


## 遺伝子


## 遺伝子リスト

# 🔍 表現型類似遺伝子群の抽出法

## データ

IMPCのデータセットは[Release-22.1 (2024-12-11)](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-22.1/results)の`statistical-results-ALL.csv.gz`を使用しています  

## 前処理

- KOマウスの表現型のP値が0.0001以下を抽出
  - 表現型に性差がある場合は、`male` または `female`を注釈

## 類似度の計算

- 類似度の指標には、Jaccard係数を使用

## 可視化

- 可視化には[cytoscape.js](https://academic.oup.com/bioinformatics/article/32/2/309/1744007)を使用

# ✉️ お問い合わせ

ご質問やご要望は、以下の方法でお問い合わせいただけます（日本語可）：

- **Googleフォーム**から送信  
  [お問い合わせフォーム](https://forms.gle/ME8EJZZHaRNgKZ979)

- **GitHubアカウント**をお持ちの方は、**GitHub Issue**をご利用いただけます  
  [GitHub Issue](https://github.com/akikuno/TSUMUGI-dev/issues/new/choose)
