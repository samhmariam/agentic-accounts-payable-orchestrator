# Day 0 — Azure Bootstrap · Trainee Pre-Reading

> **WAF Pillars:** Security · Operational Excellence  
> **Time to read:** 25 min  
> **Lab notebook:** `notebooks/day0_azure_bootstrap.py`

---

## Learning Objectives

By the end of Day 0 you will be able to:

1. Explain why Infrastructure as Code (IaC) is mandatory for production AI workloads.
2. Describe the Azure identity model: Managed Identity vs. API keys vs. Service Principals.
3. Enumerate the Azure services that make up AegisAP's runtime and state why each exists.
4. Read a Bicep template and identify resources, parameters, and role assignments.
5. Verify a deployed environment with `verify_env.py` without touching the Azure portal.

---

## 1. Why Infrastructure as Code?

When an AI workload drifts from its declared configuration — a secret hardcoded
in an env var, a network rule added through the portal, a role assigned by hand —
the system is no longer reproducible. Incidents become impossible to diagnose
because the actual state differs from the documented state.

**Infrastructure as Code (IaC)** solves this by treating every cloud resource as a
versioned artefact in source control. Azure's native IaC language is **Bicep**.

### Bicep basics

```bicep
// Declare a resource
resource kv 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: { family: 'A', name: 'standard' }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true   // <-- no access policies, RBAC only
  }
}
```

Key Bicep concepts:

| Concept | Purpose |
|---|---|
| `resource` | Declares a single Azure resource |
| `module` | Reusable template unit (like a function) |
| `param` | Externally supplied value (never hardcode secrets here) |
| `output` | Value exposed to calling templates or CI/CD |
| `existing` | References a resource that already exists (no create) |

### Azure best practice
- Keep secrets out of Bicep parameters. Reference Key Vault at deploy time using
  `getSecret()`, or inject them via the `AEGISAP_*` environment variables from a
  secure CI/CD pipeline.
- Use `az deployment sub validate` to lint templates locally before every PR.

---

## 2. The Azure Identity Model

### Managed Identity vs. API keys

| Approach | How it works | Risk |
|---|---|---|
| API key in env var | String credential passed at runtime | Exposed in logs, leaked in Docker images |
| Service Principal + secret | App ID + rotating secret | Secret must be rotated; secret can leak |
| **Managed Identity** | Azure platform issues short-lived tokens automatically | No secret to manage or rotate |

AegisAP **always** uses Managed Identity for Azure SDK calls in staging and
production. The `DefaultAzureCredential` from `azure-identity` tries credential
sources in order:

```
EnvironmentCredential → WorkloadIdentityCredential → ManagedIdentityCredential
→ AzureCliCredential → ...
```

In local development, `AzureCliCredential` (your `az login` session) satisfies
the chain. In production, `ManagedIdentityCredential` takes over automatically —
**no code change required**.

### Azure best practice
- Assign the **minimum required RBAC role** to each identity.
  - The API Container App needs `Cognitive Services OpenAI User` on the OpenAI
    account, never `Cognitive Services OpenAI Contributor`.
  - Use `AcrPull` for the user-assigned identity that pulls container images from
    Azure Container Registry.
- Prefer **system-assigned identities** for single-purpose workloads; use
  **user-assigned identities** when the same identity must traverse multiple
  resources (e.g., ACR pull across container revisions).

---

## 3. Core Azure Services in AegisAP

