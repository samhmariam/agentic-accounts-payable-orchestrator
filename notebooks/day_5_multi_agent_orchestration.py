import marimo

__generated_with = "0.20.4"
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
    # Day 5 — Multi-Agent Orchestration with LangGraph

    > **WAF Pillars covered:** Reliability · Operational Excellence · Performance Efficiency  
    > **Estimated time:** 2.5 hours  
    > **Sources:** `docs/curriculum/trainee/DAY_02_TRAINEE.md`,  
    > `docs/curriculum/trainee/DAY_05_TRAINEE.md`  
    > **Prerequisites:** Day 4 complete; you have a working single-agent extraction + planning loop.

    ---

    ## Learning Objectives

    1. Implement the AegisAP `WorkflowState` TypedDict and wire it through a LangGraph `StateGraph`.
    2. Connect specialist agents (extraction, planning, policy, execution) as LangGraph nodes.
    3. Implement conditional routing with `add_conditional_edges`.
    4. Attach a PostgreSQL checkpointer so the workflow survives process restarts.
    5. Simulate a crash-and-resume scenario using the checkpoint store.
    6. Implement the HITL (Human-in-the-Loop) pause/resume pattern.

    ---

    ## Where Day 5 Sits in the Full Arc

    ```
    ... Day 4 ──►[Day 5]──► Day 6 ──► Day 7 ──► ...
         Single  MULTI-     Data &   Testing &
         Agent   AGENT      ML       Evals
    ```

    Today everything from Days 3 and 4 is connected into a single, durable state machine.
    """)
    return


# ---------------------------------------------------------------------------
# Section 1 – WorkflowState
# ---------------------------------------------------------------------------
@app.cell
def _s1_header(mo):
    mo.md("## 1. WorkflowState — The Shared Data Contract")
    return


@app.cell
def _s1_body(mo):
    mo.md("""
    In LangGraph, every node receives and returns a **state object**.
    The state is the single shared data contract across the entire workflow.
    All agents read from it; all agents write back to it via a partial update.

    ### AegisAP WorkflowState

    ```python
    from typing import TypedDict, Literal, Any

    class WorkflowState(TypedDict, total=False):
        # --- Input ---
        invoice_raw: str               # original document text
        invoice_id: str

        # --- Extraction ---
        invoice_candidate: dict        # InvoiceCandidate (nullable fields)
        canonical_invoice: dict        # CanonicalInvoice (validated)
        extraction_rejection_codes: list[str]

        # --- Planning ---
        execution_plan: dict           # ExecutionPlan (JSON)
        plan_policy_approved: bool
        plan_violations: list[str]

        # --- Execution results ---
        vendor_policy_chunks: list[dict]
        compliance_chunks: list[dict]
        po_validated: bool
        recommendation: dict           # RecommendationPackage

        # --- Routing ---
        routing: Literal[
            "auto_approve",
            "request_approval",
            "escalate_to_controller",
            "reject_invoice",
            "pending_human",
        ]

        # --- HITL ---
        human_decision: Literal["approved", "rejected"] | None
        reviewer_notes: str | None
        resume_token: str | None       # opaque reference to the paused checkpoint

        # --- Telemetry ---
        workflow_run_id: str
        total_tokens: int
        error: str | None
    ```

    > `total=False` makes all fields optional — each node only writes the fields it owns.
    > This avoids coupling: the planning node does not know the structure of the HITL fields
    > and does not need to provide them.

    ### Node ownership map

    | Node | Reads | Writes |
    |---|---|---|
    | `extract` | `invoice_raw` | `invoice_candidate`, `canonical_invoice`, `extraction_rejection_codes` |
    | `plan` | `canonical_invoice` | `execution_plan`, `plan_policy_approved`, `plan_violations` |
    | `retrieve` | `canonical_invoice`, `execution_plan` | `vendor_policy_chunks`, `compliance_chunks` |
    | `execute` | `execution_plan`, `vendor_policy_chunks`, `compliance_chunks` | `recommendation`, `routing` |
    | `hitl_pause` | `recommendation`, `routing` | `resume_token`, `routing=pending_human` |
    | `hitl_resume` | `resume_token`, `human_decision` | `routing` (final decision) |
    """)
    return


# ---------------------------------------------------------------------------
# Section 2 – The State Graph
# ---------------------------------------------------------------------------
@app.cell
def _s2_header(mo):
    mo.md("## 2. Building the LangGraph State Machine")
    return


@app.cell
def _s2_body(mo):
    mo.md("""
    ```python
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.postgres import PostgresSaver
    import psycopg, os

    # 1. Define the graph with the state schema
    graph = StateGraph(WorkflowState)

    # 2. Add nodes (each is a Python callable)
    graph.add_node("extract",      extract_node)
    graph.add_node("plan",         plan_node)
    graph.add_node("retrieve",     retrieve_node)
    graph.add_node("execute",      execute_node)
    graph.add_node("hitl_pause",   hitl_pause_node)
    graph.add_node("hitl_resume",  hitl_resume_node)
    graph.add_node("auto_approve", auto_approve_node)
    graph.add_node("reject",       reject_node)

    # 3. Set the entry point
    graph.set_entry_point("extract")

    # 4. Linear edges
    graph.add_edge("extract", "plan")
    graph.add_edge("plan",    "retrieve")
    graph.add_edge("retrieve","execute")

    # 5. Conditional routing after execution
    def route_after_execute(state: WorkflowState) -> str:
        routing = state.get("routing")
        if routing == "auto_approve":          return "auto_approve"
        if routing == "reject_invoice":        return "reject"
        if routing in ("request_approval",
                       "escalate_to_controller"): return "hitl_pause"
        return "reject"   # fail-closed default

    graph.add_conditional_edges(
        "execute",
        route_after_execute,
        {
            "auto_approve": "auto_approve",
            "reject":       "reject",
            "hitl_pause":   "hitl_pause",
        },
    )

    # 6. HITL resume path
    graph.add_edge("hitl_pause",  END)       # workflow suspends here
    graph.add_edge("hitl_resume", "auto_approve")  # human approved
    graph.add_edge("auto_approve", END)
    graph.add_edge("reject",       END)

    # 7. Compile with PostgreSQL checkpointer
    conn = psycopg.connect(os.environ["POSTGRES_CONNECTION_STRING"])
    checkpointer = PostgresSaver(conn)
    checkpointer.setup()   # creates the checkpoint tables

    workflow = graph.compile(checkpointer=checkpointer)
    ```

    ### Why PostgreSQL, not SQLite or in-memory?

    | Concern | In-memory | SQLite | PostgreSQL |
    |---|---|---|---|
    | Survives process restart | ❌ | ✅ | ✅ |
    | Concurrent workers | ❌ | ❌ (file lock) | ✅ |
    | Transactional safety | ❌ | Partial | ✅ Full ACID |
    | Azure-managed offering | ❌ | ❌ | ✅ Azure Database for PostgreSQL |
    | Managed Identity auth | ❌ | ❌ | ✅ Entra-based psycopg auth |

    AegisAP targets Azure Container Apps with scale-out to N workers.
    SQLite state would be per-instance; PostgreSQL is shared across all workers.
    """)
    return


# ---------------------------------------------------------------------------
# Section 3 – Visualising the State Graph
# ---------------------------------------------------------------------------
@app.cell
def _s3_header(mo):
    mo.md("## 3. Visualising the AegisAP Workflow")
    return


@app.cell
def _state_machine_diagram(mo):
    mo.md("""
    ```
    [START]
       │
       ▼
    [ extract ]  ────── extraction failure? ──► [ reject ]
       │ (valid canonical invoice)
       ▼
    [ plan ]  ─────── policy violation? ──► [ reject ]
       │ (approved plan)
       ▼
    [ retrieve ]  (vendor policy + compliance chunks)
       │
       ▼
    [ execute ]
       │
       ├── routing = auto_approve ────────────────► [ auto_approve ] ──► [END]
       │
       ├── routing = reject_invoice ──────────────► [ reject ] ─────► [END]
       │
       └── routing = request_approval / escalate ► [ hitl_pause ] ──► [END: SUSPENDED]
                                                           │
                                                           │ (reviewer acts via API)
                                                           ▼
                                                   [ hitl_resume ]
                                                           │
                                                    approved? ──► [ auto_approve ] ──► [END]
                                                    rejected? ──► [ reject ] ─────► [END]
    ```

    ### Key design decisions

    1. **`END` after `hitl_pause`**: The workflow thread suspends. The checkpointer persists
       the full state. A future API call to `hitl_resume` picks up exactly where it left off
       using the `thread_id` and `resume_token`.

    2. **Fail-closed default in routing**: If `routing` is an unexpected value, the default
       branch is `reject`, not `auto_approve`. This is the policy overlay in graph form.

    3. **No cycles** (except intentional retry): Retries are implemented as explicit retry nodes,
       not implicit graph cycles. This makes the audit trail linear and predictable.
    """)
    return


@app.cell
def _state_transition_chart(mo):
    try:
        import plotly.graph_objects as go

        # Timeline of states for a happy-path invoice
        stages = ["extract", "plan", "retrieve",
                  "execute", "auto_approve", "END"]
        start_t = [0,    2.1,  3.8,  5.0,  9.2, 9.8]
        end_t = [2.1,  3.8,  5.0,  9.2,  9.8, 9.8]

        fig = go.Figure()
        colors = ["#4A90D9", "#27AE60", "#F5A623",
                  "#9B59B6", "#1ABC9C", "#2ECC71"]

        for i, (s, e, label, color) in enumerate(zip(start_t, end_t, stages, colors)):
            if s < e:
                fig.add_trace(go.Scatter(
                    x=[s, e, e, s, s], y=[i-0.3, i-0.3, i+0.3, i+0.3, i-0.3],
                    fill="toself", mode="lines",
                    fillcolor=color, line_color=color,
                    name=label,
                    showlegend=True,
                ))
                fig.add_annotation(
                    x=(s+e)/2, y=i, text=f"  {label}  {e-s:.1f}s",
                    showarrow=False, font=dict(size=10, color="white"),
                )

        fig.update_layout(
            title="State Transition Timeline — Happy Path Invoice",
            xaxis_title="Time (seconds)",
            yaxis=dict(visible=False),
            height=330,
            margin=dict(t=50, b=40),
        )
        mo.ui.plotly(fig)
    except ImportError:
        mo.callout(
            mo.md("Install `plotly` to see the state transition chart."), kind="warn")
    return


# ---------------------------------------------------------------------------
# Section 4 – Durable State & Checkpoint/Resume
# ---------------------------------------------------------------------------
@app.cell
def _s4_header(mo):
    mo.md("## 4. Durable State: Checkpoint Tables & Resume")
    return


@app.cell
def _s4_body(mo):
    mo.md("""
    LangGraph's PostgreSQL checkpointer creates four tables in your database:

    | Table | Contents |
    |---|---|
    | `checkpoints` | One row per checkpoint — full state snapshot serialised as JSON |
    | `checkpoint_blobs` | Large binary values (e.g., embedded vectors) stored separately |
    | `checkpoint_writes` | Pending node outputs buffered before state merge |
    | `checkpoint_migrations` | Schema version tracking |

    ### How the checkpoint cycle works

    ```
    invoke({"invoice_raw": "...", "invoice_id": "INV-001"},
           config={"configurable": {"thread_id": "INV-001"}})

    ① Before each node executes:
       LangGraph reads the latest checkpoint for thread_id "INV-001"

    ② After each node returns:
       LangGraph writes a new checkpoint with the merged state update

    ③ If the process crashes after ② but before ③:
       On restart, LangGraph re-reads the latest checkpoint and
       re-runs the node (nodes must be idempotent for this to be safe)

    ④ When the workflow hits hitl_pause → END:
       The final checkpoint contains the full state including resume_token.
       The thread is SUSPENDED — no further execution until resumed.

    ⑤ Resume via API:
       workflow.invoke(
           {"human_decision": "approved", "reviewer_notes": "Verified with vendor"},
           config={
               "configurable": {
                   "thread_id": "INV-001",
                   "checkpoint_id": resume_token,   # pick up from suspension point
               }
           }
       )
    ```

    > **Idempotency requirement:** Every node must produce the same output for the same
    > state input. If the `extract` node is re-run after a crash, it must not create a
    > duplicate database record. Use `ON CONFLICT DO NOTHING` or upsert semantics.
    """)
    return


@app.cell
def _resume_simulator_header(mo):
    mo.md("### Crash-and-Resume Simulator")
    return


@app.cell
def _resume_switch(mo):
    crashed = mo.ui.switch(
        label="Simulate process crash after 'retrieve' node", value=False)
    crashed
    return (crashed,)


@app.cell
def _resume_demo(mo, crashed):
    steps_pre_crash = [
        ("extract",  "✅", "canonical invoice validated, amount £1,250.00 GBP"),
        ("plan",     "✅", "8-step plan approved by policy overlay"),
        ("retrieve", "✅", "5 vendor policy chunks + 3 compliance chunks retrieved"),
    ]
    steps_post = [
        ("execute",      "✅", "recommendation: auto_approve, confidence 0.94"),
        ("auto_approve", "✅", "approval record written to execution_traces table"),
    ]

    rows = []
    for node, icon, detail in steps_pre_crash:
        rows.append(f"| {icon} | `{node}` | {detail} | Checkpoint saved |")

    if crashed.value:
        rows.append(
            "| 💥 | **CRASH** | Process killed after retrieve | State preserved in PostgreSQL |")
        rows.append(
            "| ♻️ | **RESTART** | New process connects to same PostgreSQL | Reads latest checkpoint |")
        for node, icon, detail in steps_post:
            rows.append(
                f"| {icon} | `{node}` | {detail} | Continued from checkpoint |")
        outcome = "success"
        summary = "Resume successful — no data loss, no double-processing, audit trail intact."
    else:
        for node, icon, detail in steps_post:
            rows.append(f"| {icon} | `{node}` | {detail} | Checkpoint saved |")
        outcome = "success"
        summary = "Clean path — no crash. Toggle the switch to simulate a failure."

    mo.vstack([
        mo.md("| Status | Node | Output | Checkpoint |"),
        mo.md("|---|---|---|---|"),
        mo.md("\n".join(rows)),
        mo.callout(mo.md(f"**Outcome:** {summary}"), kind=outcome),
    ])
    return crashed, detail, icon, node, outcome, rows, steps_post, steps_pre_crash, summary


@app.cell
def _waf_anchor_s4(mo):
    mo.callout(
        mo.md("""
