import io

import dash
import dash_cytoscape as cyto
import pandas as pd
from dash import html
from dash.dependencies import Input, Output

# CSVデータを文字列として扱う
csv_data = """from,to,node_size,edge_size,from_node_annotation,to_node_annotation,edge_annotation
A,B,1,1,"example A\nhogehogehogheohgoeho","example B","example A-B"
B,C,1,1,"example B","example C","example B-C"
"""

# io.StringIOを使用してCSVデータを読み込む
df = pd.read_csv(io.StringIO(csv_data))

# ノードとエッジを生成
nodes = []
edges = []

for index, row in df.iterrows():
    nodes.append({"data": {"id": row["from"], "label": row["from"], "annotation": row["from_node_annotation"]}})
    nodes.append({"data": {"id": row["to"], "label": row["to"], "annotation": row["to_node_annotation"]}})
    edges.append(
        {
            "data": {
                "source": row["from"],
                "target": row["to"],
                "label": row["edge_annotation"],
                "annotation": row["edge_annotation"],
            }
        }
    )

# ノードをユニークにする
unique_nodes = {node["data"]["id"]: node for node in nodes}.values()

# Dashアプリケーションの設定
app = dash.Dash(__name__)

cyto_layout = {
    "name": "preset",
}

app.layout = html.Div(
    [
        cyto.Cytoscape(
            id="cytoscape",
            elements=list(unique_nodes) + edges,
            layout=cyto_layout,
            style={"width": "100%", "height": "400px"},
        ),
        html.Div(
            id="tooltip",
            style={
                "position": "absolute",
                "padding": "10px",
                "background": "#ddd",
                "border-radius": "5px",
                "visibility": "hidden",
            },
        ),
    ]
)


# マウスオーバー時にツールチップを表示するためのコールバック
@app.callback(
    Output("tooltip", "children"),
    Output("tooltip", "style"),
    [
        Input("cytoscape", "mouseoverNodeData"),
        Input("cytoscape", "mouseoverEdgeData"),
        Input("cytoscape", "tapNode"),
        Input("cytoscape", "tapEdge"),
    ],
)
def display_tooltip(node_data, edge_data, tap_node, tap_edge):
    ctx = dash.callback_context

    if not ctx.triggered:
        return "", {"visibility": "hidden"}

    tooltip_text = ""
    if "tapNode" in ctx.triggered[0]["prop_id"]:
        tooltip_text = node_data["annotation"]
    elif "tapEdge" in ctx.triggered[0]["prop_id"]:
        tooltip_text = edge_data["annotation"]
    elif "mouseoverNodeData" in ctx.triggered[0]["prop_id"]:
        tooltip_text = node_data["annotation"]
    elif "mouseoverEdgeData" in ctx.triggered[0]["prop_id"]:
        tooltip_text = edge_data["annotation"]

    return html.Div(tooltip_text, style={"white-space": "pre-line"}), {
        "visibility": "visible",
        "position": "absolute",
        "padding": "10px",
        "background": "#ddd",
        "border-radius": "5px",
        "font-size": "20px",
    }


if __name__ == "__main__":
    app.run_server(debug=True)
