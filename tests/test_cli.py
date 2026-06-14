"""End-to-end CLI tests.

We inject fake synth / sim / judge callables so the audit pipeline can run
without hitting the Anthropic API. This is the same shape audit.audit_skill
uses for testability.
"""
from __future__ import annotations

import io
import json
import pathlib
import sys
from contextlib import redirect_stdout

import pytest

from skill_truth_check import audit as audit_mod
from skill_truth_check.audit import audit_skill
from skill_truth_check.cli import build_parser, main


SAMPLE_SKILL = """---
name: example-skill
description: Forecasts a Polymarket question with a probability and a falsifiable resolution criterion.
license: MIT
---

# example-skill

Use this to forecast binary questions.
"""


def _fake_synth(name, desc, n):
    return [f"prompt {i}" for i in range(n)]


def _fake_sim(body, prompt):
    return f"simulated response to: {prompt}"


def _fake_judge_all_fives(desc, prompt, response):
    return 5, "perfect"


def _fake_judge_mixed(desc, prompt, response):
    # alternate 5,3,5,3,5 → mean Brier = (0+0.25+0+0.25+0)/5 = 0.10
    if prompt.endswith(("1", "3")):
        return 3, "partial"
    return 5, "matches"


def test_audit_skill_end_to_end_perfect(tmp_path: pathlib.Path, monkeypatch):
    skill = tmp_path / "SKILL.md"
    skill.write_text(SAMPLE_SKILL, encoding="utf-8")
    # redirect persistence to tmp_path
    monkeypatch.setattr(audit_mod, "HOME", tmp_path)
    monkeypatch.setattr(audit_mod, "AUDITS", tmp_path / "audits.jsonl")

    report = audit_skill(
        skill,
        n_prompts=3,
        synth_fn=_fake_synth,
        sim_fn=_fake_sim,
        judge_fn=_fake_judge_all_fives,
    )
    assert report.skill_name == "example-skill"
    assert report.n_prompts == 3
    assert report.brier == 0.0
    assert report.verdict == "truthful"
    assert "brier=0.00" in report.summary_line()
    # ledger written
    assert (tmp_path / "audits.jsonl").exists()


def test_audit_skill_mixed_scores(tmp_path: pathlib.Path, monkeypatch):
    skill = tmp_path / "SKILL.md"
    skill.write_text(SAMPLE_SKILL, encoding="utf-8")
    monkeypatch.setattr(audit_mod, "HOME", tmp_path)
    monkeypatch.setattr(audit_mod, "AUDITS", tmp_path / "audits.jsonl")

    report = audit_skill(
        skill,
        n_prompts=5,
        synth_fn=_fake_synth,
        sim_fn=_fake_sim,
        judge_fn=_fake_judge_mixed,
    )
    # 5,3,5,3,5 -> brier = (0+0.25+0+0.25+0)/5 = 0.10
    assert abs(report.brier - 0.10) < 1e-9
    assert report.verdict == "truthful"  # boundary at 0.10 inclusive


def test_cli_parser_has_audit_and_digest_subcommands():
    parser = build_parser()
    args = parser.parse_args(["audit-skill", "/tmp/SKILL.md"])
    assert args.cmd == "audit-skill"
    assert args.source == "/tmp/SKILL.md"
    assert args.n == 5
    args2 = parser.parse_args(["digest", "--top", "3"])
    assert args2.cmd == "digest"
    assert args2.top == 3


def test_cli_version_flag(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "brier" in out


def test_cli_digest_empty_ledger(tmp_path: pathlib.Path, monkeypatch, capsys):
    monkeypatch.setattr(audit_mod, "HOME", tmp_path)
    monkeypatch.setattr(audit_mod, "AUDITS", tmp_path / "audits.jsonl")
    rc = main(["digest"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "No audits yet" in out
