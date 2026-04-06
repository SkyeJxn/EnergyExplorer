from dash import Dash, html, dcc, Input, Output, callback, State, no_update
import os, argparse
from src.app.net_config import NET_CONFIG
import plotly.express as px
from waitress import serve
import requests as rq

parser = argparse.ArgumentParser("EnergyExplorer")
parser.add_argument('-m', choices=["dev", "pre-prod", "prod"])
args = parser.parse_args()

buttons = ["pan2d", "autoscale", "select",
            "lasso", "toImage", "zoom2d", 
            "zoomIn2d", "zoomOut2d", "resetScale2d"]

mode = args.m or os.environ.get("APP_MODE") or "dev"
settings = NET_CONFIG[mode]

print(f"running {mode} environment")

# SQL setup
Backend = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")

x_options = {"Timestamp":"Timestamp",
            "Ren_share": "Renewable Share of Energy"
            }
y_options = {"Price": "Price",
            "Total_Production" : "Production",
            "Ren_share": "Renewable Share of Energy"}

x_menu = html.Div(children=[html.Label("x-axis menu"),dcc.Dropdown(x_options, "Timestamp", id="x-menu", clearable=False, persistence=True, searchable=False)], className="dropdown")
y_menu = html.Div(children=[html.Label("y-axis menu"), dcc.Dropdown(y_options, "Price", id="y-menu", clearable=False, persistence=True, searchable=False)], className="dropdown left")

dropdowns = html.Div([x_menu, y_menu])

# UI components
header = html.Div(html.H1("EnergyExplorer"), className="header")

# graph components
graph =dcc.Graph(id="graph", className="graph", config={
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": buttons
    }, clear_on_unhover=True)

pie = dcc.Graph(id="pie",className="graph" ,style={"display":"none"}, config={
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": buttons
})

# Dash app setup

app = Dash(__name__, title="EnergyExplorer")

@callback(
    Output("y-menu", "value"),
    Output("y-menu", "disabled"),
    Input("x-menu", "value"),
    State("y-menu", "value")
)

def restrict_y_menu(x_axis, curr_val):
    if x_axis == "Ren_share":
        fixed_val = "Price"
        return fixed_val, True
    else:
        return no_update, False

@callback(
    Output("graph", "figure"),
    Input("x-menu", "value"),
    Input("y-menu", "value")
)

def update_graph(x_axis, y_axis):
    if (x_axis == "Ren_share"):
        data = rq.get(f"{Backend}/bins").json()
        fig = px.bar(data, x="Bins", y="Price", labels={
            "Bins": "Renewable Energy Share"
        },title="Correlation of Price and Share of renewable Energy")
    else:
        if (y_axis == "Price"):
            data = rq.get(f"{Backend}/prices").json()
        elif (y_axis == "Total_Production"):
            data = rq.get(f"{Backend}/production").json()
        elif (y_axis == "Ren_share"):
            data = rq.get(f"{Backend}/ren_share").json()
        fig = px.line(data, x="Timestamp", y="Data", title=f"{y_axis} Over Time")

    return fig

@callback(
    Output("pie","figure"),
    Output("pie", "style"),
    Input("graph", "hoverData"),
    Input("y-menu", "value")
)
def update_pie(timestamp, y_axis):
    palette = {
        "Biomass": "blue",
        "Coal": "red",
        "Hydro": "green",
        "Oil & Gas": "purple",
        "Others": "orange",
        "Solar": "pink",
        "Wind": "cyan"
        }
    
    if y_axis == "Total_Production":
        if timestamp and "points" in timestamp and len(timestamp["points"]) > 0:
            x_value = timestamp["points"][0]["x"]
            data = rq.get(f"{Backend}/pie?x={x_value}").json()
        else:
            data = rq.get(f"{Backend}/pie").json()

        values_dict = data.get("values", {})
        keys = list(values_dict.keys())
        values = list(values_dict.values())
        title = data.get("title", "Production Breakdown")
        pie_data = {"name": keys, "value": values}

        fig = px.pie(
            pie_data,
            names="name",
            values="value",
            color="name",
            title=title,
            color_discrete_map=palette,

        )
        style = {}
    else:
        fig = None
        style = {"display":"none"}
    
    return fig, style

app.layout = html.Div([
        header,
        dropdowns,
        html.Div([graph, pie], className="graph-box")
        ])

if mode == "dev":
    app.run(host=settings["host"], port=settings["port"], debug=settings["debug"])
if mode == "pre-prod":
    app.run(host=settings["host"], port=settings["port"], dev_tools_ui=settings["dev_ui_tools"])
if mode == "prod":
    serve(app.server, host=settings["host"], port=settings["port"])