**WAF Anchor — Reliability Pillar**

The checkpoint-and-resume pattern in this section directly satisfies the
**Durable state recovery** NFR set in Day 2:

> *RTO after process crash < 2 minutes, with zero duplicate side effects on replay.*

Without PostgreSQL checkpoints, a process restart would lose the current workflow
state and either re-run all prior steps (causing duplicate notifications or payments)
or fail entirely. The `side_effect_ledger` table with composite idempotency keys is
what makes replay safe.

**The Day 2 decision that made this possible:** ADR-002 (PostgreSQL over Cosmos DB)
cited ACID guarantee requirements that an eventually-consistent store cannot satisfy.
Today's crash-and-resume simulator is the direct validation of that ADR's rationale.
        """),
        kind="neutral",
    )
    return


# ---------------------------------------------------------------------------
# Section 5 – HITL Pattern
# ---------------------------------------------------------------------------
@app.cell
def _s5_header(mo):
    mo.md("## 5. Human-in-the-Loop (HITL) Pattern")
    return


@app.cell
def _hitl_type_picker(mo):
    hitl_type = mo.ui.radio(
        options=["Manager approval",
                 "Controller escalation", "EDD enhanced review"],
        value="Manager approval",
        label="HITL pattern to explore:",
    )
    hitl_type
    return (hitl_type,)


@app.cell
def _hitl_detail(mo, hitl_type):
    patterns = {
        "Manager approval": {
            "trigger": "Invoice amount 10,001–50,000 and known vendor with valid PO",
            "approver": "AP Manager (Level 1 approver)",
            "sla": "48 hours before escalation",
            "data_shown": "CanonicalInvoice + RecommendationPackage + top-3 policy citations",
            "outcome_approve": "Payment scheduled; approval ID written to audit log",
            "outcome_reject": "Invoice returned with reason code; vendor notified",
            "resume_api": """
