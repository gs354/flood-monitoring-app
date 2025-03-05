"""Functions for interacting with the flood monitoring API."""

from datetime import datetime, timedelta

import requests

from .data import ROOT_URL, load_config

CONFIG = load_config()
N_LIMIT = CONFIG["api"]["returned_items_limit"]


def get_all_station_ids() -> list[str]:
    """Get all station IDs from the API."""
    response = requests.get(f"{ROOT_URL}")
    return [item["@id"].split("/")[-1] for item in response.json()["items"]]


def get_station_readings(station_id: str, dt: int = 1) -> dict:
    """Get readings from the API for a given station ID.

    Args:
        station_id: ID of the monitoring station
        dt: Number of days to look back. Defaults to 1.

    Returns:
        dict: JSON response from the API
    """
    start_datetime = (datetime.now() - timedelta(days=dt)).strftime(
        "%Y-%m-%dT%H:%M:00Z"
    )
    endpoint = f"{ROOT_URL}/{station_id}/readings?since={start_datetime}&_sorted&_limit={N_LIMIT}"
    response = requests.get(endpoint)
    return response.json()
