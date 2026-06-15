# X thread - skill-truth-check

**1/5 (hook, <120 chars):**

Snyk audits if a skill is malicious.
skill-truth-check audits if a skill actually does what it claims.

🔗 github.com/alex-jb/skill-truth-check

---

**2/5:**

Last 2 weeks:

- Trail of Bits skills audit (6/3)
- Snyk ToxicSkills: 13.4% of skills had critical issues
- SkillScan academic paper: 26.1% had vulnerabilities

Every paper notes the same gap: scanners can detect malice. None verify whether the description matches the behavior.

---

**3/5:**

Pipeline:

1. Parse name + description from SKILL.md
2. Synth 5-10 user prompts that target the declared capability (Haiku)
3. Simulate the skill answering each one (Haiku)
4. Judge 1-5 whether response matched the description (Sonnet 4.6)
5. Brier score (deterministic, reproducible)

Output: truthful / mostly / partially / unreliable.

---

**4/5:**

```
$ brier audit-skill ./examples/sample-skill
[example-skill] brier=0.10 verdict=truthful

$ brier audit-skill <repo-url> -n 10
[other-skill] brier=0.42 verdict=partially-truthful
```

The Brier step is deterministic. Persist the per-prompt scores once. Anyone can recompute. That is the part Snyk does not have.

---

**5/5:**

Pairs naturally with polymarket-brier-skill: same Brier pattern, applied to forecasts instead of skill docs.

v0.1.0, Python, stdlib + anthropic, MIT. 20 tests pass. Not yet run against the real skills.sh corpus, landing that next.

cc @AnthropicAI

🔗 github.com/alex-jb/skill-truth-check
