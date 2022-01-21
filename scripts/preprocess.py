import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/impc_pval.csv")

# P値の対数変換および最大値を20に設定
df["p_value"] = df["p_value"].replace(0, 10**-20)
df["p_value"] = -np.log10(df["p_value"])
df[df["p_value"] > 20] = 20

df["p_value"].describe()
df.parameter_name.describe()

# parameter_nameの欠損を0で補完
template = pd.DataFrame(df.parameter_name.unique(), columns=["parameter_name"])
template["p_value"] = 0
df_template = pd.melt(template, id_vars="parameter_name", var_name="p_value_temp", value_name="delete")

df_concat = pd.DataFrame(columns = df.columns)
for symbol in df.marker_symbol.unique():
    print(symbol)
    df_tmp = df.loc[df.marker_symbol == symbol]
    df_merge = pd.merge(df_tmp, df_template, how="right", on="parameter_name")
    df_merge.marker_symbol = df_merge.marker_symbol.fillna(symbol)
    df_merge.p_value = df_merge.p_value.fillna(0)
    df_merge = df_merge[df.columns]
    df_concat = pd.concat([df_concat, df_merge], axis=0)

df_concat.to_csv("data/impc_param_imputation.csv", index = False)

# df["p_value"].plot.hist()
# plt.show()