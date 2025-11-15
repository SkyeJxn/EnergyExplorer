import os
import requests as rq
import time as tm
import sqlite3 as sql
import pandas as pd

DB_Path = os.environ.get("DATABASE_PATH", "data/data.db")

def data_fetch(url):
    response = rq.get(url)
    return response.json()

sql_connection = sql.connect(DB_Path)
sql_cursor = sql_connection.cursor()

last_found = (sql_cursor.execute("SELECT MAX(Timestamp) FROM prices").fetchone()[0])+1

now = int(tm.time())

link = f"https://api.energy-charts.info/price?bzn=DE-LU&start={last_found}&end={now}"

resp = data_fetch(link)

df = pd.DataFrame(resp['price'], index=resp['unix_seconds']).rename(columns={0: 'Price'})

pd.io.sql.to_sql(df, 'prices', sql_connection, if_exists='append', index_label='Timestamp')