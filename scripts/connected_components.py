import networkx as nx

# 無向グラフを作成
edges = [("a", "b"), ("c", "d"), ("a", "c"), ("e", "f")]
G = nx.Graph()
G.add_edges_from(edges)

# 連結成分を取得
connected_components = list(nx.connected_components(G))

# 結果を表示
connected_components
