from src.Backend.API_fetch import price_fetch, prod_fetch
import sqlite3 as sql
from fastapi import FastAPI, HTTPException
import pandas as pd
import os
from typing import Literal

app = FastAPI()
DB_Path = os.environ.get("DATABASE_PATH", "data/data.db")

def get_conn():
    return sql.connect(DB_Path)

@app.get("/prices")
async def price():
    with get_conn() as conn:
        df = pd.read_sql_query("SELECT * FROM prices", conn)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="s", dayfirst=True, origin="unix")
    return {"Timestamp": df["Timestamp"].tolist(),
        "Data": df["Price"].tolist()}

@app.get("/production")
async def production():
    with get_conn() as conn:
        df = pd.read_sql_query("SELECT Timestamp, Total_Production FROM production", conn)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="s", dayfirst=True, origin="unix")
    return {"Timestamp": df["Timestamp"].tolist(),
        "Data": df["Total_Production"].tolist()}

@app.get("/ren_share")
async def ren_share():
    with get_conn() as conn:
        df = pd.read_sql_query("SELECT Timestamp, Ren_share FROM production", conn)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="s", dayfirst=True, origin="unix")
    df = df.dropna()
    return {"Timestamp": df["Timestamp"].tolist(),
        "Data": df["Ren_share"].tolist()}

@app.get("/bins")
async def bins():
    with get_conn() as conn:    
        df = pd.merge(pd.read_sql_query("SELECT Timestamp, Ren_share_bin FROM production", conn),
                  pd.read_sql_query("SELECT * FROM prices", conn),
                  "inner","Timestamp")
    bin_order = ["0-10","10-20","20-30","30-40","40-50","50-60","60-70","70-100"]
    df["Ren_share_bin"] = pd.Categorical(df["Ren_share_bin"], categories=bin_order, ordered=True)
    agg = df.groupby("Ren_share_bin", as_index=False)["Price"].mean()
    res = agg.dropna()
    return {
        "Bins": res["Ren_share_bin"].tolist(),
        "Price": res["Price"].astype(str).tolist()
        }


@app.get("/pie")
async def pie(x: str = ""):
    pct_cols = ["Biomass", "Coal", "Hydro", "Oil & Gas", "Others", "Solar", "Wind"]

    label = {"Biomass_pct":"Biomass",
        "Coal_pct":"Coal",
        "Hydro_pct":"Hydro",
        "Oil_Gas_pct":"Oil & Gas",
        "Others_pct":"Others",
        "Solar_pct":"Solar",
        "Wind_pct":"Wind"}

    with get_conn() as conn:
        df = pd.read_sql_query(f"SELECT Timestamp, Biomass_pct, Coal_pct, Hydro_pct, Oil_Gas_pct, Others_pct, Solar_pct, Wind_pct FROM production", conn)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="s", dayfirst=True, origin="unix")
    df = df.rename(columns=label)

    if x:
        timed = df.loc[df["Timestamp"] == x]
        values = {col: timed.iloc[0][col] for col in pct_cols}
        title = f"Production Breakdown for {x}"
    else:
        values = {col: df[col].mean() for col in pct_cols}
        title = "Mean Production Breakdown"
    
    return {"values": values,
            "title": title}

@app.post("/fetch")
async def fetch(init: bool = False, source: Literal["price", "prod", "all"] = "all"):
    price_link = "https://api.energy-charts.info/price?bzn=DE-LU"
    prod_link = "https://api.energy-charts.info/total_power?country=de"
 
    with get_conn() as conn:
        cur = conn.cursor()
        try:
            results = {}
            if source in ("prod", "all"):
                results["prod"] = prod_fetch(prod_link, conn, cur, init)
            if source in ("price", "all"):
                results["price"] = price_fetch(price_link, conn, cur, init)
        finally:
            cur.close()
        failed = {key: value for key, value in results.items() if not value.get("ok", False)}
        if failed:
            raise HTTPException(
                status_code=502,
                detail={"message": "One or more fetch operations failed", "results": results},
            )

        conn.commit()
        return {
            "detail": "Fetch completed",
            "source": source,
            "results": results,
        }
