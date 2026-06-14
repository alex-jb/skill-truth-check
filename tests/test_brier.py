"""Tests for skill_truth_check.brier."""
from __future__ import annotations

import pytest

from skill_truth_check.brier import (
    aggregate_brier,
    per_prompt_brier,
    score_to_truthfulness_p,
    verdict,
)


def test_score_to_truthfulness_p_endpoints():
    assert score_to_truthfulness_p(1) == 0.0
    assert score_to_truthfulness_p(5) == 1.0
    assert score_to_truthfulness_p(3) == 0.5


def test_score_to_truthfulness_p_rejects_out_of_range():
    with pytest.raises(ValueError):
        score_to_truthfulness_p(0)
    with pytest.raises(ValueError):
        score_to_truthfulness_p(6)
    with pytest.raises(ValueError):
        score_to_truthfulness_p(3.5)  # type: ignore[arg-type]


def test_per_prompt_brier_endpoints():
    # score=5 → truthfulness=1.0 → brier=(1-1)²=0.0 (perfect)
    assert per_prompt_brier(5) == 0.0
    # score=1 → truthfulness=0.0 → brier=(0-1)²=1.0 (worst)
    assert per_prompt_brier(1) == 1.0
    # score=3 → truthfulness=0.5 → brier=(0.5-1)²=0.25
    assert per_prompt_brier(3) == 0.25


def test_aggregate_brier_perfect_run():
    # all 5s → 0.0
    assert aggregate_brier([5, 5, 5, 5, 5]) == 0.0


def test_aggregate_brier_worst_run():
    # all 1s → 1.0
    assert aggregate_brier([1, 1, 1]) == 1.0


def test_aggregate_brier_mixed():
    # [5, 3, 1] → [(0)² + (0.5)² + (1)²] / 3 = (0 + 0.25 + 1)/3
    expected = (0.0 + 0.25 + 1.0) / 3
    assert abs(aggregate_brier([5, 3, 1]) - expected) < 1e-9


def test_aggregate_brier_empty_returns_worst():
    assert aggregate_brier([]) == 1.0


def test_verdict_buckets():
    assert verdict(0.05) == "truthful"
    assert verdict(0.20) == "mostly-truthful"
    assert verdict(0.40) == "partially-truthful"
    assert verdict(0.80) == "unreliable"
    # bucket edges (inclusive on the upper end)
    assert verdict(0.10) == "truthful"
    assert verdict(0.30) == "mostly-truthful"
    assert verdict(0.55) == "partially-truthful"


def test_verdict_rejects_out_of_range():
    with pytest.raises(ValueError):
        verdict(-0.01)
    with pytest.raises(ValueError):
        verdict(1.01)
