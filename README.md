[![License](https://img.shields.io/badge/License-MIT-9cf.svg)](https://choosealicense.com/licenses/mit/)

<p align="center">
<img src="image/tsumugi-logo.jpg" alt="Tsumugi Logo" width="90%">
</p>


## IMPC Dataset

- Release-21.1 (2024-06-13)

https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-21.1/

## Setting

```bash
conda update conda -y
conda create -y -n env-impc -c conda-forge python=3.10 \
    pip pytest ipykernel numpy pandas scikit-learn matplotlib seaborn \
    networkx dash dash_cytoscape
conda activate env-impc
```

