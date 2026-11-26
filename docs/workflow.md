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

The assignment leaves the topic, data and methods to the team. The proposed case covers one Milan-domain summer and three figures. See the [grid and visual specifications](geography.md), [file interfaces](v1.md) and [handoff change procedure](../AGENTS.md).

## Course deliverables

| Requirement | Evidence for review |
| --- | --- |
| A small module the group understands | Trace one real cell from daily temperature to its heatwave flag, then follow a component from its labelled cells to its summary row. Review AI-assisted code and be prepared to explain its scientific decisions. |
| Documented, reproducible processing | Provide source, environment, README, comments and a runnable Jupyter example. Identify the ERA5-Land source, period, input version and commands needed to reproduce the example. |
| Appropriate tests | Run the real-data suite. Independently check a local threshold, the duration decision and the component area against the rasters. Record inputs and results. |
| Personal repository contributions | Each member commits and pushes their own changes. Record the commit or PR for each contribution. |
| Individual explanation | Each member demonstrates the end-to-end workflow, including the inputs and outputs on either side of their own stage. |

## Integration commands

From the repository root, activate the project environment and obtain the provider-backed data as described in the [ingest guide](data.md). The commands below use a fresh `runs/milan` directory. Start at Events if you already have the verified snapshot. For a rerun, choose a new run directory and substitute it in every path.

```bash
python -m heatwave.ingest.download --profile full --verify-only
python -m heatwave.ingest.normalize --cache-dir data/raw/cds --baseline-out runs/milan/baseline.nc --target-out runs/milan/target.nc
python -m heatwave.events.detect --baseline runs/milan/baseline.nc --target runs/milan/target.nc --out runs/milan/events.nc
python -m heatwave.footprints.summarize --events runs/milan/events.nc --labels-out runs/milan/footprints.nc --summary-out runs/milan/footprints.csv
```

Full raw-cache verification covers **155 monthly requests**. Preserve each original request manifest, request parameters, byte count and SHA-256 alongside its matching payload. Normalization reads the verified payloads and writes separate Celsius cubes with 4,590 May-September reference dates and 153 May-September target dates on the same 9 by 15 grid.

For a shared snapshot, [verify both cubes](data.md#share-a-snapshot), place them in the run directory, and start at Events. Run `python -m pytest -q tests/real/test_case.py` to check the downstream stages. Full raw-to-output verification also needs the provider cache.

The default pytest collection is the real-data suite under `tests/real/`. It also uses the separate July 2022 pilot and the original July 1991 and July 2022 monthly payloads to check provider data against the normalized cubes. Keep the verified cache in `data/raw/cds` or point `HEATWAVE_CACHE_DIR` to its location for pytest. With only the pilot available, run `python -m pytest -q tests/real/test_pilot.py` and record this as pilot verification. Point `HEATWAVE_RUN_DIR` to the directory containing the two verified input cubes and all three generated outputs before running the tests and notebook. For the path above use `export HEATWAVE_RUN_DIR=runs/milan` in Bash or `$env:HEATWAVE_RUN_DIR = 'runs/milan'` in PowerShell.

```bash
python -m pytest -ra
python -m nbconvert --to notebook --execute notebooks/01_case.ipynb --output-dir runs/milan
```

| Reviewer | What to verify on the real case |
| --- | --- |
| FJ | Confirm full request coverage, input checksums, temperature conversion and decoded UTC dates. Keep the original and normalized grid coordinates available for comparison. |
| YY | Select a real cell and date. Check the finite sample count and linear P90 in its 15-day windows across 30 years. Inspect neighbouring target dates to confirm the strict exceedance and three-day run decision. |
| FY | For one positive daily ID, recount its cells and compare their directly summed nominal areas and peak exceedance with the CSV. Across the summer, compare the raster and CSV totals and check how unknown cells affect coverage. If no cells qualify, verify that the summary has only its header. |
| All | Check the three figures against the [map guide](geography.md#three-submission-figures). The peak-day map, if applicable, must agree with the earliest maximum positive area in the daily series. |

Record the source snapshot, code revision, commands, test counts and any missing data or skipped check. A run blocked on access to provider inputs remains pending. Use the verified ERA5-Land case for submission tests and figures.

Enter the team details, tentative title and repository URL in the course spreadsheet. Confirm the exam call in WeBeep and count back nine calendar days to the last eligible repository change.

## Synthetic fixtures

**Historical teaching example.** Run project acceptance and generate submission figures using the [real Milan data workflow](../README.md).

The committed NetCDF files are small and contain fabricated values. Run `python notebooks/data/fixtures/build_fixtures.py` from the root to regenerate them with SciPy and NumPy.

| File | Independent use |
| --- | --- |
| `baseline_fixture.nc` and `target_fixture.nc` | Events can test two reference years (2003 and leap year 2004) with P90 exactly 30 °C, plus a full synthetic target season. |
| `events_fixture.nc` | Footprints can start from a hand labelled 92 day mask with only three affected days, covering edge adjacency, diagonal contact and an unknown cell. |
| `worked_example.csv` | Five days from the same fixture, recorded with expected flags and component identifiers for hand checking. |

The first three days have two components. The first contains the two adjacent cells in the 45.4°N row, and the second contains the eastern cell in the 45.5°N row. Diagonal contact keeps the components separate. Equality or a missing value breaks each shorter run. Days four and five have zero components.
