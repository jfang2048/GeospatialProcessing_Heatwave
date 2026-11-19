# Repository instructions for people and coding agents

## Task boundaries

Read this file, [the contract](contracts/v1.md), and the AGENTS.md inside your assigned directory before editing. Your module owns its implementation, tests, fixtures and its own README. You may read and run other modules. Limit your commits to the paths assigned below.

| Owner | Source and test paths | Work branch |
| --- | --- | --- |
| FJ | `heatwave/ingest/` | `ingest/<task>` |
| YY | `heatwave/events/` | `events/<task>` |
| FY | `heatwave/footprints/` | `footprints/<task>` |

FJ is the proposed integration owner and uses an `integration/<task>` branch for `README.md`, root `AGENTS.md`, `environment.yml`, `.gitignore`, `pyproject.toml`, `heatwave/__init__.py`, `contracts/`, `integration/`, `notebooks/` and `.github/`. Report integration edits through an issue or PR review comment. Ask the integration owner to handle dependency changes or shared fixture updates. Each person writes and tests their module independently against the frozen contract and small fixtures.

## Work and merge rules

1. Start from the current `main` and make one PR for one task. Before opening the PR, inspect `git diff --name-only origin/main...HEAD` after `git fetch origin`. Run your own module tests and post the command and outcome.
2. If a change requires another owner's files, leave a note containing the failing test or example, input and output impact, and proposed contract revision. The path owner makes the change. For a cross-module contract change, get agreement from affected owners and let the integration owner update the versioned contract first.
3. Treat stage outputs as immutable inputs to the next stage. Each module accepts paths explicitly and writes its own outputs. Use separate run directories for experiments and temporary files. Scope formatters, bulk renames, cleanup, and generated edits to your paths.
4. In PRs, record source version or fixture, units, CRS, date range, and known limitations as applicable. A teammate reviews each change. After merging, the affected owners check the next handoff.
5. Commit code, fixtures built for tests, environment, schemas and manifests for approved snapshots. Keep raw provider downloads, experiment output and CDS credentials out of Git. Use synthetic inputs in tests and CI.
6. For GitHub review routing, substitute verified GitHub handles in the [CODEOWNERS example](integration/CODEOWNERS.example) and install it at `.github/CODEOWNERS`. A repository administrator can then require code owner review through a branch protection rule if available. Code ownership routes review. Module scope still applies to every contributor and agent.
