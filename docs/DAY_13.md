# Day 13 - Integration Boundary Rescue Mission

Day 13 is now an MCP and compensating-action incident. Start with:

```bash
uv run aegisap-lab incident start --day 13
```

Use `notebooks/day_13_integration_boundary_and_mcp.py` to prove the contract
drift, then repair the boundary and verify with:

```bash
uv run python -m pytest tests/day13/test_dlq_consumer.py tests/day13/test_mcp_server.py tests/day13/test_payment_hold.py -q
uv run aegisap-lab artifact rebuild --day 13
```

Success means the governed MCP contract exposes the write path again, the
boundary stays compensating-action safe, and the Day 13 artifacts under
`build/day13/` are regenerated.

## CAPSTONE_B

Day 13 feeds the capstone transfer track by proving the external contract and
compensating-action boundaries that the final release packet must preserve.
