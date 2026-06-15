# skill-truth-check - Launch Index

v0.1.0 scaffold, not yet pushed to GitHub. Run the pre-launch gate in `~/Desktop/skill-truth-check/LAUNCH-CHECKLIST.md` first (publish + PyPI). Then fire these in order.

## Pre-launch gate (Alex must run)

- [ ] `gh repo create alex-jb/skill-truth-check --public --source=. --push` (see LAUNCH-CHECKLIST.md)
- [ ] Push first, confirm `test.yml` workflow green (20/20 tests pass).
- [ ] Run `brier audit-skill` against ~5-10 real skills.sh entries, paste a real calibration table into `examples/real-corpus-2026-06-14.md` so HN body links to one real run, not just mocks.
- [ ] Decide whether v0.1.0 PyPI tag fires before or after HN. (PyPI install line in HN body assumes fired.)
- [ ] Confirm X handle in `x-thread.md` matches Alex's account; add real screenshot of `brier audit-skill` output to tweet 4 if attaching media.

## Firing order (24h staggered, per council-diff v0.4.0 pattern)

| Order | Channel | File | When | Notes |
|---|---|---|---|---|
| 1 | Hacker News Show HN | `hn-show.md` | Tue / Wed 9-10am ET | Title locked at submission, HN punishes edits |
| 2 | r/ClaudeAI | `reddit-claude.md` | HN + 4h | Tag [Tool], casual tone |
| 3 | r/LangChain | `reddit-langchain.md` | HN + 8h | Frame as cross-framework (skills + LangChain tool docstrings) |
| 4 | X thread | `x-thread.md` | HN + 12h | 5 tweets, tag @AnthropicAI in tweet 5 |
| 5 | LinkedIn EN | `linkedin-en.md` | HN + 24h | "I built X, here's why" framing |
| 6 | dev.to article | `devto-article.md` | HN + 48h | Skeleton only, flesh out before posting |
| 7 | LinkedIn ZH | `linkedin-zh.md` | LinkedIn EN + 24h | 中文版,语气更 terse |
| 8 | awesome-list PRs | (not yet drafted) | LinkedIn ZH + 24h | `awesome-claude-code`, `awesome-llm-apps` |

## Anti-spam rules (per council-diff playbook)

- Do NOT cross-post to all channels in the same 4h window.
- Do NOT delete + repost on HN if the first attempt dies. Pattern-flagged.
- Do NOT push v0.1.0 to PyPI without first running against real corpus (HN crowd will check). Mocks-only is fine for a tag, but the README's "untested against real skills.sh corpus" line must remain honest.

## HN rebuttal cheat sheet

Likely pushback and the 1-sentence reply:

| Rebuttal | Reply |
|---|---|
| "This is just an LLM judging an LLM, scores are noisy." | Yes, that is why the Brier step is deterministic and the README tells you to use -n 10 for sensitive calls. Aggregate N>=30 per source to dampen noise. |
| "Why not use Snyk?" | Snyk audits whether a skill is malicious. This audits whether a skill is honest. Both are needed, the two surfaces are orthogonal. |
| "v0.1.0 untested against real corpus, useless." | Fair. The README is honest about that. Real corpus pass is the next ship. The math + pipeline are testable today on examples/sample-skill. |
| "Why not just read the SKILL.md?" | Because at 669K skills nobody will. The point is a reproducible Brier audit anyone can run + verify, not a manual code review. |

## Risk notes

- If Karpathy or Anthropic engages, traffic spike. Repo has no DB, GitHub Pages, no risk.
- Reddit may flag as self-promo. Disclose authorship plainly in the comments.
- If real-corpus run shows poor calibration on the first 5 skills, hold the launch and tune synth / judge prompts first. Honest > on-schedule.
