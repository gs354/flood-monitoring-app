"""Command-line interface for flood monitoring data retrieval and plotting."""

import argparse
from datetime import datetime, timedelta

from .api import get_all_station_ids, get_request_json
from .data import (
    DATA_DIR,
    N_LIMIT,
    PLOTS_DIR,
    ROOT_URL,
    STATION_IDS_FILE,
    extract_readings,
    load_station_ids,
    save_readings_to_csv,
    save_station_ids,
    validate_station_id,
)
from .plotting import plot_data

LOOKBACK_DAYS_LIMIT = int(N_LIMIT / 100)


def main(
    station_id: str,
    dt: int = 1,
    update_station_ids: bool = False,
    save_fig: bool = True,
    save_csv: bool = False,
) -> None:
    """Main function to fetch and plot flood monitoring data."""

    if update_station_ids:
        station_ids = get_all_station_ids()
        save_station_ids(STATION_IDS_FILE, station_ids)

    # Validate station ID
    valid_ids = load_station_ids()
    validate_station_id(station_id=station_id, valid_ids=valid_ids)

    # Get start datetime for the request
    time_now = datetime.now()
    start_datetime = (time_now - timedelta(days=dt)).strftime("%Y-%m-%dT%H:%M:00Z")

    # Get endpoint for the request
    endpoint = f"{ROOT_URL}/{station_id}/readings?since={start_datetime}&_sorted&_limit={N_LIMIT}"

    # Get request to API for station readings
    readings = get_request_json(endpoint=endpoint)

    # Extract datetime and value pairs for each measure from the readings
    measures_data = extract_readings(readings=readings)

    # Save data to CSV files if requested
    timestamp = time_now.strftime("%Y-%m-%dT%H:%M")
    if save_csv:
        save_readings_to_csv(
            readings=measures_data,
            output_dir=DATA_DIR / "readings",
            station_id=station_id,
            timestamp=timestamp,
        )

    # Plot the data
    plot_data(
        data=measures_data,
        savefig=save_fig,
        filepath=PLOTS_DIR / f"station_{station_id}_{timestamp}.pdf",
    )


def int_in_range(value: str) -> int:
    """Convert string to integer and check if it is in range [1, LOOKBACK_DAYS_LIMIT].

    Args:
        value: String to convert to integer

    Returns:
        Integer between 1 and LOOKBACK_DAYS_LIMIT inclusive

    Raises:
        ArgumentTypeError: If value cannot be converted to int or is out of range
    """
    try:
        ivalue = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value} is not a valid integer")

    if not 1 <= ivalue <= LOOKBACK_DAYS_LIMIT:
        raise argparse.ArgumentTypeError(
            f"{value} is not in required range 1-{LOOKBACK_DAYS_LIMIT}"
        )

    return ivalue


def run_cli() -> None:
    """Run the command-line interface."""

    parser = argparse.ArgumentParser(
        description="Fetch and plot flood monitoring data for a given station."
    )
    parser.add_argument(
        "--station-id",
        "-s",
        type=str,
        required=True,
        help="ID of the monitoring station",
    )
    parser.add_argument(
        "--days-back",
        "-d",
        type=int_in_range,
        default=1,
        help=f"Number of days to look back (between 1 and {LOOKBACK_DAYS_LIMIT})",
    )
    parser.add_argument(
        "--update-station-ids",
        "-u",
        action="store_true",
        help="Update the station IDs file before processing",
    )
    parser.add_argument(
        "--save-not-display",
        "-save",
        action="store_true",
        help="Save the plot instead of displaying it",
    )
    parser.add_argument(
        "--save-csv",
        "-csv",
        action="store_true",
        help="Save the data to CSV files",
    )

    args = parser.parse_args()

    main(
        station_id=args.station_id,
        dt=args.days_back,
        update_station_ids=args.update_station_ids,
        save_fig=args.save_not_display,
        save_csv=args.save_csv,
    )


if __name__ == "__main__":
    run_cli()
