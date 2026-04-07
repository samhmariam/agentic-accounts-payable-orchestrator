import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _bootstrap():
    import sys
    from pathlib import Path
    _root = Path(__file__).resolve().parents[1]
    for _p in [str(_root / "src"), str(_root / "notebooks"), str(_root)]:
        if _p not in sys.path:
            sys.path.insert(0, _p)
    return


@app.cell
def _imports():
    import marimo as mo
    import json
    import os
    from pathlib import Path
    return json, mo, os, Path


# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------
@app.cell
def _title(mo):
    mo.md("""
    # Day 8 — CI/CD, Infrastructure as Code & Secure Deployment

    > **WAF Pillars covered:** Security · Operational Excellence · Reliability
    > **Estimated time:** 2.5 hours
    > **Sources:** `docs/curriculum/trainee/DAY_00_TRAINEE.md` (Bicep, IaC, identity),
    > `docs/curriculum/trainee/DAY_07_TRAINEE.md` (Zero Trust, identity planes),
    > `docs/curriculum/trainee/DAY_10_TRAINEE.md` (OIDC, ACA revisions, acceptance gates)
    > **Prerequisites:** Day 7 complete; `evals/score_thresholds.yaml` and gate artifacts exist.

    ---

    ## Learning Objectives

    1. Explain why Infrastructure as Code is mandatory for production AI workloads.
    2. Read a Bicep template and identify resources, modules, parameters, and role assignments.
    3. Name AegisAP's four identity planes and specify the minimum RBAC role for each.
    4. Explain `DefaultAzureCredential` and why the same code works in dev and prod.
    5. Describe Key Vault access contracts — what goes in, what does not, and why.
    6. Explain GitHub Actions OIDC federation and why it eliminates long-lived credentials.
    7. Describe the ACA revision model and execute a zero-downtime deployment and rollback.
    8. Run the six acceptance gates and interpret the release envelope.

    ---

    ## Where Day 8 Sits in the Full Arc

    ```
    Day 6  ── Day 7 ──►[Day 8]──► Day 9 ──► Day 10
    Data &     Testing  CI/CD &   Scaling  Production
    ML         & Safety IaC       & Cost   Operations
    ```

    Day 8 answers: **"How do we ship AegisAP to a live Azure environment safely,
    repeatably, and with zero stored secrets?"**  The system was proven correct
    in Day 7; now we automate the proof and the deployment.
    """)
    return


@app.cell
def _full_day_agenda(mo):
    from _shared.curriculum_scaffolds import render_full_day_agenda

    render_full_day_agenda(
        mo,
        day_label="Day 8 CI/CD, IaC, and secure deployment",
        core_outcome="connect Bicep, identity, release automation, and gate evidence into one deployable operating model",
    )
    return

@app.cell
def _notebook_guide(mo):
    from _shared.lab_guide import render_notebook_learning_context

    render_notebook_learning_context(
        mo,
        purpose='Convert the designed and tested system into a repeatable deployment model with infrastructure as code, identity, CI/CD, and acceptance gates.',
        prerequisites=['Day 7 complete.', '`evals/score_thresholds.yaml` and prior gate artifacts are available.', 'A Day 0 provisioned environment is helpful for live paths but not required for every conceptual section.'],
        resources=['`notebooks/day_8_cicd_iac_deployment.py`', '`infra/` Bicep and deployment files', '`scripts/provision-core.ps1`, `scripts/provision-full.ps1`, and `scripts/check_all_gates.py` for optional live and CLI follow-up', '`build/day8/` for `deployment_design.json` and `regression_baseline.json`', '`docs/curriculum/artifacts/day08/`'],
        setup_sequence=['Decide whether you are doing notebook-only learning or also validating a live Azure deployment.', 'If live, make sure Day 0 environment state and Azure auth are already working.', 'Run the early lineage and mastery cells so you can see how Day 8 depends on Day 7 evidence.'],
        run_steps=['Work through Bicep, identity planes, Key Vault, OIDC, ACA revisions, and gate sections in order.', 'Use the interactive resource and gate cells to connect infrastructure choices to release safety.', 'Run the baseline and artifact cells that write `build/day8/regression_baseline.json` and `build/day8/deployment_design.json`.', 'Treat external scripts as optional follow-up validation, not required reading before the notebook makes sense.'],
        output_interpretation=['Success means you can explain how infrastructure, identity, and gates form one deployment contract.', 'The concrete artifacts are `build/day8/deployment_design.json` and `build/day8/regression_baseline.json`.', 'If the notebook shows some gates yellow, interpret that in light of later-day artifacts that do not exist yet.'],
        troubleshooting=['If the infra content feels too broad, keep asking how each choice affects deployment safety or release evidence.', 'If a gate looks red, check whether the expected upstream artifact exists before assuming the logic is wrong.', 'If live deployment details feel distracting, stay in notebook mode first and return to the scripts after the model is clear.'],
        outside_references=['Long-form theory: `docs/curriculum/trainee/DAY_00_TRAINEE.md`, `docs/curriculum/trainee/DAY_07_TRAINEE.md`, `docs/curriculum/trainee/DAY_10_TRAINEE.md`', 'Trainer notes: `docs/curriculum/trainer/DAY_08_TRAINER.md`', 'Infra deep dive: `infra/` and provisioning scripts', 'Reusable references: `docs/curriculum/artifacts/day08/`'],
    )
    return


@app.cell
def _three_surface_linkage(mo):
    from _shared.lab_guide import render_surface_linkage

    render_surface_linkage(
        mo,
        portal_guide="docs/curriculum/portal/DAY_08_PORTAL.md",
        portal_activity="Inspect the live deployment, Container App revisions, IAM assignments, and Key Vault boundaries in Azure before letting Bicep or release scripts describe the platform for you.",
        notebook_activity="Use the Bicep, identity-plane, Key Vault, OIDC, revision, and gate sections to explain why the portal state is safe or unsafe rather than treating deployment history as self-explanatory.",
        automation_steps=[
            "`uv run python scripts/verify_env.py --track full` checks the same environment contract you inspected in the portal.",
            "`pwsh ./scripts/provision-full.ps1 -SubscriptionId \"$AZURE_SUBSCRIPTION_ID\" -ResourceGroup \"$AZURE_RESOURCE_GROUP\" -Location \"$AZURE_LOCATION\"` recreates the infrastructure story from code.",
            "`pwsh ./scripts/deploy_container_app.ps1 -EnvironmentName staging` and `uv run python -m pytest tests/day8 -q` formalize the deployment and regression checks after the platform model is already clear.",
        ],
        evidence_checks=[
            "Portal deployment history and revision state should agree with the notebook explanation of what was released and why.",
            "`build/day8/deployment_design.json` and `build/day8/regression_baseline.json` should encode the same release and identity decisions you observed in Azure.",
            "Any mismatch between portal state, notebook claims, and automation artifacts is drift that needs explanation before moving on.",
        ],
    )
    return


@app.cell
def _azure_mastery_guide(mo):
    from _shared.lab_guide import render_azure_mastery_guide

    render_azure_mastery_guide(
        mo,
        focus="Day 8 mastery means you can inspect the deployed platform in Azure, reproduce deployment and drift checks from the CLI, recognise the minimal identity-based SDK shape, and show concrete evidence that infra, identity, and runtime configuration line up.",
        portal_tasks="""
- Open the **Resource group** and inspect **Deployments** so you can connect the Bicep deployment history to the runtime resources you are about to trust.
- Open the **Container App** and inspect **Revisions**, **Ingress**, and **Identity** to confirm the latest revision, traffic state, and managed identity attachment.
- Inspect **Access control (IAM)** on Azure OpenAI, Azure AI Search, Storage, and Key Vault so the runtime identity story is visible in Azure rather than only in code comments.
- Open **Key Vault** and confirm only residual secrets live there; public endpoints such as `AZURE_OPENAI_ENDPOINT` and `AZURE_SEARCH_ENDPOINT` should remain configuration, not vault secrets.
""",
        cli_verification="""
**Verify the Azure environment before trusting the deployment path**

```bash
uv run python scripts/verify_env.py --track full
```

**Provision or update the full platform from code**

```bash
pwsh ./scripts/provision-full.ps1 \
  -SubscriptionId "$AZURE_SUBSCRIPTION_ID" \
  -ResourceGroup "$AZURE_RESOURCE_GROUP" \
  -Location "$AZURE_LOCATION"
```

**Deploy the Container App revision from the repo's release script**

```bash
pwsh ./scripts/deploy_container_app.ps1 -EnvironmentName staging
```

**Optional drift review from raw Azure CLI**

```bash
az deployment group what-if \
  --resource-group "$AZURE_RESOURCE_GROUP" \
  --template-file infra/full.bicep \
  --parameters @infra/full.bicepparam \
  --parameters location="$AZURE_LOCATION"
```
""",
        sdk_snippet="""
Use an identity-first SDK pattern so the same code works locally and in Azure without stored credentials.

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os

client = SecretClient(
    vault_url=os.environ["AZURE_KEY_VAULT_URI"],
    credential=DefaultAzureCredential(),
)

resume_secret = client.get_secret("aegisap-resume-token-secret").value
```
""",
        proof_in_azure="""
- `uv run python scripts/verify_env.py --track full` passes, showing the environment variables and Azure service reachability are real.
- The portal deployment history, revision state, and identity role assignments agree with the IaC story you are defending.
- `build/day8/deployment_design.json` and `build/day8/regression_baseline.json` exist and are ready for later gate consumption.
- A good Day 8 proof chain shows not only that the resources exist, but that they can be reached with `DefaultAzureCredential` and least-privilege RBAC.
""",
    )
    return