| Service | Role in AegisAP | Key Config |
|---|---|---|
| **Azure OpenAI Service** | LLM extraction and planning | Model deployment names in env vars; no raw API keys in code |
| **Azure AI Search** | Evidence retrieval for Day 3+ | Managed Identity access; semantic search tier |
| **Azure Database for PostgreSQL — Flexible Server** | Durable workflow state (Day 5+) | Requires Entra auth, not password auth |
| **Azure Container Apps (ACA)** | Hosts the API and worker | Revision-based deployments, Dapr optional |
| **Azure Container Registry (ACR)** | Stores Docker images | `AcrPull` role on ACA managed identity |
| **Azure Key Vault** | Residual secrets (any secret that isn't covered by a managed service) | RBAC authorization model; no legacy access policies |
| **Azure API Management (APIM)** | Rate-limiting, routing, cost tracking (Day 9) | Subscription keys never touch application code |
| **Azure Monitor / App Insights** | Traces, metrics, alerts (Day 8+) | OTEL exporter endpoint and connection string in env |

---

## 4. Environment Tracks

AegisAP ships two Bicep entry points:

| Track | Bicep file | Use when |
|---|---|---|
| `core` | `infra/core.bicep` | Days 0–4; local dev; no PostgreSQL |
| `full` | `infra/full.bicep` | Days 5+; includes PostgreSQL and secret plane |

The `--track` flag on `verify_env.py` checks that the right services are
available and reachable without performing any writes.

---

## 5. Resource Naming and Tagging

Azure best practice mandates consistent naming so that cost reports and security
scans are unambiguous.

AegisAP uses:
- **Prefix pattern:** `aegisap-<env>-<resource-short-name>` (e.g., `aegisap-dev-kv`)
- **Mandatory tags:** `environment`, `workload`, `owner`, `cost-centre`

Tags are declared inside Bicep modules and propagated through the `tags`
parameter so no resource can be deployed untagged.

---

## 6. Zero-Downtime Deployment Model

Azure Container Apps (ACA) uses a **revision model**:

- Every new image or config change creates a new *revision*.
- Traffic is split between revisions using percentage weights.
- Rolling back means shifting 100% of traffic to a previous revision — no
  re-deploy required.

This model underpins Day 10's deployment gate — but it starts here.

---

## Glossary

| Term | Definition |
|---|---|
| **Bicep** | Azure's declarative IaC language; compiles to ARM JSON |
| **ARM** | Azure Resource Manager — the control plane for all Azure resources |
| **Managed Identity** | Azure-assigned credential that rotates automatically, never stored as a secret |
| **RBAC** | Role-Based Access Control — permissions are assigned to identities on resources |
| **ACA** | Azure Container Apps — serverless container hosting with revision management |
| **ACR** | Azure Container Registry — private Docker image store |
| **DefaultAzureCredential** | Azure SDK class that tries multiple credential sources in order |
| **WAF** | Azure Well-Architected Framework — five pillars of production cloud design |

---

## Check Your Understanding

Answer these **before** opening the notebook:

1. Why is it unsafe to store an Azure OpenAI API key as a plain environment variable in a deployed Container App?
2. What RBAC role does AegisAP's Container App need to call Azure OpenAI, and why not a broader role?
3. In which order does `DefaultAzureCredential` try credential sources, and which source applies in production?
4. What is the difference between a `core` and a `full` environment track in AegisAP?
5. What is a Bicep `module`, and why is it preferable to one large Bicep file?

---

## Lab Readiness

- **Lab duration:** 2 hours
- **Required inputs:** provisioned `core` or `full` track, Azure CLI login, and `notebooks/day0_azure_bootstrap.py`
- **Expected artifact:** `build/day0/env_report.json`

### Pass Criteria

- The environment report shows `gate_passed = true` for the selected track.
- You can name the production credential source and the narrowest role needed for Azure OpenAI.
- You can state the exact recovery command you would run if one probe failed.

### Common Failure Signals

- `az login` is pointed at the wrong tenant or subscription.
- One required endpoint variable is missing for the selected track.
- A forbidden secret-style environment variable is present in the shell.

### Exit Ticket

1. Which `DefaultAzureCredential` source should fire in production?
2. Why is a scoped RBAC assignment safer than broad contributor access for the runtime identity?
3. What exact command would you run first if `build/day0/env_report.json` showed a failed probe?

### Remediation Task

Re-establish the environment contract with:

```bash
source ./scripts/setup-env.sh core
uv run python scripts/verify_env.py --track core --env
marimo edit notebooks/day0_azure_bootstrap.py
```

Then explain which probe failed and which Azure dependency it represents.

### Stretch Task

Write down one additional environment probe you would add for the `full` track
and explain which production failure mode it would catch earlier than Day 5.
