"""Functions for interacting with the flood monitoring API."""

import requests

from .data import ROOT_URL


def get_all_station_ids() -> list[str]:
    """Get all station IDs from the API."""
    response = requests.get(f"{ROOT_URL}")
    return [item["@id"].split("/")[-1] for item in response.json()["items"]]


def get_request_json(endpoint: str) -> dict:
    """Get JSON response from the API for a given endpoint.

    Args:
        endpoint: API endpoint

    Returns:
        dict: JSON response from the API
    """

    response = requests.get(endpoint)
    return response.json()
