"""SKILL.md parser.

SKILL.md spec (Anthropic Agent Skills open standard, 2025-12-18):
- YAML frontmatter delimited by `---` lines at top of file.
- Required keys: `name`, `description`.
- Optional keys: `license`, `allowed-tools`, `metadata`, etc.

We parse with a minimal stdlib loop instead of pulling PyYAML — frontmatter
in the wild is shallow key:value plus the occasional nested `metadata:` block,
and we only need `name` + `description` for the audit. This keeps the
install footprint to `anthropic` only.
"""
from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass, field

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


@dataclass
class SkillSpec:
    """Parsed SKILL.md."""

    name: str
    description: str
    body: str
    raw_frontmatter: str
    extra: dict[str, str] = field(default_factory=dict)


class SkillParseError(ValueError):
    """Raised when SKILL.md is missing required fields or malformed."""


def parse_skill_md(text: str) -> SkillSpec:
    """Parse a SKILL.md string. Raises SkillParseError on missing required fields.

    >>> spec = parse_skill_md('---\\nname: foo\\ndescription: bar\\n---\\nhi')
    >>> spec.name, spec.description, spec.body.strip()
    ('foo', 'bar', 'hi')
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise SkillParseError("missing YAML frontmatter (expected leading `---` block)")

    fm = m.group(1)
    body = text[m.end():]

    fields: dict[str, str] = {}
    # Walk lines; capture top-level `key: value` pairs. Nested blocks are skipped
    # but their top-level key still records (with empty string) so we can detect
    # `metadata:` presence without parsing the subtree.
    for line in fm.splitlines():
        if not line.strip():
            continue
        # nested entry (starts with whitespace)?
        if line.startswith((" ", "\t")):
            continue
        # top-level key
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            # strip surrounding quotes if any
            if value.startswith(("\"", "'")) and value.endswith(value[0]) and len(value) >= 2:
                value = value[1:-1]
            fields[key] = value
    # required
    if "name" not in fields or not fields["name"]:
        raise SkillParseError("SKILL.md frontmatter missing required `name`")
    if "description" not in fields or not fields["description"]:
        raise SkillParseError("SKILL.md frontmatter missing required `description`")

    extra = {k: v for k, v in fields.items() if k not in ("name", "description")}
    return SkillSpec(
        name=fields["name"],
        description=fields["description"],
        body=body,
        raw_frontmatter=fm,
        extra=extra,
    )


def find_skill_md(path: str | pathlib.Path) -> pathlib.Path:
    """Resolve a path (file or repo dir) to its SKILL.md.

    - If `path` is a file, return it as-is.
    - If `path` is a directory, look for SKILL.md at the root, then a single
      nested `**/SKILL.md` if there's exactly one.
    """
    p = pathlib.Path(path).expanduser()
    if not p.exists():
        raise FileNotFoundError(p)
    if p.is_file():
        return p
    root_candidate = p / "SKILL.md"
    if root_candidate.exists():
        return root_candidate
    matches = list(p.rglob("SKILL.md"))
    if len(matches) == 1:
        return matches[0]
    if len(matches) == 0:
        raise FileNotFoundError(f"no SKILL.md found under {p}")
    raise FileNotFoundError(
        f"multiple SKILL.md found under {p} — pass the explicit path: "
        + ", ".join(str(m.relative_to(p)) for m in matches)
    )
