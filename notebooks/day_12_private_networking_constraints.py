import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell
def _bootstrap():
    import sys
    from pathlib import Path
    _root = Path(__file__).resolve().parents[1]
    for _p in [str(_root / "src"), str(_root / "notebooks")]:
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
    # Day 12 — Private Networking Constraints

    > **WAF Pillars covered:** Security · Reliability · Operational Excellence  
    > **Estimated time:** 3 hours  
    > **Prerequisites:** Day 8 ACA deployment, Day 11 identity hardening  
    > **New gates:** `gate_private_network_static` (CI PR gate) + `gate_private_network_posture` (staging gate)

    ---

    ## Learning Objectives

    1. Explain VNET injection for Azure Container Apps and why it protects the data plane.
    2. Configure Private Endpoints for Azure OpenAI, Azure AI Search, and Azure Storage.
    3. Link a Private DNS zone to a VNET so that service hostnames resolve to RFC-1918 IPs.
    4. Set `publicNetworkAccess=Disabled` on all AI services via Bicep.
    5. Run the `NetworkPostureProbe` and interpret its two output artifacts.
    6. Explain the difference between the static CI gate and the live staging gate.

    ---

    ## Where Day 12 Sits in the Full Arc

    ```
    Day 11 ──►[Day 12]──► Day 13 ──► Day 14
    OBO        NETWORKING  Integration  Elite Ops
    ```

    Day 12 is the NFR from Day 2 made real: "All AI services must have
    `publicNetworkAccess=Disabled` + Private Endpoint." Two gates enforce this:
    a static CI gate that runs without Azure access, and a live staging gate.
    """)
    return


@app.cell
def _full_day_agenda(mo):
    from _shared.curriculum_scaffolds import render_full_day_agenda

    render_full_day_agenda(
        mo,
        day_label="Day 12 private networking constraints",
        core_outcome="prove private-only network posture in both AegisAP and the claims-intake transfer domain",
        afternoon_focus="Use the transfer-domain lens and policy artifacts to defend the network design without resorting to a public fallback.",
    )
    return


@app.cell
def _capstone_b_transfer_lens(mo):
    mo.callout(
        mo.md(
            """
    ## Capstone B Transfer Lens

    Days 12-14 are assessed in the **claims intake** transfer domain as well as AegisAP.

    Use today’s network posture work to reason about:
    - private access to payer and policy systems in `fixtures/capstone_b/claims_intake/`
    - zero-tolerance exposure of healthcare-regulated claim content
    - whether a security exception would still be acceptable when the external dependency is a payer portal rather than an AP system

    Keep the transfer pack open alongside this notebook:
    - `docs/curriculum/CAPSTONE_B_TRANSFER.md`
    - `fixtures/capstone_b/claims_intake/`
    """
        ),
        kind="info",
    )
    return


@app.cell
def _day12_lineage_map(mo):
    mo.callout(
        mo.md(
            """
    ## Visual Guide — Day 12 Evidence Flow

    ```
    Day 2 NFR intent
      "AI services are private-endpoint only"
             │
             ├─► Day 8 IaC and deployment wiring
             │
             ├─► build/day12/static_bicep_analysis.json
             │     └─► gate_private_network_static (CI proof)
             │
             └─► build/day12/private_network_posture.json
                   + build/day12/external_sink_disabled.json
                   └─► gate_private_network_posture (staging proof)
    ```

    Static IaC proof and live posture proof are related, but they are not interchangeable.

    | Question | Artifact that answers it | Transfer-domain equivalent |
    |---|---|---|
    | "Did we declare private-only intent in code?" | `build/day12/static_bicep_analysis.json` | Claims services still forbid public endpoints in Bicep |
    | "Does the deployed hostname really resolve privately?" | `build/day12/private_network_posture.json` | Payer or policy endpoints resolve only inside approved network paths |
    | "Did we disable public fallback?" | `build/day12/external_sink_disabled.json` | No emergency internet bypass for regulated claim content |
    """
        ),
        kind="info",
    )
    return


@app.cell
def _day12_mastery_checkpoint(mo):
    mo.callout(
        mo.md(
            """
    ## Mastery Checkpoint — Networking Discipline

    Before moving on, make sure you can say clearly:
    - why `gate_private_network_static` and `gate_private_network_posture` must both exist
    - which artifact is training-only versus authoritative live evidence
    - why a public fallback for claims-intake or AP regulated content is a governance failure, not a clever contingency
    - what a temporary security exception would have to name: owner, expiry, compensating controls, and removal proof
    """
        ),
        kind="warn",
    )
    return


@app.cell
def _day12_hidden_case_preview(mo):
    mo.callout(
        mo.md(
            """
    ## Hidden-Case Drill Preview — Assessor Pressure Test

    An assessor-only claims-intake case exists. Do **not** open it.

    Treat it as a late-breaking transfer-domain surprise and prepare your Day 12 defense:
    - Which new or updated entry would appear in the network dependency register?
    - What evidence proves you preserved private-only posture instead of taking a public shortcut?
    - Which gate should fail if someone proposes temporary public exposure to "keep the test moving"?
    - What security exception request would be rejected outright even before compensating controls are discussed?

    Weak answer pattern:
    "We would temporarily allow public access and clean it up later."
    """
        ),
        kind="warn",
    )
    return


# ---------------------------------------------------------------------------
# Section 1 — Private Networking Architecture
# ---------------------------------------------------------------------------
@app.cell
def _s1_header(mo):
    mo.md("## 1. Private Networking Architecture for AegisAP")
    return


@app.cell
def _s1_body(mo):
    mo.md("""
    ### The Problem

    By default, every Azure AI service (OpenAI, AI Search, Storage, PostgreSQL)
    has a **public endpoint** reachable from the internet with the right key or token.
    In a regulated enterprise environment, this is unacceptable because:
    - Any internet-facing endpoint is an attack surface regardless of authentication
    - Data never leaving the Microsoft network is a compliance requirement (e.g., FCA, ISO 27001)
    - A misconfigured RBAC role on a public endpoint is a full data-plane breach

    ### The Solution: Three Layers

    ```
    ┌─────────────────────────────────────────────────────────────┐
    │  Azure VNet (10.0.0.0/16)                                   │
    │                                                             │
    │  ┌─────────────────────────┐   ┌──────────────────────┐    │
    │  │  Container Apps Env     │   │  Private Endpoints   │    │
    │  │  (VNET-injected)        │──►│  • OpenAI PE         │    │
    │  │                         │   │  • AI Search PE      │    │
    │  │  AegisAP Orchestrator   │   │  • Storage PE        │    │
    │  │  AegisAP Worker         │   │  • PostgreSQL PE     │    │
    │  └─────────────────────────┘   └──────────┬───────────┘    │
    │                                            │                │
    │  ┌─────────────────────────────────────────▼───────────┐   │
    │  │  Private DNS Zones                                   │   │
    │  │  openai.azure.com → 10.0.1.x                        │   │
    │  │  search.windows.net → 10.0.2.x                      │   │
    │  │  blob.core.windows.net → 10.0.3.x                   │   │
    │  └──────────────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────────────┘
            ▲ internet can NOT reach any AI service
    ```

    | Layer | What it does | Bicep resource |
    |---|---|---|
    | VNET injection | ACA environment runs inside the VNet | `Microsoft.App/managedEnvironments` with `vnetConfiguration` |
    | Private Endpoint | AI service gets a private NIC in the VNet subnet | `Microsoft.Network/privateEndpoints` |
    | Private DNS | Service hostname resolves to private IP | `Microsoft.Network/privateDnsZones` |
    | `publicNetworkAccess=Disabled` | Refuses all requests via public endpoint | Resource property per AI service |

    All four layers are required.  Missing any one creates a bypass.
    """)
    return


# ---------------------------------------------------------------------------
# Section 2 — Bicep Patterns
# ---------------------------------------------------------------------------
@app.cell
def _s2_header(mo):
    mo.md("## 2. Bicep Patterns for Private Networking")
    return


@app.cell
def _s2_body(mo):
    mo.md("""
    ### Key Bicep snippets (see `infra/network/` for full modules)

    **Disable public endpoint on Azure OpenAI:**
    ```bicep
    resource openAI 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
      name: openAIName
      location: location
      sku: { name: 'S0' }
      kind: 'OpenAI'
      properties: {
        publicNetworkAccess: 'Disabled'       // ← required
        networkAcls: {
          defaultAction: 'Deny'
          ipRules: []
          virtualNetworkRules: []
        }
      }
    }
    ```

    **Private Endpoint for Azure OpenAI:**
    ```bicep
    resource openAIPrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-04-01' = {
      name: '${openAIName}-pe'
      location: location
      properties: {
        subnet: { id: privateEndpointSubnetId }
        privateLinkServiceConnections: [{
          name: '${openAIName}-plsc'
          properties: {
            privateLinkServiceId: openAI.id
            groupIds: ['account']
          }
        }]
      }
    }
    ```

    **Private DNS Zone link (must be linked to the VNet):**
    ```bicep
    resource dnsZoneLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
      parent: openAIDnsZone
      name: '${vnetName}-link'
      location: 'global'
      properties: {
        virtualNetwork: { id: vnet.id }
        registrationEnabled: false
      }
    }
    ```

    > **Common gotcha:** Creating a Private Endpoint but forgetting to link the DNS zone
    > means the hostname still resolves to a public IP in most environments.  The probe
    > will catch this: `dns_private=False` with `dns_ip=<public-ip>`.
    """)
    return


# ---------------------------------------------------------------------------
# Section 3 — Network Posture Probe
# ---------------------------------------------------------------------------
@app.cell
def _s3_header(mo):
    mo.md("## 3. Network Posture Probe — `aegisap.network.private_endpoint_probe`")
    return


@app.cell
def _s3_body(mo):
    mo.md("""
    The `NetworkPostureProbe` performs two checks per service:

    1. **DNS check** — resolves the hostname and confirms the IP is RFC-1918 private.
    2. **Public reachability check** — attempts a TLS connection to port 443.
       Expects failure (timeout or refused); success means public endpoint is still open.

    ```python
    from aegisap.network.private_endpoint_probe import NetworkPostureProbe

    probe = NetworkPostureProbe.from_env()  # uses AEGISAP_AI_HOSTNAMES env var
    result = probe.run()
    probe.write_artifacts(result)
    # writes:
    #   build/day12/private_network_posture.json  (always)
    ```

    ### Two Gate Artifacts

    | Artifact | Gate | When written |
    |---|---|---|
    | `build/day12/static_bicep_analysis.json` | `gate_private_network_static` | CI — produced by `scripts/check_private_network_static.py`, which compiles every Bicep file in `infra/` to ARM JSON and checks `publicNetworkAccess == "Disabled"` on every AI-tier resource; contains `written_by: "check_private_network_static"` |
    | `build/day12/private_network_posture.json` | `gate_private_network_posture` | Staging — live VNet probe (DNS resolution + public reachability); always written, even on partial failure |

    The split design means:
    - **CI (PR gate):** `gate_private_network_static` verifies `static_bicep_analysis.json`
      exists, that `written_by == "check_private_network_static"` (provenance check), and
      that `violations == []` — no Azure access required in the CI runner.
    - **Staging gate:** reads the full posture report — requires a live probe run against the
      staging environment from a machine inside the VNet.

    Canonical live command:

    ```bash
    uv run python scripts/verify_private_network_posture.py
    ```
    """)
    return


# ---------------------------------------------------------------------------
# Section 4 — Lab: Run the Probe
# ---------------------------------------------------------------------------
@app.cell
def _s4_header(mo):
    mo.md("## 4. Lab — Run the Network Posture Probe")
    return


@app.cell
def _s4_lab(mo, json, os, Path):
    import datetime

    _build = Path(__file__).resolve().parents[1] / "build" / "day12"
    _build.mkdir(parents=True, exist_ok=True)

    _hostnames_raw = os.environ.get("AEGISAP_AI_HOSTNAMES", "")
    _has_live_env = bool(_hostnames_raw)

    if _has_live_env:
        try:
            from aegisap.network.private_endpoint_probe import NetworkPostureProbe
            _probe = NetworkPostureProbe.from_env()
            _result = _probe.run()
            _probe.write_artifacts(_result)
            _report = _result.to_dict()
            _report["training_artifact"] = False
            _report["authoritative_evidence"] = True
            _report["execution_tier"] = 2
            _report["note"] = "LIVE"
            _kind = "success" if _result.all_passed else "danger"
            _msg = (
                f"Live probe complete: `all_passed={_result.all_passed}`\n\n"
                f"Services probed: {len(_result.services)}"
            )
        except Exception as _exc:
            _report = {
                "error": str(_exc),
                "all_passed": False,
                "training_artifact": False,
                "authoritative_evidence": True,
                "execution_tier": 2,
                "note": "LIVE_ERROR",
            }
            _kind = "danger"
            _msg = f"Probe error: `{_exc}`"
    else:
        # Training preview only — useful for learning the artifact shape,
        # but intentionally not acceptable as authoritative gate evidence.
        _report = {
            "all_passed": False,
            "services": [
                {
                    "hostname": "aegisap-openai.openai.azure.com",
                    "dns_private": True,
                    "dns_ip": "10.0.1.4",
                    "public_reachable": False,
                    "passed": True,
                    "detail": "TRAINING_ONLY: sample DNS -> 10.0.1.4 (private); not a live verification result.",
                },
                {
                    "hostname": "aegisap-search.search.windows.net",
                    "dns_private": True,
                    "dns_ip": "10.0.2.5",
                    "public_reachable": False,
                    "passed": True,
                    "detail": "TRAINING_ONLY: sample DNS -> 10.0.2.5 (private); not a live verification result.",
                },
            ],
            "training_artifact": True,
            "authoritative_evidence": False,
            "execution_tier": 1,
            "note": "TRAINING_ONLY: no AEGISAP_AI_HOSTNAMES set",
        }
        (_build / "private_network_posture.json").write_text(json.dumps(_report, indent=2))
        _kind = "warn"
        _msg = (
            "No `AEGISAP_AI_HOSTNAMES` set — training preview written to `build/day12/private_network_posture.json`.\n\n"
            "**`gate_private_network_posture`** will remain **red** until you run the probe from a live "
            "VNET-injected environment and produce authoritative evidence.\n\n"
            "**`gate_private_network_static`**: `static_bicep_analysis.json` is **NOT** written here — "
            "run `scripts/check_private_network_static.py` in CI (or locally against your Bicep files) "
            "to produce a real artifact.\n\n"
            "Set `AEGISAP_AI_HOSTNAMES=<host1>,<host2>` to run a live probe."
        )

    mo.callout(mo.md(_msg), kind=_kind)
    return datetime


# ---------------------------------------------------------------------------
# Section 4b — Gate comparison: static vs live
# ---------------------------------------------------------------------------
@app.cell
def _s4b_comparison(mo, json, Path):
    """Side-by-side comparison of gate_private_network_static vs gate_private_network_posture."""
    _build = Path(__file__).resolve().parents[1] / "build" / "day12"

    def _load_artifact(name: str) -> dict:
        p = _build / name
        if p.exists():
            try:
                return json.loads(p.read_text())
            except Exception as e:
                return {"error": str(e)}
        return {}

    _static_art = _load_artifact("static_bicep_analysis.json")
    _live_art = _load_artifact("private_network_posture.json")

    def _status(art: dict, key: str = "all_passed") -> str:
        if not art:
            return "⚪ not run"
        if "error" in art:
            return f"❌ error: {art['error'][:40]}"
        return "✅ passed" if art.get(key) else "❌ failed"

    _static_status = _status(_static_art)
    _live_status = _status(_live_art)
    _static_sources = ", ".join(_static_art.get(
        "bicep_files_compiled", [])) or "_none_"
    _live_services = len(_live_art.get("services", []))
    _violation_count = len(_static_art.get("violations", []))

    mo.md(f"""
