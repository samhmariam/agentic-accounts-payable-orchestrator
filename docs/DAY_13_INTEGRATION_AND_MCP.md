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
