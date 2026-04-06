# EnergyExplorer

## Usage

quickly visualizes Energy Data.

## Requirements

### for hosting

- Docker
- SQlite

### for development

- Python
- SQlite

## Installation

### for hosting

``` bash
git clone https://github.com/SkyeJxn/EnergyExplorer
cd EnergyExplorer
sqlite3 data/data.db ".read data/setup.sql"
docker compose up --build
```

### for development

``` bash
git clone https://github.com/SkyeJxn/EnergyExplorer
cd EnergyExplorer
sqlite3 data/data.db ".read data/setup.sql"
python -m venv ./venv
pip install -r src/requirements.txt
python src/app/start.py -d dev
```

in a second terminal instance:

```bash
cd path/to/EnergyExplorer
fastapi dev src/Backend/main.py
```

## Data Source

The used Data is pulled from the [Energy Charts API](https://www.energy-charts.info/api.html?l=de&c=DE).