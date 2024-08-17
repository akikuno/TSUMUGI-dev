library(tidyverse)
library(janitor)

df <- read_csv("data/impc/statistical_filtered_pvalue.csv")

system("mkdir -p data/mp_term_name")

# df <- df %>%
#     mutate(mp_term_name = make_clean_names(mp_term_name))
df %>%
    select(mp_term_name) %>%
    distinct() %>%
    arrange(mp_term_name) %>%
    pull() %>%
    walk(~ {
        mp_term_name <- make_clean_names(.x)
        df %>%
            filter(mp_term_name == .x) %>%
            write_csv(paste0("data/mp_term_name/", mp_term_name, ".csv"))
    })
