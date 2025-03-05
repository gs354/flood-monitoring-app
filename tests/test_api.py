import pytest
import requests

from flood_monitoring_app.api import get_all_station_ids, get_request_json
from flood_monitoring_app.data import ROOT_URL

# Test constants
STATION_ID = "1029TH"
MOCK_ITEMS_LIMIT = 1400

# Test data
SAMPLE_API_RESPONSE = {
    "items": [
        {
            "@id": "some/id/1",
            "dateTime": "2024-03-15T10:00:00Z",
            "measure": (
                f"http://environment.data.gov.uk/flood-monitoring/id/measures/"
                f"{STATION_ID}-level-stage-i-15_min-mASD"
            ),
            "value": 1.234,
        },
        {
            "@id": "some/id/2",
            "dateTime": "2024-03-15T10:15:00Z",
            "measure": (
                f"http://environment.data.gov.uk/flood-monitoring/id/measures/"
                f"{STATION_ID}-level-downstage-i-15_min-mASD"
            ),
            "value": 0.935,
        },
    ]
}


class MockResponse:
    """Mock response class for testing."""

    def __init__(self, json_data: dict) -> None:
        self.json_data = json_data

    def json(self) -> dict:
        return self.json_data


def test_get_request_json(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test basic API request and JSON response."""
    calls = []

    def mock_get(url: str) -> MockResponse:
        calls.append(url)
        return MockResponse(SAMPLE_API_RESPONSE)

    monkeypatch.setattr("requests.get", mock_get)

    endpoint = f"{ROOT_URL}/{STATION_ID}/readings"
    result = get_request_json(endpoint)

    assert len(calls) == 1
    assert calls[0] == endpoint
    assert result == SAMPLE_API_RESPONSE


def test_get_request_json_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test handling of API errors."""

    def mock_get_error(url: str) -> None:
        raise requests.RequestException("API Error")

    monkeypatch.setattr("requests.get", mock_get_error)

    with pytest.raises(requests.RequestException, match="API Error"):
        get_request_json("some/endpoint")


def test_get_all_station_ids(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test getting all station IDs from API."""
    expected_ids = ["1029TH", "E2043"]
    mock_response = {"items": [{"@id": f"stations/{id_}"} for id_ in expected_ids]}

    def mock_get(url: str) -> MockResponse:
        assert url == ROOT_URL  # Verify correct URL is called
        return MockResponse(mock_response)

    monkeypatch.setattr("requests.get", mock_get)
    ids = get_all_station_ids()
    assert ids == expected_ids
