"""Read, verify and publish CDS request cache entries."""

import errno
import hashlib
import json
import shutil
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile, is_zipfile

from heatwave.ingest.requests import DATASET, DATASET_DOI

NETCDF_SIGNATURES = (b"CDF\x01", b"CDF\x02", b"CDF\x05", b"\x89HDF\r\n\x1a\n")


def _netcdf_member(archive):
    members = [info for info in archive.infolist() if info.filename.lower().endswith(".nc")]
    if len(members) != 1:
        raise ValueError(f"expected one NetCDF member in ZIP, found {len(members)}")
    return members[0]


@contextmanager
def netcdf_path(payload):
    """Expose one NetCDF member to xarray, including NetCDF4/HDF5 ZIP members."""
    if payload.suffix == ".nc":
        yield payload
        return
    with ZipFile(payload) as archive, TemporaryDirectory() as scratch:
        path = Path(scratch) / "month.nc"
        with archive.open(_netcdf_member(archive)) as source, path.open("wb") as dest:
            shutil.copyfileobj(source, dest)
        yield path


def cache_entry(cache_dir, label, request):
    """Locate the cache directory keyed by both the CDS dataset and request."""
    # Retain the original key for the same one-month request across schema versions.
    encoded = json.dumps([DATASET, _cache_request(request)], sort_keys=True).encode("utf-8")
    version = hashlib.sha256(encoded).hexdigest()[:12]
    return cache_dir / f"{label}_{version}"


def payload_kind(path):
    """Identify direct NetCDF or verify the NetCDF member of a CDS ZIP."""
    with path.open("rb") as payload:
        signature = payload.read(8)
    if signature.startswith(NETCDF_SIGNATURES):
        return "nc"
    if not is_zipfile(path):
        raise ValueError("CDS response is neither NetCDF nor a readable ZIP")
    with ZipFile(path) as archive:
        member = _netcdf_member(archive)
        with archive.open(member) as source:
            if not source.read(8).startswith(NETCDF_SIGNATURES):
                raise ValueError(f"ZIP member is not NetCDF: {member.filename}")
        damaged_member = archive.testzip()
        if damaged_member is not None:
            raise ValueError(f"ZIP integrity check failed for {damaged_member}")
    return "zip"


def sha256(path):
    """Return the hexadecimal SHA-256 digest used in the cache manifest."""
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def _cache_request(request):
    month = request["month"]
    return {**request, "month": [month]} if isinstance(month, str) else request


def verify_entry(entry, request):
    """Accept a cache hit only when both the request and payload match."""
    try:
        manifest = json.loads((entry / "manifest.json").read_text(encoding="utf-8"))
        if manifest["dataset"] != DATASET or _cache_request(manifest["request"]) != _cache_request(request):
            raise ValueError("cached request differs")
        filename = manifest["payload"]
        if filename not in {"payload.zip", "payload.nc"}:
            raise ValueError("invalid payload filename")
        payload = entry / filename
        if payload.stat().st_size != manifest["bytes"]:
            raise ValueError("payload byte count differs")
        if sha256(payload) != manifest["sha256"]:
            raise ValueError("payload SHA-256 differs")
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise ValueError(f"{entry}: {error}") from error
    return payload


def publish_entry(entry, request, payload, provenance, *, match_bytes=False):
    """Publish the prepared payload and manifest together."""
    staging = payload.parent
    digest = sha256(payload)
    manifest = {
        "dataset": DATASET,
        "dataset_doi": DATASET_DOI,
        "request": request,
        **provenance,
        "payload": payload.name,
        "bytes": payload.stat().st_size,
        "sha256": digest,
    }
    (staging / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    try:
        staging.rename(entry)
    except OSError as error:
        if error.errno not in (errno.EEXIST, errno.ENOTEMPTY):
            raise
        cached = verify_entry(entry, request)
        if match_bytes and sha256(cached) != digest:
            raise ValueError("an existing pilot has different bytes; use a separate cache directory")
        return cached
    return entry / payload.name
