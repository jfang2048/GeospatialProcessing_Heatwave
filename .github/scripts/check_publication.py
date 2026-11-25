"""Check local outgoing commit metadata and ignored paths before a public push."""

import argparse
import subprocess


TEAM_IDENTITIES = {
    ("FJ", "fj@project.invalid"),
    ("FY", "fy@project.invalid"),
    ("YY", "yy@project.invalid"),
}


def git(*args):
    return subprocess.check_output(["git", *args])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", nargs="?", default="origin/main")
    parser.add_argument("tip", nargs="?", default="HEAD")
    args = parser.parse_args()
    commits = git("rev-list", f"{args.base}..{args.tip}").decode("ascii").splitlines()
    problems = 0
    for commit in commits:
        fields = git("show", "-s", "--format=%an%x00%ae%x00%cn%x00%ce", commit)
        author, author_email, committer, committer_email = fields.rstrip(b"\n").decode(
            "utf-8", errors="replace"
        ).split("\0")
        for role, pair in (("author", (author, author_email)),
                           ("committer", (committer, committer_email))):
            if pair not in TEAM_IDENTITIES:
                print(f"{commit[:12]}: configure the {role} identity for this commit")
                problems += 1

        # A file removed on the tip can still be downloaded from an earlier commit.
        paths = git("ls-tree", "-rz", "--name-only", commit)
        ignored = subprocess.run(
            ["git", "check-ignore", "--no-index", "--stdin", "-z"],
            input=paths, stdout=subprocess.PIPE,
        )
        if ignored.returncode not in (0, 1):
            raise SystemExit(ignored.returncode)
        for path in ignored.stdout.split(b"\0"):
            if path:
                print(f"{commit[:12]}: tracked path matches an ignore rule: {path!r}")
                problems += 1

    print(f"Checked {len(commits)} outgoing commit(s), found {problems} issue(s).")
    return int(problems > 0)


if __name__ == "__main__":
    raise SystemExit(main())