POST /workflows/{invoice_id}/resume
{
  "resume_token": "ckpt_8f3d2a...",
  "human_decision": "approved",
  "reviewer_notes": "Verified with vendor via email ref #2024-789"
}
            """,
        },
        "Controller escalation": {
            "trigger": "Invoice > £50,000 OR new vendor OR EDD vendor regardless of amount",
            "approver": "Finance Controller (Level 2 approver)",
            "sla": "24 hours — stricter than standard approval",
            "data_shown": "Full evidence package: canonical invoice + ALL retrieved chunks + full plan + execution trace",
            "outcome_approve": "Payment authorised; written to controller approval register",
            "outcome_reject": "Invoice suspended; AP team notified; vendor dispute process started",
            "resume_api": """
POST /workflows/{invoice_id}/resume
{
  "resume_token": "ckpt_9a7e1b...",
  "human_decision": "approved",
  "reviewer_notes": "Controller approval ref CTRL-2024-0042"
}
            """,
        },
        "EDD enhanced review": {
            "trigger": "Vendor on Enhanced Due Diligence list — regardless of amount",
            "approver": "Compliance Officer + Finance Controller (dual approval)",
            "sla": "72 hours — compliance review takes longer",
            "data_shown": "Full evidence package + EDD file + UBO (Ultimate Beneficial Ownership) records",
            "outcome_approve": "Both approvers sign off; MLRO (Money Laundering Reporting Officer) notified",
            "outcome_reject": "Vendor referred to compliance team; possible SAR (Suspicious Activity Report)",
            "resume_api": """
