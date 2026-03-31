# Day 2 — Stateful Workflow · Trainee Pre-Reading

> **WAF Pillars:** Reliability · Operational Excellence  
> **Time to read:** 20 min  
> **Lab notebook:** `notebooks/day2_stateful_workflow.py`

---

## Learning Objectives

By the end of Day 2 you will be able to:

1. Explain the difference between a *stateless function* and a *stateful workflow*.
2. Draw the AegisAP Day 2 state graph and label each node and edge.
3. Explain what LangGraph is and how it relates to a state machine.
4. Interpret a workflow state snapshot and describe what step the system is at.
5. Explain why telemetry and structured logging belong in the workflow layer.

---

## 1. From Function to Workflow

Day 1 produced a `CanonicalInvoice` with a single function call. Day 2 turns that
object into a **workflow** — a sequence of steps whose intermediate results are
explicitly tracked.

### Why workflows instead of function chains?

| Concern | Function chain | Stateful workflow |
|---|---|---|
| Observability | "Something failed somewhere" | "Step `route_for_review` failed after 2 retries" |
| Resumability | Must re-run from the start | Can resume from last checkpoint |
| Testability | Hard to inject failures | Each node is independently testable |
| Auditability | No intermediate record | Every state transition is a record |

---

## 2. State Machine Fundamentals

A **finite state machine** has:

- A finite set of **states**
- A set of **transitions** (each triggered by an event, moving from one state to another)
- An **initial state**
- One or more **terminal states**

In AegisAP Day 2 the states are workflow steps. The "event" is simply the
previous step completing successfully.

```
START
  │
  ▼
load_canonical_invoice
  │
  ▼
determine_routing         (which approval level is needed?)
  │
  ├── auto_approve ───────────► auto_approve_outcome
  │
  └── review_required ────────► human_review_outcome
                                      │
                                      ▼
                                   recommend
                                      │
                                      ▼
                                    END
```

### LangGraph and the state machine model

**LangGraph** is a Python library that lets you define a state machine as a
directed graph where each node is a Python function. The state object flows
through the graph, each node reading and writing fields on it.

```python
# Conceptual LangGraph node
def determine_routing(state: WorkflowState) -> WorkflowState:
    if state.canonical_invoice.amount > THRESHOLD:
        state.routing = "review_required"
    else:
        state.routing = "auto_approve"
    return state
```

Key LangGraph concepts:

| Concept | Description |
|---|---|
| `StateGraph` | The graph container; takes a state schema type |
| `add_node(name, fn)` | Registers a node (a plain Python function) |
| `add_edge(a, b)` | Unconditional transition from `a` to `b` |
| `add_conditional_edges(a, fn, map)` | Routes from `a` based on a routing function's return value |
| `compile()` | Produces a `CompiledGraph` ready to invoke |

---

## 3. The Workflow State Object

Every node in the graph reads from and writes to a single **typed state object**.
In AegisAP this is `WorkflowState` (or its day-specific equivalent). It contains:

- The `CanonicalInvoice` from Day 1
- Routing decision
- Review conditions / flags
- Telemetry metadata (start time, node timings)
- The final recommendation or escalation package

### Why a single state object?

A single typed object:
- Makes the full workflow state inspectable at any point
- Allows checkpointing without guessing which variables matter (Day 5 benefit)
- Prevents nodes from passing data through side-channels (global variables, files)

---

## 4. Routing Logic

AegisAP's routing step evaluates the `CanonicalInvoice` against a policy rule
set. The rules are **deterministic Python** — not decided by the LLM.

Typical rules:
- If `amount > 10 000`, require controller review
- If `vendor_id` not in approved vendor list, require PO validation
- If `po_number` is missing and `amount > 5 000`, escalate

The LLM is **not involved** in routing decisions. This is intentional: routing
is a business policy and must be auditable, testable, and explainable.

