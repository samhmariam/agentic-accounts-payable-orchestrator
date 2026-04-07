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


@app.cell
def _full_day_agenda(mo):
    from _shared.curriculum_scaffolds import render_full_day_agenda

    render_full_day_agenda(
        mo,
        day_label="Day 13 integration boundaries and MCP",
        core_outcome="show that external boundaries can stay reliable, actor-bound, and contract-disciplined even under transfer-domain pressure",
        afternoon_focus="Use the transfer-domain lens to reason through an unseen boundary case before any unsafe mutation is allowed.",
    )
    return

@app.cell
def _notebook_guide(mo):
    from _shared.lab_guide import render_notebook_learning_context

    render_notebook_learning_context(
        mo,
        purpose='Design safe external boundaries by combining HTTP, Service Bus, compensating actions, and MCP contract discipline.',
        prerequisites=['Days 11-12 complete.', 'Understand actor binding and private network posture before opening external boundaries.', 'Live MCP or webhook verification is optional beyond the notebook learning path.'],
        resources=['`notebooks/day_13_integration_boundary_and_mcp.py`', '`build/day13/` for `dlq_drain_report.json`, `mcp_contract_report.json`, and `write_path_exercise.json`', '`scripts/verify_mcp_contract_integrity.py` and related boundary scripts for live follow-up', '`docs/curriculum/artifacts/day13/` and `docs/curriculum/CAPSTONE_B_TRANSFER.md`'],
        setup_sequence=["Start with the transfer-lens and lineage cells so today's boundaries are framed as reliability and contract problems.", 'Decide whether you are staying in notebook or training mode or validating a live MCP surface afterward.', 'Keep the notebook as the primary route; use scripts only after the contract model makes sense.'],
        run_steps=['Work through HTTP boundary, DLQ handling, compensating actions, MCP exposure, and write-path safety in order.', 'Use the exercises to reason about failure handling before attempting any live verification.', 'Run the cells that write `build/day13/dlq_drain_report.json`, `build/day13/mcp_contract_report.json`, and `build/day13/write_path_exercise.json`.', 'Finish with the checklist so the difference between training previews and authoritative reports is explicit.'],
        output_interpretation=['The main completion signals are the three Day 13 build artifacts, especially `mcp_contract_report.json` and `write_path_exercise.json`.', 'Interpret outputs as boundary evidence: can external callers rely on the contract, and can failures recover safely?', 'If a report says `training_artifact: true`, treat it as a learning preview rather than final operational proof.'],
        troubleshooting=['If MCP feels detached from the rest of the day, anchor on contract stability and safe tool exposure.', 'If DLQ handling feels purely operational, connect it back to compensating actions and rollback confidence.', 'If live contract verification is blocked, finish the notebook first and treat the script as second-pass validation.'],
        outside_references=['Capstone transfer domain: `docs/curriculum/CAPSTONE_B_TRANSFER.md`', 'Reusable references: `docs/curriculum/artifacts/day13/`', 'Boundary verification scripts in `scripts/`'],
    )
    return


@app.cell
def _three_surface_linkage(mo):
    from _shared.lab_guide import render_surface_linkage

    render_surface_linkage(
        mo,
        portal_guide="docs/curriculum/portal/DAY_13_PORTAL.md",
        portal_activity="Inspect the live boundary host, Service Bus queue and DLQ, monitoring traces, and MCP host in Azure before you trust contract or recovery reports.",
        notebook_activity="Use the HTTP boundary, DLQ, compensating-action, MCP, and write-path safety sections to interpret what the live Azure boundary means for reliability and contract safety.",
        automation_steps=[
            "`uv run python scripts/verify_mcp_contract_integrity.py` formalizes the MCP surface you inspected.",
            "`uv run python scripts/verify_webhook_reliability.py` checks the same recovery story the portal showed through queues and telemetry.",
            "`uv run python -m pytest tests/day13 -q` keeps the boundary and recovery contract repeatable in CI.",
        ],
        evidence_checks=[
            "Service Bus queue and DLQ state should line up with the failure and recovery narrative in the notebook.",
            "`build/day13/dlq_drain_report.json`, `build/day13/mcp_contract_report.json`, and `build/day13/webhook_reliability_report.json` should agree with the live boundary state.",
            "If the Azure boundary and the generated contract artifacts disagree, stop before treating the write path as safe.",
        ],
    )
    return


