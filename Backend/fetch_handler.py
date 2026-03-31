from API_fetch import price_fetch, prod_fetch
import sqlite3 as sql
import os
import argparse as arg

parser = arg.ArgumentParser(description="API Fetch Script")
parser.add_argument('-i', action='store_true', help="Initial API call without table lookup")
parser.add_argument('-c', type=str, help="specify API", default="all", choices=["prod", "price", "all"])
parser.add_argument('-q', action='store_false', help="Prevents printouts to Terminal")
flags = parser.parse_args()

DB_Path = os.environ.get("DATABASE_PATH", "./data/data.db")
price_link = "https://api.energy-charts.info/price?bzn=DE-LU"
prod_link = "https://api.energy-charts.info/total_power?country=de"
 
with sql.connect(DB_Path) as conn:
    cur = conn.cursor()
    if (flags.c == "price"):
        print("fetching price API")
        if(flags.q): price_fetch(price_link, conn, cur, flags.i)
    if (flags.c == "prod"):
        if(flags.q): print("fetching production API")
        prod_fetch(prod_link, conn, cur, flags.i)
    if (flags.c == "all"):
        if(flags.q): print("fetching all APIs")
        prod_fetch(prod_link, conn, cur, flags.i)
        price_fetch(price_link, conn, cur, flags.i)
    conn.commit()
    cur.close()