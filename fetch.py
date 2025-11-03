import requests as rq
import time as tm
import sqlite3 as sql
import json

API_types = {"Hydro": ['Hydro pumped storage consumption', 'Hydro Run-of-River', 'Hydro water reservoir', 'Hydro pumped storage'],
             "Biomass":['Biomass'],
             "coal" : ['Fossil brown coal / lignite','Fossil hard coal'],
             "Oil and Gas": ['Fossil oil', 'Fossil coal-derived gas', 'Fossil gas'],
             "Wind": ['Wind offshore', 'Wind onshore'],
             "Solar": ['Solar'],
             "Others" : ['Geothermal', 'Others','Waste'],
             "ren_share":['Renewable share of generation'],
             "unwanted": ['Cross border electricity trading','Load (incl. self-consumption)', 'Residual load', 'Renewable share of load']
             }

last_found = "1762124400"

now = int(tm.time())

link = f"https://api.energy-charts.info/total_power?country=de&start={last_found}&end={last_found}"
#link = f"https://api.energy-charts.info/total_power?country=de&start={last_found}&end={now}"

def filtering(d):
    res = [entry for entry in d if entry["name"] not in API_types["unwanted"]]
    return res

def addition(d):
    res = 0
    for entry in d:
        if entry["name"] in API_types["Hydro"]:
            res["Hydro"] += entry["values"][-1][1]
        if entry["name"] in API_types["coal"]:
            res["Coal"] += entry["values"][-1][1]
        if entry["name"] in API_types["Oil and Gas"]:
            res["Oil and Gas"] += entry["values"][-1][1]
        if entry["name"] == API_types["Wind"]:
            res["Wind"] += entry["values"][-1][1]
        if entry["name"] == API_types["Others"]:
            res["Others"] += entry["values"][-1][1]
        if entry["name"] in API_types["Biomass"]:
            res["Biomass"] += entry["values"][-1][1]
        if entry["name"] in API_types["Solar"]:
            res["Solar"] += entry["values"][-1][1]
        if entry["name"] in API_types["ren_share"]:
            res["ren_share"] = entry["values"][-1][1]    
    return res

def data_fetch(url):
    response = rq.get(url)
    return response

df = data_fetch(link)
filtered = filtering(df.json())
aggregated = addition(filtered)
print("Data: ", aggregated)

print("HTTP: ", df.status_code)

