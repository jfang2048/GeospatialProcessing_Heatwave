"""Check the Milan input files before sharing them with Events."""

import argparse
from pathlib import Path
from zipfile import BadZipFile

import numpy as np
import xarray as xr

from heatwave._handoff import validate_grid
from heatwave.ingest.provider import load_month
from heatwave.ingest.requests import AREA, BASELINE, TARGET, request_plan


def milan_cube(path, years):
    """Open a saved Celsius cube and check the actual dates, grid and units."""
    cube = xr.load_dataset(path)
    validate_grid(cube)
    if cube.attrs.get("day_timezone") != "UTC":
        raise ValueError(f"{path}: expected UTC dates")
    for attr in ("source", "source_doi", "requested_bounds", "requested_period"):
        if not str(cube.attrs.get(attr, "")).strip():
            raise ValueError(f"{path}: missing {attr}")

    tx = cube.tx_c
    if tx.dims != ("time", "lat", "lon") or tx.dtype != np.float32 or tx.attrs.get("units") != "degC":
        raise ValueError(f"{path}: expected float32 tx_c(time, lat, lon) in degC")
    if np.isinf(tx.values).any() or not np.isfinite(tx.values).any():
        raise ValueError(f"{path}: expected observed temperatures and NaN for missing cells")

    dates = np.concatenate([
        np.arange(f"{year}-05-01", f"{year}-10-01", dtype="datetime64[D]") for year in years
    ])
    if not np.array_equal(cube.time.values, dates):
        raise ValueError(f"{path}: expected all May–September dates for {years[0]}–{years[-1]}")

    north, west, south, east = AREA
    for name, first, last in (("lat", south, north), ("lon", west, east)):
        wanted = np.arange(round(10 * first), round(10 * last) + 1) / 10
        if cube[name].size != wanted.size or not np.allclose(cube[name], wanted, rtol=0, atol=5e-6):
            raise ValueError(f"{path}: {name} differs from the Milan grid")
    return cube


def check_pair(baseline_path, target_path):
    baseline = milan_cube(baseline_path, BASELINE)
    target = milan_cube(target_path, (TARGET,))
    if any(not np.array_equal(baseline[axis], target[axis]) for axis in ("lat", "lon")):
        raise ValueError("Baseline and target must share the same grid coordinates")
    return baseline, target


def compare_pilot(target, payload):
    """Compare the saved target with an independently served CDS daily file."""
    _, request = next(request_plan("pilot"))
    dates, lat, lon, tx_c = load_month(payload, request)
    saved = target.tx_c.sel(time=dates)
    if not (
        np.isfinite(tx_c).any()
        and np.allclose(saved.lat, lat, rtol=0, atol=5e-6)
        and np.allclose(saved.lon, lon, rtol=0, atol=5e-6)
        and np.allclose(saved.values, tx_c, rtol=0, atol=0.001, equal_nan=True)
    ):
        raise ValueError("Target differs from the CDS pilot grid, mask or temperatures")
    return float(np.nanmax(np.abs(saved.values - tx_c)))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=Path("data/processed/milan"))
    parser.add_argument("--pilot", type=Path, help="independent seven-day CDS NetCDF or ZIP")
    args = parser.parse_args(argv)
    try:
        baseline, target = check_pair(args.run_dir / "baseline.nc", args.run_dir / "target.nc")
        print(f"Milan inputs: {baseline.sizes['time']} baseline days, {target.sizes['time']} target days, "
              f"{target.sizes['lat']} × {target.sizes['lon']} grid, float32 °C")
        if args.pilot:
            print(f"CDS pilot: dates, grid, mask and temperatures agree (max difference "
                  f"{compare_pilot(target, args.pilot):.6f} °C)")
    except (BadZipFile, KeyError, OSError, ValueError) as error:
        parser.exit(1, f"Ingest check: {error}\n")


if __name__ == "__main__":
    main()
