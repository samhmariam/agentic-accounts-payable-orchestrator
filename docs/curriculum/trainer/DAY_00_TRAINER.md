# Day 0 — Azure Bootstrap · Trainer Guide

> **Session duration:** 3–4 hours (90 min theory + 2 h lab)  
> **WAF Pillars:** Security · Operational Excellence  
> **Prerequisite for trainees:** Basic Azure familiarity (portal navigation, subscriptions)

---

## Session Goals

By the end of Day 0, every learner should be able to:
- Start from the Day 00 incident, then walk the portal surface and name the Azure resources before the scripts create or verify them
- Run `az deployment sub create` against the `core` Bicep template
- Verify a deployed environment using `verify_env.py` without portal access
- Explain why Managed Identity replaces API keys in Azure AI workloads
- Read a Bicep file and identify where identity and role assignments live

---

## Preparation Checklist

- [ ] Each learner has `Owner` or `Contributor` + `User Access Administrator` on
      the target subscription (needed for role assignments in Bicep)
- [ ] Azure CLI installed and `az login` verified for each machine
- [ ] `.venv` activated: `source .venv/bin/activate`
- [ ] A `.env` file seeded from `scripts/setup-env.sh` or `.env.example`
- [ ] Bicep CLI installed: `az bicep install`

**Expected artifact:** `.day0/core.json` or `.day0/full.json`

---

## Theory Segment (60 min)

### Block 1: Why IaC? (15 min)

**Talking points:**
1. Open the repo and show `infra/core.bicep` side by side with a manually
   provisioned resource in the portal. Ask: "If the portal resource has a
   different name, how do you know which one is correct?"
2. Explain *configuration drift*: the gap between declared state and actual
   state. IaC is the only durable fix.
3. Show how `az deployment sub validate` catches errors before they reach Azure.
4. Introduce the two tracks: `core` (Days 0–4) and `full` (Days 5+).

**Key message:** "The portal is for first-pass understanding. Bicep is the truth."

---

### Block 2: Azure Identity (25 min)

**Talking points:**
1. Walk through the credential hierarchy:
   ```
   API key in env → Service Principal + secret → Managed Identity
   ```
   Show the risk increasing left to right (rotation burden, leak surface).
2. Open `src/aegisap/security/credentials.py` and show the
   `DefaultAzureCredential` usage. Highlight that no API key is imported.
3. Demo: `az login` on a dev machine. Show what happens when you print the
   token with `az account get-access-token --scope https://ai.azure.com/.default`.
4. Explain system-assigned vs. user-assigned identity with the ACR pull example.
5. Show `infra/modules/role_assignments.bicep` and trace one role assignment
   from identity to resource to permission.

**Common question:** "Can I just use an API key in a personal env var for dev?"  
**Answer:** "Yes for local-only dev, but the IaC and CI/CD path must never contain
keys. Acceptable when developers are explicitly working around infra that isn't
provisioned yet — not as a permanent pattern."

---

### Block 3: AegisAP Service Map (20 min)

**Talking points:**
1. Draw the service map on a whiteboard or show the diagram:
   ```
   [ACA API] ──► [Foundry]
        │──────► [Azure AI Search]
        │──────► [PostgreSQL]  (full track only)
        └──────► [Key Vault]
   [ACR]  ──◄── ACA pull via managed identity
   [APIM] ──►   (Day 9)
   ```
2. For each service, state: "When does it first appear in the training journey?"
3. Explain why APIM is not provisioned on Day 0 (its value only appears in Day 9
   with cost routing and PTU overflow).
4. Walk through the naming convention in `core.bicepparam`.

---

## Lab Walkthrough Notes

### Key commands and outputs to call out in Day 0:

1. **`pwsh ./scripts/provision-core.ps1` or `pwsh ./scripts/provision-full.ps1`** — show that Day 0 emits a persisted `.day0/*.json` state file rather than relying on portal screenshots or hand-edited shell state.

2. **`source ./scripts/setup-env.sh core` or `. ./scripts/setup-env.ps1 -Track core`** — explain that later days inherit the Day 0 contract from the generated state file.

