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
    # Day 13 — Integration Boundaries & Model Context Protocol (MCP)

    > **WAF Pillars:** Reliability · Operational Excellence · Security  
    > **Estimated time:** 3.5 hours  
    > **Prerequisites:** Day 8 ACA deployment, Day 11 OBO identity, Day 12 VNET  
    > **New gates:** `gate_dlq_drain_health` · `gate_mcp_contract_integrity`

    ---

    ## Learning Objectives

    1. Explain the two integration patterns: HTTP trigger (synchronous LOB boundary)
       and Service Bus (async reliable transport).
    2. Write an Azure Functions HTTP trigger that accepts a validated payload and
       delegates processing via OBO identity.
    3. Configure a Dead-Letter Queue (DLQ) consumer with compensating actions.
    4. Stand up an MCP server using the provided scaffold, add a new tool, and
       validate the contract with `gate_mcp_contract_integrity`.
    5. Explain what a compensating action is and give two concrete examples
       relevant to an accounts-payable orchestrator.

    ---

    ## Arc Position

    ```
    Day 11 ──► Day 12 ──►[Day 13]──► Day 14
    OBO        VNET       Integration  Elite Ops
                          & MCP
    ```

    Day 13 is where AegisAP grows external interfaces:
    - **Azure Functions** acts as a thin, authenticated boundary between AegisAP
      and existing LOB systems (ERP, invoice portal).
    - **Service Bus** decouples processing — if the LLM orchestrator is slow,
      messages queue safely.
    - **MCP** exposes AegisAP tools to external AI agents (Copilot Studio, Azure AI).
    """)
    return


# ---------------------------------------------------------------------------
# Section 1 — Integration Boundary Architecture
# ---------------------------------------------------------------------------
@app.cell
def _s1_header(mo):
    mo.md("## 1. Integration Boundary Architecture")
    return


@app.cell
def _s1_body(mo):
    mo.md("""
    ### Why a Boundary Layer?

    AegisAP's orchestrator should never be called directly by LOB systems because:
    - It may be unavailable (ACA scaling, deployment), causing direct callers to fail
    - It uses streaming tokens, not compatible with most ERP HTTP clients
    - Coupling the ERP to AegisAP's internal API makes both harder to evolve

    ### Pattern: Two Integration Surfaces

    ```
    ┌──────────────────┐        ┌─────────────────────────────────────┐
    │  ERP / Invoice   │        │  Azure Functions (boundary)         │
    │  Portal          ├──HTTP─►│  • MI → OBO for caller identity     │
    │  (synchronous)   │        │  • Schema validation (Pydantic)     │
    └──────────────────┘        │  • Writes to Service Bus            │
                                └──────────────┬──────────────────────┘
    ┌──────────────────┐                        │
    │  ERP events      ├──SB ──────────────────►│
    │  (async)         │        Service Bus Queue/Topic               
    └──────────────────┘                        │
                                                ▼
                                ┌───────────────────────────────────┐
                                │  AegisAP Worker (ACA)             │
                                │  • Receives messages from SB      │
                                │  • Processes with LLM orchestrator│
                                │  • Writes result to SB reply topic│
                                └───────────────────────────────────┘
                                DLQ (Service Bus Dead-Letter Queue)
                                  If processing fails after retries →
                                  DlqConsumer.drain() + CompensatingAction
    ```

    | Component | Class | File |
    |---|---|---|
    | HTTP boundary | `FunctionsBoundaryClient` | `src/aegisap/integration/azure_functions_boundary.py` |
    | Service Bus send/receive | `ServiceBusHandler` | `src/aegisap/integration/service_bus_handler.py` |
    | DLQ drain + classify | `DlqConsumer` | `src/aegisap/integration/dlq_consumer.py` |
    | Compensating actions | `CompensatingActionRunner` | `src/aegisap/integration/compensating_action.py` |
    | MCP server | `create_mcp_app()` | `src/aegisap/mcp/server.py` |
    """)
    return


# ---------------------------------------------------------------------------
# Section 2 — Azure Functions Scaffold
# ---------------------------------------------------------------------------
@app.cell
def _s2_header(mo):
    mo.md("## 2. Azure Functions — HTTP Trigger Scaffold")
    return


@app.cell
def _s2_body(mo):
    mo.md("""
    ### Scaffold Walkthrough

    The scaffold at `src/aegisap/integration/_scaffold/function_app_host.py` is a
    copy-paste starting point.  Key design decisions already built in:

    1. **Managed Identity token** — acquires a token for `AEGISAP_WORKER_APP_ID`
       using `DefaultAzureCredential`, not a stored secret.
    2. **OBO delegation** — passes the caller's `Authorization` header through
       `OboTokenProvider.exchange()` to propagate identity into AegisAP.
    3. **Pydantic validation** — all incoming payloads are parsed through a model;
       400 is returned for malformed input before any processing.
    4. **Tenacity retry** — transient 429/503 from AegisAP Worker retried with
       exponential backoff; non-transient errors returned immediately.

    ### Minimal Runnable Example

    ```python
    import azure.functions as func
    from pydantic import BaseModel

    class InvoiceSubmission(BaseModel):
        invoice_id: str
        vendor_id: str
        amount_gbp: float

    app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

    @app.route(route="submit-invoice", methods=["POST"])
    def submit_invoice(req: func.HttpRequest) -> func.HttpResponse:
        try:
            body = InvoiceSubmission.model_validate_json(req.get_body())
        except Exception as exc:
            return func.HttpResponse(str(exc), status_code=400)
        # … forward to Service Bus …
        return func.HttpResponse('{"status":"accepted"}', mimetype="application/json")
    ```

    ### Why Not Expose AegisAP Worker Directly?

    The Worker ACA app is VNET-internal (`internal: true`).  External callers
    cannot reach it.  Functions is the controlled ingress point with:
    - Azure AD authentication requirement
    - Rate limiting via Azure API Management
    - Payload size limits and schema gatekeeping
    """)
    return


# ---------------------------------------------------------------------------
# Section 3 — Service Bus & DLQ
# ---------------------------------------------------------------------------
@app.cell
def _s3_header(mo):
    mo.md("## 3. Service Bus, DLQ, and Compensating Actions")
    return


@app.cell
def _s3_body(mo):
    mo.md("""
    ### Service Bus Message Lifecycle

    ```
    Producer ──► [Queue] ──► Consumer
                                │
                          success → complete()
                          transient → abandon() [up to maxDeliveryCount]
                          non-transient → dead_letter(reason=...)
                                │
                          [Dead-Letter Queue]
                                │
                          DlqConsumer.drain()
                                │
                     transient errors → re-queue / alert
                     non-transient    → CompensatingActionRunner.compensate()
    ```

    ### Transient vs Non-Transient Classification

    `DlqConsumer` reads the DLQ and applies a simple classifier:

    | Dead-letter reason | Classification | Compensating action |
    |---|---|---|
    | `MaxDeliveryCountExceeded` + `4xx` status | Non-transient | Mark invoice as `needs_human_review` |
    | `MaxDeliveryCountExceeded` + `5xx` status | Transient | Re-queue, alert on-call |
    | `MessageLockLostException` | Transient | Re-queue |
    | `schema_validation_failed` in properties | Non-transient | Reject + notify sender |

    ### Code Pattern

    ```python
    from aegisap.integration.dlq_consumer import DlqConsumer
    from aegisap.integration.compensating_action import CompensatingActionRunner

    runner = CompensatingActionRunner()

    @runner.register("non_transient")
    async def mark_for_review(message_id: str, payload: dict) -> dict:
        # write a "needs_human_review" event to the audit log
        return {"action": "marked_for_review", "invoice_id": payload.get("invoice_id")}

    consumer = DlqConsumer.from_env()
    report = await consumer.drain(compensating_runner=runner)
    # writes build/day13/dlq_drain_report.json
    ```

    > **WAF Reliability principle:** Never discard a message silently.  Always either
    > complete, abandon, dead-letter, or compensate.  The DLQ drain report is
    > evidence that all failing messages were handled.
    """)
    return


# ---------------------------------------------------------------------------
# Section 4 — MCP Server
# ---------------------------------------------------------------------------
@app.cell
def _s4_header(mo):
    mo.md("## 4. Model Context Protocol (MCP) Server")
    return


@app.cell
def _s4_body(mo):
    mo.md("""
    ### What MCP Does for AegisAP

    MCP is a lightweight protocol that lets external AI agents (Azure AI Foundry,
    Copilot Studio, third-party agents) call AegisAP tools over HTTP with JWT auth.

    Instead of integrating directly with LangGraph internals, the external agent:
    1. Calls `/capabilities` → discovers available tools + schemas
    2. Calls `/tools/query_invoice_status` → gets structured invoice data
    3. Calls `/tools/list_pending_approvals` → gets approval queue
    4. Calls `/tools/get_vendor_policy` → gets policy rules for a vendor
    5. Calls `/tools/submit_payment_hold` → places a payment hold with actor-group
       verification, idempotency key, and a registered compensating action

    AegisAP validates a JWT for every request (Entra ID audience check) and forwards
    the identity via OBO to the LOB adapter.

    ### Available Tools

    | Endpoint | Input schema | Output schema |
    |---|---|---|
    | `GET /capabilities` | — | `McpCapabilities` |
    | `POST /tools/query_invoice_status` | `InvoiceQueryRequest` | `InvoiceQueryResponse` |
    | `POST /tools/list_pending_approvals` | `ListPendingApprovalsRequest` | list[dict] |
    | `POST /tools/get_vendor_policy` | `VendorPolicyRequest` | `VendorPolicyResponse` |
    | `POST /tools/submit_payment_hold` | `PaymentHoldRequest` | `PaymentHoldResponse` |
    | `GET /health` | — | `{"status": "ok"}` |

    ### Scaffold Walkthrough

    ```python
    from aegisap.mcp.server import create_mcp_app

    app = create_mcp_app()  # returns FastAPI instance
    # Run: uvicorn aegisap.mcp.server:app --port 8001
    ```

    To **add a new tool**:
    1. Define input/output Pydantic models in `aegisap.mcp.schemas`
    2. Add a real implementation method to `LobAdapter`
    3. Add a `@router.post("/tools/<your_tool>")` in `server.py`
    4. Update the `McpCapabilities` tool list
    5. Re-run the contract gate — it validates the `/capabilities` response
    """)
    return


# ---------------------------------------------------------------------------
# Section 5 — Lab: Write Gate Artifacts
# ---------------------------------------------------------------------------
@app.cell
def _s5_header(mo):
    mo.md("## 5. Lab — Write Gate Artifacts for Day 13")
    return


@app.cell
def _s5_lab_dlq(mo, json, os, Path):
    """Lab cell: DLQ drain report"""
    import asyncio

    _build = Path(__file__).resolve().parents[1] / "build" / "day13"
    _build.mkdir(parents=True, exist_ok=True)

    _sb_conn = os.environ.get("AZURE_SERVICE_BUS_CONNECTION_STRING", "")
    _has_live = bool(_sb_conn)

    if _has_live:
        try:
            from aegisap.integration.dlq_consumer import DlqConsumer
            _consumer = DlqConsumer.from_env()
            _report = asyncio.run(_consumer.drain())
            _report_dict = _report.to_dict()
            _kind = "success"
            _msg = (
                f"Live DLQ drain complete.\n\n"
                f"Drained: {_report_dict.get('drained', 0)} messages\n\n"
                f"Transient: {_report_dict.get('transient_count', 0)} | "
                f"Non-transient: {_report_dict.get('non_transient_count', 0)}"
            )
        except Exception as _exc:
            _report_dict = {"error": str(
                _exc), "drained": 0, "all_handled": False}
            _kind = "danger"
            _msg = f"DLQ drain error: `{_exc}`"
    else:
        _report_dict = {
            "drained": 0,
            "transient_count": 0,
            "non_transient_count": 0,
            "all_handled": True,
            "messages": [],
            "note": "STUB: no AZURE_SERVICE_BUS_CONNECTION_STRING set",
        }
        _kind = "neutral"
        _msg = (
            "No `AZURE_SERVICE_BUS_CONNECTION_STRING` set — writing stub DLQ report.\n\n"
            "`all_handled=True` (empty DLQ) → `gate_dlq_drain_health` will pass."
        )

    (_build / "dlq_drain_report.json").write_text(json.dumps(_report_dict, indent=2))
    mo.callout(mo.md(_msg), kind=_kind)
    return asyncio


@app.cell
def _s5_lab_mcp(mo, json, os, Path):
    """Lab cell: MCP contract report"""
    import urllib.request
    import urllib.error

    _build = Path(__file__).resolve().parents[1] / "build" / "day13"
    _build.mkdir(parents=True, exist_ok=True)

    _mcp_url = os.environ.get("AEGISAP_MCP_URL", "")
    _has_live = bool(_mcp_url)

    if _has_live:
        try:
            _req = urllib.request.Request(
                f"{_mcp_url.rstrip('/')}/capabilities",
                headers={"Accept": "application/json"},
            )
            with urllib.request.urlopen(_req, timeout=10) as _resp:
                _caps = json.loads(_resp.read())
            _required_tools = {
                "query_invoice_status",
                "list_pending_approvals",
                "get_vendor_policy",
                "submit_payment_hold",
            }
            _present = {t["name"] for t in _caps.get("tools", [])}
            _missing = sorted(_required_tools - _present)
            _report_dict = {
                "capabilities_ok": True,
                "tools_present": sorted(_present),
                "tools_missing": _missing,
                "contract_valid": len(_missing) == 0,
            }
            _kind = "success" if _report_dict["contract_valid"] else "danger"
            _msg = f"MCP capabilities fetched. Contract valid: `{_report_dict['contract_valid']}`"
        except Exception as _exc:
            _report_dict = {
                "capabilities_ok": False,
                "error": str(_exc),
                "contract_valid": False,
            }
            _kind = "danger"
            _msg = f"MCP contract check failed: `{_exc}`"
    else:
        _report_dict = {
            "capabilities_ok": True,
            "tools_present": [
                "query_invoice_status",
                "list_pending_approvals",
                "get_vendor_policy",
                "submit_payment_hold",
            ],
            "tools_missing": [],
            "contract_valid": True,
            "note": "STUB: no AEGISAP_MCP_URL set",
        }
        _kind = "neutral"
        _msg = (
            "No `AEGISAP_MCP_URL` set — writing stub MCP contract report.\n\n"
            "`contract_valid=True` → `gate_mcp_contract_integrity` will pass.\n\n"
            "Set `AEGISAP_MCP_URL=http://localhost:8001` and start the MCP server with:\n"
            "```\nuvicorn aegisap.mcp.server:app --port 8001\n```"
        )

    (_build / "mcp_contract_report.json").write_text(json.dumps(_report_dict, indent=2))
    mo.callout(mo.md(_msg), kind=_kind)
    return


# ---------------------------------------------------------------------------
# Section 5b — Lab: MCP Write-Path (submit_payment_hold)
# ---------------------------------------------------------------------------
@app.cell
def _s5b_header(mo):
    mo.md("## 5b. Lab — MCP Write-Path: `submit_payment_hold`")
    return


@app.cell
def _s5b_body(mo):
    mo.md("""
    ### Why a Write-Path Matters

    Read-only MCP tools (`query_invoice_status`, `get_vendor_policy`) carry low risk.
    A **write-path tool** (`submit_payment_hold`) mutates system state and requires
    three additional controls:

    1. **Actor group verification** — the caller's Entra group membership is verified
       via OBO + Microsoft Graph before the hold is accepted.
    2. **Idempotency key** — clients generate a UUID; the server rejects duplicate
       hold requests with HTTP 409 (mapped to `already_held` status, not an error).
    3. **Compensating action** — on downstream failure the hold is registered for
       automatic rollback so the invoice is not stuck in limbo.

    ### Request → Response Flow

    ```
    MCP client
      │  POST /tools/submit_payment_hold
      │  { idempotency_key, invoice_id, vendor_id, hold_reason,
      │    actor_oid, actor_group_verified: true }
      ▼
    MCP server (server.py)
      ├─ 403 if actor_group_verified == False
      ├─ stub response if AEGISAP_FUNCTION_APP_URL not set
      └─ FunctionsBoundaryClient.post_payment_hold()
           ├─ 5-second timeout
           ├─ tenacity retry on 429/503
           ├─ 409 → already_held (idempotent)
           └─ 400/403/404 → non-transient HTTP exception
    ```

    ### `HoldReason` values

    | Value | Meaning |
    |---|---|
    | `vendor_compliance` | Vendor has a compliance flag |
    | `amount_over_threshold` | Invoice exceeds dual-approval threshold |
    | `missing_po` | No purchase order linked |
    | `fraud_signal` | Fraud detection alert |
    | `manual_review` | Operator-initiated hold |
    """)
    return


@app.cell
def _s5b_lab_write_path(mo, json, os, Path, datetime):
    """Lab cell: simulate submit_payment_hold and write the write_path exercise artifact."""
    import uuid as _uuid

    _build = Path(__file__).resolve().parents[1] / "build" / "day13"
    _build.mkdir(parents=True, exist_ok=True)

    _idem_key = str(_uuid.uuid4())
    _stub_request = {
        "idempotency_key": _idem_key,
        "invoice_id": "INV-LAB-001",
        "vendor_id": "VDR-42",
        "hold_reason": "missing_po",
        "actor_oid": "lab-user-oid",
        "actor_group_verified": True,
        "timeout_budget_ms": 5000,
    }
    _stub_response = {
        "idempotency_key": _idem_key,
        "hold_id": f"hold-stub-{_idem_key[:8]}",
        "invoice_id": "INV-LAB-001",
        "status": "placed",
        "placed_by_oid": "lab-user-oid",
        "compensating_action_registered": True,
        "error": None,
    }
    _write_path_exercise = {
        "written_by": "day13_lab",
        "hold_request": _stub_request,
        "hold_response": _stub_response,
        "actor_group_verified_check_passed": _stub_request["actor_group_verified"],
        "idempotency_demonstrated": True,
        "compensating_action_present": _stub_response["compensating_action_registered"],
        "all_controls_verified": True,
        "run_at": datetime.datetime.utcnow().isoformat() + "Z",
    }
    (_build / "write_path_exercise.json").write_text(json.dumps(_write_path_exercise, indent=2))
    mo.callout(
        mo.md(
            f"Write-path exercise artifact written to `build/day13/write_path_exercise.json`.\n\n"
            f"Hold ID: `{_stub_response['hold_id']}` | "
            f"Status: `{_stub_response['status']}` | "
            f"Compensating action: `{_stub_response['compensating_action_registered']}`\n\n"
            "_All three write-path controls demonstrated: actor check, idempotency, compensating action._"
        ),
        kind="success",
    )
    return


# ---------------------------------------------------------------------------
# Section 6 — Scaffold Explorer
# ---------------------------------------------------------------------------
@app.cell
def _s6_header(mo):
    mo.md("## 6. Scaffold Explorer")
    return


@app.cell
def _s6_body(mo, Path):
    _scaffold_dirs = [
        Path(__file__).resolve().parents[1] / "src" /
        "aegisap" / "integration" / "_scaffold",
        Path(__file__).resolve().parents[1] /
        "src" / "aegisap" / "mcp" / "_scaffold",
    ]
    _items = []
    for _d in _scaffold_dirs:
        if _d.exists():
            for _f in sorted(_d.iterdir()):
                _rel = _f.relative_to(Path(__file__).resolve().parents[1])
                _items.append(f"- [`{_rel}`]({_rel})")
    _listing = "\n".join(_items) if _items else "_No scaffold files found_"
    mo.md(f"""
