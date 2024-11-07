<img src="image/tsumugi-logo.svg" alt="Tsumugi Logo" width="200">


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

