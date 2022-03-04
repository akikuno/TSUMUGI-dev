###########################################################
# Initialization
###########################################################

options(repos = "http://cran.us.r-project.org")
if (!require("pacman", q = TRUE)) install.packages("pacman")
pacman::p_load(tidyverse, igraph, bipartite)

###########################################################
# Import data
###########################################################

df <- read_csv("reports/symbol_mp_zygosity_effectsize.csv")

###########################################################
# Compute Modules
###########################################################

df$effect_size <- abs(df$effect_size)

g <- graph_from_data_frame(df)

start <- Sys.time() #---------
modules <- as_adjacency_matrix(g, attr = "effect_size") %>%
    as.matrix() %>%
    computeModules()
end <- Sys.time() #---------


list_modules <- listModuleInformation(modules)

str(list_modules)
###########################################################
# Export
###########################################################
save(list_modules, file = "reports/list_modules.rda")

end - start # 44 min

write_csv(df_mp_term, "reports/symbol_mp_zygosity_effectsize.csv")

# End #####################################################