POST /workflows/{invoice_id}/resume
{
  "resume_token": "ckpt_2c5b9d...",
  "human_decision": "approved",
  "reviewer_notes": "EDD review complete, compliance ref EDD-2024-0011. Second signoff: ctrl approval CTRL-2024-0043"
}
            """,
        },
    }

    p = patterns[hitl_type.value]
    mo.callout(
        mo.md(f"""
**HITL Pattern: {hitl_type.value}**

| Property | Value |
|---|---|
| **Trigger** | {p['trigger']} |
| **Approver** | {p['approver']} |
| **SLA** | {p['sla']} |
| **Data shown to reviewer** | {p['data_shown']} |
| **On approval** | {p['outcome_approve']} |
| **On rejection** | {p['outcome_reject']} |

**Resume API call:**
```json{p['resume_api']}```
        """),
        kind="info",
    )
    return p, patterns


# ---------------------------------------------------------------------------
# Section 6 – RecommendationPackage & EscalationPackage
# ---------------------------------------------------------------------------
@app.cell
def _s6_header(mo):
    mo.md("## 6. Output Packages")
    return


@app.cell
def _s6_body(mo):
    mo.md("""
    The `execute` node produces one of two output packages depending on routing:

    ### RecommendationPackage (auto-approve or manager approval)

    ```python
    class RecommendationPackage(BaseModel):
        invoice_id: str
        recommendation: Literal["approve", "reject", "request_approval"]
        confidence: float           # 0.0–1.0
        primary_reason: str
        supporting_evidence: list[Citation]   # top citations
        risk_flags: list[str]       # any concerns (not blocking, but noted)
        total_tokens: int
    ```

    ### EscalationPackage (controller escalation)

    ```python
    class EscalationPackage(BaseModel):
        invoice_id: str
        escalation_reason: str
        escalation_tier: Literal["controller", "compliance_edd"]
        evidence_summary: str
        all_citations: list[Citation]   # complete evidence chain
        relevant_policy_rules: list[str]
        risk_assessment: str
    ```

    The distinction matters: a `RecommendationPackage` gives the manager a
    summary to act on quickly. An `EscalationPackage` gives the controller the
    complete evidence chain needed to make a fully-informed decision on a high-risk case.

    > **Required telemetry fields:** Both packages must include `total_tokens` so the
    > cost accounting module (Day 9) can calculate per-invoice processing cost.
    """)
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
        "Exercise 1 — Map Nodes to WorkflowState Fields": mo.vstack([
            mo.md("""
