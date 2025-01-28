# IMPCを用いた表現型類似遺伝子群の抽出


## v0.1.3 ToDO

- [ ] JS: 単一ノードを除去する
- [ ] CSS: 外枠の余白を増やす (現在は左のコントロールパネルが左枠のギリギリ)
- [ ] HTML/CSS/JS: Severityが0, 1のときには、Phenotype severityのスライドバーを非表示にする


## 目的

- IMPCの表現型データを用いて、表現型類似遺伝子群を抽出する。
  - 表現型類似遺伝子は、KOマウスの全身の表現型が類似している遺伝子群である。
- 以下をまとめる
  - 表現型類似遺伝子群のスクリーニング手法の開発
  - 表現型類似遺伝子群のリストの提示
  - 類似する表現型別の特徴
  - 類似する遺伝子群別の特徴

## 予想するアウトプット

-  [x] Webツールとする
  - [x] 表現型から遺伝子群を抽出する
  - [x] 特定の遺伝子から類似の表現型を持つ遺伝子群を抽出する

### 表現型から遺伝子群を抽出する
- ユーザーの指定
  - 興味のある組織（必須）
  - 興味のある表現型（必須）
  - Sex（任意）
  - Zygosity（任意）

- [x] 興味のある表現型を呈する遺伝子群の中で、類似度をグラフとして表示する。
- [x] エクセルとしてダウンロード可能にする

- ~~連続値の表現系の場合には、効果量がネガティブ or ポジティブで2つのグループに分ける~~ → 効果量のポジネガはMPに反映されているので分ける必要はない (e.g. increased/decreased circulating glucose level)

### 特定の遺伝子から類似の表現型を持つ遺伝子群を抽出する
- ユーザーの指定
  - 興味のある遺伝子（必須）
  - Sex（任意）
  - Zygosity（任意）


### 残す列

https://www.mousephenotype.org/help/programmatic-data-access/data-fields/

#### 解析に使用する列
- zygosity
- sex
- p_value
- sex_effect_p_value
- effect_size
- batch_significant
- mp_term_name
- top_level_mp_term_name
- marker_symbol

#### 生データにアクセスするための列

- allele_accession_id=MGI:5548394&
- phenotyping_center=HMGU
- parameter_stable_id=IMPC_CBC_009_001
- pipeline_stable_id=HMGU_001

例： https://www.mousephenotype.org/data/exportraw?allele_accession_id=MGI:5548394&phenotyping_center=HMGU&parameter_stable_id=IMPC_CBC_009_001&pipeline_stable_id=HMGU_001

#### なんだかよくわからない列
- null_test_p_value, genotype_p_value, p_valueの違い

## 戦略

### unidimensionalだけにして、homoとhetero、オスとメスの4カテゴリーに分ける
- male/homo
- male/hetero
- female/homo
- female/hetero

この4グループのそれぞれから、KOで似た表現型を呈する遺伝子群を探索する

1つの表現型だけが似ているというものを除くため、2つ以上のeffect_size != 0があるもの


