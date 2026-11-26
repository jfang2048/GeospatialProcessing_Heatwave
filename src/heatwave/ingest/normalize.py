"""Normalize the CDS monthly cache into two v1 temperature cubes."""

import argparse
import sys
from pathlib import Path
from zipfile import BadZipFile

import numpy as np

from heatwave._handoff import publish_outputs
from heatwave.ingest.cache import cache_entry, cached_payload
from heatwave.ingest.check import check_pair
from heatwave.ingest.provider import load_month, temperature_cube
from heatwave.ingest.requests import DATASET, DATASET_DOI, request_plan


def normalize(cache_dir, baseline_out, target_out):
    """Publish baseline and target cubes from the complete cache specified in docs/v1.md.

    Reject missing or misaligned partitions before publishing either cube.
    Both outputs preserve the WGS 84 grid, UTC dates and provider mask.
    """
    cache = cache_dir.resolve()
    for path in (baseline_out, target_out):
        if path.resolve().is_relative_to(cache):
            raise ValueError(f"output must be outside the provider cache: {path}")
    grid = None
    with publish_outputs((baseline_out, target_out)) as (baseline_stage, target_stage):
        for profile, output in (("target", target_stage), ("baseline", baseline_stage)):
            all_dates, all_values = [], []
            for label, request in request_plan(profile):
                payload = cached_payload(cache_entry(cache, label))
                dates, lat, lon, tx_c = load_month(payload, request)
                if grid is None:
                    grid = lat, lon
                elif not np.array_equal(lat, grid[0]) or not np.array_equal(lon, grid[1]):
                    raise ValueError(f"{payload}: latitude or longitude differs from other partitions")
                all_dates.append(dates)
                all_values.append(tx_c)
            temperature_cube(
                np.concatenate(all_dates), *grid, np.concatenate(all_values),
                source=DATASET, doi=DATASET_DOI,
            ).to_netcdf(output)
        check_pair(baseline_stage, target_stage)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--baseline-out", type=Path, required=True)
    parser.add_argument("--target-out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        normalize(args.cache_dir, args.baseline_out, args.target_out)
    except (BadZipFile, KeyError, OSError, TypeError, ValueError) as error:
        print(f"Normalization failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