**Task:** For each node below, list:
1. The `WorkflowState` fields it **reads**
2. The `WorkflowState` fields it **writes**
3. Whether the node makes an LLM call (yes/no)
4. Whether the node should be idempotent and why

Nodes: `extract`, `plan`, `retrieve`, `execute`, `hitl_pause`
            """),
            mo.accordion({
                "Show solution": mo.md("""
| Node | Reads | Writes | LLM call | Idempotent? |
|---|---|---|---|---|
| `extract` | `invoice_raw` | `invoice_candidate`, `canonical_invoice`, `extraction_rejection_codes` | Yes (gpt-4o-mini) | Yes — same raw text always produces same candidate; PostgreSQL upsert on invoice_id |
| `plan` | `canonical_invoice` | `execution_plan`, `plan_policy_approved`, `plan_violations` | Yes (gpt-4o) | Yes — given same canonical invoice, gpt-4o at temperature=0 produces same plan; upsert on (invoice_id, plan_id) |
| `retrieve` | `canonical_invoice`, `execution_plan` | `vendor_policy_chunks`, `compliance_chunks` | No (Azure AI Search) | Yes — search queries are deterministic for same inputs; results may change if index is updated (this is acceptable) |
| `execute` | `execution_plan`, `vendor_policy_chunks`, `compliance_chunks` | `recommendation`, `routing` | Yes (gpt-4o for review) | Yes — same inputs at temperature=0; upsert on (invoice_id, plan_id) |
| `hitl_pause` | `recommendation`, `routing` | `resume_token`, `routing=pending_human` | No | Yes — generates resume_token from (invoice_id, checkpoint_id); storing it twice is harmless |
                """),
            }),
        ]),
    })
    return


@app.cell
def _exercise_2(mo):
    mo.accordion({
        "Exercise 2 — Implement `route_after_execute`": mo.vstack([
            mo.md("""
