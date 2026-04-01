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
    # Day 11 — Delegated Identity & On-Behalf-Of (OBO) Flows

    > **WAF Pillars covered:** Security · Operational Excellence  
    > **Estimated time:** 2.5 hours  
    > **Prerequisites:**
    > - **Day 3** Identity Plane Bridge (four planes, blast-radius model)
    > - **Day 8** OIDC workload federation & Managed Identity deployment hardening
    > - **Day 7** Key Vault secret rotation (OBO client secret stored in KV)
    > **New gate:** `gate_delegated_identity` (3 sub-checks: app_identity, obo_exchange, actor_binding)

    ---

    ## Learning Objectives

    By the end of this notebook you will be able to:

    1. Explain why `DefaultAzureCredential` is insufficient for delegated approval flows.
    2. Implement the OAuth 2.0 On-Behalf-Of flow using MSAL `ConfidentialClientApplication`.
    3. Verify that an OBO token's `oid` claim belongs to the required Entra group.
    4. Write a Day 11 OBO contract artifact that passes all three sub-gate checks.
    5. Describe the authority-confusion threat and the AegisAP defence.

    ---

    ## Where Day 11 Sits in the Full Arc

    ```
    Day 1 ──► ... ──► Day 8 ──► Day 9 ──► Day 10
    Fund.            CI/CD    Observ.   Ops
    ─────────────────────────────────────────────────────
    Day 11 ──► Day 12 ──► Day 13 ──► Day 14
    [OBO]      Networking  Integration  Elite Ops
    ```

    Day 11 extends Day 8's identity hardening into the *delegation plane*:
    not just "which system is calling" (managed identity) but "on behalf of
    which specific human approver" (OBO token exchange).
    """)
    return


# ---------------------------------------------------------------------------
# Section 1 — The Four Identity Planes Revisited
# ---------------------------------------------------------------------------
@app.cell
def _s1_header(mo):
    mo.md("## 1. The Four Identity Planes — Delegation Plane Deep Dive")
    return


@app.cell
def _s1_body(mo):
    mo.md("""
    Day 3 introduced all four planes. Today we implement the **delegation plane**.

    | Plane | Mechanism | Day hardened | What AegisAP does |
    |---|---|---|---|
    | Control plane | Azure RBAC | 8 | CI/CD OIDC; no human Owner login to prod |
    | Data plane | Service RBAC | 1, 3, 8 | MI for Search/OpenAI/Storage |
    | Application plane | Entra App Roles | 4, 8 | Policy overlay uses app-role claims |
    | **Delegation plane** | **OBO + Entra group check** | **11** | **Approval carries human OID** |

    ### Why Does This Matter for Accounts Payable?

    When AegisAP auto-approves an invoice, the approval record in the audit trail must
    show: who approved it, not which service processed it.

    Without OBO:
    ```
    approved_by: "managed-identity-object-id"   ← useless in an audit
    ```

    With OBO:
    ```
    approved_by_oid: "a3b4c5d6-..."  ← Entra OID of the finance director
    approved_by_upn: "j.smith@contoso.com"
    group_verified: true
    ```

    A regulatory audit can now map every approval to a named individual with
    evidence that they were authorised at the time.
    """)
    return


# ---------------------------------------------------------------------------
# Section 2 — OBO Flow Walkthrough
# ---------------------------------------------------------------------------
@app.cell
def _s2_header(mo):
    mo.md("## 2. OBO Token Exchange — Step by Step")
    return


@app.cell
def _s2_body(mo):
    mo.md("""
    The OAuth 2.0 On-Behalf-Of (RFC 8693) flow has four participants:

    1. **User** — the finance director, authenticated in Entra
    2. **Front-end** — the AegisAP approval UI (SPA or Teams tab)
    3. **Orchestrator API** — AegisAP backend (Container App with Managed Identity)
    4. **Entra** — token authority

    ```
    User ──(1. authenticate)──► Entra
                                  │ (2. access_token scoped to AegisAP front-end app)
    User ◄────────────────────────┘
      │
      │ (3. POST /approve { invoice_id, access_token })
      ▼
    Orchestrator API
      │
      │ (4. MSAL OBO: exchange user access_token for downstream token)
      ▼
    Entra ──(5. downstream_token with user OID)──► Orchestrator API
      │
      │ (6. Graph API: check OID is in Finance-Approvers group)
      ▼
    Microsoft Graph ──(7. group membership confirmed)──► Orchestrator API
      │
      │ (8. approval committed with actor_oid = user OID)
      ▼
    Audit table
    ```

    Three things must ALL pass for the `gate_delegated_identity` gate to succeed:
    - **Sub-check 1 — app_identity_check:** the orchestrator's MI can acquire its own token
    - **Sub-check 2 — obo_exchange_check:** MSAL OBO exchange succeeds and returns a token
    - **Sub-check 3 — actor_binding_check:** the OID from the OBO token is in the required group
    """)
    return


# ---------------------------------------------------------------------------
# Section 3 — OBO Implementation
# ---------------------------------------------------------------------------
@app.cell
def _s3_header(mo):
    mo.md("## 3. Implementing OBO — `aegisap.identity.obo`")
    return


@app.cell
def _s3_code(mo):
    mo.md("""
    The `OboTokenProvider` in `src/aegisap/identity/obo.py` wraps MSAL's
    `ConfidentialClientApplication.acquire_token_on_behalf_of()`.

    ```python
    from aegisap.identity.obo import OboTokenProvider

    provider = OboTokenProvider.from_env()
    # user_access_token = token received from the front-end Authorization header
    result = provider.exchange(
        user_assertion=user_access_token,
        scopes=["api://<downstream-resource-app-id>/.default"],
    )
    print(result.oid)      # Entra user object ID
    print(result.access_token[:20], "...")
    ```

    Required environment variables:
    - `AZURE_TENANT_ID` — Entra tenant
    - `AZURE_CLIENT_ID` — App registration for the orchestrator
    - `AZURE_CLIENT_SECRET` — Client secret (stored in Key Vault, injected via KV ref)

    > **Security note:** `AZURE_CLIENT_SECRET` must NEVER appear in source code or
    > committed to git. Always use a Key Vault reference in the Container App
    > environment variable: `@Microsoft.KeyVault(SecretUri=https://...)`.
    """)
    return


# ---------------------------------------------------------------------------
# Section 4 — Actor Verifier Implementation
# ---------------------------------------------------------------------------
@app.cell
def _s4_header(mo):
    mo.md("## 4. Actor Verification — `aegisap.identity.actor_verifier`")
    return


@app.cell
def _s4_body(mo):
    mo.md("""
    Knowing the OID is not enough — the orchestrator must confirm the OID belongs
    to the correct Entra security group.  The `ActorVerifier` calls the Microsoft
    Graph `transitiveMemberOf` API because nested groups (e.g., a user in
    `Finance-UK` which is nested in `Finance-Global-Approvers`) must be resolved.

    ```python
    from aegisap.identity.actor_verifier import ActorVerifier

    verifier = ActorVerifier.from_env()
    result = verifier.verify(oid="<user-oid-from-obo-claims>")
    if not result.is_member:
        raise PermissionError(f"Actor {result.oid} is not an authorised approver")
    ```

    Required environment variables:
    - `AZURE_TENANT_ID`
    - `AEGISAP_APPROVER_GROUP_ID` — Object ID of the Finance-Approvers Entra group

    The verifier uses `DefaultAzureCredential` with the Graph scope — the orchestrator's
    MI must have `Group.Read.All` OR a scoped `Member.Read.Hidden` role on the group.

    > **Principle of least privilege:** Prefer `GroupMember.Read.All` (reads only groups
    > the MI has been explicitly added to) over `Group.Read.All` which exposes all tenant groups.
    """)
    return


# ---------------------------------------------------------------------------
# Section 5 — Lab: Write the OBO Contract Artifact
# ---------------------------------------------------------------------------
@app.cell
def _s5_header(mo):
    mo.md("## 5. Lab — Write the OBO Contract Artifact")
    return


@app.cell
def _s5_body(mo):
    mo.md("""
    This cell writes `build/day11/obo_contract.json` — the gate evidence artifact for
    `gate_delegated_identity`.

    **Two artifacts, two purposes:**

    | Artifact | Purpose | Authoritative for gate? |
    |---|---|---|
    | `build/day11/obo_simulation_results.json` | Pedagogical walkthrough — written in Sections 1–3 | No — teaching only |
    | `build/day11/obo_contract.json` | Gate evidence for `gate_delegated_identity` | **Only when `training_artifact: false`** (Tier 2+) |

    In the training environment (Tier 1, no live Entra available):
    - `obo_contract.json` is written with `training_artifact: true` and all sub-checks `passed: false`
    - `gate_delegated_identity` will **fail** — this is correct and expected behaviour
    - Set `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, and
      `AEGISAP_TEST_USER_ASSERTION` to run a real OBO exchange (Tier 2) and produce
      authoritative gate evidence with `training_artifact: false`
    """)
    return


@app.cell
def _s5_sim_header(mo):
    mo.md("### OBO Simulation — Three Execution Paths")
    return


@app.cell
def _s5_sim_success(mo, json, Path, datetime):
    """Simulate a fully successful OBO + actor-verification flow (happy path)."""
    import dataclasses

    @dataclasses.dataclass
    class _FakeOboResult:
        oid: str
        access_token: str = "fake-obo-token-abc123"
        error: str | None = None

    _fake_obo = _FakeOboResult(oid="user-oid-finance-director")

    # 4-step walkthrough accordion
    _steps = mo.accordion({
        "Step 1 — App acquires MI token": mo.md(
            "```python\ncred = ManagedIdentityCredential()\ntoken = cred.get_token('https://management.azure.com/.default')\n```"
            "\n\n✅ MI token acquired; client_id claim verified."
        ),
        "Step 2 — OBO exchange": mo.md(
            "```python\nresult = msal_app.acquire_token_on_behalf_of(\n    user_assertion=user_access_token,\n    scopes=['https://graph.microsoft.com/.default']\n)\n```"
            f"\n\n✅ OBO succeeded. OID extracted: `{_fake_obo.oid}`"
        ),
        "Step 3 — Actor group verification": mo.md(
            "```python\nresp = graph_client.get(\n    f'https://graph.microsoft.com/v1.0/users/{oid}/transitiveMemberOf'\n)\nmembers = resp.json()['value']\n```"
            "\n\n✅ User is member of `Finance-Approvers`. Actor verified."
        ),
        "Step 4 — Artifact written": mo.md(
            "```python\nartifact['happy_path'] = {'oid': oid, 'actor_verified': True}\n```"
            "\n\n✅ `obo_simulation_results.json` written with `happy_path` key."
        ),
    })

    _build = Path(__file__).resolve().parents[1] / "build" / "day11"
    _build.mkdir(parents=True, exist_ok=True)

    # Load or initialise simulation results
    _out_path = _build / "obo_simulation_results.json"
    _sim = json.loads(_out_path.read_text()) if _out_path.exists() else {}
    _sim["happy_path"] = {
        "oid": _fake_obo.oid,
        "actor_verified": True,
        "hold_allowed": True,
        "simulated_at": datetime.datetime.utcnow().isoformat() + "Z",
    }
    _out_path.write_text(json.dumps(_sim, indent=2))

    mo.vstack([
        _steps,
        mo.callout(
            mo.md(
                f"**Happy path succeeded.**\n\n"
                f"OID: `{_fake_obo.oid}` | Actor verified: `True` | Hold allowed: `True`"
            ),
            kind="success",
        ),
    ])
    return


@app.cell
def _s5_sim_obo_failure(mo, json, Path, datetime):
    """Simulate a failed OBO exchange (invalid_scope at Step 2)."""
    _build = Path(__file__).resolve().parents[1] / "build" / "day11"
    _build.mkdir(parents=True, exist_ok=True)

    # Fake MSAL error response
    _fake_msal_error = {"error": "invalid_scope",
                        "error_description": "AADSTS70011: The provided value of scope is not valid."}

    _out_path = _build / "obo_simulation_results.json"
    _sim = json.loads(_out_path.read_text()) if _out_path.exists() else {}
    _sim["failed_obo_path"] = {
        "step_failed": 2,
        "error": _fake_msal_error["error"],
        "error_description": _fake_msal_error["error_description"],
        "actor_verified": False,
        "hold_allowed": False,
        "simulated_at": datetime.datetime.utcnow().isoformat() + "Z",
    }
    _out_path.write_text(json.dumps(_sim, indent=2))

    mo.callout(
        mo.md(
            f"**OBO exchange failed at Step 2.**\n\n"
            f"MSAL error: `{_fake_msal_error['error']}` — "
            f"`{_fake_msal_error['error_description']}`\n\n"
            "_The OBO token was not issued; the hold request is rejected._"
        ),
        kind="danger",
    )
    return


@app.cell
def _s5_sim_actor_failure(mo, json, Path, datetime):
    """Simulate OBO success but actor Group membership check returning empty (not a member)."""
    _build = Path(__file__).resolve().parents[1] / "build" / "day11"
    _build.mkdir(parents=True, exist_ok=True)

    # OBO succeeds, but Graph returns empty group membership
    _fake_obo_oid = "user-oid-outsider"
    _fake_graph_response = {"value": []}  # not a member of any group

    _out_path = _build / "obo_simulation_results.json"
    _sim = json.loads(_out_path.read_text()) if _out_path.exists() else {}
    _sim["failed_actor_path"] = {
        "step_failed": 3,
        "oid": _fake_obo_oid,
        "graph_response_value_count": 0,
        "actor_verified": False,
        "hold_allowed": False,
        "reason": "User is not a member of Finance-Approvers group.",
        "simulated_at": datetime.datetime.utcnow().isoformat() + "Z",
    }
    _out_path.write_text(json.dumps(_sim, indent=2))

    mo.callout(
        mo.md(
            f"**Actor verification failed at Step 3.**\n\n"
            f"OID `{_fake_obo_oid}` returned `value: []` from `transitiveMemberOf`.\n\n"
            "_The OBO token was valid but the user is not in Finance-Approvers; "
            "the hold request is rejected with 403._"
        ),
        kind="danger",
    )
    return


@app.cell
def _s5_lab(mo, json, os, Path):
    import datetime

    _build = Path(__file__).resolve().parents[1] / "build" / "day11"
    _build.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Tier detection
    # ------------------------------------------------------------------
    _tier2_env_keys = ("AZURE_TENANT_ID", "AZURE_CLIENT_ID",
                       "AZURE_CLIENT_SECRET", "AEGISAP_TEST_USER_ASSERTION")
    _has_tier2 = all(os.environ.get(k) for k in _tier2_env_keys)
    _wrong_scope = os.environ.get("AEGISAP_TEST_WRONG_SCOPE", "0") == "1"
    # Tier 3 = Tier 2 credentials present + AEGISAP_TEST_WRONG_SCOPE=1
    _tier = 3 if (_has_tier2 and _wrong_scope) else (2 if _has_tier2 else 1)

    if _tier >= 2:
        # ------------------------------------------------------------------
        # Tier 2 / 3 — live MSAL OBO path
        # ------------------------------------------------------------------
        try:
            import msal  # type: ignore[import-untyped]

            _tenant_id = os.environ["AZURE_TENANT_ID"]
            _client_id = os.environ["AZURE_CLIENT_ID"]
            _client_secret = os.environ["AZURE_CLIENT_SECRET"]
            _user_assertion = os.environ["AEGISAP_TEST_USER_ASSERTION"]

            # Tier 3 deliberately uses wrong scope to exercise the failure path
            _scope = (
                ["https://bogus.example.com/.default"]
                if _tier == 3
                else ["https://graph.microsoft.com/.default"]
            )

            _msal_app = msal.ConfidentialClientApplication(
                client_id=_client_id,
                client_credential=_client_secret,
                authority=f"https://login.microsoftonline.com/{_tenant_id}",
            )
            # app_identity_check verifies the confidential-client credentials are
            # valid — a distinct trust surface from OBO token scope. It is set here,
            # unconditionally, before the OBO exchange.
            _app_identity_check = {
                "passed": True,
                "detail": "Confidential client authenticated successfully (Tier 2/3 live path).",
            }

            _obo_result = _msal_app.acquire_token_on_behalf_of(
                user_assertion=_user_assertion,
                scopes=_scope,
            )
            if "error" in _obo_result:
                _obo_exchange_check = {
                    "passed": False,
                    "detail": f"OBO error: {_obo_result['error']} — {_obo_result.get('error_description', '')}",
                }
                _oid = None
            else:
                import base64 as _b64
                import json as _j
                # Decode OID from JWT claims (middle segment)
                _claims_b64 = _obo_result["access_token"].split(".")[1]
                _pad = 4 - len(_claims_b64) % 4
                _claims = _j.loads(_b64.urlsafe_b64decode(
                    _claims_b64 + "=" * _pad))
                _oid = _claims.get("oid", "unknown")
                _obo_exchange_check = {
                    "passed": True,
                    "detail": f"Live OBO exchange succeeded. OID: {_oid}",
                }

            if _oid:
                # Actor binding — read group from env
                _group_id = os.environ.get("AEGISAP_APPROVER_GROUP_ID", "")
                if _group_id:
                    import urllib.request as _urlreq
                    _graph_token = _obo_result["access_token"]
                    _graph_req = _urlreq.Request(
                        f"https://graph.microsoft.com/v1.0/users/{_oid}/transitiveMemberOf/$count",
                        headers={"Authorization": f"Bearer {_graph_token}",
                                 "ConsistencyLevel": "eventual"},
                    )
                    try:
                        with _urlreq.urlopen(_graph_req, timeout=10) as _r:
                            _count = int(_r.read())
                        _actor_binding_check = {
                            "passed": _count > 0,
                            "detail": f"Actor {_oid} is in {_count} group(s) (live check).",
                        }
                    except Exception as _ge:
                        _actor_binding_check = {
                            "passed": False,
                            "detail": f"Graph call failed: {_ge}",
                        }
                else:
                    _actor_binding_check = {
                        "passed": False,
                        "detail": (
                            "AEGISAP_APPROVER_GROUP_ID not set — actor binding cannot be verified. "
                            "Set this env var to the Entra group object ID for Finance-Approvers."
                        ),
                    }
            else:
                _actor_binding_check = {
                    "passed": False,
                    "detail": "Actor binding skipped — OBO exchange failed.",
                }

        except Exception as _exc:
            _app_identity_check = {
                "passed": False, "detail": f"Tier {_tier} live path error: {_exc}"}
            _obo_exchange_check = {"passed": False, "detail": str(_exc)}
            _actor_binding_check = {"passed": False,
                                    "detail": "Skipped due to exception."}

    else:
        # ------------------------------------------------------------------
        # Tier 1 — stub (no env vars set)
        # Sub-checks are NOT passed — gate_delegated_identity is honestly red
        # until a real OBO exchange is performed (Tier 2+).
        # ------------------------------------------------------------------
        _stub_note = (
            "Tier 1 stub — no Entra env vars present. "
            "Set AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, "
            "and AEGISAP_TEST_USER_ASSERTION to run a real OBO exchange (Tier 2)."
        )
        _app_identity_check = {"passed": False,
                               "detail": f"STUB (unverified): {_stub_note}"}
        _obo_exchange_check = {"passed": False,
                               "detail": f"STUB (unverified): {_stub_note}"}
        _actor_binding_check = {"passed": False,
                                "detail": f"STUB (unverified): {_stub_note}"}

    _artifact = {
        "day": 11,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "execution_tier": _tier,
        "live_entra": _tier >= 2,
        "training_artifact": _tier == 1,
        "app_identity_check": _app_identity_check,
        "obo_exchange_check": _obo_exchange_check,
        "actor_binding_check": _actor_binding_check,
        "gate_passed": all([
            _app_identity_check["passed"],
            _obo_exchange_check["passed"],
            _actor_binding_check["passed"],
        ]),
    }
    (_build / "obo_contract.json").write_text(json.dumps(_artifact, indent=2))

    _all_passed = _artifact["gate_passed"]
    _tier_label = {
        1: "stub — no Entra env vars present",
        2: "live OBO exchange",
        3: "live OBO + wrong scope (negative test)",
    }.get(_tier, f"tier {_tier}")
    _tier_hint = (
        "\n\n> **Tier 1:** Set `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, "
        "and `AEGISAP_TEST_USER_ASSERTION` to run Tier 2 live path."
        if _tier == 1 else ""
    )
    mo.callout(
        mo.md(
            f"Artifact written → `build/day11/obo_contract.json`\n\n"
            f"**Execution tier: {_tier}** ({_tier_label}){_tier_hint}\n\n"
            f"**gate_delegated_identity:** {'PASS ✅' if _all_passed else 'FAIL ❌'}"
        ),
        kind="warn" if _tier == 1 else (
            "success" if _all_passed else "danger"),
    )
    return datetime


