# IMPCを用いた表現型類似遺伝子群の抽出

## 目的

- IMPCの表現型データを用いて、表現型類似遺伝子群を抽出する。
  - 表現型類似遺伝子は、KOマウスの全身の表現型が類似している遺伝子群である。
- 以下をまとめる
  - 表現型類似遺伝子群のスクリーニング手法の開発
  - 表現型類似遺伝子群のリストの提示
  - 類似する表現型別の特徴
  - 類似する遺伝子群別の特徴


## Data set

- Release-21.1 (2024-06-13)

https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-21.1/

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



## Setting

```bash
conda update conda -y
conda create -y -n impc
conda install -y -n impc -c conda-forge \
    numpy pandas scikit-learn matplotlib seaborn networkx \
    r-base r-essentials

conda activate impc
pip install -U pip
pip install k-means-constrained
```