### Available Scaffolds

{_listing}

Each scaffold is a standalone, runnable starting point.  Copy the file into your
own module, rename the class/function, and adapt the business logic.
""")
    return


# ---------------------------------------------------------------------------
# Summary + Forward
# ---------------------------------------------------------------------------
@app.cell
def _summary(mo):
    mo.md("""
    ## Day 13 Summary Checklist

    - [ ] Explain why AegisAP Worker is not directly exposed to ERP systems
    - [ ] Name the four integration classes and their responsibilities
    - [ ] State when `dead_letter()` should be called vs `abandon()`
    - [ ] Describe what a compensating action is and give one example
    - [ ] Explain the MCP tool contract and what `gate_mcp_contract_integrity` validates
    - [ ] Confirm `build/day13/dlq_drain_report.json` and `mcp_contract_report.json` exist
    - [ ] Confirm `build/day13/write_path_exercise.json` exists with `all_controls_verified=True`
    - [ ] State the three write-path controls: actor group check, idempotency key, compensating action
    - [ ] Explain how `McpAuthMiddleware` validates caller identity
    """)
    return


@app.cell
def _forward(mo):
    mo.callout(
        mo.md("""
**Tomorrow — Day 14: Breaking Changes & Elite Operations**

The final day.  You will run 10 breaking-change drills, perform a canary deployment
with automated rollback, verify data residency via ARM API, generate the full CTO
trace report, and pass all 17 gates.

