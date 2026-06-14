# Changelog

All notable changes to skill-truth-check are documented here.

## v0.1.0 — 2026-06-14

Initial scaffold.

- `brier audit-skill <repo-url-or-path>` — full pipeline: parse SKILL.md →
  synthesize N prompts → simulate skill → Claude judge → Brier score.
- `brier digest` — markdown summary of the persisted audit ledger.
- Stdlib + `anthropic` only.
- 6+ pytest tests, all running without hitting the Anthropic API
  (synth/sim/judge are injectable callables).
- v0.1.0 is **untested against the real skills.sh corpus yet** — pipeline
  runs end-to-end with mocks; production validation pending.
