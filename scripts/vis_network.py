import dash
import dash_cytoscape as cyto
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output

from pathlib import Path
import pandas as pd

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

# Create unique nodes and determine their sizes
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


# Create Cytoscape elements
elements = []

# Add nodes with size labels and color based on size
for node, size in node_sizes.items():
    scaled_size = size * 10  # Scale node size
    color = interpolate_color(size, min_size, max_size)
    elements.append(
        {
            "data": {"id": node, "label": f"{node} ({size})"},
            "style": {
                "width": scaled_size,
                "height": scaled_size,
                "background-color": color,
                "border-color": "black",
                "border-width": 2,
            },
        }
    )

# Add edges with size labels
for entry in data:
    elements.append(
        {
            "data": {
                "source": entry["from"],
                "target": entry["to"],
                "label": f"{entry['edge_size']}",  # Edge size label
            },
            "style": {"width": entry["edge_size"] * 2},  # Scale edge width
        }
    )

# Create the color scale as a vertical color bar using Plotly
colorscale_fig = go.Figure(
    go.Heatmap(
        # z=[[min_size, max_size]],
        # colorscale=[[0, "rgb(255, 255, 0)"], [1, "rgb(255, 140, 0)"]],
        showscale=True,
        colorbar=dict(
            thickness=10,
            len=1,
            outlinewidth=1,
            ticks="outside",
            tickvals=[min_size, max_size],
            ticktext=[str(min_size), str(max_size)],
            title="Node Size",
        ),
    )
)

colorscale_fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), xaxis=dict(visible=False), yaxis=dict(visible=False))

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div(
    [
        html.Div(
            [
                dcc.Dropdown(
                    id="layout-dropdown",
                    options=[
                        {"label": "Breadthfirst", "value": "breadthfirst"},
                        {"label": "Circle", "value": "circle"},
                        {"label": "Grid", "value": "grid"},
                        {"label": "Random", "value": "random"},
                        {"label": "Cose", "value": "cose"},
                        {"label": "Concentric", "value": "concentric"},
                    ],
                    value="breadthfirst",
                    clearable=False,
                    style={"width": "50%"},
                ),
                cyto.Cytoscape(
                    id="network-graph",
                    elements=elements,
                    style={"width": "100%", "height": "600px"},
                    layout={"name": "breadthfirst"},
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
            ],
            style={"width": "80%", "display": "inline-block"},
        ),
        html.Div(
            [dcc.Graph(figure=colorscale_fig, config={"displayModeBar": False})],
            style={"width": "15%", "display": "inline-block", "vertical-align": "top"},
        ),
    ]
)


# Callback to update layout based on dropdown selection
@app.callback(Output("network-graph", "layout"), Input("layout-dropdown", "value"))
def update_layout(layout):
    return {"name": layout}


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
