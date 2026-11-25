# Milan case work plan

## Milestones

The downloader, three processing commands and [case notebook](../notebooks/01_case.ipynb) are available. Their presence establishes that the team can start verification. A claim about heat in Milan requires a completed provider-backed run.

| Target | Owner | Evidence to record |
| --- | --- | --- |
| 23 Nov 2026 project session | All | Record the group's scope decision and any requested changes to the proposed v1 interface. |
| 26 Nov | FJ | Verify the seven-day CDS pilot, inspect its variables, units, archive layout, grid and dates, and record what the provider returned. Keep the pilot separate from the full reference and target. |
| 3 Dec | FJ, YY and FY | FJ supplies the verified inputs; YY and FY run their commands in order. Link each handoff to its input snapshot and producing commit. Record the precise missing input if a stage is blocked. |
| 10 Dec | All | Reproduce the real case in a fresh directory, run the real-data tests and execute the notebook. Compare the figures and CSV with the source rasters. |
| 14 Dec project session | All | Rehearse individual explanations and review each member's contributions and the submission materials. |

The assignment leaves the topic, data and methods to the team. The proposed case covers one Milan-domain summer and three figures. See the [grid and visual specifications](../contracts/geography.md), [file interfaces](../contracts/v1.md) and [handoff change procedure](../AGENTS.md).

## Course deliverables

| Requirement | Evidence for review |
| --- | --- |
| A small module the group understands | Trace one real cell from daily temperature to its heatwave flag, then follow a component from its labelled cells to its summary row. Review AI-assisted code and be prepared to explain its scientific decisions. |
| Documented, reproducible processing | Provide source, environment, README, comments and a runnable Jupyter example. Identify the ERA5-Land source, period, input version and commands needed to reproduce the example. |
| Appropriate tests | Run the real-data suite. Independently check a local threshold, the duration decision and the component area against the rasters. Record inputs and results. |
| Personal repository contributions | Each member commits and pushes their own changes. Record the commit or PR for each contribution. |
| Individual explanation | Each member demonstrates the end-to-end workflow, including the inputs and outputs on either side of their own stage. |

## Integration commands

From the repository root, activate the project environment and obtain the provider-backed data as described in the [ingest guide](../heatwave/ingest/README.md). The commands below use a fresh `runs/milan` directory. For a rerun, choose a new run directory and substitute it in every path.

```bash
python -m heatwave.ingest.download --profile full --verify-only
python -m heatwave.ingest.normalize --cache-dir data/raw/cds --baseline-out runs/milan/baseline.nc --target-out runs/milan/target.nc
python -m heatwave.events.detect --baseline runs/milan/baseline.nc --target runs/milan/target.nc --out runs/milan/events.nc
python -m heatwave.footprints.summarize --events runs/milan/events.nc --labels-out runs/milan/footprints.nc --summary-out runs/milan/footprints.csv
```

Full raw-cache verification covers **155 monthly requests**. Preserve each original request manifest, request parameters, byte count and SHA-256 alongside its matching payload. Normalization reads the verified payloads and writes separate Celsius cubes with 4,590 May-September reference dates and 153 May-September target dates on the same 9 by 15 grid.

A teammate starting from an existing normalized snapshot can place its verified `baseline.nc` and `target.nc` in a fresh run directory and start with Events. First match their sizes and SHA-256 values to the populated snapshot manifest. Record the snapshot ID, CDS dataset and DOI, source requests, bounds, reference and target periods, units and producing commit. The [manifest template](../heatwave/ingest/snapshot.example.json) shows the fields. The normalized snapshot supports downstream checks; full raw-to-output verification also requires the provider cache.

The default pytest collection is the real-data suite under `integration/real_tests/`. It also uses the separate July 2022 pilot and the original July 1991 and July 2022 monthly payloads to check provider data against the normalized cubes. Keep the verified cache in `data/raw/cds` or point `HEATWAVE_CACHE_DIR` to its location for pytest. With only the pilot available, run `python -m pytest -q integration/real_tests/test_pilot.py` and record this as pilot verification. Point `HEATWAVE_RUN_DIR` to the directory containing the two verified input cubes and all three generated outputs before running the tests and notebook. For the path above use `export HEATWAVE_RUN_DIR=runs/milan` in Bash or `$env:HEATWAVE_RUN_DIR = 'runs/milan'` in PowerShell.

```bash
python -m pytest -ra
python -m nbconvert --to notebook --execute notebooks/01_case.ipynb --output-dir runs/milan
```

| Reviewer | What to verify on the real case |
| --- | --- |
| FJ | Confirm full request coverage, input checksums, temperature conversion and decoded UTC dates. Keep the original and normalized grid coordinates available for comparison. |
| YY | Select a real cell and date. Check the finite sample count and linear P90 in its 15-day windows across 30 years. Inspect neighbouring target dates to confirm the strict exceedance and three-day run decision. |
| FY | For one positive daily ID, recount its cells and compare their directly summed nominal areas and peak exceedance with the CSV. Across the summer, compare the raster and CSV totals and check how unknown cells affect coverage. If no cells qualify, verify that the summary has only its header. |
| All | Check the three figures against the [map guide](../contracts/geography.md#three-submission-figures). The peak-day map, if applicable, must agree with the earliest maximum positive area in the daily series. |

Record the source snapshot, code revision, commands, test counts and any missing data or skipped check. A run blocked on access to provider inputs remains pending. Earlier fabricated examples in the repository are archived design material. The submission, tests and figures use the verified ERA5-Land case.

Enter the team details, tentative title and repository URL in the course spreadsheet. Confirm the exam call in WeBeep and count back nine calendar days to the last eligible repository change.
