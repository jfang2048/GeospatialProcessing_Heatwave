"""Exercise the Footprints command without running Events first."""

import csv
from pathlib import Path

import pytest
import xarray as xr

from heatwave.footprints.summarize import summarize

EXAMPLES = Path(__file__).resolve().parents[2] / "data/examples/synthetic"


def test_footprints_matches_hand_labelled_cells_and_summary(tmp_path):
    labels = tmp_path / "footprints.nc"
    summary = tmp_path / "footprints.csv"
    summarize(EXAMPLES / "events_fixture.nc", labels, summary)

    with xr.open_dataset(labels) as cube, (EXAMPLES / "worked_example.csv").open() as source:
        for row in csv.DictReader(source):
            cell = cube.footprint_id.sel(time=row["date"], lat=float(row["lat"]), lon=float(row["lon"]))
            assert cell.item() == int(row["footprint_id"])
    with summary.open() as source:
        rows = list(csv.DictReader(source))
    assert len(rows) == 6
    first = rows[0]
    assert (first["date"], first["footprint_id"], first["cell_count"]) == ("2022-06-01", "1", "2")
    assert float(first["peak_excess_c"]) == pytest.approx(2.0)
