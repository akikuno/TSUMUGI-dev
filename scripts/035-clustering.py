from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans

X = np.array([[1, 2, 3], [1, 4, 3], [1, 0, 3], [10, 2, 3], [10, 4, 3], [10, 0, 3]])

clf = KMeans(n_clusters=2)
clf.fit(X)
clf.labels_

data = [
    p.split("\t")
    for p in Path("data", "impc", "results_filtered_unidimensional.tsv")
    .read_text()
    .split("\n")[:5]
]