@app.cell
def _day8_lineage_map(mo):
    mo.callout(
        mo.md(
            """
    ## Visual Guide — Deployment Evidence Lineage

    ```
    Day 7 safety and eval posture
        └─► Day 8 Bicep, identity, OIDC, gate runner
              ├─► build/day8/deployment_design.json
              ├─► build/day8/regression_baseline.json
              ├─► Day 10 release envelope and operator decisions
              └─► Day 11-14 identity, networking, and elite gate expansion
    ```

    Day 8 is the point where earlier design decisions become a repeatable release system.

    | Day 8 output | Later dependency |
    |---|---|
    | Regression baseline | Day 10 `eval_regression`, Day 14 canary comparison |
    | Deployment design artifact | Day 10 release packaging and ownership conversation |
    | OIDC + identity plane wiring | Day 11 delegated identity and Day 12 private posture realism |
    """
        ),
        kind="info",
    )
    return


@app.cell
def _day8_mastery_checkpoint(mo):
    mo.callout(
        mo.md(
            """
    ## Mastery Checkpoint — Before You Trust The Pipeline

    You are ready to progress only if you can explain:
    - why the release system is weaker than it looks without the Day 7 safety evidence
    - which identity plane is performing each deployment action
    - why a portal hotfix is not operational speed but configuration debt
    - what Day 10 can decide because Day 8 wrote machine-readable evidence first
    """
        ),
        kind="warn",
    )
    return


# ---------------------------------------------------------------------------
# Section 1 – Why IaC is Mandatory
# ---------------------------------------------------------------------------
@app.cell
def _s1_header(mo):
    mo.md("## 1. Why Infrastructure as Code is Mandatory for AI Workloads")
    return


@app.cell
def _s1_body(mo):
    mo.md("""
    AI workloads have a higher IaC requirement than traditional web services because:

    1. **Reproducibility** — an AI model's behaviour depends on the exact combination
       of model deployment name, system prompt, search index schema, and downstream
       service endpoints. Any undocumented portal change makes the system unreproducible.

    2. **Auditability** — compliance frameworks (ISO 27001, SOC 2, FCA guidelines for
       financial services) require evidence that the deployed runtime state matches an
       approved configuration. An IaC template is the approved configuration.

    3. **Drift recovery** — without IaC, it is impossible to determine what changed
       after an incident. With IaC, `az deployment group what-if` shows the diff
       between the desired and actual state in under 30 seconds.

    ### The drift problem in practice

    ```
    Day 1 — Engineer adds a network rule via portal for testing.
    Day 5 — Incident. Network rule is the cause. No one remembers adding it.
    Day 6 — IaC diff reveals the undeclared rule immediately.
    ```

    Without IaC, step 6 takes days. With IaC, it takes seconds.

    ### AegisAP's two Bicep entry points

    | Track | Entry point | When to use |
    |---|---|---|
    | `core` | `infra/core.bicep` | Days 0–4; local dev; Storage + Search + OpenAI only |
    | `full` | `infra/full.bicep` | Days 5+; adds PostgreSQL, Key Vault, ACR, ACA, Log Analytics, App Insights |

    > **Convention:** Never deploy by hand in staging or production.
    > Every resource change goes through `az deployment group create` or
    > the GitHub Actions pipeline — no exceptions.
    """)
    return


# ---------------------------------------------------------------------------
# Section 2 – Bicep Anatomy
# ---------------------------------------------------------------------------
@app.cell
def _s2_header(mo):
    mo.md("## 2. Bicep Anatomy")
    return


@app.cell
def _s2_body(mo):
    mo.md("""
    Bicep is Azure's declarative IaC language. It compiles to ARM JSON and supports
    full type checking, module reuse, and compile-time validation.

    ### Five core Bicep concepts

    | Concept | Syntax | Purpose |
    |---|---|---|
    | `resource` | `resource kv 'Microsoft.KeyVault/vaults@2023-07-01' = { ... }` | Declares a single Azure resource |
    | `param` | `param location string = resourceGroup().location` | Externally supplied value — never hardcode secrets here |
    | `module` | `module core './core.bicep' = { ... }` | Reusable template unit — like a function |
    | `output` | `output keyVaultUri string = kv.properties.vaultUri` | Exposes a value to calling templates or CI/CD |
    | `existing` | `resource kv 'Microsoft.KeyVault/vaults@...` `existing = { name: keyVaultName }` | References an already-deployed resource without creating it |

    ### Annotated Bicep — AegisAP Key Vault resource

    ```bicep
    // ① Resource type and API version — always pin the API version
    resource kv 'Microsoft.KeyVault/vaults@2023-07-01' = {
      name: keyVaultName          // ② From param — never hardcoded
      location: location          // ② From param
      properties: {
        sku: { family: 'A', name: 'standard' }
        tenantId: subscription().tenantId  // ③ Built-in function — no hardcoded IDs

        // ④ RBAC model: enableRbacAuthorization = true
        //    This disables legacy access policies — all permissions via RBAC only
        enableRbacAuthorization: true

        // ⑤ Soft-delete and purge protection: mandatory for production
        enableSoftDelete: true
        enablePurgeProtection: true

        publicNetworkAccess: 'Enabled'
      }
    }
    ```

    > **Security note:** `enableRbacAuthorization: true` disables Key Vault's legacy
    > "access policies" model, which allowed granting permissions to ANY principal
    > without audit trail. RBAC adds standard Azure role assignment semantics
    > (assignment ID, scope, principal, role) that appear in the Activity Log.

    ### Annotated Bicep — Role assignment

    ```bicep
    // Grant the workload identity 'Key Vault Secrets User' (read-only)
    // Using the built-in role definition ID — no custom roles needed
    var kvSecretsUserRole = subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '4633458b-17de-408a-b874-0445c86b69e6'  // Key Vault Secrets User
    )

    resource kvWorkloadRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
      scope: kv          // Scoped to THIS Key Vault only — not subscription-wide
      name: guid(kv.id, workloadIdentity.id, kvSecretsUserRole)
      properties: {
        roleDefinitionId: kvSecretsUserRole
        principalId: workloadIdentity.properties.principalId
        principalType: 'ServicePrincipal'
      }
    }
    ```

    ### Bicep workflow

    ```bash
    # 1. Validate template (lint + API checks) — run before every PR
    az deployment group validate \\
      --resource-group rg-aegisap-dev \\
      --template-file infra/full.bicep \\
      --parameters @infra/full.bicepparam

    # 2. Show what would change (no writes)
    az deployment group what-if \\
      --resource-group rg-aegisap-dev \\
      --template-file infra/full.bicep \\
      --parameters @infra/full.bicepparam

    # 3. Deploy
    az deployment group create \\
      --resource-group rg-aegisap-dev \\
      --template-file infra/full.bicep \\
      --parameters @infra/full.bicepparam
    ```
    """)
    return


@app.cell
def _bicep_explorer(mo):
    _resource_options = {
        "Key Vault (Microsoft.KeyVault/vaults)": {
            "why": "Stores residual secrets — credentials for external services that do not support Managed Identity.",
            "security_settings": [
                "`enableRbacAuthorization: true` — RBAC-only; no legacy access policies",
                "`enableSoftDelete: true` + `enablePurgeProtection: true` — prevents accidental/malicious deletion",
                "Public network access enabled; scope down with private endpoints in high-security environments",
            ],
            "runtime_role": "Key Vault Secrets User (4633458b) — read-only; never Secrets Officer",
            "never_do": "Store Azure service endpoints here — they are public; only SECRETS go in Key Vault",
        },
        "Azure OpenAI (Microsoft.CognitiveServices/accounts)": {
            "why": "Hosts LLM model deployments. AegisAP uses gpt-4o for planning/review and gpt-4o-mini for extraction.",
            "security_settings": [
                "`disableLocalAuth: true` — API key authentication disabled; Managed Identity only",
                "Custom subdomain required for Managed Identity token audience",
            ],
            "runtime_role": "Cognitive Services OpenAI User (5e0bd9bd) — generate completions only; never Contributor",
            "never_do": "Pass an API key in environment variables in staging/production",
        },
        "Azure AI Search (Microsoft.Search/searchServices)": {
            "why": "Evidence retrieval for the RAG pipeline. AegisAP uses hybrid search (keyword + vector + RRF).",
            "security_settings": [
                "`disableLocalAuth: true` — API key auth disabled; Managed Identity only",
                "`publicNetworkAccess: 'enabled'` — scope down with private endpoints if needed",
            ],
            "runtime_role": "Search Index Data Reader (1407120a) — query indexes; never Search Service Contributor",
            "never_do": "Use the admin key in application code; it grants full read/write on ALL indexes",
        },
        "PostgreSQL Flexible Server (Microsoft.DBforPostgreSQL/flexibleServers)": {
            "why": "Durable state store for workflow threads, resume checkpoints, and audit logs (Days 5+).",
            "security_settings": [
                "`activeDirectoryAuth: 'Enabled'` + `passwordAuth: 'Disabled'` — Entra auth only",
                "No connection string with password; runtime connects via token from DefaultAzureCredential",
            ],
            "runtime_role": "PostgreSQL Flexible Server — application role granted via `GRANT` statement in migration",
            "never_do": "Set `AEGISAP_POSTGRES_DSN` with a password in staging/production — this fails the security posture gate",
        },
        "Azure Container Registry (Microsoft.ContainerRegistry/registries)": {
            "why": "Private Docker image store. ACA pulls images using Managed Identity — no admin credentials.",
            "security_settings": [
                "`adminUserEnabled: false` — admin user (username/password) disabled",
                "Image pull via `AcrPull` role on the user-assigned workload identity",
            ],
            "runtime_role": "AcrPull (7f951dda) on the workload identity — pull only; never AcrPush for the runtime",
            "never_do": "Enable the admin user; it creates a long-lived username/password that can be exfiltrated",
        },
        "Container Apps Environment (Microsoft.App/managedEnvironments)": {
            "why": "Hosts ACA apps and jobs. Logs flow to Log Analytics; the revision model enables zero-downtime deploys.",
            "security_settings": [
                "Log Analytics integration — all container stdout/stderr and system events go to the workspace",
                "Managed identity for image pull — no registry credentials stored in the environment",
            ],
            "runtime_role": "N/A — the environment itself has no data-plane role; apps within it use their own identities",
            "never_do": "Pass registry credentials via username/password in the ACA app template",
        },
    }

    resource_picker = mo.ui.dropdown(
        options=list(_resource_options.keys()),
        value="Key Vault (Microsoft.KeyVault/vaults)",
        label="Inspect a Bicep resource:",
    )
    resource_picker
    return _resource_options, resource_picker


