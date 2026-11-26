"""Acceptance of persisted Milan outputs using physical values from the actual run."""

import csv
from itertools import groupby

import numpy as np
import pytest


DIMS = ("time", "lat", "lon")
SUMMER = np.arange(np.datetime64("2022-06-01"), np.datetime64("2022-09-01"))
SUMMARY_COLUMNS = ["date", "footprint_id", "cell_count", "area_km2", "peak_excess_c"]


def expected_seasons(years):
    return np.concatenate([
        np.arange(np.datetime64(f"{year}-05-01"), np.datetime64(f"{year}-10-01"))
        for year in years
    ])


@pytest.mark.parametrize(("name", "years"), [
    ("baseline.nc", range(1991, 2021)), ("target.nc", [2022]),
])
def test_normalized_milan_cube(name, years, load_output):
    cube = load_output(name)
    assert cube.attrs["contract_version"] == "1"
    assert cube.attrs["day_timezone"] == "UTC"
    assert cube.attrs["source_doi"] == "10.24381/cds.e9c9c792"
    for attr in ("source", "requested_period", "requested_bounds"):
        assert str(cube.attrs[attr]).strip()
    assert cube.tx_c.dims == DIMS
    assert cube.tx_c.dtype == np.float32
    assert cube.tx_c.attrs["units"] == "degC"
    assert cube.lat.attrs["units"] == "degrees_north"
    assert cube.lon.attrs["units"] == "degrees_east"
    assert np.isfinite(cube.tx_c.values).any() and not np.isinf(cube.tx_c.values).any()
    np.testing.assert_array_equal(cube.time.values, expected_seasons(years))
    np.testing.assert_allclose(cube.lat, np.arange(451, 460) / 10, atol=5e-6, rtol=0)
    np.testing.assert_allclose(cube.lon, np.arange(86, 101) / 10, atol=5e-6, rtol=0)


def test_events_against_real_reference_and_target(load_output):
    base = load_output("baseline.nc")
    target = load_output("target.nc")
    events = load_output("events.nc")
    assert events.attrs["contract_version"] == "1"
    np.testing.assert_array_equal(base.time.values, expected_seasons(range(1991, 2021)))
    np.testing.assert_array_equal(events.time.values, SUMMER)
    for axis in ("lat", "lon"):
        np.testing.assert_array_equal(base[axis], target[axis])
        np.testing.assert_array_equal(target[axis], events[axis])
    for field in ("tx_c", "p90_c", "excess_c"):
        assert events[field].dims == DIMS and events[field].attrs["units"] == "degC"
        assert events[field].dtype.kind == "f" and not np.isinf(events[field].values).any()
    tx = target.tx_c.sel(time=SUMMER).values
    flags = events.heatwave_flag
    assert flags.dims == DIMS and flags.dtype == np.int8
    assert np.isin(flags, [-1, 0, 1]).all()
    np.testing.assert_array_equal(events.tx_c.values, tx)
    np.testing.assert_allclose(events.excess_c, tx - events.p90_c.values, atol=1e-5, rtol=0)

    # Each reference summer has 153 days. The first 15-day sample spans May 25 to June 8.
    baseline = base.tx_c.values.reshape(30, 153, *tx.shape[1:])
    expected = np.full(tx.shape, np.nan)
    for day in range(len(SUMMER)):
        samples = baseline[:, 24 + day:39 + day].reshape(450, *tx.shape[1:])
        usable = np.isfinite(samples).sum(axis=0) >= 405
        if usable.any():
            expected[day, usable] = np.nanpercentile(
                samples[:, usable].astype("float64"), 90, method="linear", axis=0,
            )
    np.testing.assert_allclose(events.p90_c, expected, atol=1e-5, rtol=0)
    known = np.isfinite(expected) & np.isfinite(tx)
    np.testing.assert_array_equal(flags.values == -1, ~known)
    # Group each cell's strict exceedances in date order. Unknowns break the run.
    for row, col in np.ndindex(tx.shape[1:]):
        exceed = tx[:, row, col] > expected[:, row, col]
        wanted = np.where(known[:, row, col], 0, -1)
        for hot, group in groupby(range(len(SUMMER)), key=lambda i: exceed[i]):
            dates = list(group)
            if hot and len(dates) >= 3:
                wanted[dates] = 1
        np.testing.assert_array_equal(flags.values[:, row, col], wanted, err_msg=f"cell {row},{col}")


def angular_edges(centres):
    values = np.asarray(centres, dtype=float)
    inner = (values[1:] + values[:-1]) / 2
    return np.deg2rad(np.r_[2 * values[0] - inner[0], inner, 2 * values[-1] - inner[-1]])


def components(mask):
    # Traverse edge neighbours from the first remaining cell in latitude-major order.
    remaining = set(zip(*np.nonzero(mask)))
    while remaining:
        first = min(remaining)
        stack = [first]
        remaining.remove(first)
        cells = []
        while stack:
            r, c = stack.pop()
            cells.append((r, c))
            for neighbor in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    stack.append(neighbor)
        yield tuple(zip(*cells))


def test_footprint_labels_summary_and_area(load_output, run_dir):
    events = load_output("events.nc")
    output = load_output("footprints.nc")
    ids = output.footprint_id
    assert output.attrs["contract_version"] == "1"
    assert output.attrs["connectivity"] == 4
    assert output.attrs["earth_radius_km"] == pytest.approx(6371.0088)
    assert ids.dims == DIMS and ids.dtype.kind == "i"
    np.testing.assert_array_equal(ids.time.values, SUMMER)
    for axis in DIMS:
        np.testing.assert_array_equal(ids[axis], events[axis])
    flags = events.heatwave_flag.values
    np.testing.assert_array_equal(ids.values == -1, flags == -1)
    np.testing.assert_array_equal(ids.values == 0, flags == 0)
    areas = 6371.0088**2 * np.outer(
        np.diff(np.sin(angular_edges(ids.lat))), np.diff(angular_edges(ids.lon)),
    )
    path = run_dir / "footprints.csv"
    assert path.is_file(), f"Missing real-case summary {path}"
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        assert reader.fieldnames == SUMMARY_COLUMNS
        rows = list(reader)
    expected_keys = []
    for t, day in enumerate(np.datetime_as_string(SUMMER, unit="D")):
        daily_sum = 0.0
        hot = flags[t] == 1
        for component, cells in enumerate(components(hot), start=1):
            assert (ids.values[t][cells] == component).all()
            assert len(rows) > len(expected_keys), f"Missing CSV component on {day}"
            row = rows[len(expected_keys)]
            expected_keys.append((day, component))
            assert int(row["cell_count"]) == len(cells[0])
            assert float(row["area_km2"]) == pytest.approx(areas[cells].sum(), rel=1e-5, abs=1e-6)
            assert float(row["peak_excess_c"]) == pytest.approx(events.excess_c.values[t][cells].max(), abs=1e-5)
            daily_sum += float(row["area_km2"])
        assert daily_sum == pytest.approx(areas[hot].sum(), rel=1e-5, abs=1e-6)
    assert [(row["date"], int(row["footprint_id"])) for row in rows] == expected_keys
