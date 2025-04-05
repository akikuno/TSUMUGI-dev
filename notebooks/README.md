## Setting

```bash

if ! { conda info --envs | grep -q "env-tsumugi"; }; then
    conda create -y -n env-tsumugi -c conda-forge python=3.12
    conda install -y -n env-tsumugi \
        pip pytest ipykernel numpy pandas scikit-learn matplotlib seaborn tqdm \
        networkx dash dash_cytoscape nodejs yarn prettier
fi

conda activate env-tsumugi
```

