# Synthetic handoffs for parallel development

The committed NetCDF files are small and contain fabricated values. Run `python integration/fixtures/build_fixtures.py` from the root to regenerate them with SciPy and NumPy.

| File | Independent use |
| --- | --- |
| `baseline_fixture.nc` and `target_fixture.nc` | Events can test two reference years (2003 and leap year 2004) with P90 exactly 30 °C, plus a full synthetic target season. |
| `events_fixture.nc` | Footprints can start from a hand labelled 92 day mask with only three affected days, covering edge adjacency, diagonal contact and an unknown cell. |
| `worked_example.csv` | Five days from the same fixture, recorded with expected flags and component identifiers for hand checking. |

The first three days have two components. The first contains the two adjacent cells in the 45.4°N row, and the second contains the eastern cell in the 45.5°N row. Diagonal contact keeps the components separate. Equality or a missing value breaks each shorter run. Days four and five have zero components.
