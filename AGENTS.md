# Contribution rules

Each owner maintains their module's code, tests, fixtures, and documentation. Use the [v1 contract](contracts/v1.md) for file handoffs and acceptance checks.

| Owner | Module | Branch | Starting point |
| --- | --- | --- | --- |
| FJ | `heatwave/ingest/` | `ingest/<task>` | [CDS pilot and snapshot guide](heatwave/ingest/README.md) |
| YY | `heatwave/events/` | `events/<task>` | [Baseline and target fixtures](integration/fixtures/README.md) |
| FY | `heatwave/footprints/` | `footprints/<task>` | [Events fixture](integration/fixtures/README.md) |

FJ owns shared files and dependencies on `integration/<task>` branches. Use issues or PR reviews to request shared changes. For a handoff change, include a failing example, affected inputs and outputs, and the proposed contract revision. The integration owner versions the contract after the affected owners agree.

A module PR may change only files under its owner's module directory. FJ uses a separate integration PR for root files, dependencies, `contracts/`, `integration/`, and `notebooks/`. Shared fixtures and expected results belong to integration. Before review, run `git fetch origin` and inspect `git diff --name-status origin/main...HEAD`, including both paths of renames. Route any out-of-scope edit to its owner.

## Module acceptance

- Give the stage a callable Python interface with explicit paths and parameters. Keep argument parsing, file I/O and scientific rules separate enough to test each rule on a small array. Exchange versioned files across modules. Keep imports and tests independent of sibling modules' private functions.
- Validate the [file contract](contracts/v1.md) on entry and before publishing output. Treat inputs as read-only. Close files on success and failure. Process the full case within a documented memory budget, carrying the necessary time window or spatial context across chunk boundaries if processing in chunks.
- Exercise the public CLI in a temporary run directory. Cover a valid input, a scientific boundary, a malformed input, and a failed write followed by a retry. Check exit status, diagnostics, output values and input integrity. Use fixed offline fixtures and independent expected values.
- Include reproduction commands and test results in the PR. A teammate checks ownership, file compatibility and the error path. For a bug fix, add a case that fails on the old behavior. Record any new dependency in a separate integration change with its purpose and supported version.

## Public repository checklist

Use team initials `FJ`, `FY` or `YY` in files, notebooks, commit messages, Git identities, and GitHub discussions. Keep member full names, personal email addresses, personal filesystem paths, credentials, private links, raw provider downloads, and run artifacts in local or approved private storage. Publish synthetic fixtures and sanitized manifests. Share private snapshot links through the team's private channel.

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
git log --no-use-mailmap --format=fuller --stat -m -p origin/main..HEAD
```

- Review each ref separately when pushing multiple branches or tags. Check author and committer names and emails in each commit. Check commit messages, filenames and diffs for private information, including lines removed in later commits. Open changed binary files and inspect their metadata. Review notebook cells, outputs and metadata.
- Fix the commit that contains a finding and rerun the checks before pushing. If private information has already reached GitHub, notify the team privately and rotate any exposed credentials. Coordinate history cleanup with the integration owner.

## Work and merge rules

1. Start each task from current `main` and open one PR. Run your module tests and include the command and result. Use synthetic inputs in tests and CI.
2. Treat stage outputs as immutable inputs to the next module. Pass paths explicitly and use separate run directories. Keep edits within your owned paths.
3. Record the source version or fixture, units, CRS, date range and limitations as applicable. A teammate reviews each PR. After merging, affected owners verify the next handoff.
