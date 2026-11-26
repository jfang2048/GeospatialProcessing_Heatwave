"""Regenerate the tiny synthetic handoffs used by the proposal notebook."""

import csv
from datetime import date, timedelta
from pathlib import Path

import numpy as np
from scipy.io import netcdf_file


HERE = Path(__file__).resolve().parent
EPOCH = date(1970, 1, 1)
LAT = [45.4, 45.5]
LON = [9.1, 9.2, 9.3]


def days(first, last):
    return [first + timedelta(days=i) for i in range((last - first).days + 1)]


def warm_season(year):
    return days(date(year, 5, 1), date(year, 9, 30))


def write_cube(filename, dates, variables, **attributes):
    with netcdf_file(HERE / filename, mode="w", version=2) as cube:
        cube.contract_version = "1"
        cube.source = "Synthetic course example"
        cube.day_timezone = "UTC"
        cube.requested_bounds = "45.5, 9.1, 45.4, 9.3"
        cube.requested_period = f"{dates[0]} to {dates[-1]}"
        for name, size in (("time", len(dates)), ("lat", len(LAT)), ("lon", len(LON))):
            cube.createDimension(name, size)
        time = cube.createVariable("time", "i4", ("time",))
        time[:] = [(day - EPOCH).days for day in dates]
        time.units = "days since 1970-01-01 00:00:00"
        time.calendar = "proleptic_gregorian"
        for name, values, units in (
            ("lat", LAT, "degrees_north"), ("lon", LON, "degrees_east")
        ):
            coord = cube.createVariable(name, "f8", (name,))
            coord[:] = values
            coord.units = units
        for name, values in variables.items():
            dtype = "i1" if name == "heatwave_flag" else "f4"
            variable = cube.createVariable(name, dtype, ("time", "lat", "lon"))
            variable[:] = values
            if dtype == "f4":
                variable.units = "degC"
        for key, value in attributes.items():
            setattr(cube, key, value)


def main():
    baseline_dates = warm_season(2003) + warm_season(2004)
    baseline = np.full((len(baseline_dates), 2, 3), 30.0)
    write_cube("baseline_fixture.nc", baseline_dates, {"tx_c": baseline})

    target_dates = warm_season(2022)
    target = np.full((len(target_dates), 2, 3), 29.0)
    june = target_dates.index(date(2022, 6, 1))
    # Human-readable cell order is the two rows of increasing latitude.
    target[june : june + 5] = np.array([
        [[31, 32, 29], [31, 31, 31]],
        [[32, 33, 29], [31, np.nan, 32]],
        [[33, 34, 29], [30, 31, 33]],
        [[30, 29, 29], [29, 29, 30]],
        [[29, 29, 29], [29, 29, 29]],
    ])
    write_cube("target_fixture.nc", target_dates, {"tx_c": target})

    dates = days(date(2022, 6, 1), date(2022, 8, 31))
    tx_c = target[june : june + len(dates)]
    p90_c = np.full_like(tx_c, 30.0)
    heatwave_flag = np.zeros(tx_c.shape, dtype=np.int8)
    heatwave_flag[:3, 0, :2] = 1
    heatwave_flag[:3, 1, 2] = 1
    heatwave_flag[1, 1, 1] = -1
    write_cube(
        "events_fixture.nc", dates,
        {"tx_c": tx_c, "p90_c": p90_c, "excess_c": tx_c - p90_c,
         "heatwave_flag": heatwave_flag},
        percentile=90, window_days=15, min_run_days=3, baseline_years="2003, 2004",
        minimum_reference_coverage=0.9,
    )

    with (HERE / "worked_example.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["date", "lat", "lon", "tx_c", "p90_c", "heatwave_flag", "footprint_id"])
        for t, day in enumerate(dates[:5]):
            for row, lat in enumerate(LAT):
                for col, lon in enumerate(LON):
                    flag = int(heatwave_flag[t, row, col])
                    footprint_id = 2 if flag == 1 and row == 1 else flag
                    tx = tx_c[t, row, col]
                    writer.writerow([day, lat, lon, "" if np.isnan(tx) else tx, 30, flag,
                                     footprint_id])


if __name__ == "__main__":
    main()
