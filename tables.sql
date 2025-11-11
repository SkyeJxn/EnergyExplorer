DROP TABLE IF EXISTS production;
DROP TABLE IF EXISTS prices;

CREATE TABLE production (
    Timestamp INTEGER PRIMARY KEY,
    Biomass REAL,
    Coal REAL,
    Hydro REAL,
    Oil_Gas REAL,
    Others REAL,
    Solar REAL,
    Total_Production REAL,
    Wind REAL,
    Ren_share REAL
);

CREATE TABLE prices (
    Timestamp INTEGER PRIMARY KEY,
    Price REAL
);