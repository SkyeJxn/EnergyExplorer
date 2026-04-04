import requests as rq
import pandas as pd
import time
import sqlite3 as sql

def data_fetch(url, sql_cursor, table, init=False):
    initial_start = 1763679600

    if init:
        start = initial_start
    else:
        try:
            row = sql_cursor.execute(f"SELECT MAX(Timestamp) FROM {table}").fetchone()
            max_ts = row[0] if row else None
        except sql.OperationalError as e:
            raise RuntimeError(f"Database query failed for table '{table}': {e}") from e
        except sql.ProgrammingError as e:
            raise RuntimeError(f"Invalid database cursor/connection while reading '{table}': {e}") from e
        except sql.DatabaseError as e:
            raise RuntimeError(f"Unexpected database error while reading '{table}': {e}") from e

        start = initial_start if max_ts is None else int(max_ts) + 1

    end = int(time.time())
    if start > end:
        return None

    link = f"{url}&start={start}&end={end}"

    try:
        response = rq.get(link, timeout=30)
        response.raise_for_status()
        payload = response.json()
    except rq.RequestException as e:
        raise RuntimeError(f"External API request failed for '{table}': {e}") from e
    except ValueError as e:
        raise RuntimeError(f"External API returned invalid JSON for '{table}': {e}") from e

    if not isinstance(payload, dict):
        return None

    unix_seconds = payload.get("unix_seconds")
    if not unix_seconds:
        return None

    return payload

def build_production_df(data, key_name, value_name, outer_key, index_name):
    flat_dict = {item[key_name]: item[value_name] for item in data[outer_key]}
    df = pd.DataFrame(flat_dict, index=data[index_name])
    return df

def price_fetch(url, sql_connection, sql_cursor, init = False):
    try:
        data = data_fetch(url, sql_cursor, "prices", init)
    except RuntimeError as e:
        return {"ok":False,"message": str(e)}
    if data is None:
        return {"ok": True, "message": "No new Price data"}
    
    df = pd.DataFrame(data['price'], index=data['unix_seconds']).rename(columns={0:'Price'})
    try:
        pd.io.sql.to_sql(df, 'prices', sql_connection, if_exists='append', index_label='Timestamp')
    except sql.IntegrityError as e:
        return {"ok": False, "message": str(e)}
    except sql.OperationalError as e:
        return {"ok": False, "message": str(e)}
    except sql.DatabaseError as e:
        return {"ok": False, "message": str(e)}
    return {"ok": True, "message":"Fetched new Price data"}
        

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
    try:
        data = data_fetch(url, sql_cursor, "production", init)
    except RuntimeError as e:
        return {"ok": False, "message": str(e)}
    if data is None:
        return {"ok": True, "message": "No new Production data"}

    df = build_production_df(data, 'name', 'data', 'production_types', 'unix_seconds').drop(columns=unwanted_prod, errors="ignore")
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

    try:
        pd.io.sql.to_sql(df, 'production', sql_connection, if_exists='append', index_label='Timestamp')
    except sql.IntegrityError as e:
        return {"ok": False, "message": str(e)}
    except sql.OperationalError as e:
        return {"ok": False, "message": str(e)}
    except sql.DatabaseError as e:
        return {"ok": False, "message": str(e)}
    return {"ok": True, "message":"Fetched new Production data"}