### Gate Comparison: Static Analysis vs Live Probe

| | `gate_private_network_static` | `gate_private_network_posture` |
|---|---|---|
| **When it runs** | CI (every PR) — no Azure creds needed | Post-deploy staging only |
| **How it works** | Compiles Bicep → ARM JSON, checks `publicNetworkAccess` | DNS + TCP probe from inside the VNet |
| **Artifact** | `build/day12/static_bicep_analysis.json` | `build/day12/private_network_posture.json` |
| **Written by** | `check_private_network_static` | `verify_private_network_posture` |
| **Current status** | {_static_status} | {_live_status} |
| **Resources/services checked** | {_static_art.get('resources_checked', '—')} resources | {_live_services} services |
| **Violations** | {_violation_count} | — |
| **Bicep sources** | {_static_sources[:80]} | — |

**Why both gates exist:**
- Static analysis catches misconfigurations in Bicep *before* deployment (shift-left).
- Live probe confirms the actual running environment matches the policy *after* deployment.
- Neither is sufficient alone: Bicep might be correct but a manual portal change could re-enable
  public access. The live probe catches this drift.
    """)
    return


# ---------------------------------------------------------------------------
# Section 5 — Zero-Trust Pattern for ACA
# ---------------------------------------------------------------------------
@app.cell
def _s5_header(mo):
    mo.md("## 5. Zero-Trust Checklist for VNET-Injected ACA")
    return


@app.cell
def _s5_body(mo):
    mo.md("""
    ### Production Hardening Checklist

    - [ ] Container App Environment has `vnetConfiguration.infrastructureSubnetId` set
    - [ ] `publicNetworkAccess=Disabled` on: Azure OpenAI, Azure AI Search, Azure Storage, Azure PostgreSQL
    - [ ] Private Endpoints created for each AI service in the PE subnet
    - [ ] Private DNS zones created and linked to the VNet for each service FQDN
    - [ ] No NSG rule allows inbound from `Internet` to PE subnet
    - [ ] Azure Firewall or NVA egress policy blocks all non-Microsoft outbound traffic
    - [ ] Container App managed environment has `internal: true` (no public IP)
    - [ ] APIM fronts external requests; backend is internal ACA only
    - [ ] `gate_private_network_static` passes in CI (static JSON check)
    - [ ] `gate_private_network_posture` passes in staging (live probe from inside VNet)

    ### Egress Control

    Even with VNET injection, containers can still make outbound internet calls unless
    egress is controlled.  Use Azure Firewall application rules to allow-list:
    - `login.microsoftonline.com` (Entra token endpoint)
    - `graph.microsoft.com` (Graph API for actor verification)
    - `api.cognitive.microsoft.com` (Cognitive Services)
    - Block everything else.

    > **Exam question:** "How does AegisAP prevent a malicious prompt from exfiltrating
    > data to an attacker's server?"
    > Answer: Combined threat — content safety pre-filter (Day 7) + network egress control
    > (Day 12) + policy overlay action allow-list (Day 4). All three must be present.
    """)
    return


# ---------------------------------------------------------------------------
# Summary + Forward
# ---------------------------------------------------------------------------
@app.cell
def _summary(mo):
    mo.md("""
    ## Day 12 Summary Checklist

    - [ ] List the four layers of private networking and state what happens if any one is missing
    - [ ] Write the Bicep property to disable public endpoint on Azure OpenAI
    - [ ] Explain the difference between `gate_private_network_static` and `gate_private_network_posture`
    - [ ] State what `static_bicep_analysis.json` contains and how `check_private_network_static.py` produces it
    - [ ] Confirm `build/day12/private_network_posture.json` and `static_bicep_analysis.json` exist
    - [ ] Describe how DNS resolution is used to verify a private endpoint is correctly configured
    - [ ] Defend how you would handle an unseen transfer-domain dependency without introducing a public fallback
    """)
    return


@app.cell
def _forward(mo):
    mo.callout(
        mo.md("""