@app.cell
def _bicep_resource_detail(mo, _resource_options, resource_picker):
    detail = _resource_options[resource_picker.value]
    security_bullets = "\n".join(
        f"  - {s}" for s in detail["security_settings"])
    mo.callout(
        mo.md(f"""
**Why it exists:** {detail['why']}

**Security settings to check:**
{security_bullets}

**Runtime identity role:** `{detail['runtime_role']}`

**Never do:** {detail['never_do']}
        """),
        kind="neutral",
    )
    return detail, security_bullets


# ---------------------------------------------------------------------------
# Section 3 – Four Identity Planes
# ---------------------------------------------------------------------------
@app.cell
def _s3_header(mo):
    mo.md("## 3. AegisAP's Four Identity Planes")
    return


@app.cell
def _s3_body(mo):
    mo.md("""
    AegisAP formalises four separate managed identities — each with distinct permissions
    and a distinct threat surface.  Using a single identity for everything would give
    a compromised container the ability to destroy indexes, rotate secrets, or exfiltrate
    the knowledge base.

    | Plane | Identity name | Principal type | Scope |
    |---|---|---|---|
    | **Runtime API** | `id-aegisap-workload` | User-assigned | Inference, search queries, PG reads/writes, KV secret reads |
    | **Jobs scaffold** | `id-aegisap-jobs` | User-assigned | Same as runtime, plus search index management |
    | **Search admin** | `id-aegisap-search-admin` | User-assigned | Create/delete search indexes only |
    | **Developer / Ops** | Individual Entra accounts + groups | Human | Portal read, log query — NO data writes in production |

    ### Full RBAC matrix

    | Resource | Runtime API | Jobs | Search admin | Dev/Ops |
    |---|---|---|---|---|
    | Azure OpenAI | `Cognitive Services OpenAI User` | `Cognitive Services OpenAI User` | — | `Reader` |
    | Azure AI Search | `Search Index Data Reader` | `Search Index Data Contributor` | `Search Service Contributor` | `Reader` |
    | PostgreSQL | connect (via Entra group) | connect (via Entra group) | — | — |
    | Key Vault | `Key Vault Secrets User` | — | — | `Reader` |
    | ACR | `AcrPull` | `AcrPull` | — | `Reader` |
    | App Insights | — | — | — | `Log Analytics Reader` |

    ### In Bicep

    ```bicep
    // Three identities declared in full.bicep
    resource workloadIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
      name: workloadIdentityName        // id-aegisap-workload
      location: location
    }

    resource jobsIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
      name: jobsIdentityName            // id-aegisap-jobs
      location: location
    }

    resource searchAdminIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
      name: searchAdminIdentityName     // id-aegisap-search-admin
      location: location
    }
    ```

    ### Blast radius principle

    If `id-aegisap-workload` is compromised (e.g., through a container breakout):

    - It can read Key Vault secrets → **impact: credentials for external services leak**
    - It **cannot** modify Key Vault secrets (not `Secrets Officer`)
    - It **cannot** delete or recreate search indexes (not `Search Service Contributor`)
    - It **cannot** push new images to ACR (not `AcrPush`)
    - It **cannot** read other teams' resources (scoped at resource level, not subscription)

    The blast radius is bounded to the services AegisAP actually needs.
    """)
    return


@app.cell
def _identity_plane_picker(mo):
    plane_picker = mo.ui.radio(
        options=[
            "Runtime API (id-aegisap-workload)",
            "Jobs scaffold (id-aegisap-jobs)",
            "Search admin (id-aegisap-search-admin)",
            "Developer / Ops",
        ],
        value="Runtime API (id-aegisap-workload)",
        label="Select an identity plane to inspect:",
    )
    plane_picker
    return (plane_picker,)


@app.cell
def _identity_plane_detail(mo, plane_picker):
    _planes = {
        "Runtime API (id-aegisap-workload)": {
            "description": "The Container App's user-assigned identity. This is the identity that runs inference, retrieves evidence, and writes audit logs during normal operation.",
            "roles": [
                ("Azure OpenAI", "Cognitive Services OpenAI User",
                 "Generate completions — cannot see billing or manage deployments"),
                ("Azure AI Search", "Search Index Data Reader",
                 "Query indexes — cannot create, update, or delete indexes"),
                ("PostgreSQL", "Connect via Entra group membership",
                 "Runtime INSERT/SELECT on aegisap schema tables"),
                ("Key Vault", "Key Vault Secrets User",
                 "Read named secrets — cannot create, update, or delete secrets"),
                ("ACR", "AcrPull", "Pull images — cannot push new images"),
            ],
            "missing_intentionally": ["Search Index Data Contributor", "Key Vault Secrets Officer", "AcrPush"],
        },
        "Jobs scaffold (id-aegisap-jobs)": {
            "description": "Used by Container App Jobs — evaluation runs, migration scripts, and index management tasks that run on a schedule or are triggered by CI/CD.",
            "roles": [
                ("Azure OpenAI", "Cognitive Services OpenAI User",
                 "Needed for eval suite runs that call the model"),
                ("Azure AI Search", "Search Index Data Contributor",
                 "Index documents and update schema — evaluation ingestion"),
                ("PostgreSQL", "Connect via Entra group membership",
                 "Apply migrations, read audit logs for eval"),
                ("Key Vault", "Key Vault Secrets User",
                 "Read LangSmith key if needed for eval traces"),
                ("ACR", "AcrPull", "Pull the eval container image"),
            ],
            "missing_intentionally": ["Search Service Contributor", "Key Vault Secrets Officer"],
        },
        "Search admin (id-aegisap-search-admin)": {
            "description": "Narrow identity for one-time setup scripts: creating and configuring search indexes. Excluded from all other resource types.",
            "roles": [
                ("Azure AI Search", "Search Service Contributor",
                 "Create indexes, manage settings — admin-level on search only"),
            ],
            "missing_intentionally": ["Any role on OpenAI, PostgreSQL, Key Vault, or ACR"],
        },
        "Developer / Ops": {
            "description": "Human engineers. Read-only in production. Cannot trigger deployments or modify data directly — must use the pipeline.",
            "roles": [
                ("All resources", "Reader", "Portal read — view configs, not data"),
                ("Log Analytics / App Insights", "Log Analytics Reader",
                 "Query logs and traces for incident response"),
            ],
            "missing_intentionally": ["Contributor or Owner on any resource", "Data-plane roles (e.g., Search Index Data Reader)"],
        },
    }

    plane = _planes[plane_picker.value]
    role_rows = "\n".join(
        f"| {r[0]} | `{r[1]}` | {r[2]} |"
        for r in plane["roles"]
    )
    missing_bullets = "\n".join(
        f"- `{m}`" for m in plane["missing_intentionally"])

    mo.vstack([
        mo.callout(
            mo.md(f"**{plane_picker.value}**\n\n{plane['description']}"), kind="neutral"),
        mo.md(f"""
**Assigned roles:**

| Resource | Role | Why this role? |
|---|---|---|
{role_rows}

**Intentionally NOT assigned:**
{missing_bullets}
        """),
    ])
    return missing_bullets, plane, plane_picker, role_rows


# ---------------------------------------------------------------------------
# Section 4 – DefaultAzureCredential
# ---------------------------------------------------------------------------
@app.cell
def _s4_header(mo):
    mo.md("## 4. `DefaultAzureCredential`: One Line for Dev and Prod")
    return


