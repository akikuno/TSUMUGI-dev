import pandas as pd

file = "data/impc/results/statistical-results-ALL.csv.gz"

df = pd.read_csv(file)
df_pval = df[df["p_value"] < 0.05]

cols = ["marker_symbol", "parameter_name", "p_value"]
df_out = df_pval[cols]
df_out = df_out.drop_duplicates(subset = cols)
df_out = df_out.sort_values(["marker_symbol", "p_value"])

df_out.to_csv("data/impc_pval.csv", index = False)
