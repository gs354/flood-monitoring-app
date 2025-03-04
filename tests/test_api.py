import pytest
import requests

from flood_monitoring_app.api import get_all_station_ids, get_station_readings

SAMPLE_API_RESPONSE = {
    "items": [
        {
            "@id": "some/id/1",
            "dateTime": "2024-03-15T10:00:00Z",
            "measure": "http://environment.data.gov.uk/flood-monitoring/id/measures/1029TH-level-stage-i-15_min-mASD",
            "value": 1.234,
        },
        {
            "@id": "some/id/2",
            "dateTime": "2024-03-15T10:15:00Z",
            "measure": "http://environment.data.gov.uk/flood-monitoring/id/measures/1029TH-level-downstage-i-15_min-mASD",
            "value": 0.935,
        },
    ]
}


@pytest.mark.parametrize("dt", [1, 2, 7])
def test_get_station_readings(dt, monkeypatch):
    """Test API request construction with different time periods."""
    calls = []

    def mock_get(url):
        calls.append(url)

        class MockResponse:
            def json(self):
                return SAMPLE_API_RESPONSE

        return MockResponse()

    # Replace requests.get with mock_get
    monkeypatch.setattr("requests.get", mock_get)
    # Use mock_get instead of requests.get in function call
    result = get_station_readings("1029TH", dt)

    assert len(calls) == 1
    url = calls[0]
    assert "1029TH" in url
    assert "&_sorted" in url
    assert "readings?since=" in url
    assert result == SAMPLE_API_RESPONSE


def test_get_station_readings_error(monkeypatch):
    """Test handling of API errors."""

    def mock_get_error(url):
        raise requests.RequestException("API Error")

    monkeypatch.setattr("requests.get", mock_get_error)
    with pytest.raises(requests.RequestException):
        get_station_readings("1029TH")


def test_get_all_station_ids(monkeypatch):
    """Test getting all station IDs from API."""

    def mock_get(url):
        class MockResponse:
            def json(self):
                return {
                    "items": [{"@id": "stations/1029TH"}, {"@id": "stations/E2043"}]
                }

        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)
    ids = get_all_station_ids()
    assert ids == ["1029TH", "E2043"]
