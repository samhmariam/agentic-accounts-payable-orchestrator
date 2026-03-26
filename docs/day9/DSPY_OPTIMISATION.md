# Day 9 DSPy Optimisation Guide

DSPy is optional in Day 9 and is not a hosted-runtime dependency by default.

## In Scope

- invoice field extraction or normalisation
- narrow classification prompts
- stable retrieval summary prompts

## Out of Scope

- compliance review
- refusal reasoning
- final recommendation prompts

Compiled prompt artifacts are treated like code: they are versioned, compared
against a baseline, and promoted only when slice metrics say the change is
safe.