@app.cell
def _s4_body(mo):
    mo.md("""
    `DefaultAzureCredential` from the `azure-identity` package tries a chain of
    credential providers in order. The same line of code works in every environment
    without modification.

    ### The credential chain

    ```
    1.  EnvironmentCredential          AZURE_CLIENT_ID + _SECRET + _TENANT_ID in env
    2.  WorkloadIdentityCredential     Kubernetes workload identity federation
    3.  ManagedIdentityCredential  ◄── ACA production path
    4.  AzureCliCredential         ◄── Local dev `az login` path
    5.  AzurePowerShellCredential
    6.  AzureDeveloperCliCredential
    ```

    In **local development**: step 4 fires — your `az login` session provides a token.
    In **production ACA**: step 3 fires — the Container App's managed identity provides a token.

    ### Usage across AegisAP services

    ```python
    from azure.identity import DefaultAzureCredential

    credential = DefaultAzureCredential()

    # Azure OpenAI
    from openai import AzureOpenAI
    client = AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_ad_token_provider=credential.get_token,
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    )

    # Azure AI Search
    from azure.search.documents import SearchClient
    search = SearchClient(
        endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
        index_name=os.environ["AZURE_SEARCH_INDEX_NAME"],
        credential=credential,
    )

    # Key Vault
    from azure.keyvault.secrets import SecretClient
    kv = SecretClient(
        vault_url=os.environ["AZURE_KEY_VAULT_URI"],
        credential=credential,
    )
    ```

    ### Production tuning

    ```python
    from azure.identity import DefaultAzureCredential

    # In ACA: exclude sources that cannot fire in a containerised environment
    # This avoids long credential-chain delays when workload identity is absent
    credential = DefaultAzureCredential(
        exclude_workload_identity_credential=True,   # Not using AKS
        exclude_environment_credential=True,          # No AZURE_CLIENT_SECRET in prod
        exclude_azure_developer_cli_credential=True,
        exclude_powershell_credential=True,
    )
    ```

    > **Never** use `AzureCliCredential` directly in production code — it requires
    > the Azure CLI to be installed and will always fail inside a container without it.

    ### Testing credential resolution

    ```python
    import logging
    logging.basicConfig(level=logging.DEBUG)

    # With DEBUG logging enabled, the SDK logs which credential source fired:
    # azure.identity INFO: DefaultAzureCredential.get_token succeeded with ManagedIdentityCredential
    ```
    """)
    return


# ---------------------------------------------------------------------------
# Section 5 – Key Vault Contracts
# ---------------------------------------------------------------------------
@app.cell
def _s5_header(mo):
    mo.md("## 5. Key Vault Access Contracts")
    return


@app.cell
def _s5_body(mo):
    mo.md("""
    Key Vault holds **residual secrets** — credentials for services that do not
    support Managed Identity.  It does NOT hold credentials for services that do.

    ### What goes IN Key Vault

    | Secret name | Value type | Why |
    |---|---|---|
    | `langsmith-api-key` | LangSmith token | External SaaS; no Azure Managed Identity support |
    | `notification-webhook-token` | Third-party webhook | External; no Azure identity |

    ### What does NOT go in Key Vault

    | Service | Why Key Vault is NOT needed |
    |---|---|
    | Azure OpenAI | `DefaultAzureCredential` + `Cognitive Services OpenAI User` RBAC |
    | Azure AI Search | `DefaultAzureCredential` + `Search Index Data Reader` RBAC |
    | PostgreSQL | Entra authentication — token from `DefaultAzureCredential` |
    | Azure Blob Storage | `DefaultAzureCredential` + `Storage Blob Data Reader` RBAC |

    > **Security posture gate rule:** If `AZURE_OPENAI_API_KEY` appears as an
    > environment variable in the Container App, the security posture gate **fails
    > the release**. The endpoint only — never the key.

    ### Key Vault access pattern

    ```python
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential
    import os

    def get_secret(name: str) -> str:
        \"\"\"Read a single secret from Key Vault. Never cache the value.\"\"\"
        client = SecretClient(
            vault_url=os.environ["AZURE_KEY_VAULT_URI"],
            credential=DefaultAzureCredential(),
        )
        return client.get_secret(name).value
    ```

    ### Best practices

    - Grant only `Key Vault Secrets User` (read) to the runtime identity.
      Never `Key Vault Secrets Officer` (read + write + delete).
    - Enable **soft-delete** (`enableSoftDelete: true`) and
      **purge protection** (`enablePurgeProtection: true`) in Bicep.
      Without these, a compromised identity can permanently delete secrets.
    - Use Key Vault's **rotation policies** for supported secret types.
      LangSmith API keys: rotate quarterly minimum.
    """)
    return


@app.cell
def _kv_contract_quiz(mo):
    _items = {
        "Azure OpenAI endpoint (https://my-aoai.openai.azure.com/)":
            ("not_kv", "This is a public endpoint — not a secret. Store as a plain environment variable `AZURE_OPENAI_ENDPOINT`. Access via Managed Identity, not API key."),
        "Azure OpenAI API key":
            ("forbidden", "Never store this. `disableLocalAuth: true` in Bicep means this key doesn't even exist in production. Security posture gate BLOCKS the release if it's present."),
        "LangSmith API key (ls-...)":
            ("kv", "LangSmith is an external SaaS with no Azure identity support. This is a genuine residual secret → store in Key Vault as `langsmith-api-key`."),
        "PostgreSQL connection string with password":
            ("forbidden", "Forbidden — security posture gate fails if `AEGISAP_POSTGRES_DSN` contains a password. Use Entra auth (token from DefaultAzureCredential) instead."),
        "Azure AI Search endpoint":
            ("not_kv", "Public endpoint — not a secret. Store as `AZURE_SEARCH_ENDPOINT`. Access via DefaultAzureCredential."),
        "Notification webhook token (third-party)":
            ("kv", "Third-party service with no Azure identity support. Genuine residual secret → Key Vault."),
        "ACR login server URL":
            ("not_kv", "Public URL — not a secret. The Container App pulls images via AcrPull RBAC role, no credentials needed."),
    }

    item_picker = mo.ui.dropdown(
        options=list(_items.keys()),
        value="LangSmith API key (ls-...)",
        label="Where should this value live?",
    )
    item_picker
    return _items, item_picker


@app.cell
def _kv_contract_answer(mo, _items, item_picker):
    classification, explanation = _items[item_picker.value]
    kind_map = {"kv": "success", "not_kv": "neutral", "forbidden": "danger"}
    label_map = {
        "kv": "✅ Store in Key Vault",
        "not_kv": "ℹ️  Plain environment variable (not a secret)",
        "forbidden": "❌ Forbidden — must NOT exist in staging/production",
    }
    mo.callout(
        mo.md(f"**{label_map[classification]}**\n\n{explanation}"),
        kind=kind_map[classification],
    )
    return classification, explanation, item_picker, kind_map, label_map


# ---------------------------------------------------------------------------
# Section 6 – GitHub Actions OIDC Federation
# ---------------------------------------------------------------------------
@app.cell
def _s6_header(mo):
    mo.md("## 6. GitHub Actions OIDC Federation: No Stored Secrets in CI/CD")
    return


@app.cell
def _s6_body(mo):
    mo.md("""
    Traditional CI/CD stores a Service Principal client secret as a GitHub Actions
    secret.  OIDC federation eliminates the secret entirely.

    ### How OIDC federation works

    ```
    GitHub Actions job starts
           │
           ▼
    GitHub generates a short-lived OIDC token (JWT) for THIS specific run
    Token claims: repo, branch, workflow, run ID — all verifiable
           │
           ▼
    azure/login action presents token to Microsoft Entra ID
           │
           ▼
    Entra validates: correct repo? correct branch? correct workflow?
           │
           ▼
    Entra issues an access token valid for THIS job only (~1 hour)
           │
           ▼
    az / Azure SDK calls use the token — no secret ever stored or transmitted
    ```

    ### Comparison

    | Property | Service Principal + secret | OIDC federation |
    |---|---|---|
    | Secret stored | GitHub Secrets | **None** |
    | Token lifetime | Months (must rotate) | Minutes (per-job) |
    | Scope | Any workflow that knows the secret | Bound to specific repo + branch + workflow |
    | Rotation burden | Manual | **None** |
    | Exfiltration risk | Secret leaked → permanent access | Leaked token expires in minutes |
    | Audit trail | Client secret use not tied to a specific run | Every use has a unique run ID |

    ### Bicep: configuring the federated credential

    ```bicep
    // The deployment identity is a user-assigned managed identity
    resource deployIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
      name: 'id-aegisap-deploy'
      location: location
    }

    // Federated credential bound to EXACTLY this repo + branch + workflow
    resource federatedCredential 'Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials@2023-01-31' = {
      parent: deployIdentity
      name: 'github-deploy-main'
      properties: {
        audiences: ['api://AzureADTokenExchange']
        issuer: 'https://token.issuer.actions.githubusercontent.com'
        // Subject scopes the credential to a SPECIFIC workflow on a SPECIFIC branch
        // Never use a wildcard here — it defeats the purpose
        subject: 'repo:your-org/agentic-accounts-payable-orchestrator:ref:refs/heads/main'
      }
    }
    ```

    ### GitHub Actions workflow snippet

    ```yaml
    jobs:
      deploy:
        runs-on: ubuntu-latest
        # Required for OIDC — grants the job the right to request the token
        permissions:
          id-token: write
          contents: read

        steps:
          - uses: actions/checkout@v4

          - name: Azure login (OIDC — no secrets)
            uses: azure/login@v2
            with:
              client-id: ${{ vars.AZURE_CLIENT_ID }}      # non-secret var
              tenant-id: ${{ vars.AZURE_TENANT_ID }}      # non-secret var
              subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}  # non-secret var

          - name: Build and push image (SHA tag)
            run: |
              az acr build \\
                --registry ${{ vars.ACR_NAME }} \\
                --image aegisap-api:${{ github.sha }} \\
                docker/Dockerfile.api

          - name: Run acceptance gates before deploy
            run: uv run python scripts/check_all_gates.py --skip-deploy

          - name: Deploy to ACA (creates new revision)
            run: |
              az containerapp update \\
                --name aegisap-api \\
                --resource-group ${{ vars.RESOURCE_GROUP }} \\
                --image ${{ vars.ACR_NAME }}.azurecr.io/aegisap-api:${{ github.sha }} \\
                --revision-suffix rev-${{ github.sha }}
    ```

    > **Rule:** Never use `latest` as an image tag in a deployment. Always use the
    > Git SHA. This makes every deployed revision uniquely traceable to a commit.
    """)
    return