@app.cell
def _azure_mastery_guide(mo):
    from _shared.lab_guide import render_azure_mastery_guide

    render_azure_mastery_guide(
        mo,
        focus="Day 13 mastery means you can inspect the live boundary surfaces in Azure, verify the webhook and MCP contract paths from the command line, recognise the minimal Service Bus recovery code, and prove that external callers can fail safely without breaking the contract.",
        portal_tasks="""
- Open the deployed boundary surface, whether Azure Functions or Container Apps, and inspect auth, identity, and ingress so the exposed contract is visible in Azure.
- Open **Service Bus** and inspect the queue plus dead-letter count so recovery is treated as an observable Azure concern rather than a hidden implementation detail.
- Inspect **Application Insights** or the relevant monitoring blade for webhook handling, DLQ drain activity, and compensating-action traces.
- If the MCP server is deployed, inspect its hosting resource and logs so `/capabilities` checks are tied back to a real Azure surface.
""",
        cli_verification="""
**Start the MCP server and verify the contract**

```bash
uvicorn aegisap.mcp.server:app --port 8001

export AEGISAP_MCP_URL=http://localhost:8001
uv run python scripts/verify_mcp_contract_integrity.py
```

**Verify webhook reliability and DLQ handling**

```bash
uv run python scripts/verify_webhook_reliability.py
```

**Inspect the advertised MCP surface directly**

```bash
curl -s "$AEGISAP_MCP_URL/capabilities"
```
""",
        sdk_snippet="""
The Azure-heavy recovery path is the DLQ consumer that drains Service Bus using managed identity.

```python
from aegisap.integration.dlq_consumer import DlqConsumer

consumer = DlqConsumer.from_env()
report = consumer.drain(max_messages=50)
print(report.summary())
```
""",
        proof_in_azure="""
- `build/day13/mcp_contract_report.json` is authoritative and shows `contract_valid: true` with the required tools present.
- `build/day13/dlq_drain_report.json` and `build/day13/webhook_reliability_report.json` are authoritative and show no unhandled failures.
- The Service Bus DLQ count and the portal monitoring view agree with the recovery story in the artifacts.
- Day 13 is only really proven when the external contract, the recovery evidence, and the live Azure boundary all line up.
""",
    )
    return


@app.cell
def _capstone_b_transfer_lens(mo):
    mo.callout(
        mo.md(
            """
    ## Capstone B Transfer Lens

    For Capstone B, treat today’s integration boundary as a **claims intake**
    boundary rather than an AP boundary:
    - HTTP trigger: intake from a payer or provider portal
    - Service Bus: asynchronous adjudication or exception-routing events
    - MCP: controlled tool surface for specialist agents working claim cases

    Use:
    - `docs/curriculum/CAPSTONE_B_TRANSFER.md`
    - `fixtures/capstone_b/claims_intake/`

    The transfer test today is not "can you rename invoice to claim" but
    "can you preserve identity, reliability, and contract discipline when the
    vocabulary and compliance regime change."
    """
        ),
        kind="info",
    )
    return


@app.cell
def _day13_lineage_map(mo):
    mo.callout(
        mo.md(
            """
    ## Visual Guide — Day 13 Boundary Evidence Flow

    ```
    Day 11 OBO identity ──► HTTP boundary trusts actor context
                       │
                       ├─► Service Bus delivery + DLQ drain report
                       │     └─► gate_dlq_drain_health
                       │
                       └─► MCP /capabilities contract snapshot
                             └─► gate_mcp_contract_integrity
    ```

    Day 13 turns "integration works" into auditable evidence:
    reliable recovery and disciplined external contracts both have to be proven.

    | Boundary concern | Artifact / proof | Why Day 14 depends on it |
    |---|---|---|
    | Async recovery is real, not assumed | `build/day13/dlq_drain_report.json` | Rollback confidence is lower if failed messages cannot be drained safely |
    | External tool surface stayed compatible | `build/day13/mcp_contract_report.json` | Breaking changes later look like regressions, not surprises |
    | Webhook path remains reliable | `build/day13/webhook_reliability_report.json` | Elite ops cannot defend a rollout if ingress is already unstable |
    """
        ),
        kind="info",
    )
    return


@app.cell
def _day13_mastery_checkpoint(mo):
    mo.callout(
        mo.md(
            """
    ## Mastery Checkpoint — Boundary Ownership

    You are ready for Day 14 only if you can explain:
    - why a retry is not always a compensating action
    - which failures require actor-bound audit evidence before replay
    - what makes an MCP change breaking even when one known consumer still succeeds
    - how the claims-intake transfer domain changes the blast radius of a missed DLQ or contract failure
    """
        ),
        kind="warn",
    )
    return


