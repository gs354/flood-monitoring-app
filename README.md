# Flood Monitoring App

A Python application for fetching and visualising flood monitoring data from the UK Environment Agency's real-time API.

## Installation

1. Create and activate a virtual environment, e.g. on MacOs/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Clone the package and move into the directory:
```bash
git clone https://github.com/gs354/flood-monitoring-app.git
cd flood-monitoring-app
```

3. Install the package for users (no development dependencies):
```bash
pip install -e .
```

4. Or install the package with development dependencies (required to run tests):
```bash
pip install -e ".[dev]"
```

## Project Structure

```
flood-monitoring-app/
├── src/flood_monitoring_app/
│   ├── api.py          # API interaction functions
│   ├── cli.py          # Command-line interface
│   ├── data.py         # Data handling utilities
│   └── plotting.py     # Plotting functions
├── config/
│   └── config.toml     # Configuration settings
├── data/               # Data files (e.g. station IDs) *
├── plots/              # Generated plot files *
└── tests/              
    ├── test_api.py     # API tests
    └── test_cli.py     # CLI tests
```

\* The app will create the `data` and `plots` directories on first run.

## Configuration

The app uses a TOML configuration file located at `config/config.toml`, which contains:
- API endpoint root URL
- Limit on the number of items returned by the API
- Paths for a station IDs text file and the directory for saving plot images


## Usage

The app provides a command-line interface to fetch and plot flood monitoring data. 
It accesses the endpoint `https://environment.data.gov.uk/flood-monitoring/id/stations/<station_id>/readings` to fetch readings for all measures from a particular station up to a specified number of days ago.

### Options

- `-s, --station-id`: ID of the monitoring station (required)
- `-d, --days-back`: Number of days of data to fetch (default: 1; allowed range: 1-14<sup>*</sup>)
- `-u, --update-station-ids`: Update the station IDs file before processing
- `-save, --save-not-display`: Save the plot instead of displaying it

\* The limit on the number of items returned by the API is set in the config file to 1400. The corresponding number of days is set as one hundredth of this limit, i.e. 14. 

### On first use
- Run with the `-u` flag to create a station IDs file in the `data` directory.


### Examples

Update station IDs and then display plot for station 2067 for the last day's data:

```bash
flood-monitor -s 2067 -u
```

Display plot for station 1491TH for the last three days' data:

```bash
flood-monitor -s 1491TH -d 3
```

Save plot for station 2067 for the last day's data:

```bash
flood-monitor -s 2067 --save
```


### Running tests

```bash
pytest
```



## Dependencies

- Python 3.12+
- matplotlib
- requests

For development:
- pytest
- ruff

## Data Source

This application uses Environment Agency flood and river level data from the real-time data API (Beta)


    