## Setting

```bash
conda create -y -n env-tsumugi -c conda-forge python=3.10

conda install -y -n env-tsumugi \
    pip pytest ipykernel numpy pandas scikit-learn matplotlib seaborn \
    networkx dash dash_cytoscape nodejs yarn

conda activate env-tsumugi
```