**Tomorrow — Day 13: Integration Boundaries & MCP**

We build the integration layer: Azure Functions at LOB boundaries, Service Bus
reliable transport, DLQ processing with compensating actions, and the Model
Context Protocol (MCP) server that exposes AegisAP tools to external agents.

Starter scaffolds are provided in `src/aegisap/integration/_scaffold/` and
`src/aegisap/mcp/_scaffold/` — use them as your starting point.

Open `notebooks/day_13_integration_boundary_and_mcp.py` when ready.
        """),
        kind="success",
    )
    return



@app.cell
def _fde_learning_contract(mo):
    mo.md(r"""
    ---
    ## FDE Learning Contract — Day 12: Private Networking, Egress Control, and Security Dependency Management
    
> **Zero-tolerance day** — a hard-fail on any zero-tolerance condition sets the day score to 0.
> **Capstone B day** — primary deliverables are in the claims intake transfer domain.

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
    | Network Posture Design | 30 |
| Static Vs Live Proof Understanding | 20 |
| Dependency Management Realism | 20 |
| Security Exception Handling | 15 |
| Oral Defense | 15 |

    Pass bar: **80 / 100**   Elite bar: **90 / 100**

    ### Oral Defense Prompts

    1. Which network dependency has the longest lead time and what is your plan if it is not resolved before production cutover?
2. You temporarily enable a public endpoint in dev. Walk through every compensating control, the expiry date, and who holds the removal obligation.
3. Who approves a security exception in your enterprise, what evidence is mandatory in the request, and what happens at expiry if no renewal is filed?
4. An assessor introduces an unseen claims-intake dependency during cutover pressure. Explain why your design still refuses a public shortcut and which Day 12 artifacts prove that decision.

    ### Artifact Scaffolds

    - `docs/curriculum/artifacts/day12/NETWORK_DEPENDENCY_REGISTER.md`
- `docs/curriculum/artifacts/day12/SECURITY_EXCEPTION_REQUEST.md`
- `docs/curriculum/artifacts/day12/EGRESS_CONTROL_POLICY.md`

    See `docs/curriculum/MENTAL_MODELS.md` for mental models reference.
    See `docs/curriculum/ASSESSOR_CALIBRATION.md` for scoring anchors.
    """)
    return


if __name__ == "__main__":
    app.run()
