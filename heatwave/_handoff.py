"""Coordinate and output-file conventions shared by the v1 processing stages."""

from contextlib import ExitStack, contextmanager
import os
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np


def validate_grid(ds):
    """Check v1 centre coordinates and unique, increasing UTC day labels."""
    if ds.attrs.get("contract_version") != "1":
        raise ValueError("expected contract_version '1'")
    for axis, units in (("lat", "degrees_north"), ("lon", "degrees_east")):
        if axis not in ds.coords or ds[axis].dims != (axis,):
            raise ValueError(f"expected one-dimensional {axis} centres")
        coord = ds[axis]
        if coord.attrs.get("units") != units or coord.dtype.kind not in "fiu":
            raise ValueError(f"{axis} must contain numeric centres in {units}")
        values = coord.values.astype(float)
        steps = np.diff(values)
        if not steps.size or not np.isfinite(values).all() or not (steps > 0).all():
            raise ValueError(f"{axis} requires at least two increasing finite centres")
        # Input coordinates may have been stored as float32 decimal degrees.
        tolerance = 2 * max(abs(np.spacing(coord.values)).max(), 1e-12) if coord.dtype.kind == "f" else 0
        if not np.allclose(steps, steps[0], atol=tolerance, rtol=1e-6):
            raise ValueError(f"{axis} centres must be regularly spaced")
    if "time" not in ds.coords or ds.time.dims != ("time",) or ds.time.dtype.kind != "M":
        raise ValueError("expected decoded Gregorian dates on a one-dimensional time axis")
    times = ds.time.values
    days = times.astype("datetime64[D]")
    if not len(days) or np.isnat(days).any() or not np.array_equal(times, days):
        raise ValueError("time labels must be finite dates at midnight UTC")
    if not (days[1:] > days[:-1]).all():
        raise ValueError("dates must be unique and strictly increasing")


@contextmanager
def publish_outputs(paths):
    """Stage a complete handoff beside each fresh destination, then publish it."""
    outputs = [Path(path).resolve() for path in paths]
    if len(set(outputs)) != len(outputs):
        raise ValueError("each output needs a distinct path")
    with ExitStack() as stack:
        staged = []
        for path in outputs:
            if path.exists():
                raise FileExistsError(f"choose a fresh output path: {path}")
            path.parent.mkdir(parents=True, exist_ok=True)
            folder = stack.enter_context(TemporaryDirectory(dir=path.parent))
            staged.append(Path(folder) / path.name)
        yield tuple(staged)
        published = []
        try:
            for temporary, destination in zip(staged, outputs, strict=True):
                # Publishing with a hard link also rejects a concurrent writer
                # that created the destination while this stage was working.
                os.link(temporary, destination)
                published.append(destination)
        except OSError:
            for destination in published:
                destination.unlink()
            raise
