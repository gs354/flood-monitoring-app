"""Tests for data handling functions."""

from pathlib import Path

import pytest

from flood_monitoring_app.data import (
    extract_readings,
    load_station_ids,
    validate_station_id,
)

# Test data
SAMPLE_STATION_IDS = """1029TH
E2043
52119
"""

SAMPLE_API_RESPONSE = {
    "items": [
        {
            "@id": "some/id/1",
            "dateTime": "2024-03-15T10:00:00Z",
            "measure": (
                "http://environment.data.gov.uk/flood-monitoring/id/measures/"
                "1029TH-level-stage-i-15_min-mASD"
            ),
            "value": 1.234,
        },
        {
            "@id": "some/id/2",
            "dateTime": "2024-03-15T10:15:00Z",
            "measure": (
                "http://environment.data.gov.uk/flood-monitoring/id/measures/"
                "1029TH-level-downstage-i-15_min-mASD"
            ),
            "value": 0.935,
        },
    ]
}

# Expected test values
STAGE_MEASURE = "1029TH-level-stage-i-15_min-mASD"
DOWNSTAGE_MEASURE = "1029TH-level-downstage-i-15_min-mASD"
VALID_IDS = {"1029TH", "E2043", "52119"}


@pytest.fixture
def mock_station_ids_file(tmp_path: Path) -> Path:
    """Create a temporary station IDs file.

    Args:
        tmp_path: Pytest fixture providing temporary directory path

    Returns:
        Path to temporary station IDs file
    """
    file_path = tmp_path / "station_ids.txt"
    file_path.write_text(SAMPLE_STATION_IDS)
    return file_path


def test_load_station_ids(
    mock_station_ids_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test loading station IDs from file."""
    monkeypatch.setattr(
        "flood_monitoring_app.data.STATION_IDS_FILE", mock_station_ids_file
    )
    ids = load_station_ids()
    assert isinstance(ids, set)
    assert len(ids) == 3
    assert ids == VALID_IDS


def test_validate_station_id_valid() -> None:
    """Test validating a valid station ID."""
    validate_station_id("1029TH", VALID_IDS)  # Should not raise


def test_validate_station_id_invalid() -> None:
    """Test validating an invalid station ID."""
    with pytest.raises(ValueError, match="Invalid station ID"):
        validate_station_id("INVALID_ID", VALID_IDS)


def test_extract_readings() -> None:
    """Test extracting readings from API response."""
    readings = extract_readings(SAMPLE_API_RESPONSE)

    assert len(readings) == 2

    # Check stage measure readings
    assert STAGE_MEASURE in readings
    assert len(readings[STAGE_MEASURE]) == 1
    assert readings[STAGE_MEASURE][0] == ("2024-03-15T10:00:00Z", 1.234)

    # Check downstage measure readings
    assert DOWNSTAGE_MEASURE in readings
    assert len(readings[DOWNSTAGE_MEASURE]) == 1
    assert readings[DOWNSTAGE_MEASURE][0] == ("2024-03-15T10:15:00Z", 0.935)
