"""skill-truth-check — core audit pipeline.

Flow:
  1. parse_skill_md(text) -> SkillSpec
  2. generate_prompts(name, description, n) -> list[str]
  3. for each prompt:
       response = simulate_skill_response(body, prompt)
       score, reason = judge_response(description, prompt, response)
  4. brier = aggregate_brier(scores); verdict = verdict(brier)
  5. emit JSON report + 1-line CLI summary

Persisted to ~/.stc/audits.jsonl, append-only, JSONL shape that other agents
(sfos-eval, polymarket-brier) can consume.
"""
from __future__ import annotations

import json
import os
import pathlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Callable, Optional

from .brier import aggregate_brier, verdict
from .judge import JudgeResult, judge_response, simulate_skill_response
from .parse import SkillSpec, find_skill_md, parse_skill_md
from .synthetic import generate_prompts

HOME = pathlib.Path(os.environ.get("STC_HOME", str(pathlib.Path.home() / ".stc")))
AUDITS = HOME / "audits.jsonl"


@dataclass
class AuditReport:
    """JSON-serializable audit report."""

    ts: str
    skill_name: str
    skill_description: str
    skill_source: str
    n_prompts: int
    model_synthesizer: str
    model_simulator: str
    model_judge: str
    brier: float
    verdict: str
    results: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def summary_line(self) -> str:
        """One-line CLI summary: `[name] brier=0.34 verdict=mostly-truthful`."""
        return f"[{self.skill_name}] brier={self.brier:.2f} verdict={self.verdict}"


def _ensure_dir() -> None:
    HOME.mkdir(parents=True, exist_ok=True)


def _persist(report: AuditReport) -> None:
    _ensure_dir()
    with AUDITS.open("a") as f:
        f.write(json.dumps(report.to_dict()) + "\n")


def audit_skill(
    source: str | pathlib.Path,
    n_prompts: int = 5,
    *,
    persist: bool = True,
    synth_fn: Optional[Callable[[str, str, int], list[str]]] = None,
    sim_fn: Optional[Callable[[str, str], str]] = None,
    judge_fn: Optional[Callable[[str, str, str], tuple[int, str]]] = None,
) -> AuditReport:
    """Run the full audit pipeline on a local SKILL.md (file or repo dir).

    The three model-calling functions are injectable so tests can run
    end-to-end without hitting the Anthropic API.
    """
    skill_path = find_skill_md(source)
    spec: SkillSpec = parse_skill_md(skill_path.read_text(encoding="utf-8"))

    # default plumbing (real Claude calls)
    if synth_fn is None:
        synth_fn = lambda name, desc, n: generate_prompts(name, desc, n)  # noqa: E731
    if sim_fn is None:
        sim_fn = lambda body, prompt: simulate_skill_response(body, prompt)  # noqa: E731
    if judge_fn is None:
        judge_fn = lambda desc, prompt, resp: judge_response(desc, prompt, resp)  # noqa: E731

    prompts = synth_fn(spec.name, spec.description, n_prompts)
    if not prompts:
        raise RuntimeError("synthesizer returned no prompts — refusing to score")

    results: list[JudgeResult] = []
    for prompt in prompts:
        response = sim_fn(spec.body, prompt)
        score, reason = judge_fn(spec.description, prompt, response)
        results.append(JudgeResult(prompt=prompt, response=response, score=score, reason=reason))

    brier = aggregate_brier(r.score for r in results)
    v = verdict(brier)

    report = AuditReport(
        ts=datetime.now(timezone.utc).isoformat(),
        skill_name=spec.name,
        skill_description=spec.description,
        skill_source=str(skill_path),
        n_prompts=len(results),
        model_synthesizer=os.environ.get("STC_MODEL", "claude-haiku-4-5"),
        model_simulator=os.environ.get("STC_MODEL", "claude-haiku-4-5"),
        model_judge=os.environ.get("STC_JUDGE_MODEL", "claude-sonnet-4-6"),
        brier=brier,
        verdict=v,
        results=[asdict(r) for r in results],
    )
    if persist:
        _persist(report)
    return report


def read_audits() -> list[dict]:
    """Read the persisted audit ledger (JSONL append-only)."""
    if not AUDITS.exists():
        return []
    out = []
    with AUDITS.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out
