# Day 7 — Security, Identity & Auditability · Trainer Guide

> **Session duration:** 4 hours (75 min theory + 2.5 h lab + 15 min wrap-up)  
> **WAF Pillars:** Security  
> **Prerequisite:** Day 6 complete; `full` track environment with Key Vault

---

## Session Goals

By the end of Day 7, every learner should be able to:
- Explain the Zero Trust model and map its three principles to AegisAP controls
- Read the Bicep role assignments and trace each identity to its permissions
- Verify that no search admin key exists in application code
- Demonstrate PII redaction at the log boundary
- Inspect an audit row in PostgreSQL and confirm it contains no raw PII

---

## Preparation Checklist

- [ ] `full` track environment provisioned: Key Vault exists with `langsmith-api-key` secret
- [ ] Container App has system-assigned identity with correct RBAC roles
- [ ] User-assigned identity for ACR pull exists and is attached
- [ ] `uv run python scripts/verify_env.py --track full --env` exits 0
- [ ] Day 6 complete; Day 6 review outcome in latest checkpoint
- [ ] Tests for Day 7 pass: `uv run pytest tests/day7 -q`

**Expected artifact:** `build/day7/security_posture.json`

---

## Theory Segment (75 min)

### Block 1: Zero Trust for AI Workloads (20 min)

**Talking points:**
1. Write the three Zero Trust principles on the board:
   ```
   1. Verify explicitly
   2. Use least privilege
   3. Assume breach
   ```
2. For each principle, show the AegisAP implementation:
   - **Verify explicitly**: `DefaultAzureCredential` with Managed Identity.
     Every API call is authenticated; no anonymous access anywhere.
   - **Use least privilege**: The API identity has `Cognitive Services
     OpenAI User` — NOT `Contributor`. It can call models; it cannot create
     deployments, change content filters, or view billing.
   - **Assume breach**: PII is redacted before logs are emitted. If an
     attacker reads the log files, they see `[REDACTED]` not contact details.
3. Introduce the **blast radius** concept: if the Container App is
   compromised, what can an attacker do with the runtime identity?
   If the identity has only `Search Index Data Reader` and `Cognitive
   Services OpenAI User`, the blast radius is bounded.
4. Ask: "What would the blast radius be if the runtime identity had
   `Contributor` on the entire resource group?" (Answer: delete indexes,
   rotate secrets, modify Bicep templates, access all secrets.)

---

### Block 2: AegisAP's Four Identity Planes (25 min)

**Talking points:**
1. Draw the four planes on the board with their identities and permissions.
   Use AegisAP's actual identities from the Bicep templates.
2. Walk through `infra/modules/role_assignments.bicep` live in the editor.
   For each role assignment, trace: *who* gets *which role* on *which resource*.
3. **System-assigned vs. user-assigned identity demonstration:**
   - System-assigned: created with the Container App, deleted with it.
     Good for: the runtime API's Azure service calls.
   - User-assigned: pre-created, assigned to the app. Can survive the
     app being deleted/recreated. Required for: ACR pull (must be consistent
     across revision changes).
4. Open `src/aegisap/security/credentials.py`. Show `DefaultAzureCredential`.
   Ask: "Which credential source fires in our Container App?" (ManagedIdentity.)
   Ask: "Which fires locally?" (AzureCliCredential.)

**Azure best practice moment:**  
Show `az identity show --name aegisap-runtime --resource-group ...` to get
the object ID. Then show `az role assignment list --assignee <object-id>` to
confirm what roles the identity actually has. Teach learners to verify, not
just trust that the Bicep ran correctly.

---

### Block 3: PII Redaction and Audit Logging (30 min)

**Talking points:**
1. Show the PII categories that AegisAP redacts (from `security/redaction.py`):
   - Contact names in vendor correspondence
   - Email addresses
   - Bank account fragments
   - Free-text case notes
2. Show the redaction code. Emphasise: **redaction happens before any data
   leaves the Python process** destined for logs, traces, or external sinks.
3. Contrast redaction with encryption. Ask: "If I encrypt a log line and store
   it, can I later search for 'all log lines mentioning John Smith'?"
   Expected: not without decrypting everything. Conclusion: for searchable
   audit logs, redact; for data you need to recover, encrypt.
4. Walk through the audit log row schema. For each field, ask a learner:
   "Why does this field exist? Who needs it?"
5. Show the append-only contract. Open the PostgreSQL role definition that
   prohibits `UPDATE` and `DELETE` on the `audit_log` table. Explain: this
   is not just convention — it is enforced at the database level.
6. Show a completed audit row from a Day 6 review outcome. Point out that
   `decision_summary` contains no raw PII — it's a redacted narrative.

---

## Lab Walkthrough Notes

### Key cells to call out in `day7_security_identity.py`:

1. **`_identity_probe` cell** — queries the runtime identity via Azure SDK.
   Shows the managed identity object ID and its current role assignments.

2. **`_pii_redaction_lab` cell** — feeds a sample invoice comment containing
   names and an email address through the redaction function. Walk through
   the before/after comparison.