@app.cell
def _oidc_diagram(mo):
    try:
        import plotly.graph_objects as go

        labels = [
            "GitHub\nActions Job",
            "GitHub OIDC\nToken (JWT)",
            "Microsoft\nEntra ID",
            "Access Token\n(~1 hour)",
            "Azure\nResources",
        ]
        x = [0.1, 0.3, 0.5, 0.7, 0.9]
        y = [0.5, 0.5, 0.5, 0.5, 0.5]

        fig = go.Figure()
        # Nodes
        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode="markers+text",
            marker=dict(size=50, color=[
                "#3498DB", "#F39C12", "#9B59B6", "#27AE60", "#E74C3C"
            ]),
            text=labels,
            textposition="bottom center",
            hoverinfo="text",
        ))
        # Arrows as annotations
        arrow_labels = ["OIDC token request",
                        "Validate claims", "Access token", "API calls"]
        for i in range(len(x) - 1):
            mid_x = (x[i] + x[i + 1]) / 2
            fig.add_annotation(
                x=x[i + 1] - 0.02, y=0.52,
                ax=x[i] + 0.02, ay=0.52,
                xref="paper", yref="paper",
                axref="paper", ayref="paper",
                arrowhead=2, arrowsize=1.2, arrowwidth=2,
                arrowcolor="#555",
                text=arrow_labels[i],
                font=dict(size=9, color="#555"),
                showarrow=True,
            )

        fig.add_annotation(
            x=0.5, y=0.72, xref="paper", yref="paper",
            text="No secret is ever stored or transmitted",
            font=dict(size=12, color="#27AE60"),
            showarrow=False,
        )
        fig.update_layout(
            title="OIDC Federation Flow — No Secrets",
            showlegend=False,
            height=280,
            margin=dict(t=60, b=80, l=20, r=20),
            xaxis=dict(visible=False, range=[0, 1]),
            yaxis=dict(visible=False, range=[0.2, 0.9]),
        )
        mo.ui.plotly(fig)
    except ImportError:
        mo.callout(
            mo.md("Install `plotly` to see the OIDC flow diagram."), kind="warn")
    return


# ---------------------------------------------------------------------------
# Section 7 – ACA Revision Model
# ---------------------------------------------------------------------------
@app.cell
def _s7_header(mo):
    mo.md("## 7. Azure Container Apps Revision Model: Zero-Downtime Deployment")
    return


@app.cell
def _s7_body(mo):
    mo.md("""
    ACA's **revision model** is the operational unit for safe deployments.
    Every code or config change creates an immutable **revision** — a snapshot
    of the container image and configuration at that point in time.

    ### Key concepts

    | Concept | Description |
    |---|---|
    | **Revision** | Immutable snapshot of image + config. The rollback unit. |
    | **Traffic split** | Percentage of requests routed to each active revision. |
    | **Inactive revision** | A revision that exists but receives 0% traffic — kept for fast rollback. |
    | **SHA-tagged image** | `aegisap-api:<git-sha>` — never `latest`. Traceability + unambiguous rollback. |

    ### Deployment flow (with gate checks)

    ```
    1. Push code → GitHub Actions triggers
           │
           ▼
    2. Build image tagged with git SHA
       az acr build --image aegisap-api:<sha>
           │
           ▼
    3. Run acceptance gates (--skip-deploy): all 6 must pass
       python scripts/check_all_gates.py --skip-deploy
           │
           ▼ (all gates pass)
    4. Deploy new revision (receives 0% traffic initially)
       az containerapp update --revision-suffix rev-<sha>
           │
           ▼
    5. Post-deploy ACA health gate: revision must be 'Running'
       gate_aca_health() checks provision_state + HTTP 200
           │
           ▼ (health passes)
    6. Shift traffic to new revision
       az containerapp ingress traffic set --revision-weight "rev-<sha>=100"
    ```

    ### Rollback procedure (< 2 minutes)

    ```bash
    # Step 1: Allow multiple revisions to be active simultaneously
    az containerapp revision set-mode \\
      --name aegisap-api \\
      --resource-group rg-aegisap-prod \\
      --mode multiple

    # Step 2: Shift 100% traffic back to the last known-good revision
    # No re-deploy — the revision image is still in ACR and already warm
    az containerapp ingress traffic set \\
      --name aegisap-api \\
      --resource-group rg-aegisap-prod \\
      --revision-weight "aegisap-api--stable=100"
    ```

    > **Why this is fast:** The stable revision's container image is already pulled
    > and the instances may still be running (inactive = 0% traffic, but not
    > necessarily stopped). Traffic shift is a control-plane operation — it does not
    > require a new container start.

    ### Production tagging convention

    ```bash
    # Human-readable revision suffix (also in deploy script)
    REVISION_SUFFIX="rev-$(date +%Y%m%d)-${GITHUB_SHA:0:7}"
    # e.g. rev-20240326-a1b2c3
    ```

    Keep at least **two previous revisions** inactive so one rollback layer is
    always available without hitting the revision retention limit.
    """)
    return


@app.cell
def _aca_revision_chart(mo):
    try:
        import plotly.graph_objects as go

        stages = [
            "New revision created\n(0% traffic)",
            "Gates run:\n-skip-deploy",
            "ACA health check\n(HTTP 200?)",
            "Traffic shift:\n100% → new rev",
            "Old revision\n(inactive, kept)",
        ]
        colors = ["#4A90D9", "#F39C12", "#F39C12", "#27AE60", "#95A5A6"]
        results = ["Created", "All 6 pass", "Healthy", "Live", "Kept 2 revs"]

        fig = go.Figure()
        for i, (stage, color, result) in enumerate(zip(stages, colors, results)):
            fig.add_trace(go.Bar(
                x=[result],
                y=[1],
                name=stage,
                marker_color=color,
                text=[f"Step {i + 1}\n{stage}"],
                textposition="inside",
                showlegend=False,
            ))
        # Reconfigure as horizontal flow
        fig = go.Figure(go.Bar(
            x=list(range(len(stages))),
            y=[1] * len(stages),
            text=[f"<b>Step {i+1}</b><br>{s}" for i, s in enumerate(stages)],
            textposition="inside",
            marker_color=colors,
            showlegend=False,
        ))
        fig.update_layout(
            title="ACA Zero-Downtime Deployment Flow",
            xaxis=dict(
                tickvals=list(range(len(stages))),
                ticktext=[f"Step {i+1}" for i in range(len(stages))],
            ),
            yaxis=dict(visible=False, range=[0, 1.5]),
            height=250, margin=dict(t=50, b=40),
            bargap=0.1,
        )
        mo.ui.plotly(fig)
    except ImportError:
        mo.callout(
            mo.md("Install `plotly` to see the deployment flow chart."), kind="warn")
    return


# ---------------------------------------------------------------------------
# Section 8 – The Six Acceptance Gates
# ---------------------------------------------------------------------------
@app.cell
def _s8_header(mo):
    mo.md("## 8. The Six Acceptance Gates")
    return


@app.cell
def _s8_body(mo):
    mo.md("""
    Before any revision can receive production traffic, six machine-checked gates
    must pass.  A single failure blocks the release.

    | Gate | What it checks | Feeds from |
    |---|---|---|
    | `security_posture` | No forbidden secrets, security contract met | `aegisap.security.posture.run_posture_check()` |
    | `eval_regression` | No score drop below threshold vs. baseline | `build/day8/regression_baseline.json` |
    | `budget` | Sample cost ledger within daily ceiling | `build/day9/routing_report.json` |
    | `refusal_safety` | Malicious-case refusal rate ≥ threshold | `build/day6/golden_thread_day6.json` |
    | `resume_safety` | Resume replay has zero duplicate side effects | `build/day5/golden_thread_day5_resumed.json` |
    | `aca_health` | Target revision is Running + HTTP 200 | Live Azure ACA API |

    ### What the security posture gate blocks

    | Forbidden condition | Why |
    |---|---|
    | `AZURE_OPENAI_API_KEY` in env | Managed Identity must be used; key should not exist |
    | ACR pull via username/password | Must use `AcrPull` RBAC on managed identity |
    | `LANGSMITH_API_KEY` absent from Key Vault | Must be a Key Vault secret, not a plain env var |
    | `AEGISAP_POSTGRES_DSN` contains a password | Entra auth required; password DSN is forbidden |

    ### Running the gates locally

    ```bash
    # Run all gates, skip the live ACA check (before deploy step):
    uv run python scripts/check_all_gates.py --skip-deploy

    # Run all gates including ACA health (after deploy):
    uv run python scripts/check_all_gates.py

    # Write release envelope to a file
    uv run python scripts/check_all_gates.py \\
      --out build/day10/release_envelope.json
    ```

    ### Release envelope structure

    ```json
    {
      "all_passed": true,
      "gates": [
        {
          "name": "security_posture",
          "passed": true,
          "detail": "All checks passed.",
          "evidence": { "checks": ["no_openai_key", "no_acr_password", ...] }
        },
        {
          "name": "eval_regression",
          "passed": true,
          "detail": "No regressions.",
          "evidence": { "regressed": [] }
        }
      ]
    }
    ```
    """)
    return


