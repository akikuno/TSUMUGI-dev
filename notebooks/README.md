## Setting

```bash

if ! { conda info --envs | grep -q "env-tsumugi"; }; then
    conda create -y -n env-tsumugi python=3.12
    conda install -y -n env-tsumugi -c conda-forge \
        numpy pandas polars matplotlib seaborn plotnine scikit-learn statsmodels \
        ipykernel ipywidgets nbstripout \
        tqdm networkx dash dash_cytoscape nodejs yarn prettier
fi

conda activate env-tsumugi

if ! grep -q nbstripout .gitattributes; then
    nbstripout --install
    echo "*.ipynb filter=nbstripout" >> .gitattributes
fi
```


