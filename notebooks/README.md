## Setting

```bash
conda create -y -n env-tsumugi -c conda-forge python=3.12

if ! { conda info --envs | grep -q "env-tsumugi"; }; then
    conda install -y -n env-tsumugi \
        pip pytest ipykernel numpy pandas scikit-learn matplotlib seaborn \
        networkx dash dash_cytoscape nodejs yarn
fi

conda activate env-tsumugi
```

