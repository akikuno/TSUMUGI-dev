## Setting

```bash

if ! { conda info --envs | grep -q "env-tsumugi"; }; then
    conda create -y -n env-tsumugi --clone base2
    conda install -y -n env-tsumugi -c conda-forge \
        polars tqdm networkx dash dash_cytoscape nodejs yarn prettier
fi

conda activate env-tsumugi
```

