# LinkedIn - English

I built skill-truth-check, a Brier-style helpfulness audit for SKILL.md files. Here is why.

Three independent audits landed in the past 6 weeks. Trail of Bits published its supply-chain analysis on June 3. Snyk's ToxicSkills paper found 13.4% of scanned skills had critical security issues. SkillScan, an academic paper out earlier this year, found 26.1% had vulnerabilities. Every one of them flags the same blind spot in plain language:

*Scanning systems cannot verify whether a skill's natural-language documentation faithfully represents its actual executable behavior.*

That is the helpfulness gap, not the security gap. Snyk and Trail of Bits cover malice. Nobody covers honesty. With around 669K skills published to skills.sh and zero curation, the gap is real.

skill-truth-check is the smallest tool I could write that fills it:

1. Parse `name` + `description` from the SKILL.md YAML frontmatter.
2. Generate 5 to 10 synthetic user prompts that target the declared capability.
3. Simulate the skill answering each prompt.
4. Ask a Claude judge to score 1 to 5 whether the response actually matches the declared description.
5. Map per-prompt scores to a deterministic Brier score plus a verdict bucket: truthful, mostly, partially, unreliable.

The Brier step is reproducible. Persist the per-prompt scores once, and any reviewer can recompute the verdict without re-running the API calls. That is the property Snyk's audit format does not have.

It is v0.1.0. Twenty pytest tests pass. The pipeline has not yet been run against the real skills.sh corpus. Single audits should be treated as directional until at least 30 accumulate per source. The README is honest about all of this.

Maps onto Karpathy's Software 3.0 framing from his Sequoia talk: synthesizer is the spec, simulator is the behavior, judge plus Brier is the verification loop. Without the verification loop, the 669K skills on skills.sh are unverified AI artifacts.

MIT, Python, stdlib plus the Anthropic SDK only.

https://github.com/alex-jb/skill-truth-check
