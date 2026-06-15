# r/LangChain - skill-truth-check

**Title:**
[Tool] Brier-style helpfulness audit for agent skills, closes the docs vs behavior gap

**Body:**

A small Python tool that audits whether a skill (Anthropic SKILL.md / agent prompt manifest) actually does what its description claims.

The motivating problem is shared across LangChain agents too: a tool / skill / chain has a docstring or schema that says "answers Q about X with criterion Y," but at runtime it sometimes wanders off, returns partial answers, or drifts into adjacent topics. Three audits in the last 6 weeks flagged this (Trail of Bits 6/3, Snyk ToxicSkills, SkillScan), all noting that **scanners cannot verify whether the documentation faithfully represents the executable behavior**.

skill-truth-check tries to close that gap:

- Reads the declared description.
- Synthesizes 5-10 user prompts (1 Haiku call).
- Simulates the skill answering them (N Haiku calls).
- Judges 1-5 whether the response matches the description (N Sonnet calls).
- Maps to a deterministic Brier score (0 perfect, 1 worst, 0.25 random).

Output bucket: truthful / mostly / partially / unreliable.

The Brier step is reproducible. Once per-prompt scores are persisted, anyone can recompute. That's the property that lets multiple auditors compare results without re-running every API call.

Adapting it for LangChain `Tool` docstrings or chain prompts is straightforward (parse description, swap the simulator), happy to help if anyone wants to fork.

v0.1.0, 20 tests pass, not yet validated against the real skills.sh corpus.

MIT, stdlib + anthropic. https://github.com/alex-jb/skill-truth-check

Open to feedback on the synth / judge prompt design.
