DROP TABLE IF EXISTS production;
DROP TABLE IF EXISTS prices;

CREATE TABLE production (
    Timestamp INTEGER PRIMARY KEY,
    Biomass REAL,
    Biomass_pct REAL,
    Coal REAL,
    Coal_pct REAL,
    Hydro REAL,
    Hydro_pct REAL,
    Oil_Gas REAL,
    Oil_Gas_pct REAL,
    Others REAL,
    Others_pct REAL,
    Solar REAL,
    Solar_pct REAL,
    Wind REAL,
    Wind_pct REAL,
    Total_Production REAL,
    Ren_share REAL,
    Ren_share_bin REAL
);

CREATE TABLE prices (
    Timestamp INTEGER PRIMARY KEY,
    Price REAL
);