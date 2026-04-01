# DAY 14 — Breaking Changes & Elite Operations

> **Status:** Part of AegisAP curriculum v3 (Days 11-14 extension)  
> **WAF:** All five pillars  
> **Notebook:** `notebooks/day_14_breaking_changes_elite_ops.py`  
> **Gates validated:** ALL 17

---

## Summary

Day 14 is the convergence point for the full 14-day curriculum.  All gate artifacts
from Days 1-14 are aggregated into a CTO trace report.  Ten breaking-change drills
exercise every failure mode introduced in Days 11-13.

## Drills

| # | Name | Gate |
|---|---|---|
| 01 | IAM Drift | `gate_actor_binding` |
| 02 | OBO Scope Mismatch | `gate_obo_exchange` |
| 03 | DNS Misconfiguration | `gate_private_network_posture` |
| 04 | Public Endpoint Re-enabled | `gate_private_network_static` |
| 05 | DLQ Overflow | `gate_dlq_drain_health` |
| 06 | MCP Contract Break | `gate_mcp_contract_integrity` |
| 07 | Model Version Regression | `gate_canary_regression` |
| 08 | Data Residency Violation | `gate_data_residency` |
| 09 | Correlation Gap | `gate_trace_correlation` |
| 10 | Rollback Failure | all gates |

Full drill definitions in `evals/failure_drills/`.

## Gate Artifacts (Day 14)

| Artifact | Path | Gate |
|---|---|---|
| Canary regression | `build/day14/canary_regression_report.json` | `gate_canary_regression` |
| Data residency | `build/day14/data_residency_report.json` | `gate_data_residency` |
| Trace correlation | `build/day14/trace_correlation_report.json` | `gate_trace_correlation` |
| CTO trace report | `build/day14/cto_trace_report.json` | (aggregator) |

## Scripts

```bash
# Write all Day 14 artifacts (stub mode if no Azure creds)
python notebooks/day_14_breaking_changes_elite_ops.py

# Run all 17 gates
python scripts/check_all_gates_v2.py

# Generate CTO report
python scripts/generate_cto_trace_report.py
```

## CI Workflows

| Workflow | Trigger | Gates |
|---|---|---|
| `gate_private_network_static.yml` | PR on infra/network/` | `gate_private_network_static` |
| `gate_trace_correlation.yml` | Daily 06:00 UTC | `gate_trace_correlation` |
| `gate_canary_regression.yml` | Manual | `gate_canary_regression` |
| `gate_rollback_readiness.yml` | Weekly Monday | All 17 gates |

## Operational Runbooks

- [rollback_runbook.md](../runbooks/rollback_runbook.md)
- [incident_response_runbook.md](../runbooks/incident_response_runbook.md)
- [dlq_runbook.md](../runbooks/dlq_runbook.md)
