library(tidyverse)

df <- read_csv("data/impc/statistical_filtered_pvalue.csv")

df %>% colnames() %>% sort()

data <- df %>% select("marker_symbol", "mp_term_name") %>% distinct()

write_csv(data, "data/marker_mpterm.csv")

# # データを読み込む
# data <- tibble(
#     marker_symbol = c("A", "A", "B", "C", "C"),
#     mp_term_name = c("aaa", "bbb", "bbb", "aaa", "ccc")
# )

# mp_term_nameをリスト形式でまとめる
data_list <- data %>%
    group_by(marker_symbol) %>%
    summarise(mp_term_list = list(mp_term_name))

start <- Sys.time()
# 重複度を計算する
overlap_ratios <-
    expand.grid(from = unique(data$marker_symbol), to = unique(data$marker_symbol)) %>%
    rowwise() %>%
    mutate(group = c(from, to) %>% sort() %>% str_c(collapse="_")) %>%
    select(group) %>%
    distinct() %>%
    separate_wider_delim(group, "_", names = c("from", "to")) %>%
    rowwise() %>%
    mutate(overlap_ratio = {
        list_from <- data_list %>% filter(marker_symbol == from) %>% pull(mp_term_list) %>% unlist()
        list_to <- data_list %>% filter(marker_symbol == to) %>% pull(mp_term_list) %>% unlist()
        intersect_count <- length(intersect(list_from, list_to))
        union_count <- length(union(list_from, list_to))
        overlap_ratio = intersect_count / union_count
        overlap_ratio
    }) %>%
    filter(overlap_ratio > 0) %>%
    mutate(overlap_ratio = if_else(from == to, 0, overlap_ratio))

# 結果を表示
# print(overlap_ratios, n = 10)
end <- Sys.time()
print(end - start)  # だいたいスタートは18:00くらい
write_csv(overlap_ratios, "data/overlap_ratios.csv")