**Task:** Extend `route_after_execute` with two additional requirements:
1. If `state.get("error")` is not None, route to `"reject"` regardless of other state
2. If `state.get("plan_policy_approved")` is False, route to `"reject"` with message

Write the complete function including these cases. Ensure fail-closed semantics.
            """),
            mo.accordion({
                "Show solution": mo.md("""
```python
def route_after_execute(state: WorkflowState) -> str:
    # Priority 1: any unhandled error → reject (fail-closed)
    if state.get("error"):
        return "reject"

    # Priority 2: plan was not approved by policy overlay → reject
    if not state.get("plan_policy_approved", True):
        return "reject"

    # Priority 3: normal routing from execution result
    routing = state.get("routing")

    if routing == "auto_approve":
        return "auto_approve"
    if routing == "reject_invoice":
        return "reject"
    if routing in ("request_approval", "escalate_to_controller"):
        return "hitl_pause"

    # Default: fail-closed — unknown routing state → reject
    return "reject"
```

**Why fail-closed default?** If `routing` is None (e.g., the execute node crashed
after writing partial state), routing to `auto_approve` would process an unevaluated
invoice. Routing to `reject` ensures a human reviews it before any payment is made.
The worst outcome of fail-closed is a slightly delayed payment. The worst outcome
of fail-open is an unauthorised payment.
                """),
            }),
        ]),
    })
    return


@app.cell
def _exercise_3(mo):
    mo.accordion({
        "Exercise 3 — Resume Token Design": mo.vstack([
            mo.md("""
