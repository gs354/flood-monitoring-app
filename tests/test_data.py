import pytest

from flood_monitoring_app.data import (
    extract_readings,
    load_station_ids,
    validate_station_id,
)

SAMPLE_STATION_IDS = """1029TH
E2043
52119
"""

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


@pytest.fixture
def mock_station_ids_file(tmp_path):
    """Create a temporary station IDs file."""
    file_path = tmp_path / "station_ids.txt"
    file_path.write_text(SAMPLE_STATION_IDS)
    return file_path


def test_load_station_ids(mock_station_ids_file, monkeypatch):
    """Test loading station IDs from file."""
    monkeypatch.setattr(
        "flood_monitoring_app.data.STATION_IDS_FILE", mock_station_ids_file
    )
    ids = load_station_ids()
    assert isinstance(ids, set)
    assert len(ids) == 3
    assert "1029TH" in ids
    assert "E2043" in ids
    assert "52119" in ids


def test_validate_station_id_valid():
    """Test validating a valid station ID."""
    valid_ids = {"1029TH", "E2043", "52119"}
    validate_station_id("1029TH", valid_ids)  # Should not raise


def test_validate_station_id_invalid():
    """Test validating an invalid station ID."""
    valid_ids = {"1029TH", "E2043", "52119"}
    with pytest.raises(ValueError):
        validate_station_id("INVALID_ID", valid_ids)


def test_extract_readings():
    """Test extracting readings from API response."""
    readings = extract_readings(SAMPLE_API_RESPONSE)

    assert len(readings) == 2

    stage_measure = "1029TH-level-stage-i-15_min-mASD"
    assert stage_measure in readings
    assert len(readings[stage_measure]) == 1
    assert readings[stage_measure][0] == ("2024-03-15T10:00:00Z", 1.234)

    downstage_measure = "1029TH-level-downstage-i-15_min-mASD"
    assert downstage_measure in readings
    assert len(readings[downstage_measure]) == 1
    assert readings[downstage_measure][0] == ("2024-03-15T10:15:00Z", 0.935)
