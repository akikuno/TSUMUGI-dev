###########################################################
# Initialization
###########################################################

options(repos = "http://cran.us.r-project.org")
if (!require("pacman", q = TRUE)) install.packages("pacman")
pacman::p_load(tidyverse, fs)

dir_create("reports", recurse = TRUE)

###########################################################
# Select data
###########################################################

df <- read_csv("data/impc/results/statistical-results-ALL.csv.gz")

cols <- c("marker_symbol", "mp_term_name", "zygosity", "effect_size")

df_select <- df %>% select(all_of(cols))

df_mp_term <- df_select %>% drop_na()

###########################################################
# Export
###########################################################

write_csv(df_mp_term, "reports/symbol_mp_zygosity_effectsize.csv")

# End #####################################################