### Azure best practice
Externalise threshold values (like `10 000`) to Azure App Configuration or
environment variables so they can be changed without a code deployment. Flag
any change to routing thresholds in a change log.

---

## 5. Structured Telemetry

Every workflow run should emit structured events that can be queried. "Structured"
means machine-parseable — not free-text log strings.

Bad:
```python
print(f"Invoice {inv_id} routed to review")
```

Good:
```python
logger.info("invoice.routed", extra={
    "invoice_id": inv_id,
    "routing": "review_required",
    "amount": float(amount),
    "currency": currency,
    "threshold": THRESHOLD,
})
```

When every event has consistent field names, you can write KQL queries like:
```kusto
traces
| where customDimensions.event_name == "invoice.routed"
| where customDimensions.routing == "review_required"
| summarize count() by bin(timestamp, 1h)
```

### Azure best practice
Use the **OpenTelemetry Python SDK** (`opentelemetry-sdk`) integrated with
Azure Monitor's OTLP exporter. This produces both spans (for distributed tracing)
and structured log records in a single pipeline. Don't use two separate logging
libraries.

---

## 6. Recommendations vs. Escalations

A Day 2 workflow always terminates in one of two outputs:

| Output | Meaning | Next step |
|---|---|---|
| `RecommendationPackage` | System recommends approval; evidence is sufficient | Passed to Day 4 planner |
| `EscalationPackage` | System cannot recommend; human judgment required | Routed to human review queue |

Both are **first-class typed outputs**. There is no "silent failure" mode.

---

## Glossary

| Term | Definition |
|---|---|
| **LangGraph** | Python library for building stateful, graph-based workflows (nodes + edges + state) |
| **StateGraph** | LangGraph's main class; defines nodes and transitions for a typed state |
| **Conditional edge** | A graph transition that routes to different nodes based on a function's output |
| **WorkflowState** | AegisAP's typed state object that flows through all workflow nodes |
| **Routing** | The step that decides which approval path an invoice takes |
| **Structured log** | A log entry with key-value fields rather than a free-text string |
| **RecommendationPackage** | Workflow output when the system can advise approval |
| **EscalationPackage** | Workflow output when the system cannot proceed without human review |

---

## Check Your Understanding

1. What is the difference between a stateless function and a stateful workflow? Give a concrete example from an accounts payable context.
2. Draw (or describe in words) the Day 2 state graph for AegisAP.
3. Why is routing logic implemented in Python rather than delegated to the LLM?
4. What is a `StateGraph` in LangGraph, and what arguments does its constructor take?
5. Why is a structured log entry preferable to `print()` for workflow events?

---

## Lab Readiness

- **Lab duration:** 2.5 hours
- **Required inputs:** `build/day1/golden_thread_day1.json` and `notebooks/day2_stateful_workflow.py`
- **Expected artifact:** `build/day2/golden_thread_day2.json`

### Pass Criteria

- The workflow completes with a visible route, final status, and state diff.
- A seeded escalation path reaches the correct branch without breaking the artifact contract.
- You can explain which part of the state Day 3 depends on next.

### Common Failure Signals

- The route is chosen from implicit notebook state rather than the typed workflow state.
- The artifact is missing the downstream state Day 3 expects.
- The learner cannot explain why a human-review branch was selected.

### Exit Ticket

1. Which field in the state object tells you where the workflow is now?
2. Why is deterministic routing safer than model-selected routing at this stage?
3. What exact command would you run to regenerate the Day 2 artifact from the Day 1 handoff?

### Remediation Task

Rebuild the workflow artifact with:

```bash
uv run python scripts/run_day2_workflow.py --day1-artifact build/day1/golden_thread_day1.json --known-vendor
```

Then explain how the route changed the resulting state and what would trigger an
escalation instead of the clean path.

### Stretch Task

Add one more branch condition you think finance operations would need and explain
which state fields should drive it so the graph remains auditable.
