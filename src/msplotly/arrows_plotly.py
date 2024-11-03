"""Plot arrows and change their color by selecting them."""

import plotly.graph_objects as go
from plotly.graph_objects import Figure
import dash
from dash import html, dcc, Input, Output, callback

from arrow import Arrow


def plot_polygon(
    fig: Figure, x_values: int, y_values: int, color="blue", name=None
) -> None:
    """Plot  representing genes or homology regions."""
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=y_values,
            fill="toself",
            mode="lines+text",
            line=dict(color=color),
            fillcolor=color,
            name=name,
            hoverlabel=dict(font_size=18),
            hovertemplate=f"<b>{name}</b><extra></extra>",
        )
    )


# create figure
fig = go.Figure()

# Customize layout
fig.update_layout(
    height=1200,
    width=1400,
    clickmode="event+select",
)

head_height = 20 * 0.2
arrow_1 = Arrow(x1=10, x2=30, y=10, head_height=head_height)
arrow_2 = Arrow(x1=20, x2=40, y=20, head_height=head_height)

# plot first gene
x_val, y_val = arrow_1.get_coordinates()
plot_polygon(fig, x_val, y_val, name="gene1")
# plot second gene
x_val, y_val = arrow_2.get_coordinates()
plot_polygon(fig, x_val, y_val, name="gene2")

# initialize the Dash app
app = dash.Dash(__name__)

# create app layout
app.layout = html.Div(
    [dcc.Graph(id="arrows", figure=fig), html.Div(id="selected-data")]
)


@callback(
    Output("selected-data", "children"),
    # Input("arrows", "selectedData"),
    Input("arrows", "clickData"),
)
def display_selected_data(clickData):
    print(clickData)


app.run(debug=True)
