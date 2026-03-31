# Day 7 — Security, Identity & Auditability · Trainee Pre-Reading

> **WAF Pillars:** Security  
> **Time to read:** 30 min  
> **Lab notebook:** `notebooks/day7_security_identity.py`

---

## Learning Objectives

By the end of Day 7 you will be able to:

1. Explain the Zero Trust principle and how it applies to an AI workload.
2. Describe AegisAP's four identity planes and what each covers.
3. Explain `DefaultAzureCredential` and why it replaces API keys.
4. Define PII redaction as a system boundary responsibility and describe what AegisAP redacts.
5. Explain what an audit row must contain to be legally defensible.

---

## 1. Zero Trust for AI Workloads

**Zero Trust** is a security model based on three principles:

1. **Verify explicitly** — always authenticate and authorise, using all available data points
2. **Use least privilege** — limit access to the minimum required
3. **Assume breach** — design systems as if attackers are already inside

Applied to an AI workload like AegisAP:

| Principle | Implication |
|---|---|
| Verify explicitly | Every Azure SDK call uses Managed Identity; no API key fallback permitted |
| Use least privilege | The runtime identity cannot write to Key Vault; it can only read named secrets |
| Assume breach | PII is redacted before logs are emitted; audit rows don't contain raw case data |

---

## 2. AegisAP's Four Identity Planes

Day 7 formalises four distinct identity planes. Each has different permissions
and a different trust surface:

| Plane | Who | Permissions | Example RBAC roles |
|---|---|---|---|
| **Runtime API** | The Container App's system-assigned managed identity | Read Key Vault secrets, call OpenAI, query Search, write to PostgreSQL | `Key Vault Secrets User`, `Cognitive Services OpenAI User`, `Search Index Data Reader`, `PostgreSQL Flexible Server` connect |
| **Jobs scaffold** | Container App jobs (evaluation, migration) | Same as runtime + write search (for index management) | Above + `Search Index Data Contributor` |
| **Search admin scaffold** | One-time setup scripts | Create/delete search indexes | `Search Service Contributor` |
| **Developer / Ops** | Human engineers | Portal read, log query, no data write in production | `Reader`, `Log Analytics Reader` |

### Why separate runtime from admin?

If the runtime identity had admin-level permissions, a compromised container
could delete indexes, rotate secrets, or exfiltrate the entire knowledge base.
Separating the identities limits blast radius.

---

## 3. DefaultAzureCredential

`DefaultAzureCredential` from the `azure-identity` package tries a chain of
credential providers in order:

```
1. EnvironmentCredential          (AZURE_CLIENT_ID / _SECRET / _TENANT_ID)
2. WorkloadIdentityCredential     (Kubernetes workload identity)
3. ManagedIdentityCredential      ← production ACA path
4. AzureCliCredential             ← local dev `az login` path
5. AzurePowerShellCredential
6. AzureDeveloperCliCredential
```

In **local development**: step 4 fires — your `az login` session provides a token.  
In **production**: step 3 fires — the Container App's managed identity provides a token.

**No code change is required when moving from dev to prod.** The credential
source changes automatically based on the environment.

### Azure best practice
- Never use `AzureCliCredential` directly in production code — it always fails
  in an environment without the Azure CLI.
- Explicitly exclude workload identity credential if not using AKS, to avoid
  confusing fallback behaviour: `DefaultAzureCredential(exclude_workload_identity_credential=True)`.
- Test credential resolution in staging by checking which credential fired
  (the SDK emits debug logs at level `logging.DEBUG`).

---

## 4. Key Vault Secret Access Contracts

### What goes in Key Vault

Key Vault holds **residual secrets** — credentials for services that do not
support Managed Identity natively. Examples in AegisAP:
- LangSmith API key (tracing backend — external, no Azure identity)
- Notification webhook token (third-party systems)

### What does NOT go in Key Vault

Services that support Managed Identity do not need Key Vault entries:
- Azure OpenAI endpoint → accessed via `DefaultAzureCredential` + `RBAC`
- Azure AI Search endpoint → accessed via `DefaultAzureCredential` + `RBAC`
- PostgreSQL → accessed via Entra authentication

### Access pattern

```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

client = SecretClient(
    vault_url=os.environ["AZURE_KEY_VAULT_URI"],
    credential=DefaultAzureCredential(),
)
secret = client.get_secret("langsmith-api-key")
value = secret.value  # use this; never persist it
```

### Azure best practice
- Grant the runtime identity only `Key Vault Secrets User` (read-only).
  Never `Key Vault Secrets Officer` (read + write) for the application identity.
