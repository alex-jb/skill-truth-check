---
name: sample-skill
description: A toy skill used by skill-truth-check's own tests and demos. Forecasts a binary outcome with a probability between 0 and 1 and returns a falsifiable resolution criterion in one sentence.
license: MIT
metadata:
  version: "0.1.0"
---

# sample-skill

Use this to forecast a binary outcome. Output JSON: `{"p": <float>,
"criterion": "<one sentence>"}`.

This file exists so `brier audit-skill ./examples/sample-skill` runs out of
the box.
