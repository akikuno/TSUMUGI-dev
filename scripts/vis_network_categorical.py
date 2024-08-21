from pathlib import Path

import dash
import dash_cytoscape as cyto
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output

path_network = Path("data", "network.csv")
df_network = pd.read_csv(path_network)
data = df_network.to_dict(orient="records")

# # Raw CSV-like data
# data = [
#     {"from": "A", "to": "B", "node_size": 3, "edge_size": 1},
#     {"from": "B", "to": "C", "node_size": 1, "edge_size": 3},
#     {"from": "C", "to": "A", "node_size": 2, "edge_size": 2},
#     {"from": "C", "to": "D", "node_size": 1, "edge_size": 1},
# ]

scale_node_size = 20
scale_edge_size = 10
# -----------------------------------------------------------------------------
# Add nodes with size labels and color based on size
# -----------------------------------------------------------------------------

# Determine max/min sizes of nodes (= effect size)

node_sizes = {}
max_size = 0
min_size = float("inf")
for entry in data:
    for node in [entry["from"], entry["to"]]:
        if node not in node_sizes:
            node_sizes[node] = entry["node_size"]
        else:
            node_sizes[node] = max(node_sizes[node], entry["node_size"])
        max_size = max(max_size, node_sizes[node])
        min_size = min(min_size, node_sizes[node])


# Function to interpolate colors between yellow and dark orange
def interpolate_color(size, min_size, max_size):
    ratio = (size - min_size) / (max_size - min_size) if max_size != min_size else 1
    yellow = [255, 255, 0]  # Yellow (RGB)
    dark_orange = [255, 140, 0]  # Dark Orange (RGB)
    color = [int(yellow[i] + (dark_orange[i] - yellow[i]) * ratio) for i in range(3)]
    return f"rgb({color[0]}, {color[1]}, {color[2]})"


nodes = []

for entry in data:
    scaled_size = entry["node_size"] * scale_node_size  # Scale node size
    color = interpolate_color(entry["node_size"], min_size, max_size)
    nodes.append(
        {
            "data": {"id": entry["from"], "label": entry["from"], "annotation": entry["from_mp"].replace("\\n", "\n")},
            "style": {
                "width": scaled_size,
                "height": scaled_size,
                "background-color": color,
            },
        }
    )
    nodes.append(
        {
            "data": {"id": entry["to"], "label": entry["to"], "annotation": entry["to_mp"].replace("\\n", "\n")},
            "style": {
                "width": scaled_size,
                "height": scaled_size,
                "background-color": color,
            },
        }
    )

# for node, size in node_sizes.items():
#     scaled_size = size * scale_node_size  # Scale node size
#     color = interpolate_color(size, min_size, max_size)
#     nodes.append(
#         {
#             "data": {"id": node, "label": node},
#             "style": {
#                 "width": scaled_size,
#                 "height": scaled_size,
#                 "background-color": color,
#             },
#         }
#     )

unique_nodes = list({node["data"]["id"]: node for node in nodes}.values())
# -----------------------------------------------------------------------------
# Add edges with size labels
# -----------------------------------------------------------------------------
edges = []

for entry in data:
    edges.append(
        {
            "data": {
                "source": entry["from"],
                "target": entry["to"],
                "label": f"{entry['edge_size']}",  # Edge size label
                "annotation": entry["edge_mp"].replace("\\n", "\n"),
            },
            "style": {"width": entry["edge_size"] * scale_edge_size},  # Scale edge width
        }
    )


elements = unique_nodes + edges

###############################################################################
# Dash app
###############################################################################

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div(
    [
        html.Div(
            [
                html.H1("Phenotypic similarity gene network of 'Male Infertility'", style={"textAlign": "center"}),
                html.P("Select Network layout:"),
                dcc.Dropdown(
                    id="layout-dropdown",
                    options=[
                        {"label": "Breadthfirst", "value": "breadthfirst"},
                        {"label": "Circle", "value": "circle"},
                        {"label": "Cose", "value": "cose"},
                        {"label": "Grid", "value": "grid"},
                        {"label": "Random", "value": "random"},
                        {"label": "Concentric", "value": "concentric"},
                    ],
                    value="cose",
                    clearable=False,
                    style={"width": "50%", "align-items": "center", "justify-content": "center"},
                ),
                cyto.Cytoscape(
                    id="network-graph",
                    elements=elements,
                    style={"width": "100%", "height": "1000px"},
                    layout={"name": "cose"},
                    stylesheet=[
                        {
                            "selector": "node",
                            "style": {"label": "data(label)", "text-valign": "center", "text-halign": "center"},
                        },
                        {
                            "selector": "edge",
                            "style": {
                                "curve-style": "bezier",
                                "label": "data(label)",
                                "font-size": "10px",
                                "text-rotation": "autorotate",
                            },
                        },
                    ],
                ),
                html.Div(id="tooltip"),
            ],
            style={"width": "100%", "display": "inline-block"},
        ),
    ]
)


@app.callback(
    [Output("network-graph", "layout"), Output("tooltip", "children"), Output("tooltip", "style")],
    [
        Input("layout-dropdown", "value"),
        Input("network-graph", "mouseoverNodeData"),
        Input("network-graph", "mouseoverEdgeData"),
        Input("network-graph", "tapNode"),
        Input("network-graph", "tapEdge"),
    ],
)
def update_layout_and_display_tooltip(layout, node_data, edge_data, tap_node, tap_edge):
    ctx = dash.callback_context

    # 1. レイアウトドロップダウンが変更された場合
    if "layout-dropdown.value" in ctx.triggered[0]["prop_id"]:
        return {"name": layout}, dash.no_update, dash.no_update

    # 2. ノードやエッジがタップまたはマウスオーバーされた場合
    tooltip_text = ""
    if "tapNode" in ctx.triggered[0]["prop_id"]:
        tooltip_text = node_data["annotation"]
    elif "tapEdge" in ctx.triggered[0]["prop_id"]:
        tooltip_text = edge_data["annotation"]
    elif "mouseoverNodeData" in ctx.triggered[0]["prop_id"]:
        tooltip_text = node_data["annotation"]
    elif "mouseoverEdgeData" in ctx.triggered[0]["prop_id"]:
        tooltip_text = edge_data["annotation"]

    tooltip_style = {
        "visibility": "visible",
        "position": "absolute",
        "padding": "20px",
        "background": "#ddd",
        "border-radius": "5px",
        "font-size": "20px",
        "width": "50%",
        "margen": "0, auto",
        "display": "flex",
        "align-items": "center",
        "justify-content": "center",
        "line-height": "1.5",
        "text-align": "center",
    }

    return dash.no_update, html.Div(tooltip_text, style={"white-space": "pre-line"}), tooltip_style


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
