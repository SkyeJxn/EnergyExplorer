import requests as rq
import time as tm
import sqlite3 as sql
import pandas as pd

def data_fetch(url):
    response = rq.get(url)
    return response.json()

def build_production_df(data, key_name, value_name, outer_key, index_name):
    flat_dict = {item[key_name]: item[value_name] for item in data[outer_key]}
    df = pd.DataFrame(flat_dict, index=data[index_name])
    return df

sqlite_file = './data/data.db'

sql_connection = sql.connect(sqlite_file)
sql_cursor = sql_connection.cursor()

prod_sums = {"Hydro": ['Hydro Run-of-River', 'Hydro water reservoir', 'Hydro pumped storage'],
             "Coal" : ['Fossil brown coal / lignite','Fossil hard coal'],
             "Oil_Gas": ['Fossil oil', 'Fossil coal-derived gas', 'Fossil gas'],
             "Wind": ['Wind offshore', 'Wind onshore'],
             "Others" : ['Geothermal', 'Others','Waste'],
             "Ren_share":['Renewable share of generation'],
             }

unwanted_prod = ['Hydro pumped storage consumption', 'Cross border electricity trading','Load (incl. self-consumption)', 'Residual load', 'Renewable share of load']

last_found = (sql_cursor.execute("SELECT MAX(Timestamp) FROM production").fetchone()[0])+1

now = int(tm.time())

link = f"https://api.energy-charts.info/total_power?country=de&start={last_found}&end={now}"

resp = data_fetch(link)

df = build_production_df(resp, 'name', 'data', 'production_types', 'unix_seconds').drop(columns=unwanted_prod)

df["Total_Production"] = df.sum(axis=1)

for key, values in prod_sums.items():
    df[key] = df[values].sum(axis=1)

df = df.drop(columns=[item for sublist in prod_sums.values() for item in sublist if item != 'Others'])

pd.io.sql.to_sql(df, 'production', sql_connection, if_exists='append', index_label='Timestamp')