@app.cell
def _live_gate_runner(mo, Path):
    mo.md("### Live Gate Runner")
    return


@app.cell
def _run_gates(mo, Path):
    """Run gates with skip_deploy=True and display results."""
    try:
        from aegisap.deploy.gates import run_all_gates, build_release_envelope, format_gate_row

        results = run_all_gates(skip_deploy=True)
        rows = [format_gate_row(r) for r in results]
        all_passed = all(r.passed for r in results)

        rows_md = "\n".join(f"| `{r.name}` | {'✅ PASS' if r.passed else '❌ FAIL'} | {r.detail} |"
                            for r in results)
        table = (
            "| Gate | Result | Detail |\n"
            "|---|---|---|\n"
            + rows_md
        )
        overall_kind = "success" if all_passed else "warn"
        overall_msg = "🟢 All gates pass — revision eligible for traffic shift" if all_passed \
            else "🟡 One or more gates need attention (expected before Day 9/10 artifacts exist)"

        mo.vstack([
            mo.md(table),
            mo.callout(mo.md(overall_msg), kind=overall_kind),
        ])
    except Exception as e:
        mo.callout(
            mo.md(
                f"Gate runner returned: `{e}`\n\n"
                "This is expected in a notebook-only environment. "
                "Run `scripts/check_all_gates.py --skip-deploy` in a terminal "
                "once Day 5, 6, 9 artifacts exist."
            ),
            kind="neutral",
        )
    return


@app.cell
def _break_diagnose_header(mo):
    mo.md("""
    ### Break and Diagnose: Gate Failure Simulation

    Check the box below to override the `budget` gate to a **FAIL** state and observe
    what a blocked release looks like. Then answer the three diagnostic questions.
    """)
    return


@app.cell
def _bd_checkbox(mo):
    _bd_toggle = mo.ui.checkbox(
        label="Simulate budget gate failure (override budget gate result to FAIL)",
        value=False,
    )
    _bd_toggle
    return (_bd_toggle,)


@app.cell
def _bd_output(mo, json, _bd_toggle):
    if _bd_toggle.value:
        _failed_envelope = {
            "all_passed": False,
            "gates": [
                {
                    "name": "security_posture",
                    "passed": True,
                    "detail": "All checks passed.",
                },
                {
                    "name": "eval_regression",
                    "passed": True,
                    "detail": "No regressions detected.",
                },
                {
                    "name": "budget",
                    "passed": False,
                    "detail": "[SIMULATED] $6.24 / $5.00 daily limit. EXCEEDS BUDGET.",
                    "evidence": {
                        "total_cost_usd": 6.24,
                        "daily_limit_usd": 5.00,
                        "within_budget": False,
                        "overage_usd": 1.24,
                    },
                },
                {
                    "name": "refusal_safety",
                    "passed": True,
                    "detail": "Refusal rate: 97.3% (required >= 95.0%)",
                },
                {
                    "name": "resume_safety",
                    "passed": True,
                    "detail": "No duplicate side effects detected.",
                },
                {
                    "name": "aca_health",
                    "passed": True,
                    "detail": "Revision Running. HTTP 200.",
                },
            ],
        }
        mo.vstack([
            mo.callout(
                mo.md(
                    "**🔴 Release BLOCKED: `budget` gate failed.**  \n"
                    "The revision cannot receive production traffic until the gate passes."
                ),
                kind="danger",
            ),
            mo.md("```json\n" + json.dumps(_failed_envelope, indent=2) + "\n```"),
            mo.md("""
**Diagnose this failure — answer these three questions before looking at the analysis:**

1. Which gate failed and what does it check?
2. What is the specific condition that caused the failure?
3. What is the remediation, and what is the rollback command if this reached production?
            """),
            mo.accordion({
                "Show analysis": mo.md("""
**Gate that failed:** `budget`

**What the `budget` gate checks:** It reads `build/day9/routing_report.json` and
verifies that the sample cost ledger's daily total stays within the ceiling set
by `DAILY_BUDGET_USD` (default `$5.00` / day).

**Specific condition:** The simulated sample shows `$6.24` for the current period — `$1.24`
over the `$5.00` ceiling. The `within_budget` field in the routing report is `false`.

**Remediation steps:**

1. Open `build/day9/routing_report.json` and identify which task class accounts for
   the most tokens — look for high `estimated_cost_usd` rows.
2. Check whether GPT-4o is being used for task classes where GPT-4o-mini would be
   sufficient (e.g., `extract_fields` vs. `compliance_review`).
3. Enable semantic caching for repeated retrieval queries on high-volume vendor paths.
4. If the budget ceiling is genuinely too low for the workload, raise `DAILY_BUDGET_USD`
   in the ACA environment *with business sign-off* — do not simply raise it silently.

**Rollback command (if this revision had already reached production):**

```bash
az containerapp ingress traffic set \\
  --name aegisap-api \\
  --resource-group rg-aegisap-prod \\
  --revision-weight "aegisap-api--stable=100"
```

**Why this gate exists:** Without a budget gate, a misconfigured model routing policy
(e.g., always using GPT-4o, disabling caching) could increase costs 10× before anyone
notices the monthly bill. The gate makes cost overrun a release-blocking event, not
a retrospective finance problem.
                """),
            }),
        ])
    else:
        mo.callout(
            mo.md(
                "Check the box above to simulate a `budget` gate failure "
                "and see what the blocked release envelope looks like."
            ),
            kind="info",
        )
    return


# ---------------------------------------------------------------------------
# Lab Exercises
# ---------------------------------------------------------------------------
@app.cell
def _exercises_header(mo):
    mo.md("## Exercises")
    return


@app.cell
def _exercise_1(mo):
    mo.accordion({
        "Exercise 1 — Read and Extend a Bicep Template": mo.vstack([
            mo.md("""
**Task:**

Open `infra/full.bicep`. Without running any deployment:

1. Identify the three user-assigned managed identities declared in the template.
2. Find the PostgreSQL server resource. What setting disables password authentication?
3. The `infra/modules/diagnostic_settings.bicep` module is referenced for Key Vault.
   What are the parameters passed to the module, and what does the module likely do?
4. Write a NEW Bicep role assignment that grants `id-aegisap-jobs` the
   `Storage Blob Data Contributor` role (role ID: `ba92f5b4-2d11-453d-a403-e96b0029c9fe`)
   on the storage account. Use the existing `jobsIdentity` resource reference.
            """),
            mo.accordion({
                "Show solution": mo.md(r"""
**1. Three user-assigned managed identities:**

```bicep
resource workloadIdentity  // id-aegisap-workload — runtime API
resource jobsIdentity      // id-aegisap-jobs — background jobs
resource searchAdminIdentity  // id-aegisap-search-admin — index admin
```
These are declared near the Container Apps environment resource.

**2. PostgreSQL password auth disabled:**

```bicep
properties: {
  authConfig: {
    activeDirectoryAuth: 'Enabled'
    passwordAuth: 'Disabled'    // ← this setting
    tenantId: subscription().tenantId
  }
```
`passwordAuth: 'Disabled'` forces all connections to use Entra tokens.

**3. `diagnostic_settings.bicep` module:**

Parameters passed:
- `keyVaultName: kv.name`
- `logAnalyticsWorkspaceName: law.name`

The module creates a `Microsoft.Insights/diagnosticSettings` resource scoped
to the Key Vault, forwarding audit logs (AuditEvent, AzurePolicyEvaluationDetails)
to the Log Analytics workspace. This enables KQL queries over who accessed
which secret and when — essential for compliance audit evidence.

**4. New role assignment:**

```bicep
var storageBlobDataContributorRole = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  'ba92f5b4-2d11-453d-a403-e96b0029c9fe'   // Storage Blob Data Contributor
)

resource jobsStorageRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  // Scope to the storage account — not the subscription
  scope: st
  name: guid(st.id, jobsIdentity.id, storageBlobDataContributorRole)
  properties: {
    roleDefinitionId: storageBlobDataContributorRole
    principalId: jobsIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}
```

Key points:
- `scope: st` — important: scoped to the storage resource, not subscription-wide
- `guid(...)` — deterministic name prevents duplicate assignments on re-deploy
- `principalType: 'ServicePrincipal'` — required for managed identities (they are service principals)
                """),
            }),
        ]),
    })
    return


