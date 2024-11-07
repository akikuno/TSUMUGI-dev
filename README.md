[![License](https://img.shields.io/badge/License-MIT-9cf.svg)](https://choosealicense.com/licenses/mit/)

<p align="center">
    <a href="https://www.md.tsukuba.ac.jp/LabAnimalResCNT/TSUMUGI/" target="_blank">
        <img src="image/tsumugi-logo.jpg" alt="Tsumugi Logo" width="90%">
    </a>
</p>

TSUMUGI (Trait-driven Surveillance for Mutation-based Gene module Identification) is a web tool for visualizing phenotype-driven gene networks.

## IMPC Dataset

- [Release-21.1 (2024-06-13)](https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-21.1/)

## Setting

```bash
conda create -y -n env-tsumugi -c conda-forge python=3.10 \
    pip pytest ipykernel numpy pandas scikit-learn matplotlib seaborn \
    networkx dash dash_cytoscape
conda activate env-tsumugi
```