- Enable **soft-delete** and **purge protection** on Key Vault. This prevents
  accidental or malicious deletion of secrets.
- Rotate secrets on a schedule. Use Key Vault's rotation policies for supported
  secret types.

---

## 5. PII Redaction

PII (Personally Identifiable Information) must never appear in:
- Application logs
- Trace spans (OpenTelemetry attributes)
- Error messages passed to external services
- Audit summaries posted to external dashboards

**Redaction must happen at the system boundary** — before any data leaves the
AegisAP process destined for an external sink.

### What AegisAP redacts

| Category | Examples | Redaction approach |
|---|---|---|
| Vendor contact names | "John Smith, Accounts Manager" | Regular expression + named entity detection |
| Email addresses | `john.smith@acme.com` | Regex |
| Bank account fragments | `****1234` patterns | Regex |
| Free-text case notes | Unstructured content in attachments | Replaced with `[REDACTED]` label |

### Redaction is not encryption

Redaction removes or obscures the value. Encryption preserves it in a
unreadable form. For logs and traces, **redaction** is correct — you do not
want to re-identify the data by decrypting a log file.

---

## 6. Audit Logging

Every significant decision in AegisAP — approval, refusal, resumption,
escalation — must produce a **durable, tamper-evident audit row** in PostgreSQL.

A legally defensible audit row contains:

| Field | Purpose |
|---|---|
| `audit_id` | UUID — unique identity of this audit event |
| `thread_id` | Which business thread this event belongs to |
| `workflow_run_id` | Which run within that thread |
| `event_type` | `approved`, `refused`, `resumed`, `escalated` |
| `actor_identity` | The managed identity object ID that triggered the action |
| `decision_summary` | Redacted summary — no raw PII |
| `policy_ids` | Policy rules evaluated |
| `evidence_ids` | Document chunks referenced |
| `created_at` | UTC timestamp |
| `trace_id` | Correlates to observability trace (Day 8) |

No audit row is ever updated or deleted. The table has an append-only contract
enforced by PostgreSQL row-level security (insert only, no update or delete).

---

## Glossary

| Term | Definition |
|---|---|
| **Zero Trust** | Security model: verify explicitly, use least privilege, assume breach |
| **Managed Identity** | Azure-issued credential tied to a resource; no password or secret to manage |
| **DefaultAzureCredential** | Azure SDK credential class that tries multiple sources in order |
| **Key Vault** | Azure service for storing and accessing secrets, keys, and certificates |
| **PII** | Personally Identifiable Information — any data that can identify an individual |
| **Redaction** | Removing or obscuring sensitive data before it crosses a trust boundary |
| **Audit row** | A durable, append-only record of a significant system decision |
| **Blast radius** | The scope of damage an attacker or bug can cause if a component is compromised |

---

## Check Your Understanding

1. Name the three Zero Trust principles and give one example of how each applies to AegisAP.
2. What are AegisAP's four identity planes? What permissions does each need?
3. Which credential source fires in production, and which fires in local development with `DefaultAzureCredential`?
4. What types of residual secrets belong in Key Vault? What is an example of a credential that does NOT need Key Vault?
5. What fields must an audit row contain to be legally defensible, and why is the table append-only?

---

## Lab Readiness

- **Lab duration:** 2.5 hours
- **Required inputs:** full-track environment, `build/day5/golden_thread_day5_resumed.json` or Day 6 artifact, and `notebooks/day7_security_identity.py`
- **Expected artifact:** `build/day7/security_posture.json`

### Pass Criteria

- The posture report shows either green checks or a clearly isolated failure with a recovery path.
- The learner can explain the separation between runtime, deployment, admin, and data identities.
- A seeded security misconfiguration is repaired and the artifact is regenerated.

### Common Failure Signals

- A plain secret is accepted where managed identity or Key Vault should be used.
- The learner cannot explain the blast radius of a compromised Container App.
- Audit evidence is discussed without naming the append-only fields that make it defensible.

### Exit Ticket

1. Which identity plane should never be able to mutate production IaC?
2. Why is `disableLocalAuth: true` on Azure AI Search a control-plane decision?
3. What exact command would you run first if the Day 7 posture report failed?

### Remediation Task

Re-run the environment and posture checks with:

```bash
uv run python scripts/verify_env.py --track full --env
marimo edit notebooks/day7_security_identity.py
```

Then explain which control failed, what its blast radius would have been, and
which artifact proves the recovery.

### Stretch Task

Describe how you would harden the current public-endpoint training setup toward
private endpoints without changing the four identity planes.