@app.cell
def _exercise_2(mo):
    mo.accordion({
        "Exercise 2 — Design the OIDC Federated Credential Scope": mo.vstack([
            mo.md("""
**Scenario:** Your team maintains two branches: `main` (production deployments)
and `staging` (staging deployments). You need separate OIDC federated credentials
for each. Additionally, there's a `security-scan.yml` workflow that should not
be able to deploy — it needs read-only access.

**Task:**

1. Sketch the Bicep `federatedIdentityCredentials` for the `main` → production
   deployment, the `staging` → staging deployment, and a DENY for the security
   scan workflow (hint: simply don't create a credential for it).
2. What `subject` value would you use for each?
3. What would happen if a developer opened a Pull Request and tried to run a
   workflow that deploys from a feature branch `feature/fix-123`?
            """),
            mo.accordion({
                "Show solution": mo.md(r"""
**1 & 2. Bicep federated credentials:**

```bicep
// Production deploy identity (separate from staging)
resource deployIdentityProd 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-aegisap-deploy-prod'
  location: location
}

resource federatedCredProd 'Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials@2023-01-31' = {
  parent: deployIdentityProd
  name: 'github-deploy-main'
  properties: {
    audiences: ['api://AzureADTokenExchange']
    issuer: 'https://token.issuer.actions.githubusercontent.com'
    // Bound to: main branch + deploy-production.yml workflow
    subject: 'repo:your-org/agentic-accounts-payable-orchestrator:ref:refs/heads/main'
  }
}

// Staging deploy identity
resource deployIdentityStaging 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-aegisap-deploy-staging'
  location: location
}

resource federatedCredStaging 'Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials@2023-01-31' = {
  parent: deployIdentityStaging
  name: 'github-deploy-staging'
  properties: {
    audiences: ['api://AzureADTokenExchange']
    issuer: 'https://token.issuer.actions.githubusercontent.com'
    subject: 'repo:your-org/agentic-accounts-payable-orchestrator:ref:refs/heads/staging'
  }
}

// Security scan workflow: NO federated credential created.
// The workflow only needs read permission on the repo — no Azure access needed.
// If it accidentally tries 'azure/login', it will fail with "subject not found".
```

**3. Feature branch PR:**

Entra ID validates the `subject` claim in the OIDC token. A feature branch
workflow produces a token with:
```
subject: repo:your-org/...:ref:refs/heads/feature/fix-123
```

This does NOT match either federated credential (`main` or `staging`).
Entra rejects the token with an authentication error.

**The feature branch cannot deploy — by design.** This is one of the key security
properties of OIDC federation. No secret to steal means no way to deploy from
an unauthorised branch, even with code execution on the runner.
                """),
            }),
        ]),
    })
    return


@app.cell
def _exercise_3(mo):
    mo.accordion({
        "Exercise 3 — Trace a Security Posture Gate Failure": mo.vstack([
            mo.md("""
**Scenario:** A new staging deployment fails on the `security_posture` gate with:

```
[FAIL] security_posture      Failed: openai_api_key_found, postgres_password_dsn_found
```

**Task:**

1. Explain specifically what each failing check means — what was detected?
2. What changes need to be made to the deployment configuration to fix each check?
3. After the fix is deployed, the `eval_regression` gate also fails:
   ```
   [FAIL] eval_regression  No regression baseline found. Run Day 8 notebook first.
   ```
   What is the correct remediation? Is this a security issue or a process gap?
            """),
            mo.accordion({
                "Show solution": mo.md(r"""
**1. What each failure means:**

`openai_api_key_found`:
- An environment variable named `AZURE_OPENAI_API_KEY` (or similar) is present
  in the Container App's environment configuration.
- The API key authentication path is defined in `infra/full.bicep` as
  `disableLocalAuth: true`, which means this key should not exist in the runtime.
  Its presence indicates either (a) the Bicep deployment didn't run before the
  ACA configuration, or (b) a developer added the key manually via portal or CLI.

`postgres_password_dsn_found`:
- An environment variable `AEGISAP_POSTGRES_DSN` is present and contains a password.
- The PostgreSQL Flexible Server is configured with `passwordAuth: 'Disabled'`
  in Bicep. A password DSN will fail at runtime AND indicates a security control failure.

**2. Fixes:**

Fix 1 — OpenAI API key:
```bash
# Remove the forbidden environment variable from the Container App
az containerapp update \\
  --name aegisap-api \\
  --resource-group rg-aegisap-staging \\
  --remove-env-vars AZURE_OPENAI_API_KEY

# Verify the workload identity has the correct role
az role assignment list \\
  --assignee <workload-identity-principal-id> \\
  --scope /subscriptions/.../providers/Microsoft.CognitiveServices/accounts/aoai-name
# Expected: Cognitive Services OpenAI User (5e0bd9bd...)
```

Fix 2 — PostgreSQL password DSN:
```bash
# Remove the password DSN
az containerapp update \\
  --name aegisap-api \\
  --resource-group rg-aegisap-staging \\
  --remove-env-vars AEGISAP_POSTGRES_DSN

# Set the correct Entra-auth connection string (no password)
az containerapp update \\
  --name aegisap-api \\
  --set-env-vars "AEGISAP_POSTGRES_HOST=<host>" \\
                 "AEGISAP_POSTGRES_DB=aegisap" \\
                 "AEGISAP_POSTGRES_USER=<entra-user>"
# The application uses DefaultAzureCredential to get a token for Entra auth
```

**3. `eval_regression` gap:**

This is a **process gap**, not a security issue.

The `eval_regression` gate requires `build/day8/regression_baseline.json`,
which is written by running the Day 8 notebook's baseline cell after a known-good
eval suite run.

Remediation:
1. Run the eval suite: `uv run python -m evals.run_eval_suite --suite synthetic`
2. Open the Day 8 notebook and run the regression baseline cell to record scores
3. Re-run `check_all_gates.py --skip-deploy` — `eval_regression` should now pass

The gate is blocking correctly — there is no baseline to compare against, so the
system cannot know if the current build regresses. Generating the baseline is
the expected pre-deployment step for a new environment.
                """),
            }),
        ]),
    })
    return


@app.cell
def _exercise_4(mo):
    mo.accordion({
        "Exercise 4 — Design a Canary Deployment Strategy": mo.vstack([
            mo.md("""
**Context:** AegisAP processes 500 invoices per day in production. The team wants
to introduce canary deployments: route 10% of traffic to the new revision, observe
for 30 minutes, then shift 100% if no errors.

The current deployment shifts 100% immediately after gate checks.

**Task:**

1. Identify the `az containerapp ingress traffic set` commands for:
   - Initial canary: 10% new revision, 90% stable
   - Full shift: 100% new revision
   - Emergency rollback: 100% back to stable
2. What metric(s) would you monitor during the 30-minute canary window?
3. What is the risk with AegisAP specifically (as an accounts-payable orchestrator)
   of running two model revisions simultaneously?
            """),
            mo.accordion({
                "Show solution": mo.md(r"""
**1. Traffic shift commands:**

```bash
# Initial canary: 10% to new, 90% to stable revision
# Requires 'multiple' revision mode
az containerapp revision set-mode \\
  --name aegisap-api \\
  --resource-group rg-aegisap-prod \\
  --mode multiple

az containerapp ingress traffic set \\
  --name aegisap-api \\
  --resource-group rg-aegisap-prod \\
  --revision-weight \\
    "aegisap-api--stable=90" \\
    "aegisap-api--rev-$(git rev-parse --short HEAD)=10"

# Wait 30 minutes, evaluate metrics...

# Full shift to new revision (canary graduates)
az containerapp ingress traffic set \\
  --name aegisap-api \\
  --resource-group rg-aegisap-prod \\
  --revision-weight "aegisap-api--rev-$(git rev-parse --short HEAD)=100"

# Emergency rollback (no re-deploy needed)
az containerapp ingress traffic set \\
  --name aegisap-api \\
  --resource-group rg-aegisap-prod \\
  --revision-weight "aegisap-api--stable=100"
```

**2. Metrics to monitor during canary window:**

| Metric | Source | Alert threshold |
|---|---|---|
| HTTP 5xx error rate | App Insights / Log Analytics | > 0.5% — new revision is crashing |
| `mandatory_escalation_recall` on canary slice | Custom trace attribute | Any miss → immediate rollback |
| `outcome = not_authorised_to_continue` rate | Trace attribute | Spike > 2x baseline → model behaving differently |
| P99 latency | App Insights / ACA metrics | > 2× baseline → performance regression |
| Structured refusal rate on malicious cases | Eval suite alert | < 1.0 → safety regression |

**3. Risk specific to AegisAP:**

Running two model revisions simultaneously creates **split decision risk**:

- Invoice `INV-001` arrives, gets routed to the canary revision (10%) which uses
  a new prompt — produces `needs_human_review`
- Invoice `INV-002` (very similar) gets routed to stable — produces `approved_to_proceed`

An auditor reviewing the audit log will see two similar invoices treated differently
for no apparent reason. This creates:
- **Audit inconsistency** — decisions can't be compared against a single policy
- **Compliance exposure** — if the stable path auto-approves something the canary
  would flag, the canary's safety improvement doesn't protect those 90% of cases

**Mitigation:** Use **session affinity** or **case-level routing** — route all
invoices for a given vendor or case class to the same revision during the canary
window. This preserves decision consistency per vendor while still exercising
the canary revision on a meaningful subset.

For financial-control workloads, a more conservative rollout is:
- 30-minute canary on read-only probes only (retrieval + extraction)
- Batch replay of the previous 24 hours of cases through both revisions
- Compare decisions before shifting any live traffic
                """),
            }),
        ]),
    })
    return


