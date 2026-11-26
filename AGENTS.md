# Contribution rules

Each owner maintains their module's code, acceptance checks and documentation. Use the [v1 contract](docs/v1.md) for file handoffs and acceptance checks.

| Owner | Module | Branch | Starting point |
| --- | --- | --- | --- |
| FJ | `heatwave/ingest/` | `ingest/<task>` | [CDS data guide](docs/data.md) |
| YY | `heatwave/events/` | `events/<task>` | [Baseline and target files](docs/data.md) |
| FY | `heatwave/footprints/` | `footprints/<task>` | [Events raster and daily footprint handoff](docs/v1.md) |

FJ maintains shared files and dependencies. Use issues or PR reviews to request shared changes. For a handoff change, include a failing example, affected inputs and outputs, and the proposed contract revision. The integration owner versions the contract after the affected owners agree.

## Local releases

For FJ's local checkout, make and test changes on `dev`. Commit each related batch, run the publication checks, merge it into local `main`, and push `origin main`. Verify the remote commit before returning to `dev`. Keep the local `dev` branch available for the next batch.

## Public repository checklist

Use team initials `FJ`, `FY` or `YY` in files, notebooks, commit messages, Git identities, and GitHub discussions. Keep member full names, personal email addresses, personal filesystem paths, credentials, private links, raw provider downloads, and run artifacts in local or approved private storage. Cite the data source in public examples. The teaching sample is a seven-row derived temperature series. Its README records the data licence, source date range, coordinates, conversion and rounding. Share the two NetCDF inputs through the team folder.

Configure your identity once per clone. Substitute your assigned initials and the matching placeholder email. This example is for FJ.

```bash
git config --local user.name FJ
git config --local user.email fj@project.invalid
git var GIT_AUTHOR_IDENT
git var GIT_COMMITTER_IDENT
```

Before every push, fetch and review the files and **every outgoing commit** on the current branch from the repository root.

```bash
git fetch origin
git status --short
git diff --cached --check
python .github/scripts/check_publication.py origin/main HEAD
git diff --check origin/main...HEAD
git log --no-use-mailmap --format=fuller --stat -m -p origin/main..HEAD
```

- Run the publication check after committing, from the repository root. It checks the author and committer pair on every outgoing commit and flags tracked paths matching the checkout's active ignore rules. Run it for each ref you intend to publish, using its base and tip. Inspect the tag message and tagger separately for an annotated tag.
- Review commit messages (including co-author trailers), filenames and diffs for private information, including lines removed in later commits. Inspect changed binary files, NetCDF attributes, and notebook cells, outputs and metadata. A credential or private URL in an ordinary source file can pass the automated check. Store executed notebooks under `runs/`. Keep any example settings free of live values.
- Fix the commit that contains a finding and rerun the checks before pushing. If private information has already reached GitHub, notify the team privately and rotate any exposed credentials. Coordinate history cleanup with the integration owner.

## Work and merge rules

1. Each member makes their own commits and pushes their own branch to the project repository. Start each task from current `main` and open one PR. Identify the affected handoff and run the applicable real-data checks. Include the command and result. Record any input-access blocker explicitly.
2. Treat stage outputs as immutable inputs to the next module. Pass paths explicitly and use separate run directories. Keep edits within your owned paths.
3. Record the input source, output units and date range. A teammate reviews each PR. After merging, affected owners verify the next handoff.
4. In the PR description, give the input files, changed handoff, test command and result. Set `HEATWAVE_RUN_DIR` to the completed local case directory and run `python -m pytest -ra` for the default real-data suite. CI checks without provider-backed inputs establish code readiness only. Use the [work plan](docs/workflow.md#tests) for full real-case verification.
5. Review and publish only the code, documentation and sanitized evidence needed to reproduce the run. Apply the publication checklist before the first push to a topic branch as well as later pushes. GitHub displays the accounts opening and reviewing PRs.

## Code comments and docstrings

The assignment asks for code comments, READMEs and a reproducible demonstration. It leaves the comment format open. The team uses English for shared code, CLI help, comments and docstrings. Document a public stage entry point where it is defined. Give its input and output files, the conditions it rejects, and a reference to the relevant contract section. Include units, coordinate order or UTC date semantics wherever a caller could otherwise interpret a value in two ways.

Use comments to explain scientific choices and boundary cases, such as why an unknown day breaks a run or why cell-area arithmetic uses radians. In a numerical test, explain how to obtain any non-obvious expected value independently of the implementation. Cite the source by name or link when a formula or rule comes from a reference. Keep comments concise and update them alongside the behaviour they describe.

For example, a comment next to the longitude-width term can say `# Longitude spacing is in degrees; the spherical area formula uses radians.` Notebook Markdown should identify the input layer, date, unit and meaning of each plotted result. Follow the [map specifications](docs/geography.md) for captions and legends.
