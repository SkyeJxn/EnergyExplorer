from dash import Dash, html, dcc, Input, Output, callback
import os, time
import sqlite3 as sql
import plotly.express as px
import pandas as pd

# SQL setup
DB_Path = os.environ.get("DATABASE_PATH", "data/data.db")
sql_conn = sql.connect(DB_Path)
sql_cursor = sql_conn.cursor()

# Data fetching function
def fetch_new_data(n_clicks):
    if n_clicks:
        time.sleep(2)  # Simulate time delay for fetching data
        return renew_data()
    return df

# Data extraction function
def renew_data():
    prod_data = pd.read_sql_query("SELECT * FROM production", sql_conn)
    price_data = pd.read_sql_query("SELECT * FROM prices", sql_conn)
    df = pd.merge(prod_data, price_data, on="Timestamp", how="inner")
    df = df.rename(columns={"Ren_share": "Renewable share of energy"})
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="s", dayfirst=True, origin="unix")
    return df

df = renew_data()

# UI components
header = html.H1("Welcome to the Data Visualization Dashboard")

x_options = ["Timestamp", "Price"]
x_menu = html.Div(children=[html.Label("x-axis menu"),dcc.Dropdown(x_options, "Timestamp")])

y_options = ["Price", "Production", "Renewable share of energy"]
y_menu = html.Div(children=[html.Label("y-axis menu"), dcc.Dropdown(y_options, "Price")])

graph = dcc.Graph(id="graph")

refresh_data = html.Button("Refresh Data")

get_new_data = html.Button("Get New Data")

# Dash app setup

app = Dash()

@callback(
        Output(renew_data(), "data"),
        Input(refresh_data, "n_clicks")
)

@callback(
    Output(fetch_new_data()),
    Input(get_new_data, "n_clicks")
)

@callback(
    Output("graph", "figure"),
    Input(x_menu.children[1], "value"),
    Input(y_menu.children[1], "value")
)

def update_graph(x_axis, y_axis):
    prod_types = ["Biomass","Coal", "Hydro",
                  "Oil_Gas", "Others", "Solar",
                  "Wind", "Total_Production"]
    
    if (y_axis == "Production"):
        fig = px.line(df, x=x_axis, y=prod_types, title="Energy Production Over Time", )
    else:
        fig = px.line(df, x=x_axis, y=y_axis, title=f"{y_axis} Over Time")

    return fig

app.layout = html.Div([header, refresh_data, get_new_data, x_menu, y_menu, graph])

app.run(host="localhost", port=8080, debug=True)