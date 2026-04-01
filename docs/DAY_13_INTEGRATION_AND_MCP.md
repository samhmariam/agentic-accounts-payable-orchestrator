# DAY 13 — Integration Boundaries & Model Context Protocol

> **Status:** Part of AegisAP curriculum v3 (Days 11-14 extension)  
> **WAF:** Reliability · Operational Excellence · Security  
> **Notebook:** `notebooks/day_13_integration_boundary_and_mcp.py`  
> **New gates:** `gate_dlq_drain_health` · `gate_mcp_contract_integrity`

---

## Summary

Day 13 builds the two external interfaces for AegisAP:

1. **Azure Functions HTTP trigger** — authenticated LOB boundary for synchronous ERP calls
2. **Service Bus** — reliable async transport with DLQ + compensating actions
3. **MCP server** — FastAPI-based tool exposure for external AI agents

## Source Modules

| Module | Key class |
|---|---|
| `src/aegisap/integration/azure_functions_boundary.py` | `FunctionsBoundaryClient` |
| `src/aegisap/integration/service_bus_handler.py` | `ServiceBusHandler` |
| `src/aegisap/integration/dlq_consumer.py` | `DlqConsumer` |
| `src/aegisap/integration/compensating_action.py` | `CompensatingActionRunner` |
| `src/aegisap/mcp/server.py` | `create_mcp_app()` |

## Bicep Modules

| File | Purpose |
|---|---|
| `infra/integration/service_bus.bicep` | Premium Service Bus namespace + queues |
| `infra/integration/function_app.bicep` | Flex Consumption Functions + MI auth |

## Gate Artifacts

| Artifact | Path | Gate |
|---|---|---|
| DLQ drain report | `build/day13/dlq_drain_report.json` | `gate_dlq_drain_health` |
| MCP contract report | `build/day13/mcp_contract_report.json` | `gate_mcp_contract_integrity` |

## Scripts

```bash
# Drain DLQ
python scripts/verify_webhook_reliability.py

# Validate MCP contract
python scripts/verify_mcp_contract_integrity.py
```

## MCP Server

Start the server locally:
```bash
AEGISAP_MCP_SKIP_AUTH=1 uvicorn aegisap.mcp.server:app --port 8001
```

Available tools: `query_invoice_status`, `list_pending_approvals`, `get_vendor_policy`

## Common Failure Modes

See `evals/failure_drills/drill_05_dlq_overflow.json` and
`evals/failure_drills/drill_06_mcp_contract_break.json`.

<!-- CAPSTONE_B -->

---

## FDE Rubric — Day 13 (100 points)

| Dimension | Points |
|---|---|
| Boundary architecture correctness | 25 |
| Reliability design | 20 |
| Contract / versioning quality | 20 |
| External stakeholder communication | 20 |
| Oral defense | 15 |

**Pass bar: 80.  Elite bar: 90.**

**Capstone B day** — primary deliverables are in the claims intake transfer domain.

## Oral Defense Prompts

1. A partner demands direct access to the orchestrator. Walk through your boundary defense and what you offer instead.
2. If a compensating action fails silently, what is the blast radius and what is your detection and recovery path?
3. Who approves a breaking change to an external API contract, what is the minimum notice period, and what evidence must accompany the deprecation notice?

## Artifact Scaffolds

- `docs/curriculum/artifacts/day13/EXTERNAL_CONTRACT_POLICY.md`
- `docs/curriculum/artifacts/day13/COMPENSATING_ACTION_CATALOG.md`
- `docs/curriculum/artifacts/day13/API_CHANGE_COMMUNICATION_PLAN.md`
