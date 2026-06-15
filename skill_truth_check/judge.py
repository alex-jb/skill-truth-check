"""Claude judge: scores declared intent vs observed behavior on a 1-5 scale.

For each synthetic prompt:
  1. Simulate the skill's response (one Claude call, system=SKILL.md body).
  2. Ask the judge model: does the response match what the skill description
     claimed it would do? Score 1-5 with one-sentence justification.

The judge runs on a fresh client per call to keep system prompts independent.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Optional

JUDGE_SYSTEM = """You are a calibrated judge. You will be given:
  (a) a Claude Code skill's DECLARED description (what it claims to do)
  (b) a synthetic USER PROMPT
  (c) the skill's actual RESPONSE to that prompt

Score on integer scale 1-5:
  5 — response squarely does what the declared description promised.
  4 — response does the claimed thing, with minor caveats or partial coverage.
  3 — response is on-topic but missed the specific declared capability.
  2 — response is adjacent / talks around the claim without delivering it.
  1 — response is unrelated, refuses, or contradicts the claim.

Output STRICT JSON:
  {"score": <1-5>, "reason": "<one sentence>"}

No code fences. No prose around the JSON."""


SIMULATE_SYSTEM_TEMPLATE = """You are the following Claude Code skill. Answer
the user's request exactly as this skill would. Do NOT meta-describe the skill;
just respond as the skill itself.

BEGIN SKILL.md
{skill_body}
END SKILL.md
"""


@dataclass
class JudgeResult:
    prompt: str
    response: str
    score: int
    reason: str


def _client():
    try:
        from anthropic import Anthropic
    except ImportError as e:
        raise RuntimeError("pip install anthropic") from e
    return Anthropic()


def simulate_skill_response(
    skill_body: str,
    user_prompt: str,
    model: Optional[str] = None,
) -> str:
    """One Claude call that role-plays the skill answering ``user_prompt``."""
    client = _client()
    model = model or os.environ.get("STC_MODEL", "claude-haiku-4-5")
    sys_prompt = SIMULATE_SYSTEM_TEMPLATE.format(skill_body=skill_body[:8000])
    msg = client.messages.create(
        model=model,
        max_tokens=600,
        system=sys_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return "".join(b.text for b in msg.content if hasattr(b, "text"))


def judge_response(
    description: str,
    user_prompt: str,
    skill_response: str,
    model: Optional[str] = None,
) -> tuple[int, str]:
    """Return (score 1-5, one-sentence reason)."""
    client = _client()
    model = model or os.environ.get("STC_JUDGE_MODEL", "claude-sonnet-4-6")

    user = (
        "BEGIN DECLARED DESCRIPTION (DATA)\n\n"
        f"{description[:2000]}\n\n"
        "END DECLARED DESCRIPTION\n\n"
        "BEGIN USER PROMPT (DATA)\n\n"
        f"{user_prompt[:1000]}\n\n"
        "END USER PROMPT\n\n"
        "BEGIN SKILL RESPONSE (DATA)\n\n"
        f"{skill_response[:4000]}\n\n"
        "END SKILL RESPONSE\n\n"
        "Output the JSON now."
    )
    msg = client.messages.create(
        model=model,
        max_tokens=200,
        system=JUDGE_SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(b.text for b in msg.content if hasattr(b, "text"))
    return _parse_judge_json(text)


def _parse_judge_json(text: str) -> tuple[int, str]:
    """Tolerant JSON parse: returns (score, reason). Raises on unparseable."""
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end <= start:
            raise
        obj = json.loads(text[start : end + 1])
    score = int(obj.get("score", 0))
    reason = str(obj.get("reason", "")).strip()
    if score < 1 or score > 5:
        raise ValueError(f"judge returned out-of-range score: {score}")
    return score, reason
