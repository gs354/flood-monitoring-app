"""Command-line interface for flood monitoring."""

import argparse

from .api import get_all_station_ids, get_station_readings
from .data import (
    PLOTS_DIR,
    STATION_IDS_FILE,
    extract_readings,
    load_station_ids,
    save_station_ids,
    validate_station_id,
)
from .plotting import plot_data


def main(
    station_id: str,
    dt: int = 1,
    update_station_ids: bool = False,
    save_fig: bool = True,
) -> None:
    print(station_id, dt, update_station_ids, save_fig)
    """Main function to fetch and plot flood monitoring data."""
    if update_station_ids:
        station_ids = get_all_station_ids()
        save_station_ids(STATION_IDS_FILE, station_ids)

    # Validate station ID
    valid_ids = load_station_ids()
    validate_station_id(station_id=station_id, valid_ids=valid_ids)

    # Get request to API for station readings
    readings = get_station_readings(station_id=station_id, dt=dt)

    # Extract datetime and value pairs for each measure from the readings
    measures_data = extract_readings(readings=readings)

    # Plot the data
    plot_data(
        data=measures_data,
        savefig=save_fig,
        savepath=PLOTS_DIR / f"station_{station_id}.pdf",
    )


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
        type=int,
        default=1,
        help="Number of days to look back",
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

    args = parser.parse_args()

    main(
        station_id=args.station_id,
        dt=args.days_back,
        update_station_ids=args.update_station_ids,
        save_fig=args.save_not_display,
    )


if __name__ == "__main__":
    run_cli()