3. **`_show_redaction` cell** — shows the redacted output as it would appear
   in a structured log. Ask: "Is there any information in this redacted record
   that an attacker could use to identify a specific person?"

4. **`_audit_log` cell** — queries the audit log table and shows the entries
   written by Day 6. Verify: no raw PII in `decision_summary`. Verify:
   `evidence_ids` present. Verify: `trace_id` present (will connect to Day 8).

5. **Security gate cell** — `verify_env.py --track full`. Show what a failing
   check looks like by unsetting `AZURE_KEY_VAULT_URI` temporarily.

### Expected lab friction points

| Issue | Likely cause | Resolution |
|---|---|---|
| `DefaultAzureCredential` authentication fails | Local dev: not logged in to correct tenant | `az login --tenant <tenant-id>` |
| Key Vault `403 Forbidden` | `Key Vault Secrets User` role not yet propagated (takes 2–5 min) | Wait for role propagation; `az role assignment list --assignee ...` |
| Audit row missing `trace_id` | Day 8 OTEL not yet configured | Expected — trace correlation is Day 8's responsibility |
| PII redaction misses a phone number | Regex not covering that format | Show how to extend the redaction pattern; good exercise |

---

## Facilitation Addendum

### Observable Mastery Signals

- Learner can map permissions to the four identity planes without over-privileging any of them.
- Learner explains blast radius using the actual runtime and audit contracts.
- Learner repairs a posture failure and regenerates `build/day7/security_posture.json`.

### Intervention Cues

- If someone proposes copying secrets into `.env` for convenience, pause and restate the Day 7 runtime contract immediately.
- If a learner cannot distinguish runtime from deployment identity, redraw the identity planes before continuing.
- If auditability is discussed abstractly, require them to name concrete fields from the audit row.

### Fallback Path

- If Azure access is unavailable, score a saved `build/day7/security_posture.json` and use sample audit evidence instead of live posture checks.

### Exit Ticket Answer Key

1. The deployment/admin identity should not be able to impersonate runtime decisions casually.
2. `disableLocalAuth: true` forces search access back through Entra and RBAC.
3. Strong answers start with `uv run python scripts/verify_env.py --track full --env`.

### Time-box Guidance

- Cap environment posture debugging at 15 minutes before moving to saved artifacts.
- Protect at least 20 minutes for blast-radius discussion and audit evidence review.

---

## Common Misconceptions

| Misconception | Correction |
|---|---|
| "Managed Identity is only for Azure services" | DefaultAzureCredential works for any Azure SDK call; the same pattern applies to Key Vault, Storage, Service Bus, etc. |
| "Role assignment in Bicep is enough; no need to verify" | Bicep deploys the intent; platform propagation can take minutes. Always verify with `az role assignment list`. |
| "PII redaction is a privacy feature, not a security feature" | It is both. Redacting PII from logs limits attacker exfiltration value if logs are accessed. |
| "Append-only audit logs are for compliance only" | They are also for forensics: if an incident occurs, the unmodified audit trail is evidence. |

---

## Discussion Prompts

1. "The AegisAP Container App is compromised. An attacker has execution in the
   container. Given the current identity model, what can they access? What
   can they NOT access? What is the blast radius?"

2. "A developer wants to test the full Key Vault integration locally. They cannot
   use Managed Identity on their laptop. What is the approved approach?
   What must never be done?"

3. "An auditor asks for the decision trail for invoice INV-3001. What tables
   and fields in AegisAP's database would you query, and what would you show them?"

---

## Expected Q&A

**Q: Can we use Azure Managed Identity to access PostgreSQL Flexible Server?**  
A: Yes — PostgreSQL Flexible Server supports Entra authentication. The
application uses `DefaultAzureCredential` to get a token for
`https://ossrdbms-aad.database.windows.net/.default`, which is passed as
the password in the connection string. Day 7's `verify_env.py` checks that
no plain-text DSN is in use.

**Q: Why not use Azure Private Endpoints for all services?**  
A: Private Endpoints are the recommendation for production. AegisAP's training
environment uses public endpoints with firewall rules for simplicity. In the
`full` Bicep track, this is noted as a production hardening step in the Bicep
comments. The identity and RBAC model is the same either way.

**Q: How do you handle secrets rotation if the application is reading from Key Vault at startup?**  
A: Read secrets at runtime, not at startup. The `get_secret()` call is made
lazily on each request (or cached for a short TTL, e.g., 5 minutes) rather than
once during app initialisation. This way, a rotated secret is picked up without
restarting the Container App.

---

## Next-Day Bridge (5 min)

> "We've hardened the identity model. Every call is authenticated. Every
> secret is properly controlled. But we still can't answer: 'how long does
> this workflow take? which step is the slowest? did this week's model update
> make it worse?' Tomorrow we add OpenTelemetry — every workflow run emits
> a trace, the slowest steps become queryable, and our evaluation dataset
> becomes an executable regression suite."