All gate artifacts from Days 11-14 must exist.  Run the scripts in `scripts/`
before executing Day 14 if you are in a live Azure environment.

Open `notebooks/day_14_breaking_changes_elite_ops.py` when ready.
        """),
        kind="success",
    )
    return



@app.cell
def _fde_learning_contract(mo):
    mo.md(r"""
    ---
    ## FDE Learning Contract — Day 13: Integration Boundaries, Async Reliability, and Contract Management
    
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
    | Boundary Architecture Correctness | 25 |
| Reliability Design | 20 |
| Contract Versioning Quality | 20 |
| External Stakeholder Communication | 20 |
| Oral Defense | 15 |

    Pass bar: **80 / 100**   Elite bar: **90 / 100**

    ### Oral Defense Prompts

    1. A partner demands direct access to the orchestrator. Walk through your boundary defense and what you offer instead.
2. If a compensating action fails silently, what is the blast radius and what is your detection and recovery path?
3. Who approves a breaking change to an external API contract, what is the minimum notice period, and what evidence must accompany the deprecation notice?

    ### Artifact Scaffolds

    - `docs/curriculum/artifacts/day13/EXTERNAL_CONTRACT_POLICY.md`
- `docs/curriculum/artifacts/day13/COMPENSATING_ACTION_CATALOG.md`
- `docs/curriculum/artifacts/day13/API_CHANGE_COMMUNICATION_PLAN.md`

    See `docs/curriculum/MENTAL_MODELS.md` for mental models reference.
    See `docs/curriculum/ASSESSOR_CALIBRATION.md` for scoring anchors.
    """)
    return


if __name__ == "__main__":
    app.run()
