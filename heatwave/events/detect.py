"""Detect daily summer heatwaves from normalized baseline and target NetCDFs."""

import argparse
from datetime import date
from math import ceil
from pathlib import Path
import sys

import numpy as np
import xarray as xr

from heatwave._handoff import publish_outputs, validate_grid


DIMENSIONS = ("time", "lat", "lon")
WINDOW_RADIUS = 7
MIN_COVERAGE = 0.9
MIN_RUN = 3


def load_temperatures(path):
    """Read one normalized Celsius cube and verify the Ingest handoff."""
    try:
        ds = xr.load_dataset(path)
        validate_grid(ds)
        if ds.attrs.get("day_timezone") != "UTC":
            raise ValueError("day_timezone must be UTC")
        for name in ("source", "requested_bounds", "requested_period"):
            if name not in ds.attrs:
                raise ValueError(f"missing global attribute {name}")
        if "tx_c" not in ds or ds.tx_c.dims != DIMENSIONS:
            raise ValueError("expected tx_c(time, lat, lon)")
        if ds.tx_c.dtype != np.float32 or ds.tx_c.attrs.get("units") != "degC":
            raise ValueError("tx_c must contain float32 values in degC")
        if np.isinf(ds.tx_c.values).any():
            raise ValueError("tx_c contains infinity; missing data must use NaN")
        return ds
    except (ValueError, KeyError, OSError) as error:
        raise ValueError(f"{path}: {error}") from error


def summer_thresholds(baseline, number_of_days):
    """Return daily Celsius P90s and the years used in their reference pools."""
    dates = baseline.time.values.astype("datetime64[D]").tolist()
    years = sorted({day.year for day in dates})
    # Distances from each year's June 1 align summer dates across leap years.
    offsets = np.array([(day - date(day.year, 6, 1)).days for day in dates])
    min_samples = ceil(MIN_COVERAGE * (2 * WINDOW_RADIUS + 1) * len(years))
    tx = baseline.tx_c.values
    thresholds = np.full((number_of_days, *tx.shape[1:]), np.nan)
    for day in range(number_of_days):
        samples = tx[np.abs(offsets - day) <= WINDOW_RADIUS]
        usable = np.isfinite(samples).sum(axis=0) >= min_samples
        if usable.any():
            pool = samples[:, usable].astype(np.float64)
            thresholds[day, usable] = np.nanquantile(pool, 0.9, axis=0, method="linear")
    return thresholds, years


def flags_for_runs(temperatures, thresholds):
    """Mark all dates in runs of at least three consecutive strict exceedances."""
    observed = np.isfinite(temperatures) & np.isfinite(thresholds)
    hot = observed & (temperatures > thresholds)
    triples = hot[:-2] & hot[1:-1] & hot[2:]
    # Overlapping triples cover an entire longer run, including its first days.
    qualifies = np.zeros_like(hot)
    for offset in range(MIN_RUN):
        qualifies[offset:offset + len(triples)] |= triples
    return np.where(observed, qualifies, -1).astype(np.int8)


def detect_events(baseline, target):
    """Calculate v1 Events layers on the target grid for June through August."""
    for coordinate in ("lat", "lon"):
        if not np.array_equal(baseline[coordinate].values, target[coordinate].values):
            raise ValueError(f"baseline and target {coordinate} grids differ")
    years = np.unique(target.time.dt.year)
    if len(years) != 1:
        raise ValueError("target must contain one calendar year")
    year = years[0]
    dates = np.arange(np.datetime64(f"{year}-06-01"), np.datetime64(f"{year}-09-01"))
    summer = target.tx_c.reindex(time=dates)
    thresholds, reference_years = summer_thresholds(baseline, len(dates))
    tx = summer.values
    temperatures = {"units": "degC"}
    return xr.Dataset(
        {
            "tx_c": (DIMENSIONS, tx, temperatures),
            "p90_c": (DIMENSIONS, thresholds, temperatures),
            "excess_c": (DIMENSIONS, tx - thresholds, temperatures),
            "heatwave_flag": (DIMENSIONS, flags_for_runs(tx, thresholds)),
        },
        coords=summer.coords,
        attrs={
            "contract_version": "1", "day_timezone": "UTC",
            "baseline_years": ", ".join(map(str, reference_years)),
            "percentile": 90, "window_days": 2 * WINDOW_RADIUS + 1,
            "minimum_reference_coverage": MIN_COVERAGE, "min_run_days": MIN_RUN,
        },
    )


def run(baseline_path, target_path, output_path):
    """Write events.nc from two v1 input cubes as specified in contracts/v1.md, B.

    Reject malformed inputs, different spatial grids and multiple target years.
    Keep the target grid and report one slice per UTC day of the target summer.
    """
    paths = [Path(path).resolve() for path in (baseline_path, target_path, output_path)]
    if len(set(paths)) != 3:
        raise ValueError("baseline, target and output paths must be distinct")
    baseline = load_temperatures(baseline_path)
    target = load_temperatures(target_path)
    result = detect_events(baseline, target)
    with publish_outputs([output_path]) as (staged,):
        result.to_netcdf(staged, encoding={"heatwave_flag": {"_FillValue": None}})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True, help="normalized reference cube")
    parser.add_argument("--target", type=Path, required=True, help="normalized single-year cube")
    parser.add_argument("--out", type=Path, required=True, help="new Events NetCDF path")
    args = parser.parse_args(argv)
    try:
        run(args.baseline, args.target, args.out)
    except (ValueError, OSError, RuntimeError) as error:
        print(f"Events ({args.baseline}, {args.target}): {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
