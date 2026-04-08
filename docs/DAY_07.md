# Day 7 - Guardrail Breach Rescue Mission

Day 7 is now a live guardrail incident. Start with:

```bash
uv run aegisap-lab incident start --day 07
```

Use `notebooks/day_7_testing_eval_guardrails.py` to prove where sensitive audit
evidence is leaking, then repair the guardrail and verify with:

```bash
uv run python -m pytest tests/day7/security/test_redaction.py tests/day7/audit/test_audit_row_written_for_sensitive_decision.py -q
uv run aegisap-lab artifact rebuild --day 07
```

Success means the redaction boundary strips sensitive evidence before audit
persistence and `build/day7/eval_report.json` is regenerated.
