library(tidyverse)

# Load data
df <- read_csv("data/impc/statistical-results-ALL.csv")

colnames(df)

df_url <-
    df %>%
    mutate(url = str_glue(
        "https://www.mousephenotype.org/data/exportraw?allele_accession_id={allele_accession_id}&phenotyping_center={phenotyping_center}&parameter_stable_id={parameter_stable_id}&pipeline_stable_id={pipeline_stable_id}"
    ))


threshold <- 1e-4

df_filter <-
    df_url %>%
    filter(p_value < threshold & (batch_significant == "FALSE" | is.na(batch_significant)))

# df_filter %>%
#     filter(parameter_stable_id == "IMPC_FER_001_001") %>%
#     pull(url)


df_select <-
    df_filter %>%
    select(marker_symbol, parameter_name, top_level_mp_term_name, p_value, effect_size, zygosity, sex, data_type, url)
    # %>%
    # select(marker_symbol, parameter_name, data_type) %>%
    # head(100) %>%
    # as.data.frame()

write_tsv(df_select, "data/impc/results_filtered.tsv")

df_select %>%
    select(top_level_mp_term_name) %>%
    group_by(top_level_mp_term_name) %>%
    summarise(Unique_Elements = n()) %>%
    as.data.frame()
