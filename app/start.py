from dash import Dash, html, dcc, Input, Output, callback, State, no_update
import os
import sqlite3 as sql
import plotly.express as px
import pandas as pd
import numpy as np
from waitress import serve

#app name (dev, pre-prod, prod) and socket values
appName = "dev"

socket = {
    "IP": "localhost",
    "Port": 8080
    }


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

df = build_data()

# UI components
header = html.H1("Visual Dashboard for Energy Data")

x_options = {"Timestamp":"Timestamp",
            "Ren_share": "Renewable Share of Energy"
            }
x_menu = html.Div(children=[html.Label("x-axis menu"),dcc.Dropdown(x_options, "Timestamp", id="x-menu")])

y_options = {"Price": "Price",
            "Production" : "Production",
            "Ren_share": "Renewable Share of Energy"}
y_menu = html.Div(children=[html.Label("y-axis menu"), dcc.Dropdown(y_options, "Price", id="y-menu")])

graph = dcc.Graph(id="graph")

refresh_button = html.Button("Refresh Data", id="rfs-btn")

initial_store = df.copy()
initial_store["Timestamp"] = initial_store["Timestamp"].astype(str)

# Dash app setup

app = Dash(appName)

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
    if n_clicks:
        new_df = build_data()
        new_store = new_df.copy()
        new_store["Timestamp"] = new_store["Timestamp"].astype(str)
        return new_store.to_dict("records")
    return initial_store.to_dict("records")

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

app.layout = html.Div([header, refresh_button, x_menu, y_menu, dcc.Store(id="df-store", data=initial_store.to_dict("records")), graph])

if appName == "dev":
    app.run(host=socket["IP"], port=socket["Port"], debug=True)
if appName == "pre-prod":
    app.run(host=socket["IP"], port=socket["Port"], dev_tools_ui=False)
if appName == "prod":
    serve(app.server, host=socket["IP"], port=socket["Port"])