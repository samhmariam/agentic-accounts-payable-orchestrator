# Day 8 - Identity Drift Rescue Mission

Day 8 is now an IaC and identity drift incident. Start with:

```bash
uv run aegisap-lab incident start --day 08
```

Use `notebooks/day_8_cicd_iac_deployment.py` to inspect the role-assignment
contract, then repair the runtime identity boundary and verify with:

```bash
uv run python -m pytest tests/day7/security/test_search_token_auth_only.py tests/day8/test_security_and_context.py tests/day8/test_observability_contract.py -q
uv run aegisap-lab artifact rebuild --day 08
```

Success means runtime search access is least-privilege again and the Day 8
deployment artifacts are regenerated under `build/day8/`.
