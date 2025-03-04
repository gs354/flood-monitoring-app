"""Plotting functions for flood monitoring data."""

from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import AutoMinorLocator, FixedFormatter, FixedLocator


def plot_data(data: dict, savefig: bool = False, savepath: Path | None = None) -> None:
    """Plot each measure's readings on a separate subplot. Colour data by date.

    Args:
        data: Dictionary with measure types as keys and lists of (datetime, value) tuples as values
        savefig: Whether to save the figure to a file
        savepath: Path where to save the figure if savefig is True
    """
    n_measures = len(data)
    fig, axes = plt.subplots(n_measures, 1, figsize=(10, 4 * n_measures))

    if n_measures == 1:
        axes = [axes]

    for (measure, readings), ax in zip(data.items(), axes):
        # Extract y-axis label from measure string
        y_label = measure.split("-")[-1]

        # Sort readings chronologically
        readings = sorted(
            readings, key=lambda x: datetime.strptime(x[0], "%Y-%m-%dT%H:%M:%SZ")
        )

        # Convert datetime strings to datetime objects for easier manipulation
        dates = [
            datetime.strptime(reading[0], "%Y-%m-%dT%H:%M:%SZ") for reading in readings
        ]
        values = [reading[1] for reading in readings]

        # Get unique dates for color coding and sort them
        unique_dates = sorted(list(set(d.date() for d in dates)))
        colors = plt.cm.rainbow(np.linspace(0, 1, len(unique_dates)))
        date_color_map = dict(zip(unique_dates, colors))

        # Keep track of all time points for x-axis ticks
        all_times = []

        # Plot each date's data with different colors
        for i, unique_date in enumerate(unique_dates[:-1]):  # Exclude last date
            mask = [d.date() == unique_date for d in dates]

            date_values = [v for m, v in zip(mask, values) if m]
            date_times = [d.strftime("%H:%M") for m, d in zip(mask, dates) if m]
            all_times.extend(date_times)

            # Get the first point of the next date's series to ensure continuity of the plotted line
            next_date = unique_dates[i + 1]
            next_mask = [d.date() == next_date for d in dates]
            next_value = next(v for m, v in zip(next_mask, values) if m)
            next_time = next(d.strftime("%H:%M") for m, d in zip(next_mask, dates) if m)

            date_values.append(next_value)
            date_times.append(next_time)

            ax.plot(
                date_times,
                date_values,
                label=unique_date.strftime("%Y-%m-%d"),
                color=date_color_map[unique_date],
            )

        # Plot the last date's data
        if unique_dates:
            last_date = unique_dates[-1]
            mask = [d.date() == last_date for d in dates]
            date_values = [v for m, v in zip(mask, values) if m]
            date_times = [d.strftime("%H:%M") for m, d in zip(mask, dates) if m]
            all_times.extend(date_times)

            ax.plot(
                date_times,
                date_values,
                label=last_date.strftime("%Y-%m-%d"),
                color=date_color_map[last_date],
            )

        # Set up hourly major ticks
        unique_hours = sorted(list(set(t.split(":")[0] + ":00" for t in all_times)))
        major_ticks = [i for i, t in enumerate(all_times) if t in unique_hours]

        if major_ticks:
            ax.xaxis.set_major_locator(FixedLocator(major_ticks))
            ax.xaxis.set_major_formatter(
                FixedFormatter([all_times[i] for i in major_ticks])
            )
            ax.xaxis.set_minor_locator(AutoMinorLocator())

            ax.tick_params(axis="x", which="major", length=10, rotation=90)
            ax.tick_params(axis="x", which="minor", length=3)
            ax.grid(True, which="major", linestyle="-", alpha=0.3)

        ax.set_title(measure)
        ax.set_xlabel("Time")
        ax.set_ylabel(y_label)
        ax.legend(title="Date", bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.tight_layout()

    if savefig:
        if isinstance(savepath, str):
            savepath = Path(savepath)
        savepath.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(savepath, bbox_inches="tight")
    else:
        plt.show()

    plt.close(fig)
