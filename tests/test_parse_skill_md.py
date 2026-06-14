"""Tests for skill_truth_check.parse."""
from __future__ import annotations

import pathlib

import pytest

from skill_truth_check.parse import SkillParseError, find_skill_md, parse_skill_md


VALID = """---
name: example-skill
description: An example skill that does X when invoked with Y.
license: MIT
---

# example-skill

Body text.
"""


def test_parse_skill_md_extracts_name_and_description():
    spec = parse_skill_md(VALID)
    assert spec.name == "example-skill"
    assert spec.description == "An example skill that does X when invoked with Y."
    assert spec.extra.get("license") == "MIT"
    assert "Body text." in spec.body


def test_parse_skill_md_raises_on_missing_frontmatter():
    with pytest.raises(SkillParseError):
        parse_skill_md("# no frontmatter here\n")


def test_parse_skill_md_raises_on_missing_required_keys():
    with pytest.raises(SkillParseError):
        parse_skill_md("---\nname: foo\n---\nhi\n")
    with pytest.raises(SkillParseError):
        parse_skill_md("---\ndescription: hi\n---\nhi\n")


def test_parse_skill_md_tolerates_nested_metadata_block():
    text = """---
name: foo
description: bar
metadata:
  version: "0.1.0"
  author: alex
---

body
"""
    spec = parse_skill_md(text)
    assert spec.name == "foo"
    assert spec.description == "bar"


def test_find_skill_md_resolves_file_and_directory(tmp_path: pathlib.Path):
    skill = tmp_path / "SKILL.md"
    skill.write_text(VALID, encoding="utf-8")
    # file path returns itself
    assert find_skill_md(skill) == skill
    # directory finds the root SKILL.md
    assert find_skill_md(tmp_path) == skill


def test_find_skill_md_raises_when_absent(tmp_path: pathlib.Path):
    with pytest.raises(FileNotFoundError):
        find_skill_md(tmp_path)