# ---------------------------------------------------------------------------
# Artifact
# ---------------------------------------------------------------------------
@app.cell
def _regression_baseline(mo, json, Path):
    """Write regression baseline from current eval thresholds (simulated scores)."""
    import datetime as _dt

    _baseline = {
        "recorded_at": _dt.datetime.utcnow().isoformat() + "Z",
        "source": "day8_notebook_initial_baseline",
        "scores": {
            "faithfulness": 0.92,
            "compliance_decision_accuracy": 0.94,
            "mandatory_escalation_recall": 1.00,
            "structured_refusal_rate": 1.00,
            "schema_valid_rate": 1.00,
        },
    }
    _baseline_path = Path(__file__).resolve(
    ).parents[1] / "build" / "day8" / "regression_baseline.json"
    _baseline_path.parent.mkdir(parents=True, exist_ok=True)
    _baseline_path.write_text(json.dumps(_baseline, indent=2))
    mo.callout(
        mo.md(f"Regression baseline written to `build/day8/regression_baseline.json`"),
        kind="neutral",
    )
    return _baseline, _baseline_path


@app.cell
def _artifact_write(mo, json, Path):
    import datetime as _dt

    # Read regression baseline if available
    _baseline_path2 = (
        Path(__file__).resolve().parents[1] /
        "build" / "day8" / "regression_baseline.json"
    )
    _baseline_scores = {}
    if _baseline_path2.exists():
        try:
            _baseline_scores = json.loads(
                _baseline_path2.read_text()).get("scores", {})
        except Exception:
            pass

    artifact = {
        "day": 8,
        "title": "CI/CD, Infrastructure as Code & Secure Deployment",
        "completed_at": _dt.datetime.utcnow().isoformat() + "Z",
        "bicep_tracks": {
            "core": "infra/core.bicep — Days 0–4; Storage + Search + OpenAI",
            "full": "infra/full.bicep — Days 5+; adds PG, KV, ACR, ACA, Log Analytics",
        },
        "identity_planes": {
            "workload": {
                "bicep_name": "id-aegisap-workload",
                "roles": [
                    "Cognitive Services OpenAI User",
                    "Search Index Data Reader",
                    "Key Vault Secrets User",
                    "AcrPull",
                ],
            },
            "jobs": {
                "bicep_name": "id-aegisap-jobs",
                "roles": [
                    "Cognitive Services OpenAI User",
                    "Search Index Data Contributor",
                    "Key Vault Secrets User",
                    "AcrPull",
                ],
            },
            "search_admin": {
                "bicep_name": "id-aegisap-search-admin",
                "roles": ["Search Service Contributor"],
            },
        },
        "oidc_federation": {
            "no_stored_secrets": True,
            "subject_scope": "repo + branch + workflow",
            "token_lifetime_minutes": 60,
        },
        "aca_revision_model": {
            "image_tag_convention": "aegisap-api:<git-sha>",
            "rollback_time_minutes": 2,
            "minimum_inactive_revisions_kept": 2,
        },
        "acceptance_gates": [
            "security_posture",
            "eval_regression",
            "budget",
            "refusal_safety",
            "resume_safety",
            "aca_health",
        ],
        "security_posture_forbidden_conditions": [
            "AZURE_OPENAI_API_KEY in env",
            "ACR pull via username/password",
            "LANGSMITH_API_KEY absent from Key Vault",
            "AEGISAP_POSTGRES_DSN contains password",
        ],
        "regression_baseline": _baseline_scores,
        "gate_passed": True,
    }

    out_dir = Path(__file__).resolve().parents[1] / "build" / "day8"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "deployment_design.json"
    out_path.write_text(json.dumps(artifact, indent=2))

    mo.callout(
        mo.md(
            f"Artifacts written:\n"
            f"- `build/day8/deployment_design.json`\n"
            f"- `build/day8/regression_baseline.json`"
        ),
        kind="success",
    )
    return artifact, out_dir, out_path


# ---------------------------------------------------------------------------
# Production Reflection
# ---------------------------------------------------------------------------
@app.cell
def _reflection(mo):
    mo.md("""
    ## Production Reflection

    1. **IaC drift audit:** A security assessment finds that a network rule was added
       to the PostgreSQL server by a developer three months ago and is not in any Bicep
       template. The rule allows connections from `0.0.0.0/0`. What is the immediate
       containment action, and what process change prevents this in the future?

    2. **OIDC token validation failure:** A GitHub Actions workflow fails at
       `azure/login` with `AADSTS70021: No matching federated identity record found`.
       The workflow worked yesterday. What are the three most likely causes, and
       how do you diagnose each?

    3. **Blast radius assessment:** Suppose the Container App running `id-aegisap-workload`
       is compromised via a container escape. Map the exact blast radius:
       what can the attacker read, write, or delete?  What data and services are safe?
    """)
    return


@app.cell
def _day8_unscaffolded_block(mo):
    from _shared.curriculum_scaffolds import render_unscaffolded_block

    render_unscaffolded_block(
        mo,
        title="Unscaffolded Afternoon Block — Release Architecture From Scratch",
        brief=(
            "Without using the nearby Bicep and gate examples, draft the minimum secure "
            "release architecture for a new agentic service: identity planes, IaC boundary, "
            "secrets policy, rollback unit, and one gate that would block production."
        ),
        done_when=(
            "The design names the rollback unit and the authority that can trigger it.",
            "No long-lived credential is required for the normal release path.",
            "At least one gate consumes prior-day evidence instead of only live health.",
        ),
    )
    return


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
@app.cell
def _summary(mo):
    mo.md("""
    ## Day 8 Summary Checklist

    - [ ] Explain why IaC is mandatory for AI workloads (reproducibility, auditability, drift detection)
    - [ ] Identify `resource`, `param`, `module`, `output`, and `existing` in a Bicep template
    - [ ] Name the three managed identity resources in `infra/full.bicep` and their Bicep names
    - [ ] State the minimum RBAC role for the runtime API identity on each of the 5 core services
    - [ ] Explain the `DefaultAzureCredential` chain — which step fires in dev and which in prod
    - [ ] Identify what SHOULD and what SHOULD NOT go in Key Vault (with reasons)
    - [ ] Explain OIDC federation: no stored secrets, per-job tokens, subject scoping
    - [ ] Describe the ACA revision model: create → gate check → traffic shift → rollback
    - [ ] List the six acceptance gates and what each one feeds from (prior day artifact or live check)
    - [ ] State all four conditions that cause the security posture gate to fail
    - [ ] Artifacts `build/day8/deployment_design.json` and `build/day8/regression_baseline.json` exist
    """)
    return


@app.cell
def _forward(mo):
    mo.callout(
        mo.md("""
**Tomorrow — Day 9: Scaling, Monitoring & Cost Optimisation**

The deployment pipeline is now secure and gate-checked.  Tomorrow we focus on
operating AegisAP at scale: the OpenTelemetry data model, KQL for trace-driven
incident response, PAYG vs. PTU economics, task-class-aware model routing, the
cost ledger, and semantic cache bypass — building the `routing_report.json`
artifact that feeds the Day 10 budget gate.

Open `notebooks/day_9_scaling_monitoring_cost.py` when ready.
        """),
        kind="success",
    )
    return



@app.cell
def _fde_learning_contract(mo):
    mo.md(r"""
    ---
    ## FDE Learning Contract — Day 08: IaC, Identity Planes, and Secure Release Ownership
    

    ### Four Daily Outputs

    | # | Output type | Location |
    |---|---|---|
    | 1 | Technical build | `LAB_OUTPUT/` |
    | 2 | Design defense memo | `DECISION_MEMOS/` |
    | 3 | Corporate process artifact | `PROCESS_ARTIFACTS/` |
    | 4 | Oral defense prep notes | `ORAL_DEFENSE/` |

    ### Rubric Weights (100 points total)

    | Dimension | Points |
    |---|---|
    | Iac Correctness | 25 |
| Identity Security Reasoning | 25 |
| Ownership Clarity | 20 |
| Review Packet Quality | 15 |
| Oral Defense | 15 |

    Pass bar: **80 / 100**   Elite bar: **90 / 100**

    ### Oral Defense Prompts

    1. Which IaC pattern did you choose over an alternative and what is the security consequence of the rejected approach?
2. If federated credentials drift and the pipeline loses access at 2am, what is the blast radius and who is the first call?
3. Who owns the release machinery in production, and what evidence would a platform team require before granting break-glass access?

    ### Artifact Scaffolds

    - `docs/curriculum/artifacts/day08/RELEASE_OWNERSHIP_MAP.md`
- `docs/curriculum/artifacts/day08/SECURITY_REVIEW_PACKET.md`
- `docs/curriculum/artifacts/day08/DRIFT_RESPONSE_PLAYBOOK.md`

    See `docs/curriculum/MENTAL_MODELS.md` for mental models reference.
    See `docs/curriculum/ASSESSOR_CALIBRATION.md` for scoring anchors.
    """)
    return


if __name__ == "__main__":
    app.run()