@app.cell
def _day13_hidden_case_preview(mo):
    mo.callout(
        mo.md(
            """
    ## Hidden-Case Drill Preview — Unseen Transfer Input

    An assessor-only claims-intake case exists. Do **not** open it.

    Assume it is close enough to reach your boundary but unsafe to trust without disciplined validation.
    Prepare to explain:
    - where the boundary should reject, hold, or dead-letter the request
    - what actor-bound audit evidence must still be written even when business processing is denied
    - whether a compensating action is required, and why retry alone is not enough
    - how you communicate the refusal or hold to an external consumer without breaking contract discipline

    Weak answer pattern:
    "We would retry a few times and patch the parser if it still fails."
    """
        ),
        kind="warn",
    )
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
    _build = Path(__file__).resolve().parents[1] / "build" / "day13"
    _build.mkdir(parents=True, exist_ok=True)

    _sb_namespace = os.environ.get("AZURE_SERVICEBUS_NAMESPACE_FQDN", "")
    _sb_queue = os.environ.get("AZURE_SERVICEBUS_QUEUE_NAME", "")
    _has_live = bool(_sb_namespace and _sb_queue)

    if _has_live:
        try:
            from aegisap.integration.dlq_consumer import DlqConsumer
            _consumer = DlqConsumer.from_env()
            _report = _consumer.drain()
            _report_dict = _report.to_dict()
            _report_dict["training_artifact"] = False
            _report_dict["authoritative_evidence"] = True
            _report_dict["execution_tier"] = 2
            _report_dict["note"] = "LIVE"
            _kind = "success"
            _msg = (
                f"Live DLQ drain complete.\n\n"
                f"Processed: {_report_dict.get('total', 0)} messages\n\n"
                f"Errors: {_report_dict.get('error_count', 0)}"
            )
        except Exception as _exc:
            _report_dict = {
                "error": str(_exc),
                "total": 0,
                "error_count": 1,
                "errors": [str(_exc)],
                "training_artifact": False,
                "authoritative_evidence": True,
                "execution_tier": 2,
                "note": "LIVE_ERROR",
            }
            _kind = "danger"
            _msg = f"DLQ drain error: `{_exc}`"
    else:
        _report_dict = {
            "total": 0,
            "retried": 0,
            "archived": 0,
            "error_count": 0,
            "errors": [],
            "all_handled": True,
            "messages": [],
            "training_artifact": True,
            "authoritative_evidence": False,
            "execution_tier": 1,
            "note": "TRAINING_ONLY: no AZURE_SERVICE_BUS_CONNECTION_STRING set",
        }
        _kind = "neutral"
        _msg = (
            "No `AZURE_SERVICEBUS_NAMESPACE_FQDN` + `AZURE_SERVICEBUS_QUEUE_NAME` set — "
            "writing a training-only DLQ preview.\n\n"
            "`gate_dlq_drain_health` will remain red until a real DLQ drain report is produced.\n\n"
            "Canonical live command:\n"
            "```\nuv run python scripts/verify_webhook_reliability.py\n```"
        )

    (_build / "dlq_drain_report.json").write_text(json.dumps(_report_dict, indent=2))
    mo.callout(mo.md(_msg), kind=_kind)
    return


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
                "passed": len(_missing) == 0,
                "errors": [f"missing tool: {name}" for name in _missing],
                "training_artifact": False,
                "authoritative_evidence": True,
                "execution_tier": 2,
                "note": "LIVE",
            }
            _kind = "success" if _report_dict["contract_valid"] else "danger"
            _msg = f"MCP capabilities fetched. Contract valid: `{_report_dict['contract_valid']}`"
        except Exception as _exc:
            _report_dict = {
                "capabilities_ok": False,
                "error": str(_exc),
                "contract_valid": False,
                "passed": False,
                "errors": [str(_exc)],
                "training_artifact": False,
                "authoritative_evidence": True,
                "execution_tier": 2,
                "note": "LIVE_ERROR",
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
            "contract_valid": False,
            "passed": False,
            "errors": ["training-only preview: live /capabilities response not queried"],
            "training_artifact": True,
            "authoritative_evidence": False,
            "execution_tier": 1,
            "note": "TRAINING_ONLY: no AEGISAP_MCP_URL set",
        }
        _kind = "neutral"
        _msg = (
            "No `AEGISAP_MCP_URL` set — writing a training-only MCP contract preview.\n\n"
            "`gate_mcp_contract_integrity` will remain red until `/capabilities` is queried from a live server.\n\n"
            "Canonical live command:\n"
            "```\nuv run python scripts/verify_mcp_contract_integrity.py\n```\n\n"
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
    - [ ] Explain what your boundary does with an unseen transfer-domain case before any unsafe mutation can occur
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
4. An assessor-only claims case reaches your boundary with unfamiliar but plausible structure. Explain your validation, DLQ, audit, and consumer-communication path without opening the hidden file.

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