3. **`uv run python scripts/verify_env.py --track core --env`** — call out the contract-only check before learners chase live-service failures.

4. **`uv run python scripts/verify_env.py --track core`** — the first live Foundry inference call. Walk through what `DefaultAzureCredential` is doing under the hood and why the repo still uses the OpenAI-compatible endpoint on top of a Foundry resource.

5. **`.day0/core.json` or `.day0/full.json`** — open the generated state file and point out the Foundry endpoint, OpenAI-compatible endpoint, Search endpoint, and storage settings that later days inherit.

### Expected lab friction points

| Issue | Likely cause | Resolution |
|---|---|---|
| `az login` asks for device code | Browser not opening | Run `az login --use-device-code` |
| `AZURE_SUBSCRIPTION_ID` not set | `.env` not loaded | `source scripts/setup-env.sh` |
| Role assignment fails | Insufficient permission on subscription | Verify `Owner` role or add `User Access Administrator` |
| Foundry inference call returns 401 | Missing `Cognitive Services User` role on the learner principal or missing `Cognitive Services OpenAI User` on the runtime identity | Check the Day 0 RBAC assignments; re-deploy |

---

## Facilitation Addendum

### Observable Mastery Signals

- Learner can identify the production credential source without guessing.
- Learner reruns `verify_env.py` and inspects `.day0/*.json` instead of relying on portal screenshots.
- Learner distinguishes `core` and `full` track requirements in terms of runtime contracts, not just service names.

### Intervention Cues

- If a learner proposes long-lived secrets, stop and reconnect to the Day 0 zero-secret runtime contract.
- If debugging turns into portal clicking, bring them back to `verify_env.py` and the `.day0` state file.
- If Azure access is the blocker, require the learner to name the failed probe before offering help.

### Fallback Path

- If Azure access is unstable, use a saved `.day0/core.json` or `.day0/full.json` plus a saved `verify_env.py` transcript and whiteboard the failed probe instead of spending the session on tenant issues.

### Exit Ticket Answer Key

1. Production should use Managed Identity through `DefaultAzureCredential`.
2. Least privilege limits blast radius and keeps the runtime posture auditable.
3. Strong answers start with `uv run python scripts/verify_env.py --track core --env`.

### Time-box Guidance

- Cap individual environment debugging at 15 minutes before regrouping the cohort.
- If more than a third of the room is blocked on Azure posture, switch to shared troubleshooting and defer optional depth.

---

## Discussion Prompts

1. "What happens to your deployment process if a team member adds a subnet rule
   manually in the portal?"

2. "How many different places in this repo could you accidentally print an Azure
   API key? What would you scan for in a PR review?"

3. "The `full` track adds PostgreSQL. What new identity considerations does that
   introduce compared to the `core` track?"

---

## Expected Q&A

**Q: Can we use connection strings for PostgreSQL instead of Entra auth?**  
A: In local dev, yes — `AEGISAP_POSTGRES_DSN` is the local escape hatch. But
Day 7 explicitly forbids password-based DSNs in staging and production. Entra
auth is the target from Day 5 onward.

**Q: What's the difference between `core.bicep` and `full.bicep`?**  
A: `full.bicep` includes PostgreSQL Flexible Server, the secret plane in Key
Vault, and the Day 7-required identity constraints. `core.bicep` is the minimum
set for Days 0–4.

**Q: Why does the training not use Azure Developer CLI (azd)?**  
A: `azd` is a good choice for greenfield projects. AegisAP uses the low-level
Bicep + `az deployment` path to expose exactly what is happening at each step.
Once learners understand the primitives, adopting `azd` is straightforward.

---

## Next-Day Bridge (5 min)

Close Day 0 with:

> "We now have a running Azure environment with properly scoped identities.
> Tomorrow we take our first raw invoice and apply a trust boundary —
> turning noisy OCR text into a typed, auditable `CanonicalInvoice`.
> The infrastructure we provisioned today is what makes that call to
> Foundry happen without a single API key in our code, even though the app still
> uses the OpenAI-compatible inference surface."