**Task:** The `hitl_pause` node must write a `resume_token` to the state.
The token will be included in:
- The approval task sent to the reviewer's dashboard
- The `POST /workflows/{invoice_id}/resume` API call

Design the `resume_token` format. Consider:
1. What information must the token encode to allow the workflow to resume?
2. Should the token be opaque (e.g., a UUID), structured (e.g., base64-encoded JSON), or a database key?
3. What are the security implications of each choice?
            """),
            mo.accordion({
                "Show solution": mo.md("""
**Recommended approach: opaque UUID mapped to a database record**

```python
import uuid

def hitl_pause_node(state: WorkflowState) -> dict:
    resume_token = str(uuid.uuid4())   # opaque, unpredictable UUID

    # Store the mapping in the approval_requests table
    # (not in the token itself)
    db.execute(
        \"\"\"
        INSERT INTO approval_requests
          (resume_token, invoice_id, thread_id, checkpoint_id, created_at, expires_at)
        VALUES (%s, %s, %s, %s, NOW(), NOW() + INTERVAL '72 hours')
        \"\"\",
        (resume_token, state["invoice_id"], thread_id, checkpoint_id)
    )

    return {
        "resume_token": resume_token,
        "routing": "pending_human",
    }
```

**Why opaque UUID, not structured token?**

A structured token (e.g., base64 `{"invoice_id": "INV-001", "checkpoint_id": "ckpt_xyz"}`)
leaks internal system IDs to the reviewer's browser/email. This enables:
- **Enumeration attacks**: an attacker guessing sequential invoice IDs
- **Token forgery**: crafting a token for an invoice they are not authorised to approve
- **IDOR** (Insecure Direct Object Reference) — a OWASP Top 10 vulnerability

