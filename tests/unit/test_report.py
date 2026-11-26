"""Check plotted values against a small, hand-calculated report case."""

import csv

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest
import xarray as xr

from heatwave.report import figures, main

matplotlib.use("Agg")


@pytest.fixture
def report_case(tmp_path):
    coords = {
        "time": np.arange("2022-07-01", "2022-07-05", dtype="datetime64[D]"),
        "lat": ("lat", [45.5, 45.6], {"units": "degrees_north"}),
        "lon": ("lon", [9.2, 9.3], {"units": "degrees_east"}),
    }
    dims = ("time", "lat", "lon")
    flags = np.array([
        [[0, 0], [0, 0]],
        [[-1, -1], [-1, -1]],
        [[1, -1], [0, 0]],
        [[1, 0], [0, 0]],
    ], dtype=np.int8)
    tx = np.where(flags == -1, np.nan, np.where(flags == 1, 36.0, 30.0))
    threshold = np.full(flags.shape, 32.0)
    attrs = {"contract_version": "1", "source": "Synthetic example"}
    events = xr.Dataset(
        {"tx_c": (dims, tx), "p90_c": (dims, threshold), "heatwave_flag": (dims, flags)},
        coords=coords, attrs=attrs,
    )
    events[["tx_c"]].to_netcdf(tmp_path / "target.nc")
    events.to_netcdf(tmp_path / "events.nc")
    labels = xr.Dataset(
        {"footprint_id": (dims, flags.astype(np.int32))},
        coords=coords, attrs={**attrs, "earth_radius_km": 6371.0088},
    )
    labels.to_netcdf(tmp_path / "footprints.nc")
    # One hot cell lies between 45.45 and 45.55°N, with a longitude width of 0.1°.
    low, high = np.deg2rad([45.45, 45.55])
    area = 6371.0088**2 * (np.sin(high) - np.sin(low)) * np.deg2rad(0.1)
    with (tmp_path / "footprints.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["date", "footprint_id", "cell_count", "area_km2", "peak_excess_c"])
        writer.writerows([[f"2022-07-0{day}", 1, 1, area, 4] for day in (3, 4)])
    return tmp_path, area


def test_figures_plot_observed_area_and_choose_earliest_peak(report_case):
    folder, area = report_case
    plots = figures(folder)
    try:
        temp = plots["temperature"].axes[0]
        np.testing.assert_allclose(temp.lines[0].get_ydata(), [30, np.nan, 36, 36])
        np.testing.assert_allclose(temp.lines[1].get_ydata(), [32, 32, 32, 32])
        np.testing.assert_array_equal(temp.collections[0].get_offsets()[:, 1], [36, 36])

        daily, coverage = plots["area"].axes
        np.testing.assert_allclose(daily.lines[0].get_ydata(), [0, np.nan, area, area])
        np.testing.assert_array_equal(coverage.lines[0].get_ydata(), [100, 0, 75, 100])
        assert len(daily.collections[0].get_offsets()) == 1

        peak = plots["footprints"].axes[0]
        assert "2022-07-03 UTC" in peak.get_title()
        mesh = peak.collections[0]
        coords = mesh.get_coordinates()
        np.testing.assert_allclose(coords[0, 0], [9.15, 45.45])
        np.testing.assert_allclose(coords[-1, -1], [9.35, 45.65])
        np.testing.assert_array_equal(mesh.get_array().ravel(), [2, 0, 1, 1])
    finally:
        for figure in plots.values():
            plt.close(figure)


def test_export_can_be_repeated(report_case):
    folder, _ = report_case
    output = folder / "report"
    args = ["--run-dir", str(folder), "--output-dir", str(output)]
    main(args)
    first = {path.name: path.read_bytes() for path in output.iterdir()}
    assert set(first) == {"temperature.png", "area.png", "footprints.png"}
    assert all(content.startswith(b"\x89PNG\r\n\x1a\n") for content in first.values())
    main(args)
    assert {path.name: path.read_bytes() for path in output.iterdir()} == first


def test_report_rejects_an_area_csv_from_a_different_run(report_case):
    folder, _ = report_case
    summary = folder / "footprints.csv"
    summary.write_text("date,footprint_id,area_km2\n2022-07-03,1,999\n", encoding="utf-8")
    with pytest.raises(ValueError, match="CSV areas disagree"):
        figures(folder)


def test_report_describes_a_season_without_qualifying_cells(report_case):
    folder, _ = report_case
    paths = (folder / "events.nc", folder / "footprints.nc")
    for path, variable in zip(paths, ("heatwave_flag", "footprint_id"), strict=True):
        ds = xr.load_dataset(path)
        ds[variable] = ds[variable].clip(max=0)
        ds.to_netcdf(path)
    (folder / "footprints.csv").write_text(
        "date,footprint_id,area_km2\n", encoding="utf-8",
    )
    plots = figures(folder)
    try:
        peak = plots["footprints"].axes[0]
        assert [label.get_text() for label in peak.texts] == ["No qualifying cells on observed days."]
        assert not peak.collections
    finally:
        for figure in plots.values():
            plt.close(figure)
