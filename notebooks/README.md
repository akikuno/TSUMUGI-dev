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

# Configuration of nbstripout to exclude output and metadata of .ipynb files from Git commits.
[  -f .gitattributes ] || touch .gitattributes
if ! grep -q nbstripout .gitattributes; then
    nbstripout --install
    echo '{"metadata": false, "cell_metadata": false, "output": false}' > .nbstripout
    echo "*.ipynb filter=nbstripout" >> .gitattributes
fi

```


