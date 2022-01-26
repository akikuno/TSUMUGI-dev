import os
import numpy as np
import pandas as pd

os.makedirs("data/reports")

###############################################################################
# Import data
###############################################################################

in_file = "data/reports/param_imputation.csv"
df = pd.read_csv(in_file)

###############################################################################
# Transform
###############################################################################


df_test = pd.concat([df.head(1000), df.tail(10000)])
df_test.pivot(index="marker_symbol", columns="parameter_name", values="p_value")

