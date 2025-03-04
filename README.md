# Flood Monitoring App

A Python application for fetching and visualising flood monitoring data from the UK Environment Agency's real-time API.

## Installation


```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Clone and install the package
git clone https://github.com/yourusername/flood-monitoring-app.git
cd flood-monitoring-app
```

For users:
```bash
pip install -e .
```

For developers:
```bash
pip install -e ".[dev]"  # Includes development dependencies
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
├── data/               # Generated data files
├── plots/              # Generated plot files
└── tests/              # Test files
```

## Configuration

The app uses a TOML configuration file located at `config/config.toml`, which contains:
- API endpoint root URL
- Paths for a station IDs text file and the directory for saving plot images

Before first use:
1. Create the `data` directory for storing station IDs
2. Create the `plots` directory for saving plot outputs
3. Run with the `-u` flag to populate the station IDs file


## Usage

The app provides a command-line interface to fetch and plot flood monitoring data. 
It accesses the endpoint `https://environment.data.gov.uk/flood-monitoring/id/stations/{station_id}/readings` to fetch readings for all measures from a particular station up to a specified number of days ago.

### Options

- `-s, --station-id`: ID of the monitoring station (required)
- `-d, --days-back`: Number of days of data to fetch (default: 1)
- `-u, --update-station-ids`: Update the station IDs file before processing
- `-save, --save-not-display`: Save the plot instead of displaying it

### Examples

Update station IDs and then display plot for station 2067 for the last day's data:

```bash
flood-monitoring-app -s 2067 -u
```

Display plot for station 2067 for the last day's data:

```bash
flood-monitoring-app -s 2067
```

Save plot for station 2067 for the last 3 days' data:

```bash
flood-monitoring-app -s 2067 --d 3 --save
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

This application uses data from the UK Environment Agency's real-time flood monitoring API. The API provides water level readings from monitoring stations across the UK.


    