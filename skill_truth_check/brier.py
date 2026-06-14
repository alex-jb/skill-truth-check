"""Brier transformation for skill-truth-check.

Judge returns an integer 1-5 score per synthetic prompt (5 = perfect match
between declared intent and observed behavior, 1 = total mismatch). We
transform that into a per-prompt Brier-style probability error:

    truthfulness_p = (score - 1) / 4      # 1->0.0, 5->1.0
    target = 1.0                          # we want truthfulness=1.0
    per_prompt_brier = (truthfulness_p - target) ** 2

The overall Brier is the mean across N prompts. A score of 0.0 means every
synthetic call perfectly matched the declared description; 1.0 is worst.

Verdict thresholds (calibrated to be conservative — a v0.1.0 audit running
against a 5-prompt sample should not over-state confidence):

    [0.00, 0.10] truthful
    [0.10, 0.30] mostly-truthful
    [0.30, 0.55] partially-truthful
    [0.55, 1.00] unreliable
"""
from __future__ import annotations

from typing import Iterable


SCORE_MIN = 1
SCORE_MAX = 5


def score_to_truthfulness_p(score: int) -> float:
    """Map judge 1..5 integer score to a [0.0, 1.0] truthfulness probability."""
    if not isinstance(score, int) or score < SCORE_MIN or score > SCORE_MAX:
        raise ValueError(f"score must be int in [{SCORE_MIN},{SCORE_MAX}], got {score!r}")
    return (score - SCORE_MIN) / (SCORE_MAX - SCORE_MIN)


def per_prompt_brier(score: int) -> float:
    """Brier-style error for a single judge score. Target truthfulness=1.0."""
    p = score_to_truthfulness_p(score)
    return (p - 1.0) ** 2


def aggregate_brier(scores: Iterable[int]) -> float:
    """Mean per-prompt Brier across N synthetic prompts. Empty -> 1.0 (worst)."""
    scores = list(scores)
    if not scores:
        return 1.0
    return sum(per_prompt_brier(s) for s in scores) / len(scores)


def verdict(brier: float) -> str:
    """Map an aggregate Brier to one of four human-readable buckets."""
    if not 0.0 <= brier <= 1.0:
        raise ValueError(f"brier must be in [0,1], got {brier}")
    if brier <= 0.10:
        return "truthful"
    if brier <= 0.30:
        return "mostly-truthful"
    if brier <= 0.55:
        return "partially-truthful"
    return "unreliable"
