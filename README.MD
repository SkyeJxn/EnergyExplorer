# EnergyExplorer

## Usage

quickly visualizes Energy Data.

## Requirements

- Docker
- SQlite

## Installation

``` bash
git clone https://github.com/SkyeJxn/EnergyExplorer
cd EnergyExplorer
sqlite3 data/data.db ".read data/setup.sql"
docker compose up --build
```

## Data Source

The used Data is pulled from the [Energy Charts API](https://www.energy-charts.info/api.html?l=de&c=DE).