# Incident Response Runbook — AegisAP

**Version:** 1.0  
**Severity levels:** P1 (critical, < 15 min response) · P2 (high, < 1 h) · P3 (medium, < 4 h)

---

## Severity Guide

| Condition | Severity |
|---|---|
| Data exfiltration possible (public endpoint re-enabled) | P1 |
| All invoices failing to process | P1 |
| Identity / auth fully broken | P1 |
| DLQ overflow, processing degraded | P2 |
| Single feature broken, workaround available | P2 |
| Single gate failing, service operational | P3 |

---

## P1 — Data Plane Breach / Public Endpoint Exposed

1. **IMMEDIATELY** disable public network access on the affected resource via Azure Portal or CLI:
   ```bash
   az cognitiveservices account update \
     --name <account> --resource-group $AZURE_RESOURCE_GROUP \
     --custom-domain <account>.openai.azure.com \
     --api-properties publicNetworkAccess=Disabled
   ```
2. Pull network activity logs from Log Analytics:
   ```kql
   AzureDiagnostics
   | where ResourceType == "COGNITIVESERVICES"
   | where TimeGenerated > ago(2h)
   | where ResultSignature == "200"
   | project TimeGenerated, CallerIPAddress, OperationName
   | order by TimeGenerated desc
   ```
3. Escalate to Security Team immediately.
4. Re-run `verify_private_network_posture.py` to confirm remediation.
5. Run `check_all_gates_v2.py` — all 17 gates must pass before standing down.

---

## P1 — Authentication Failure (401 spike)

1. Check if MI still exists:
   ```bash
   az identity show --name aegisap-worker-mi --resource-group $AZURE_RESOURCE_GROUP
   ```
2. Check role assignments:
   ```bash
   az role assignment list --assignee <principal-id> --output table
   ```
3. If MI deleted: recreate and reassign roles per `infra/` Bicep.
4. Restart ACA revision to flush cached credentials:
   ```bash
   az containerapp revision restart --name aegisap-worker \
     --resource-group $AZURE_RESOURCE_GROUP --revision <REVISION>
   ```
5. Re-run `verify_delegated_identity_contract.py`.

---

## P2 — DLQ Overflow

See [dlq_runbook.md](dlq_runbook.md).

---

## P2 — MCP Contract Break

1. Identify which tool was removed by checking the failed gate artifact:
   ```bash
   cat build/day13/mcp_contract_report.json | python -m json.tool
   ```
2. Restore the tool in `src/aegisap/mcp/server.py`.
3. Deploy hotfix revision.
4. Re-run `verify_mcp_contract_integrity.py`.

---

## Escalation Path

| Level | Contact | When |
|---|---|---|
| L1 | On-call engineer | All incidents |
| L2 | Platform team lead | P1 or unresolved P2 after 1 h |
| L3 | CISO + Engineering Director | Data breach or regulatory impact |