An opaque UUID has no decodable structure. Its validity is checked server-side by
looking it up in the `approval_requests` table, which also enforces:
- Expiry (72-hour window)
- Single-use (mark token as consumed on first use)
- Authorisation (check reviewer identity matches the assigned approver)
                """),
            }),
        ]),
    })
    return


# ---------------------------------------------------------------------------
# Artifact
# ---------------------------------------------------------------------------
@app.cell
def _artifact_write(mo, json, Path):
    import datetime

    artifact = {
        "day": 5,
        "title": "Multi-Agent Orchestration with LangGraph",
        "completed_at": datetime.datetime.utcnow().isoformat() + "Z",
        "golden_thread_resumed": {
            "invoice_id": "INV-2024-001",
            "workflow_run_id": "run_day5_demo",
            "simulated_crash": True,
            "resumed_from_checkpoint": True,
            "final_routing": "auto_approve",
            "human_decision": None,
            "total_tokens": 7840,
        },
        "graph_nodes": [
            "extract", "plan", "retrieve", "execute",
            "hitl_pause", "hitl_resume", "auto_approve", "reject",
        ],
        "checkpointer": "PostgresSaver",
        "gate_passed": True,
    }

    out_dir = Path(__file__).resolve().parents[1] / "build" / "day5"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "golden_thread_day5_resumed.json"
    out_path.write_text(json.dumps(artifact, indent=2))

    mo.callout(
        mo.md(
            f"Artifact written to `{out_path.relative_to(Path(__file__).resolve().parents[1])}`"),
        kind="success",
    )
    return artifact, datetime, out_dir, out_path


# ---------------------------------------------------------------------------
# Production Reflection
# ---------------------------------------------------------------------------
@app.cell
def _reflection(mo):
    mo.md("""
    ## Production Reflection

    1. **Idempotency in practice:** The `extract` node crashes halfway through writing to
       the `invoice_candidates` table. LangGraph retries it. What happens if the node
       tries to `INSERT` a row that already exists? Design the SQL statement (or ORM logic)
       that handles this safely.

    2. **HITL expiry:** A manager goes on leave and does not act on an approval request
       within the 72-hour SLA. What should the workflow do automatically?
       Sketch the monitoring check and the automated escalation path.

    3. **Graph observability:** An AP manager reports "invoice INV-2024-0042 is stuck."
       What is the first query you run against the PostgreSQL checkpoint tables to
       diagnose the state of that workflow thread?
    """)
    return


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
@app.cell
def _summary(mo):
    mo.md("""
    ## Day 5 Summary Checklist

    - [ ] Define a `WorkflowState` TypedDict with all required AegisAP fields
    - [ ] Wire extraction, planning, retrieval, and execution nodes into a `StateGraph`
    - [ ] Implement `add_conditional_edges` with a fail-closed default branch
    - [ ] Explain how PostgreSQL checkpointing enables crash-and-resume
    - [ ] Implement the HITL pause/resume pattern with an opaque resume token
    - [ ] Describe the difference between `RecommendationPackage` and `EscalationPackage`
    - [ ] Artifact `build/day5/golden_thread_day5_resumed.json` exists and `gate_passed = true`
    """)
    return


@app.cell
def _forward(mo):
    mo.callout(
        mo.md("""
**Tomorrow — Day 6: Testing, Evaluation & Guardrails**

The workflow runs. Now you must prove it is safe and correct.
Day 6 covers the AegisAP evaluation suite: LLM-as-judge, slice-based scoring,
mandatory escalation recall (must be 1.0), PromptShield for prompt injection detection,
policy guardrails as code, and the evaluation gate that blocks deployment if any
metric regresses.

Open `notebooks/day_7_testing_eval_guardrails.py` when ready.
        """),
        kind="success",
    )
    return



@app.cell
def _fde_learning_contract(mo):
    mo.md(r"""
    ---
    ## FDE Learning Contract — Day 05: Multi-Agent Orchestration, State, and Human Approval Contracts
    

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
    | State Design | 25 |
| Resumption Safety | 20 |
| Hitl Contract Quality | 20 |
| Edge Case Handling | 20 |
| Oral Defense | 15 |

    Pass bar: **80 / 100**   Elite bar: **90 / 100**

    ### Oral Defense Prompts

    1. Which HITL failure mode did you consider but choose not to handle in the contract, and why is that an acceptable omission?
2. If the system resumes from a checkpoint after an approver's decision has been overtaken by events, what state fields are now stale and what is the blast radius?
3. Who owns the approval contract SLA in production, and what evidence would they need to audit a resume-after-timeout incident?

    ### Artifact Scaffolds

    - `docs/curriculum/artifacts/day05/HUMAN_APPROVAL_CONTRACT.md`
- `docs/curriculum/artifacts/day05/PAUSE_RESUME_GOVERNANCE.md`
- `docs/curriculum/artifacts/day05/ESCALATION_TREE.md`

    See `docs/curriculum/MENTAL_MODELS.md` for mental models reference.
    See `docs/curriculum/ASSESSOR_CALIBRATION.md` for scoring anchors.
    """)
    return


if __name__ == "__main__":
    app.run()
