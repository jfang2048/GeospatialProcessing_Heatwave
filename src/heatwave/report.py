"""Render the temperature, area and footprint figures for a completed case."""

import argparse
import csv
from datetime import UTC
from pathlib import Path

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch

from heatwave._handoff import validate_grid
from heatwave.footprints.summarize import cell_edges

DEFAULT_CASE = Path("data/processed/milan")
DEFAULT_OUTPUT = Path("reports/milan")


def _daily_area(flag, labels, summary_path):
    """Return the observed area and fraction of known cells for every day."""
    lat = np.deg2rad(cell_edges(flag.lat.values))
    lon = np.deg2rad(cell_edges(flag.lon.values))
    weights = labels.attrs["earth_radius_km"] ** 2 * np.outer(np.diff(np.sin(lat)), np.diff(lon))
    observed = ((flag.values == 1) * weights).sum(axis=(1, 2))

    dates = np.datetime_as_string(flag.time.values, unit="D")
    totals = dict.fromkeys(dates, 0.0)
    with summary_path.open(encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            if row["date"] not in totals:
                raise ValueError("Footprint CSV contains dates outside the raster.")
            totals[row["date"]] += float(row["area_km2"])
    if not np.allclose(observed, list(totals.values()), rtol=1e-5, atol=1e-6):
        raise ValueError("Daily footprint CSV areas disagree with the heatwave raster.")

    coverage = (flag.values != -1).mean(axis=(1, 2))
    return np.where(coverage > 0, observed, np.nan), coverage


def _temperature(events, latitude, longitude):
    cell = events.sel(lat=latitude, lon=longitude, method="nearest")
    dates = cell.time.values
    hot = cell.heatwave_flag.values == 1
    year = np.datetime_as_string(dates[0], unit="Y")
    fig, ax = plt.subplots(figsize=(9, 3.5), layout="constrained")
    ax.plot(dates, cell.tx_c, color="#164c6b", label="Daily maximum")
    ax.plot(dates, cell.p90_c, "--", color="#ac6a16", label="Local P90")
    ax.scatter(
        dates[hot], cell.tx_c.values[hot], s=20, color="#ad3d35", zorder=3, label="Heatwave day",
    )
    ax.set(
        title=f"{year} temperature at {cell.lat.item():.2f}°N, {cell.lon.item():.2f}°E",
        ylabel="Temperature (°C)", xlabel="UTC date",
    )
    ax.margins(x=0)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b", tz=UTC))
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    return fig


def _area(dates, area, coverage):
    partial = (coverage > 0) & (coverage < 1)
    fig, (ax, cov) = plt.subplots(
        2, 1, sharex=True, figsize=(9, 5), height_ratios=[3, 1], layout="constrained",
    )
    ax.plot(dates, area, color="#17614f", label="Observed affected area")
    if partial.any():
        ax.scatter(
            dates[partial], area[partial], color="#ac6a16", s=22,
            label="Partial coverage", zorder=3,
        )
    year = np.datetime_as_string(dates[0], unit="Y")
    ax.set(title=f"{year} daily heatwave area", ylabel="Area (km²)")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    cov.plot(dates, 100 * coverage, color="#36586a")
    cov.set(ylabel="Known cells (%)", xlabel="UTC date", ylim=(-5, 105), yticks=[0, 50, 100])
    cov.margins(x=0)
    cov.xaxis.set_major_formatter(mdates.DateFormatter("%d %b", tz=UTC))
    return fig


def _peak(ids, area, coverage, source):
    fig, ax = plt.subplots(figsize=(8, 5), layout="constrained")
    positive = area > 0
    if not positive.any():
        message = "No qualifying cells on observed days." if coverage.any() else "All cells are unknown."
        ax.text(0.5, 0.5, message, transform=ax.transAxes, ha="center", va="center")
        ax.set_axis_off()
        fig.suptitle("Peak daily footprints")
        return fig

    # The time axis increases, so argmax uses the earliest day in a tie.
    peak = int(np.nanargmax(area))
    layer = ids.isel(time=peak).values
    components = np.unique(layer[layer > 0])
    # Map possibly sparse label values to consecutive colour slots.
    categories = np.searchsorted(np.r_[-1, 0, components], layer)
    palette = plt.get_cmap("tab20")
    colours = ["#64696f", "#f1f3f4", *(palette(i % 20) for i in range(len(components)))]
    cmap = ListedColormap(colours)
    ax.pcolormesh(
        cell_edges(ids.lon.values), cell_edges(ids.lat.values), categories,
        cmap=cmap, norm=BoundaryNorm(np.arange(cmap.N + 1) - 0.5, cmap.N), shading="flat",
        edgecolors=(1, 1, 1, 0.35), linewidth=0.25,
    )
    for component in components:
        cells = np.argwhere(layer == component)
        distance = ((cells - cells.mean(axis=0)) ** 2).sum(axis=1)
        y, x = cells[distance.argmin()]
        ax.text(
            ids.lon.values[x], ids.lat.values[y], str(component), ha="center", va="center",
            fontsize=8, bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8, "pad": 1},
        )
    day = np.datetime_as_string(ids.time.values[peak], unit="D")
    count = np.count_nonzero(layer > 0)
    ax.set(
        title=f"{day} UTC · {area[peak]:,.1f} km² observed · {coverage[peak]:.1%} known",
        xlabel="Longitude (°E)", ylabel="Latitude (°N)",
        aspect=1 / np.cos(np.deg2rad(ids.lat.values.mean())),
    )
    ax.legend(
        handles=[
            Patch(color=colours[0], label="Unknown"),
            Patch(color=colours[1], label="Background"),
            Patch(facecolor=colours[2], label=f"Footprints ({count}/{layer.size} cells)"),
        ],
        loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False,
    )
    fig.suptitle(f"Peak daily footprints · {source}", fontsize=11, wrap=True)
    return fig


def figures(run_dir=DEFAULT_CASE, *, latitude=45.5, longitude=9.2):
    """Read a v1 case and return named figures for the selected grid cell and full area."""
    run_dir = Path(run_dir)
    target = xr.load_dataset(run_dir / "target.nc")
    events = xr.load_dataset(run_dir / "events.nc")
    labels = xr.load_dataset(run_dir / "footprints.nc")
    for dataset in (target, events, labels):
        validate_grid(dataset)
    # Compare the displayed temperature to the input rather than combining different runs.
    xr.testing.assert_equal(events.tx_c, target.tx_c.sel(time=events.time))
    flag, ids = xr.align(events.heatwave_flag, labels.footprint_id, join="exact")
    if not np.array_equal(np.sign(ids.values), flag.values):
        raise ValueError("Footprint labels disagree with heatwave flags.")
    area, coverage = _daily_area(flag, labels, run_dir / "footprints.csv")
    return {
        "temperature": _temperature(events, latitude, longitude),
        "area": _area(flag.time.values, area, coverage),
        "footprints": _peak(ids, area, coverage, target.attrs["source"]),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_CASE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    matplotlib.use("Agg")
    try:
        plots = figures(args.run_dir)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for name, fig in plots.items():
            output = args.output_dir / f"{name}.png"
            fig.savefig(output, dpi=180)
            plt.close(fig)
            print(output)
    except (AssertionError, KeyError, OSError, ValueError) as error:
        parser.exit(1, f"Report: {error}\n")


if __name__ == "__main__":
    main()
