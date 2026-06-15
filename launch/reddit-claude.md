# r/ClaudeAI - skill-truth-check

**Title:**
[Tool] skill-truth-check - Brier-audit for SKILL.md (does the skill actually do what it claims?)

**Flair:** Tool / Project

**Body:**

Built this last week after reading the Trail of Bits skills audit (June 3) and the Snyk ToxicSkills paper. Both flagged the same gap: scanners can tell you a skill is not malicious, but neither can tell you whether the natural-language description in SKILL.md actually matches how the skill behaves at runtime.

With ~669K skills on skills.sh and zero curation, drift between docs and behavior is the next problem.

skill-truth-check is a small Python CLI that:

1. Parses `name` + `description` out of a SKILL.md YAML frontmatter.
2. Generates 5-10 synthetic user prompts that target the declared capability (1 Haiku call).
3. Role-plays the skill answering each prompt (N Haiku calls).
4. Asks Sonnet 4.6 to score 1-5 whether the response actually matched the declared intent.
5. Returns a Brier-calibration score (deterministic, reproducible from the per-prompt scores) plus a verdict bucket: truthful / mostly / partially / unreliable.

```
$ brier audit-skill ./examples/sample-skill
[example-skill] brier=0.10 verdict=truthful

$ brier audit-skill https://github.com/owner/some-other-skill -n 10
[some-other-skill] brier=0.42 verdict=partially-truthful
```

The Brier step is deterministic. Once N per-prompt scores are in, anyone can recompute the verdict. That is the part Snyk audits do not have.

Honest about v0.1.0:
- 20 tests pass, but not yet run against the real skills.sh corpus. Single audits should be treated as directional until ~30 audits accumulate per source.
- N=5 is noisy. Use `-n 10` for sensitive calls.
- Not a security scanner. Use Snyk / Trail of Bits / SkillScan for malice detection. This is orthogonal.

MIT, Python, stdlib + anthropic. Repo: https://github.com/alex-jb/skill-truth-check

Curious what skills people would want audited first.
