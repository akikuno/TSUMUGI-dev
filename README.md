# IMPC-project
 
## Data set

release-15.1 (12-Oct-2021 15:42)

https://web.archive.org/web/20211203001926/https://www.mousephenotype.org/data/release


## Setting

```bash
conda update conda -y
conda create -y -n impc
conda install -y -n impc -c conda-forge \
    numpy pandas scikit-learn matplotlib seaborn hdbscan umap-learn networkx \
    r-base r-essentials

Rscript -e 'install.packages(c("arules", "arulesVis"), repos = "http://cran.us.r-project.org")'
Rscript -e 'install.packages(c("tnet", "bipartite"), repos = "http://cran.us.r-project.org" )'
```