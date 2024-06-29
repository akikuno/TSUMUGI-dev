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

## Setting

```bash
conda update conda -y
conda create -y -n impc
conda install -y -n impc -c conda-forge \
    numpy pandas scikit-learn matplotlib seaborn hdbscan umap-learn networkx \
    r-base r-essentials
```
