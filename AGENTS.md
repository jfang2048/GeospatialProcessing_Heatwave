# Working on Heatwave

| Owner | Module | Topic branch |
| --- | --- | --- |
| FJ | `src/heatwave/ingest/` | `ingest/<task>` |
| YY | `src/heatwave/events/` | `events/<task>` |
| FY | `src/heatwave/footprints/` | `footprints/<task>` |

Keep module code, tests and docs with the owner. FJ maintains shared files and dependencies. Agree on file-format changes with both the writer and the reader, then update the [file guide](docs/v1.md).

Start from current `main` and make one PR per task. Each member commits and pushes their own work. Give reviewers the input files, the command you ran and the result. Explain scientific choices in English code comments and docstrings. Keep each stage's paths explicit and give new runs their own directories. [Test commands](docs/workflow.md#tests)

## Local releases

For FJ's checkout, work and test on local `dev`. Commit each related batch, check what will go public, merge into local `main`, and push `origin main`. Verify the remote commit, then switch back to `dev`.

## Public repository checklist

Use team initials in public files, commits and discussions. Configure your own initials and placeholder email in each clone. Here is FJ's setup.

```bash
git config --local user.name FJ
git config --local user.email fj@project.invalid
```

Keep full names, personal addresses and paths, CDS credentials, private links, raw downloads and run outputs in local or team storage. Use the team folder for the two input NetCDFs and `reports/` for executed notebooks. Cite data sources in public examples.

```bash
git fetch origin
python .github/scripts/check_publication.py origin/main HEAD
git log --no-use-mailmap --format=fuller --stat -m -p origin/main..HEAD
```

Review each outgoing commit, including author and committer identities, notebook metadata and changed binary files. Apply the same check to every branch or tag you publish. Correct findings before pushing. For private information already on GitHub, notify the team privately and rotate any exposed credentials.