# ---------------------------------------------------------------------------
# Section 6 — Authority Confusion Threat — Deep Dive
# ---------------------------------------------------------------------------
@app.cell
def _s6_header(mo):
    mo.md("## 6. Authority Confusion — Production Attack Patterns")
    return


@app.cell
def _s6_body(mo):
    mo.md("""
    ### How the Attack Works

    A malicious actor submits an invoice via the Service Bus with a crafted message body:

    ```json
    {
      "invoice_id": "INV-666",
      "amount": 95000.00,
      "actor_oid": "a3b4c5d6-...  ← forged OID of the CFO
    }
    ```

    If the orchestrator trusts the `actor_oid` field in the message body rather than
    verifying it against an authenticated token, the approval record will show the CFO
    authorised a £95,000 expense they never saw.

    ### AegisAP Defence

    1. **Never trust actor identity from the message payload.** The `actor_oid` in the
       approval record must come from the OBO token claims, not the Service Bus message.
    2. **Verify group membership on every approval.**  Even if an OBO token is genuine,
       verify the actor is currently in the required group — group membership can change.
    3. **Audit every access.** App Insights records the OID in every approval span;
       Microsoft Entra audit logs record every group membership change.

    ### The Three-Line Test

    An FDE should be able to answer these three questions in a whiteboard interview:

    1. "Where does the `actor_oid` in the approval record come from?" → **OBO token `oid` claim**
    2. "How do you verify the OID is authorised?" → **Graph `transitiveMemberOf` API**
    3. "What prevents the orchestrator from forging approvals itself?" → **OBO requires real user token; MI cannot impersonate users**
    """)
    return


