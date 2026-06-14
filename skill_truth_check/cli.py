"""skill-truth-check CLI.

Subcommands:
    brier audit-skill <path-or-url> [-n 5] [--json] [--quiet]
    brier digest [--top 5]

Console entry point: ``brier`` (see pyproject.toml).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import tempfile

from . import __version__


def _cmd_audit(args: argparse.Namespace) -> int:
    """Run the audit pipeline against a local path (or a cloned URL)."""
    from .audit import audit_skill  # local import: avoids heavy deps on `brier --help`

    source = args.source
    if source.startswith("http://") or source.startswith("https://") or source.startswith("git@"):
        cloned = _clone_repo(source)
        target: pathlib.Path = cloned
    else:
        target = pathlib.Path(source).expanduser()

    report = audit_skill(target, n_prompts=args.n)
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    elif not args.quiet:
        print(report.summary_line())
        for i, r in enumerate(report.results, 1):
            print(f"  prompt {i}: score={r['score']} — {r['reason']}")
    else:
        print(report.summary_line())
    return 0


def _cmd_digest(args: argparse.Namespace) -> int:
    from .digest import render_markdown

    print(render_markdown(top_n=args.top))
    return 0


def _clone_repo(url: str) -> pathlib.Path:
    """git-clone a remote URL into a tempdir and return the path. stdlib only."""
    import subprocess

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="stc-"))
    res = subprocess.run(
        ["git", "clone", "--depth", "1", url, str(tmp / "repo")],
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        raise RuntimeError(f"git clone failed: {res.stderr.strip()}")
    return tmp / "repo"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="brier",
        description="skill-truth-check — Brier-style helpfulness audit for SKILL.md files.",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    audit = sub.add_parser(
        "audit-skill",
        help="Audit a single SKILL.md (file path, repo dir, or git URL).",
    )
    audit.add_argument("source", help="Path to SKILL.md, repo dir, or git URL")
    audit.add_argument("-n", type=int, default=5, help="Synthetic prompts to run (default 5)")
    audit.add_argument("--json", action="store_true", help="Emit full JSON report to stdout")
    audit.add_argument("--quiet", action="store_true", help="Only print the one-line summary")
    audit.set_defaults(func=_cmd_audit)

    digest = sub.add_parser("digest", help="Render the persisted audit ledger.")
    digest.add_argument("--top", type=int, default=5, help="Top/bottom N skills (default 5)")
    digest.set_defaults(func=_cmd_digest)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
