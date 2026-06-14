# skill-truth-check — Launch Checklist

v0.1.0 scaffold landed locally on 2026-06-14. This file tracks what's
left to publish and promote. Alex's punch list.

---

## (a) Publish to GitHub

Repo does NOT exist on GitHub yet. From `~/Desktop/skill-truth-check/`:

```bash
gh repo create alex-jb/skill-truth-check --public --source=. --push \
    --description "Brier-style helpfulness audit for SKILL.md files — does the skill do what it claims?"
```

Then verify:

```bash
gh repo view alex-jb/skill-truth-check --web
```

After push, the `test.yml` workflow fires on `main`. Confirm green:

```bash
gh run list --repo alex-jb/skill-truth-check --limit 5
```

## (b) Publish to PyPI via Trusted Publisher

Per `~/Desktop/Interview-Prep/Projects/alex-brain/research/2026-04-30-pypi-release-howto.md`:

1. **One-time TP setup** at https://pypi.org/manage/account/publishing/ →
   "Add a new pending publisher":

   | Field | Value |
   |---|---|
   | PyPI Project Name | `skill-truth-check` |
   | Owner | `alex-jb` |
   | Repository name | `skill-truth-check` |
   | Workflow filename | `release.yml` |
   | Environment name | (leave blank) |

   ⚠️ PyPI limits 3 pending TP setups at a time. As of 2026-05-08 Alex has
   5/11 agents published — check current pending count first. See
   `~/.claude/projects/-Users-alexji-Desktop-vibex/memory/reminder_pypi_pending_continue.md`.

2. **Tag + push** to trigger the release workflow:

   ```bash
   cd ~/Desktop/skill-truth-check
   git tag v0.1.0
   git push --tags
   gh release create v0.1.0 --title "v0.1.0 — initial scaffold" --notes "
   - brier audit-skill <repo-url-or-path> end-to-end pipeline.
   - brier digest for the persisted audit ledger.
   - Stdlib + anthropic only.
   - 20 pytest tests green (no API calls; synth/sim/judge are injectable).
   - v0.1.0 is UNTESTED against real skills.sh corpus yet.
   "
   ```

3. **Verify** the workflow uploaded the sdist+wheel:

   ```bash
   gh run list --repo alex-jb/skill-truth-check --workflow=release.yml --limit 3
   pip index versions skill-truth-check
   ```

## (c) Launch posts (per Alex's promote-every-repo rule)

Per `~/.claude/projects/-Users-alexji-Desktop-vibex/memory/feedback_promote_every_new_repo.md` — draft 4-6 channels into `launch/` BEFORE asking:

- `launch/01-hn-show.md` — Show HN: skill-truth-check — Brier-style helpfulness audit for the 669K SKILL.md skills on skills.sh (hook: Trail of Bits + Snyk + SkillScan all flagged 13-26% security issues last 2 weeks, but none audit helpfulness)
- `launch/02-reddit-claudeai.md` — r/ClaudeAI cross-post focused on the calibration ledger angle
- `launch/03-reddit-skills-or-langchain.md` — r/LangChain or r/LocalLLaMA (depending on which has higher recent skill-related engagement)
- `launch/04-x-thread.md` — 5-tweet thread:
  (1) hook with Trail of Bits / Snyk audit stats
  (2) one-liner: Snyk audits malice; we audit honesty
  (3) Brier table screenshot
  (4) pair with polymarket-brier-skill
  (5) `npx skills i alex-jb/skill-truth-check` + repo URL
- `launch/05-linkedin.md` — agentic-engineering Karpathy frame ("AI automates what you can verify")
- `launch/06-devto.md` — long-form: 30-day skills.sh growth, why helpfulness ≠ security, how Brier closes the loop
- `launch/07-awesome-claude-pr.md` — PR body to add to `awesome-claude-code` list

Use `~/Desktop/marketing-agent/marketing_agent/viral_patterns.py` helpers
(negative_space / recruit_invite / wave_borrow / humanizer_zh / lint_draft) —
do NOT rewrite from scratch.

Distribution surfaces (per 2026-06-12 5-channel strategy):
- PyPI (lib install)
- GitHub (source)
- **skills.sh** — register via `npx skills login && npx skills publish .`
  after the repo is public
- npm (n/a — Python only)
- VibeXForge.com (dogfood project — submit per `vibex_side_projects_rule.md`)

## Known open questions (Alex input needed)

1. **Skill registration on skills.sh** — does `npx skills publish` require a
   SKILL.md at root only, or specific package metadata? Confirm before tagging
   v0.1.0 so the PyPI release matches the skills.sh manifest.
2. **Real-corpus validation** — before HN launch, run `brier audit-skill` on
   ~10 known-good skills (anthropic's own `frontend-design`, vercel-labs
   `find-skills`, polymarket-brier-skill itself) and pin the digest output to
   `examples/real-corpus-2026-06-14.md`. v0.1.0 README is honest about being
   un-validated, but a HN launch should ship with at least one calibration
   table from a real run.
3. **Judge model pin** — current default `claude-sonnet-4-6`. Decide whether
   to also support `claude-opus-4-7` for high-stakes audits (more expensive
   but tighter calibration). Default stays Sonnet for v0.1.0.
