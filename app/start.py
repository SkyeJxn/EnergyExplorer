from dash import Dash, html, dcc, Input, Output, callback, State, no_update
import os, argparse
from config import CONFIG
import sqlite3 as sql
import plotly.express as px
import pandas as pd
import numpy as np
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
        header, refresh_button,
        dropdowns,
        dcc.Store(id="df-store", data=initial_store.to_dict("records")), graph])
    

# UI components
header = html.Div(html.H1("EnergyExplorer"), className="header")

# Dropdown builder
x_options = {"Timestamp":"Timestamp",
            "Ren_share": "Renewable Share of Energy"
            }
y_options = {"Price": "Price",
            "Production" : "Production",
            "Ren_share": "Renewable Share of Energy"}

x_menu = html.Div(children=[html.Label("x-axis menu"),dcc.Dropdown(x_options, "Timestamp", id="x-menu", clearable=False)], className="dropdown")
y_menu = html.Div(children=[html.Label("y-axis menu"), dcc.Dropdown(y_options, "Price", id="y-menu", clearable=False)], className="dropdown left")

dropdowns = html.Div([x_menu, y_menu])

# graph component
graph =dcc.Graph(id="graph", config={
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": ["pan2d", "autoscale"]
})

refresh_button = html.Button("Refresh Data", id="rfs-btn")

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
    Output("df-store", "data"),
    Input("rfs-btn", "n_clicks")
)

def refresh_data(n_clicks):
    new_df = build_data()
    new_store = new_df.copy()
    new_store["Timestamp"] = new_store["Timestamp"].astype(str)
    return new_store.to_dict("records")

@callback(
    Output("graph", "figure"),
    Input("df-store", "data"),
    Input("x-menu", "value"),
    Input("y-menu", "value")
)

def update_graph(store_data, x_axis, y_axis):
    prod_types = ["Biomass","Coal", "Hydro",
                  "Oil_Gas", "Others", "Solar",
                  "Wind", "Total_Production"]
    
    df_loc = pd.DataFrame(store_data)

    if (x_axis == "Ren_share"):
        df_loc["Ren_share"] = pd.to_numeric(df_loc["Ren_share"], errors="coerce")
        agg = df_loc.groupby("Ren_share", as_index=False)["Price"].mean()
        fig = px.bar(agg, x="Ren_share", y="Price", title="Correlation of Price and Share of renewable Energy")
    else:
        if (y_axis == "Production"):
            fig = px.line(df_loc, x=x_axis, y=prod_types, title="Energy Production Over Time")
        else:
            fig = px.line(df_loc, x=x_axis, y=y_axis, title=f"{y_axis} Over Time")

    return fig

app.layout = serve_layout()

if mode == "dev":
    app.run(host=settings["host"], port=settings["port"], debug=settings["debug"])
if mode == "pre-prod":
    app.run(host=settings["host"], port=settings["port"], dev_tools_ui=settings["dev_ui_tools"])
if mode == "prod":
    serve(app.server, host=settings["host"], port=settings["port"])