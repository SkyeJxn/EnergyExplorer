import requests as rq
import pandas as pd
import time

def data_fetch(url, sql_cursor, table, init = False):
    if (init == False):
        last_found = str((sql_cursor.execute(f"SELECT MAX(Timestamp) FROM {table}").fetchone()[0])+1)
        now = str(int(time.time()))
        link = ""
        link = str.join("",[url, "&start=", last_found, "&end=", now])
        response = rq.get(link)
    else:
        response = rq.get(url)
    return response.json()

def build_production_df(data, key_name, value_name, outer_key, index_name):
    flat_dict = {item[key_name]: item[value_name] for item in data[outer_key]}
    df = pd.DataFrame(flat_dict, index=data[index_name])
    return df

def price_fetch(url, sql_connection, sql_cursor, init = False):
    data = data_fetch(url, sql_cursor, "prices", init)
    df = pd.DataFrame(data['price'], index=data['unix_seconds']).rename(columns={0:'Price'})
    pd.io.sql.to_sql(df, 'prices', sql_connection, if_exists='append', index_label='Timestamp')

def prod_fetch(url, sql_connection, sql_cursor, init = False):
    prod_sums = {"Hydro": ['Hydro Run-of-River', 'Hydro water reservoir', 'Hydro pumped storage'],
             "Coal" : ['Fossil brown coal / lignite','Fossil hard coal'],
             "Oil_Gas": ['Fossil oil', 'Fossil coal-derived gas', 'Fossil gas'],
             "Wind": ['Wind offshore', 'Wind onshore'],
             "Others" : ['Geothermal', 'Others','Waste'],
             "Ren_share":['Renewable share of generation'],
             }
    unwanted_prod = ['Hydro pumped storage consumption', 'Cross border electricity trading','Load (incl. self-consumption)', 'Residual load', 'Renewable share of load']

    data = data_fetch(url, sql_cursor, "production", init)

    df = build_production_df(data, 'name', 'data', 'production_types', 'unix_seconds').drop(columns=unwanted_prod)

    df["Total_Production"] = df.sum(axis=1)

    for key, values in prod_sums.items():
        df[key] = df[values].sum(axis=1)

    df = df.drop(columns=[item for sublist in prod_sums.values() for item in sublist if item != 'Others'])

    pd.io.sql.to_sql(df, 'production', sql_connection, if_exists='append', index_label='Timestamp')