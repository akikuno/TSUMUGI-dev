import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

os.makedirs("data/reports")

###############################################################################
# Import data
###############################################################################

in_file = "data/reports/param_imputation.csv"
df = pd.read_csv(in_file)

###############################################################################
# Transform
###############################################################################

df_pivot = df.pivot(index="marker_symbol", columns="parameter_name", values="p_value")
df_pivot.reset_index(inplace=True)

###############################################################################
# PCA
###############################################################################

df_pca = df_pivot.iloc[:, 1:]

pca = PCA(n_components=10)
pca.fit(df_pca)

print(pca.explained_variance_ratio_)
print(pca.singular_values_)

t = pd.DataFrame(pca.transform(df_pca))

t
fig, ax = plt.subplots()
ax.plot(t[0], t[1], "bo")
plt.show()

fig, ax = plt.subplots()
ax.plot(t[1], t[2], "bo")
plt.show()
