"""Data handling functions and constants."""

from collections import defaultdict
from pathlib import Path

import tomllib


def load_config() -> dict:
    """Load configuration from TOML file."""
    config_path = Path(__file__).parent.parent.parent / "config" / "config.toml"
    with open(config_path, "rb") as f:
        return tomllib.load(f)


# Load configuration
CONFIG = load_config()
ROOT_URL = CONFIG["api"]["root_url"]
SCRIPT_DIR = Path(__file__).parent.parent.parent
STATION_IDS_FILE = SCRIPT_DIR / CONFIG["paths"]["station_ids"]
PLOTS_DIR = SCRIPT_DIR / CONFIG["paths"]["plots"]


def save_station_ids(file_path: Path, station_ids: list[str]) -> None:
    """Save station IDs to file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w") as f:
        for station_id in station_ids:
            f.write(f"{station_id}\n")


def load_station_ids() -> set[str]:
    """Load station IDs from file into a set."""
    if not STATION_IDS_FILE.exists():
        raise FileNotFoundError(
            f"Station IDs file not found at {STATION_IDS_FILE}. "
            "Run with --update-station-ids to create it."
        )

    with open(STATION_IDS_FILE) as f:
        return {line.strip() for line in f if line.strip()}


def validate_station_id(station_id: str, valid_ids: set[str]) -> None:
    """Validate that the station ID exists."""
    if station_id not in valid_ids:
        raise ValueError(
            f"Invalid station ID: {station_id}. "
            f"Must be one of the IDs listed in {STATION_IDS_FILE}"
        )


def extract_readings(readings: dict) -> dict:
    """Extract datetime and value pairs for each measure from the readings."""
    measures_data = defaultdict(list)

    for item in readings["items"]:
        measure = item["measure"].split("/")[-1]
        datetime_str = item["dateTime"]
        value = item["value"]
        measures_data[measure].append((datetime_str, value))

    return dict(measures_data)
