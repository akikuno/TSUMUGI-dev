import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs("data/reports")

###############################################################################
# Import data
###############################################################################

in_file = "data/impc/results/statistical-results-ALL.csv.gz"
df = pd.read_csv(in_file)

###############################################################################
# Select columns
###############################################################################

cols = ["marker_symbol", "mp_term_name", "zygosity", "effect_size"]
df_select = df[cols]

tmp = df_select.dropna()

tmp.effect_size.plot(style=".")
plt.show()
###############################################################################
# Filter P value < 0.05 and Effect size > ± 75%
###############################################################################
tmp: pd.DataFrame = df_select

tmp = tmp[tmp.marker_symbol == "Maf"]
tmp[tmp.effect_size == 1]

pval_filter = df_select["p_value"] < 0.05

qhigh = df_select["effect_size"].quantile(0.95)
qlow = df_select["effect_size"].quantile(0.05)
es_filter = (df_select["effect_size"] > qhigh) | (df_select["effect_size"] < qlow)

df_filter = df_select[pval_filter & es_filter]
df_filter = df_filter.drop_duplicates(subset=cols)
df_filter = df_filter.sort_values(["marker_symbol", "p_value"])

tmp = df_filter["effect_size"]
tmp = pd.DataFrame(tmp.describe())
target = ["min", "25%", "50%", "75%", "max"]
tmp[tmp.index.isin(target)].boxplot()
plt.show()
# 192632
# 一時保存
df_filter.to_csv("data/reports/pval_filter.csv", index=False)

###############################################################################
# Convert to -log10 P value
###############################################################################

df_filter["effect_size"].describe()
df_filter = pd.read_csv("data/reports/pval_filter.csv")

# P値の対数変換および最大値を20に設定
df_log = df_filter.copy()
df_log["p_value"] = df_log["p_value"].replace(0, 10 ** -20)
df_log["p_value"] = -np.log10(df_log["p_value"])
df_log[df_log["p_value"] > 20] = 20

# symbolとparameterが重複している場合には-logPが大きい方を選択する
df_log = (
    df_log.groupby(["marker_symbol", "parameter_name"]).aggregate(np.max).reset_index()
)

df_log["p_value"].describe()
df_log.parameter_name.describe()

###############################################################################
# Imputate missing "parameter_name" with 0
###############################################################################

template = pd.DataFrame(df.parameter_name.unique(), columns=["parameter_name"])
template["p_value"] = 0
df_template = pd.melt(
    template, id_vars="parameter_name", var_name="p_value_temp", value_name="delete"
)

df_concat = pd.DataFrame(columns=df_log.columns)
for symbol in df_log.marker_symbol.unique():
    print(symbol)
    df_tmp = df_log.loc[df_log.marker_symbol == symbol]
    df_merge = pd.merge(df_tmp, df_template, how="right", on="parameter_name")
    df_merge.marker_symbol = df_merge.marker_symbol.fillna(symbol)
    df_merge.p_value = df_merge.p_value.fillna(0)
    df_merge = df_merge[df_log.columns]
    df_concat = pd.concat([df_concat, df_merge], axis=0)

df_concat.to_csv("data/reports/param_imputation.csv", index=False)

