import plotly.graph_objects as go

# データの定義
x_value = ["Single Bar"]
y_value = [3]  # Y軸の値を3に設定

# グラデーション用に小さなバーを重ねて作成
num_sections = 100  # グラデーションの細かさ
colors = ["yellow", "darkorange"]  # グラデーションの開始と終了の色

fig = go.Figure()

for i in range(num_sections):
    fraction = i / num_sections
    color = f"rgba(255,{255 - int(255 * fraction)},0,{fraction})"
    fig.add_trace(
        go.Bar(x=x_value, y=[y_value[0] / num_sections], marker=dict(color=color), offsetgroup=i, showlegend=False)
    )

# レイアウトの設定
fig.update_layout(
    yaxis=dict(range=[0, 3]),
    title="グラデーション付きの単一棒グラフ",
    xaxis_title="Category",
    yaxis_title="Value",
    barmode="stack",
)

# グラフの表示
fig.show()

from pathlib import Path

Path("tmp.html").write_text(fig.to_html())
