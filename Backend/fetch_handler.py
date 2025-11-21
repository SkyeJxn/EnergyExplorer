from API_fetch import price_fetch, prod_fetch
import sqlite3 as sql
import os

DB_Path = os.environ.get("DATABASE_PATH", "data/data.db")
conn = sql.connect(DB_Path)
cur = conn.cursor()

price_link = "https://api.energy-charts.info/price?bzn=DE-LU"
prod_link = "https://api.energy-charts.info/total_power?country=de"

price_fetch(price_link, conn, cur)
prod_fetch(prod_link, conn, cur)

conn.commit()
conn.close()