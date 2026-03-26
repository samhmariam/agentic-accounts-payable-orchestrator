# Day 9 Semantic Cache Policy

Semantic cache is allowed only for low-risk, retrieval-grounded, versionable
answers.

## Cacheable

- stable retrieval-backed summaries
- repeated operator-help answers grounded in unchanged policy or vendor facts
- routine rendering where source scope is stable

## Never Cache

- compliance decisions
- contradiction resolution
- refusal reasoning
- approval recommendations
- fresh user-specific evidence without source/version scope

## Keying and Bypass

Cache keys incorporate tenant, `task_class`, `policy_version`, source snapshot
hash, and prompt hash. Cache is bypassed when evidence is stale, retrieval
confidence is low, conflict evidence exists, or the case carries high-risk
flags.
