"""Label edge-connected heatwave cells and measure their area on each UTC day."""

import argparse
import csv
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage
import xarray as xr

from heatwave._handoff import publish_outputs, validate_grid


EARTH_RADIUS_KM = 6371.0088
DIMS = ("time", "lat", "lon")
COLUMNS = ("date", "footprint_id", "cell_count", "area_km2", "peak_excess_c")


def validate_events(events):
    """Check the dates, parameters and literal raster values required by v1."""
    validate_grid(events)
    dates = events.time.values.astype("datetime64[D]")
    year = str(dates[0])[:4]
    expected = np.arange(np.datetime64(f"{year}-06-01"), np.datetime64(f"{year}-09-01"))
    if not np.array_equal(dates, expected):
        raise ValueError("expected all 92 consecutive days of one June-August season")
    for name in ("tx_c", "p90_c", "excess_c", "heatwave_flag"):
        if name not in events or events[name].dims != DIMS:
            raise ValueError(f"expected {name}{DIMS}")
    for name in ("tx_c", "p90_c", "excess_c"):
        field = events[name]
        if field.dtype.kind != "f" or field.attrs.get("units") != "degC":
            raise ValueError(f"{name} must be a floating-point field in degC")
        if np.isinf(field.values).any():
            raise ValueError(f"{name} contains infinity")
    flag = events.heatwave_flag
    if flag.dtype != np.int8 or not np.isin(flag.values, [-1, 0, 1]).all():
        raise ValueError("heatwave_flag must contain signed byte codes -1, 0 and 1")
    for attr in ("_FillValue", "missing_value", "scale_factor", "add_offset"):
        if attr in flag.encoding or attr in flag.attrs:
            raise ValueError(f"literal heatwave_flag codes cannot use {attr}")
    reference = events.tx_c.values - events.p90_c.values
    if not np.allclose(events.excess_c.values, reference, equal_nan=True, rtol=1e-5, atol=1e-5):
        raise ValueError("excess_c disagrees with tx_c minus p90_c")
    if not np.array_equal(flag.values == -1, np.isnan(reference)):
        raise ValueError("unknown flags disagree with missing temperature or threshold")
    if (events.excess_c.values[flag.values == 1] <= 0).any():
        raise ValueError("qualifying heatwave cells require positive excess_c")
    for attr, value in (("percentile", 90), ("window_days", 15), ("min_run_days", 3),
                        ("minimum_reference_coverage", 0.9)):
        actual = events.attrs.get(attr)
        if not isinstance(actual, (int, float, np.integer, np.floating)) or not np.isclose(actual, value):
            raise ValueError(f"expected event attribute {attr}={value}")
    if "baseline_years" not in events.attrs or not str(events.attrs["baseline_years"]).strip():
        raise ValueError("missing baseline_years")


def cell_edges(centres):
    """Use adjacent midpoints and extend each outer edge by half a grid step."""
    values = np.asarray(centres, dtype=np.float64)
    half_steps = np.diff(values) / 2
    return np.r_[values[0] - half_steps[0], values[:-1] + half_steps, values[-1] + half_steps[-1]]


def label_summer(events):
    """Return daily labels and summary rows for a validated Events cube."""
    lat_edges = np.deg2rad(cell_edges(events.lat))
    lon_edges = np.deg2rad(cell_edges(events.lon))
    cell_areas = EARTH_RADIUS_KM**2 * np.outer(np.diff(np.sin(lat_edges)), np.diff(lon_edges))
    flags = events.heatwave_flag.values
    excess = events.excess_c.values
    ids = np.empty(flags.shape, dtype=np.int32)
    rows = []
    neighbours = ndimage.generate_binary_structure(2, 1)
    for i, date in enumerate(np.datetime_as_string(events.time.values, unit="D")):
        # A C-order scan visits each latitude row from west to east before
        # moving north. Each day starts a fresh ID sequence.
        affected = np.ascontiguousarray(flags[i] == 1)
        count = ndimage.label(affected, structure=neighbours, output=ids[i])
        if count:
            labels = ids[i].ravel()
            counts = np.bincount(labels)
            areas = np.bincount(labels, weights=cell_areas.ravel())
            peaks = ndimage.maximum(excess[i], labels=ids[i], index=np.arange(1, count + 1))
            for component in range(1, count + 1):
                rows.append((date, component, counts[component], areas[component], peaks[component - 1]))
        ids[i][flags[i] == -1] = -1
    labels = xr.Dataset(
        {"footprint_id": (DIMS, ids)},
        coords={name: events.coords[name] for name in DIMS},
        attrs={"contract_version": "1", "connectivity": 4, "earth_radius_km": EARTH_RADIUS_KM},
    )
    return labels, rows


def summarize(events_path, labels_path, summary_path):
    """Read a v1 Events season and write its label NetCDF and component CSV.

    Reject an invalid Events cube or overlapping file paths. Publish both
    products to fresh destinations only after their contents are complete.
    """
    paths = (events_path, labels_path, summary_path)
    if len({Path(path).resolve() for path in paths}) != len(paths):
        raise ValueError("events, labels and summary paths must be distinct")
    with xr.open_dataset(events_path) as events:
        validate_events(events)
        labels, rows = label_summer(events)
        with publish_outputs((labels_path, summary_path)) as (label_temp, summary_temp):
            labels.to_netcdf(label_temp, engine="scipy", encoding={"footprint_id": {"_FillValue": None}})
            with summary_temp.open("w", encoding="utf-8", newline="") as file:
                writer = csv.writer(file, lineterminator="\n")
                writer.writerow(COLUMNS)
                writer.writerows(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", required=True, type=Path, help="v1 daily Events NetCDF")
    parser.add_argument("--labels-out", required=True, type=Path, help="new daily label NetCDF")
    parser.add_argument("--summary-out", required=True, type=Path, help="new component summary CSV")
    args = parser.parse_args(argv)
    try:
        summarize(args.events, args.labels_out, args.summary_out)
    except (OSError, RuntimeError, ValueError, TypeError, KeyError) as exc:
        print(f"{args.events}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
