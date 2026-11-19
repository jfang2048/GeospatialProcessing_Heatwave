# Ingest ownership · FJ

Edit files under `heatwave/ingest/` on `ingest/<task>` branches. Use a separate integration branch for your shared repository responsibilities. Follow the [v1 contract](../../contracts/v1.md) and [download guide](README.md).

Own `download.py`, the planned `normalize.py`, data acquisition documentation, the approved input snapshot manifest and all ingest tests. Start with the seven day pilot. Inspect ZIP members, units, date labels and coordinate order, then write validation and normalization before fetching the full reference data. Publish only the two normalized cubes to downstream owners, identified by snapshot ID and checksums. Keep raw files and run artifacts under ignored root directories.
