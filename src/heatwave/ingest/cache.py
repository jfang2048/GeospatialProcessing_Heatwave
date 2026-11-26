"""Locate downloaded monthly files and open NetCDFs inside CDS ZIPs."""

import shutil
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile, is_zipfile


def cache_entry(cache_dir, label):
    entry = cache_dir / label
    if entry.exists():
        return entry
    # Reuse downloads stored under the old date-and-hash folder names.
    return next(cache_dir.glob(f"{label}_" + "[0-9a-f]" * 12), entry)


def cached_payload(entry):
    for name in ("payload.nc", "payload.zip"):
        path = entry / name
        if path.is_file():
            return path
    raise FileNotFoundError(f"No CDS download in {entry}")


NETCDF_SIGNATURES = (b"CDF\x01", b"CDF\x02", b"CDF\x05", b"\x89HDF\r\n\x1a\n")


def _netcdf_name(archive):
    members = [name for name in archive.namelist() if name.lower().endswith(".nc")]
    if len(members) != 1:
        raise ValueError("Expected one NetCDF file in the CDS ZIP")
    return members[0]


def payload_suffix(path):
    if is_zipfile(path):
        with ZipFile(path) as archive, archive.open(_netcdf_name(archive)) as source:
            if source.read(8).startswith(NETCDF_SIGNATURES):
                return ".zip"
    else:
        with path.open("rb") as source:
            if source.read(8).startswith(NETCDF_SIGNATURES):
                return ".nc"
    raise ValueError("CDS response does not contain a NetCDF file")


@contextmanager
def netcdf_path(payload):
    if payload.suffix == ".nc":
        yield payload
        return
    with ZipFile(payload) as archive, TemporaryDirectory() as scratch:
        path = Path(scratch) / "data.nc"
        with archive.open(_netcdf_name(archive)) as source, path.open("wb") as target:
            shutil.copyfileobj(source, target)
        yield path
