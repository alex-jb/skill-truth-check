"""skill-truth-check — `brier digest` renderer.

1-page markdown showing the persisted audit ledger:
- Top truthful skills (lowest Brier)
- Bottom unreliable skills (highest Brier)
- Most-recently audited (last 5)
"""
from __future__ import annotations

from datetime import datetime, timezone

from .audit import read_audits


def render_markdown(top_n: int = 5) -> str:
    rows = read_audits()
    ts = datetime.now(timezone.utc).isoformat()
    parts = [
        "# skill-truth-check — digest",
        f"_{ts}_",
        "",
        f"## Audit ledger ({len(rows)} skill audits persisted)",
        "",
    ]
    if not rows:
        parts.append(
            "_No audits yet — run `brier audit-skill <repo-url-or-path>` first._"
        )
        return "\n".join(parts) + "\n"

    sorted_by_brier = sorted(rows, key=lambda r: r["brier"])
    parts += [
        f"## Most truthful (top {top_n})",
        "",
        "| skill | brier | verdict | n |",
        "|---|---|---|---|",
    ]
    for r in sorted_by_brier[:top_n]:
        parts.append(
            f"| `{r['skill_name']}` | {r['brier']:.2f} | {r['verdict']} | {r['n_prompts']} |"
        )

    parts += [
        "",
        f"## Least truthful (bottom {top_n})",
        "",
        "| skill | brier | verdict | n |",
        "|---|---|---|---|",
    ]
    for r in sorted_by_brier[-top_n:][::-1]:
        parts.append(
            f"| `{r['skill_name']}` | {r['brier']:.2f} | {r['verdict']} | {r['n_prompts']} |"
        )

    parts += [
        "",
        "## Most recent (last 5)",
        "",
        "| ts | skill | brier | verdict |",
        "|---|---|---|---|",
    ]
    for r in rows[-5:][::-1]:
        parts.append(
            f"| {r['ts'][:19]} | `{r['skill_name']}` | {r['brier']:.2f} | {r['verdict']} |"
        )

    return "\n".join(parts) + "\n"
