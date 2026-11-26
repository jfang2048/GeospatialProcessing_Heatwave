"""First check after downloading the real seven-day pilot; no stage outputs needed."""

import csv
from pathlib import Path

import numpy as np


def test_real_cds_pilot(load_raw_kelvin):
    temperature = load_raw_kelvin(2022, 15, 21)
    assert temperature.shape == (7, 9, 15)
    sample = Path(__file__).resolve().parents[2] / "notebooks" / "data" / "pilot_milan_cell.csv"
    with sample.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    assert {(float(row["lat_deg_north"]), float(row["lon_deg_east"])) for row in rows} == {(45.5, 9.2)}
    cell = temperature.sel(lat=45.5, lon=9.2, method="nearest")
    assert [row["date_utc"] for row in rows] == np.datetime_as_string(cell.time.values, unit="D").tolist()
    # The public extract rounds the CF-decoded temperature to a thousandth of a degree.
    np.testing.assert_allclose(
        [float(row["tx_c"]) for row in rows], cell.values.astype(float) - 273.15,
        atol=0.000501, rtol=0,
    )
