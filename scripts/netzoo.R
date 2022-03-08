###########################################################
# Initialization
###########################################################

options(repos = "http://cran.us.r-project.org")
if (!require("pacman", q = TRUE)) install.packages("pacman")
pacman::p_load(tidyverse, Matrix, remotes, igraph, bipartite)
pacman::p_load_gh("netZoo/netZooR")
source("scripts/ALPACA.R")

###########################################################
# Import data
###########################################################

df <- read_csv("reports/symbol_mp_zygosity_effectsize.csv")

###########################################################
# Compute Modules
###########################################################

g_continue <- df %>%
    select(!zygosity) %>%
    filter(effect_size != 1) %>%
    as.data.frame()

g_discrete <- df %>%
    select(!zygosity) %>%
    filter(effect_size == 1) %>%
    as.data.frame()

start <- Sys.time() #---------
result_louvain_continue <- alpacaWBMlouvain(g_continue)
result_louvain_discrete <- alpacaWBMlouvain(g_discrete)
end <- Sys.time() #---------
end - start # 30 sec

glimpse(result_louvain_discrete)
result_louvain_continue[[1]] %>% table()
result_louvain_discrete[[1]] %>% table()

df_community <- result_louvain_discrete[[1]] %>%
    as.data.frame(check.names = FALSE) %>%
    rownames_to_column(var = "gene_id") %>%
    as_tibble() %>%
    rename(community = 2)

df_community %>%
    filter(community == 7) %>%
    as.data.frame()
df_community %>%
    filter(community == 10) %>%
    as.data.frame()
df %>% filter(effect_size == 1)
df %>% filter(marker_symbol == "Stx7")
# df$effect_size <- abs(df$effect_size)

###########################################################
# Export
###########################################################

# write_csv(df_mp_term, "reports/symbol_mp_zygosity_effectsize.csv")

# End #####################################################