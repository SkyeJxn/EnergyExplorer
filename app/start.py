from dash import Dash, html, dcc, Input, Output, callback, State, no_update
import os, argparse
from config import CONFIG
import sqlite3 as sql
import plotly.express as px
import pandas as pd
from waitress import serve

parser = argparse.ArgumentParser("EnergyExplorer")
parser.add_argument('-m', choices=["dev", "pre-prod", "prod"])
args = parser.parse_args()

mode = args.m or os.environ.get("APP_MODE") or "dev"
settings = CONFIG[mode]

print(f"running {mode} environment")

# SQL setup
DB_Path = os.environ.get("DATABASE_PATH", "data/data.db")

def get_conn():
    return sql.connect(DB_Path)

# Data extraction function
def build_data():
    with get_conn() as conn:
        prod_data = pd.read_sql_query("SELECT * FROM production", conn)
        price_data = pd.read_sql_query("SELECT * FROM prices", conn)
    df = pd.merge(prod_data, price_data, on="Timestamp", how="inner")

    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="s", dayfirst=True, origin="unix")
    return df

def serve_layout():
    df = build_data()
    initial_store = df.copy()
    initial_store["Timestamp"] = initial_store["Timestamp"].astype(str)
    return html.Div([
        header,
        dropdowns,
        dcc.Store(id="df-store",data=initial_store.to_dict("records")),
        html.Div([graph, pie], className="graph-box")
        ])

x_options = {"Timestamp":"Timestamp",
            "Ren_share": "Renewable Share of Energy"
            }
y_options = {"Price": "Price",
            "Production" : "Production",
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
    "modeBarButtonsToRemove": ["pan2d", "autoscale"]
})

pie = dcc.Graph(id="pie",className="graph" ,style={"display":"none"}, config={
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": ["pan2d", "autoscale"]
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
    Input("df-store", "data"),
    Input("x-menu", "value"),
    Input("y-menu", "value")
)

def update_graph(store_data, x_axis, y_axis):
    labeling = ["<10", "10-20", "20-30", "30-40","40-50","50-60","60-70",">70"]
    
    df_loc = pd.DataFrame(store_data)

    if (x_axis == "Ren_share"):
        df_loc["Ren_share"] = pd.to_numeric(df_loc["Ren_share"], errors="coerce")
        df_loc["Ren_share_group"] = pd.cut(x=df_loc["Ren_share"], bins=[0,10,20,30,40,50,60,70,100], right=False, labels=labeling)
        agg = df_loc.groupby("Ren_share_group", as_index=False)["Price"].mean()
        fig = px.bar(agg, x="Ren_share_group", y="Price", title="Correlation of Price and Share of renewable Energy")
    else:
        if (y_axis == "Production"):
            fig = px.line(df_loc, x=x_axis, y="Total_Production", title="Energy Production Over Time")

        else:
            fig = px.line(df_loc, x=x_axis, y=y_axis, title=f"{y_axis} Over Time")

    return fig

@callback(
    Output("pie","figure"),
    Output("pie", "style"),
    Input("df-store", "data"),
    Input("graph", "clickData"),
    Input("y-menu", "value")
)
def update_pie(store_data, timestamp, y_axis):
    prod_types = ["Biomass","Coal", "Hydro",
                  "Oil_Gas", "Others", "Solar",
                  "Wind"]
    
    if timestamp and "points" in timestamp and len(timestamp["points"]) > 0:
        x_value = timestamp["points"][0]["x"]
    else:
        x_value = None

    df_loc = pd.DataFrame(store_data).drop(columns=["Ren_share", "Price"])
    df_loc["Timestamp"] = pd.to_datetime(df_loc["Timestamp"]).dt.strftime('%Y-%m-%d %H:%M')

    timed = df_loc.loc[df_loc["Timestamp"] == x_value]

    if (y_axis == "Production" and x_value != None):
        fig = px.pie(
            names=prod_types,
            values=[timed.iloc[0][ptype] for ptype in prod_types],
            title=f"Production Breakdown for {x_value}"
        )
        style = {}
    else:
        fig = None
        style = {"display":"none"}
    
    return fig, style

app.layout = serve_layout()

if mode == "dev":
    app.run(host=settings["host"], port=settings["port"], debug=settings["debug"])
if mode == "pre-prod":
    app.run(host=settings["host"], port=settings["port"], dev_tools_ui=settings["dev_ui_tools"])
if mode == "prod":
    serve(app.server, host=settings["host"], port=settings["port"])