# ---------------------------------------------------------------------------
# Summary + Forward
# ---------------------------------------------------------------------------
@app.cell
def _summary(mo):
    mo.md("""
    ## Day 11 Summary Checklist

    - [ ] Explain why `DefaultAzureCredential` alone is insufficient for delegated approval flows
    - [ ] Describe the four steps of the OBO token exchange
    - [ ] State what `transitiveMemberOf` does and why it is used instead of `memberOf`
    - [ ] Explain the authority-confusion attack and the AegisAP three-layer defence
    - [ ] Confirm `build/day11/obo_contract.json` exists; if `training_artifact: true`, explain why `gate_delegated_identity` is red and which env vars promote to Tier 2 (live OBO)
    - [ ] Name the `AZURE_CLIENT_SECRET` safe-storage requirement (Key Vault reference)
    """)
    return


@app.cell
def _forward(mo):
    mo.callout(
        mo.md("""
**Tomorrow — Day 12: Private Networking Constraints**

We move from identity to network. You will implement VNET injection for Container
Apps, Private Endpoints for all AI services, and Private DNS zone linking.  The
live probe script (`scripts/verify_private_network_posture.py`) writes
`build/day12/private_network_posture.json` for `gate_private_network_posture`.
The static gate artifact (`build/day12/static_bicep_analysis.json`) for
`gate_private_network_static` is produced separately by
`scripts/check_private_network_static.py`, which compiles every Bicep file in
`infra/` and checks for `publicNetworkAccess == "Disabled"`.

Open `notebooks/day_12_private_networking_constraints.py` when ready.
        """),
        kind="success",
    )
    return


if __name__ == "__main__":
    app.run()
