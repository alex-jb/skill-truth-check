# Show HN - skill-truth-check

**Title** (≤60 chars):
Show HN: skill-truth-check – does a skill do what it claims?

**URL:**
https://github.com/alex-jb/skill-truth-check

**Body (≤300 words):**

Snyk audits if a skill is malicious. We audit if a skill actually does what it claims.

Three things happened in the last 2 weeks:

1. Trail of Bits published its skills-supply-chain audit (2026-06-03).
2. Snyk's ToxicSkills paper found 13.4% of scanned skills had critical security issues.
3. SkillScan (academic, 2026-01-15) found 26.1% of skills had vulnerabilities.

Every paper notes the same gap: scanning tools can verify a skill is not malicious, but cannot verify a skill's declared behavior matches its actual behavior. With ~669K skills on skills.sh and zero curation, that gap is real.

skill-truth-check is a Brier-style helpfulness audit. It reads a SKILL.md, generates 5-10 synthetic prompts that target the declared description, simulates the skill answering each one, asks a Claude judge whether observed behavior matches declared intent, then returns a Brier-calibration score (0.0 perfect / 1.0 worst) plus a one-line verdict.

```
$ brier audit-skill ./examples/sample-skill
[example-skill] brier=0.10 verdict=truthful
```

How it differs from Snyk: orthogonal. They detect malice, this detects drift between docs and behavior. Both are needed.

Honest constraints, v0.1.0:
- 20 pytest tests pass, but the pipeline has NOT been run against the real skills.sh corpus yet.
- Brier on N=5 synthetic prompts is noisy. Run -n 10 for an honest verdict.
- Judge defaults to Sonnet 4.6. Pin STC_JUDGE_MODEL for reproducibility.
- Prompt-injection wrapped (SKILL.md descriptions are treated as data, not instructions).

Pairs with polymarket-brier-skill (same Brier pattern, different surface).

MIT, Python, stdlib + anthropic only. Feedback welcome on synth/judge prompt design.
