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
        response = rq.get(f"{url}&start=1763679600")
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
             }
    unwanted_prod = ['Hydro pumped storage consumption', 'Cross border electricity trading',
                     'Load (incl. self-consumption)', 'Residual load', 'Renewable share of load']
    labeling = ["<10", "10-20", "20-30", "30-40","40-50","50-60","60-70",">70"]
    bins = [0,10,20,30,40,50,60,70,100]
    prod_types = ["Biomass","Coal", "Hydro",
                  "Oil_Gas", "Others", "Solar",
                  "Wind"]

    data = data_fetch(url, sql_cursor, "production", init)

    df = build_production_df(data, 'name', 'data', 'production_types', 'unix_seconds').drop(columns=unwanted_prod)
    df = df.rename(columns={"Renewable share of generation":"Ren_share"})

    df["Total_Production"] = df.sum(axis=1)

    for key, values in prod_sums.items():
        df[key] = df[values].sum(axis=1)


    df = df.drop(columns=[item for sublist in prod_sums.values() for item in sublist if item != 'Others'])

    df["Ren_share_bin"] = pd.cut(x=df["Ren_share"], bins=bins, right=False, labels=labeling)

    # for ptype in prod_types:
    #     df[ptype + "_pct"] = df[ptype].iloc[][ptype]

    for ptype in prod_types:
        df[f"{ptype}_pct"] = round(df[ptype] / df['Total_Production'], 2)

    pd.io.sql.to_sql(df, 'production', sql_connection, if_exists='append', index_label='Timestamp')