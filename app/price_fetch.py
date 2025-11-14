import requests as rq
import time as tm
import sqlite3 as sql
import pandas as pd

def data_fetch(url):
    response = rq.get(url)
    return response.json()

sqlite_file = './data/data.db'

sql_connection = sql.connect(sqlite_file)
sql_cursor = sql_connection.cursor()

last_found = (sql_cursor.execute("SELECT MAX(Timestamp) FROM prices").fetchone()[0])+1

now = int(tm.time())

link = f"https://api.energy-charts.info/price?bzn=DE-LU&start={last_found}&end={now}"

resp = data_fetch(link)

df = pd.DataFrame(resp['price'], index=resp['unix_seconds']).rename(columns={0: 'Price'})

pd.io.sql.to_sql(df, 'prices', sql_connection, if_exists='append', index_label='Timestamp')