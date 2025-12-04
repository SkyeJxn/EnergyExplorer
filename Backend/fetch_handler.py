from API_fetch import price_fetch, prod_fetch
import sqlite3 as sql
import os
import argparse as arg

parser = arg.ArgumentParser(description="API Fetch Script")
parser.add_argument('-i', action='store_true', help="Initial API call without table lookup")
flags = parser.parse_args()

print(flags.i)

DB_Path = os.environ.get("DATABASE_PATH", "./data/data.db")
price_link = "https://api.energy-charts.info/price?bzn=DE-LU"
prod_link = "https://api.energy-charts.info/total_power?country=de"
 
with sql.connect(DB_Path) as conn:
    cur = conn.cursor()
    price_fetch(price_link, conn, cur, flags.i)
    prod_fetch(prod_link, conn, cur, flags.i)
    conn.commit()
    cur.close()