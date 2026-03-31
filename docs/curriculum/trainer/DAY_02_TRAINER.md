# Day 2 — Stateful Workflow · Trainer Guide

> **Session duration:** 3 hours (45 min theory + 2 h lab + 15 min wrap-up)  
> **WAF Pillars:** Reliability · Operational Excellence  
> **Prerequisite:** Day 1 complete; `golden_thread_day1.json` present

---

## Session Goals

By the end of Day 2, every learner should be able to:
- Draw the Day 2 state graph with nodes and conditional edges
- Explain what LangGraph adds over a plain function chain
- Interpret a `WorkflowState` snapshot at any intermediate node
- Add a new routing condition without breaking existing paths

---

## Preparation Checklist

- [ ] Day 1 artifact present: `build/day1/golden_thread_day1.json`
- [ ] `scripts/run_day2_workflow.py` runs cleanly in fixture mode
- [ ] `build/day2/` directory created by a test run (notebooks write here)
- [ ] Have a short code snippet ready demoing LangGraph `StateGraph` construction

**Expected artifact:** `build/day2/golden_thread_day2.json`

---

## Theory Segment (45 min)

### Block 1: Why Workflows over Function Chains? (15 min)

**Talking points:**
1. Start with this scenario: "You have three functions: extract → route → recommend.
   They work perfectly. What happens at 2 AM when `recommend` crashes after
   `route` already logged an audit event?"
   - Invite answers. Expected: "restart from scratch." Now introduce the problem:
     the audit event was already logged — restarting logs it again.
2. Draw the contrast: function chain (no persistent state, no intermediate
   record) vs. stateful workflow (each node writes to state, failure is
   recoverable).
3. Show that observability changes: from "something crashed" to "the recommendation
   node crashed after the routing node succeeded at 14:32:05 with routing=review_required."
4. Make the connection to Day 5: "Today we're not yet persisting to a database.
   Day 5 adds that. But the graph design today is exactly what Day 5 persists."

---

### Block 2: LangGraph State Machine (20 min)

**Talking points:**
1. Open `src/aegisap/` and find the Day 2 graph definition. Walk through:
   ```python
   graph = StateGraph(WorkflowState)
   graph.add_node("determine_routing", determine_routing)
   graph.add_node("auto_approve", auto_approve)
   graph.add_node("recommend", recommend)
   graph.add_conditional_edges(
       "determine_routing",
       route_selection_fn,
       {"auto_approve": "auto_approve", "review_required": "recommend"}
   )
   ```
2. Draw this graph live on the whiteboard as you explain each line.
3. Explain `add_conditional_edges`: the routing function returns a string key,
   and the map translates that key to the next node name.
4. Compile the graph and show what `graph.invoke(initial_state)` does:
   - Starts at the entry point
   - Calls each node function in sequence
   - Each node receives and returns the full state
   - The graph terminates at a terminal node

**Interactive activity:** Ask learners to predict what edge the golden thread
invoice takes. Have them trace through: amount = GBP 12,500 > threshold → `review_required`.

---

### Block 3: Structured Telemetry (10 min)

**Talking points:**
1. Show a bad log line: `print("Done routing")`
2. Show a good structured log: JSON with `invoice_id`, `routing`, `amount`, `threshold`
3. Ask: "If I want to query 'all invoices worth more than £10,000 that were
   auto-approved in the last 24 hours' — which log format lets me do that?"
4. Briefly preview Day 8: "In five days, we'll replace these `logger.info` calls
   with OTEL spans. The *structure* is the same — only the transport changes."

---

## Lab Walkthrough Notes

### Key cells to call out in `day2_stateful_workflow.py`:

1. **State definition cell** — show `WorkflowState` and its typed fields.
   Ask: "Why is `routing` a `str | None` and not just `str`?"
   (Answer: it starts as `None` before the routing node runs — the state is
   always valid, even before all fields are populated.)

2. **Graph construction cell** — walk through the conditional edge setup.
   If time allows, have learners modify the routing threshold and observe
   the golden thread taking a different path.

3. **Invoke cell** — run the workflow and watch the state evolve.
   Pause after each node and show the intermediate state snapshot.

4. **Recommendation vs. escalation cell** — open both output shapes side by
   side. Ask: "What information does the escalation package contain that the
   recommendation package doesn't?" (Answer: escalation reason, assigned
   reviewer, expected resolution timeframe.)

### Expected lab friction points

| Issue | Likely cause | Resolution |
|---|---|---|
| `KeyError` on state field | Accessing a field before it's set | Check node execution order; ensure the previous node ran first |
| Graph loops indefinitely | Missing terminal node or missing edge to END | Add `graph.add_edge("last_node", END)` |
| `WorkflowState` Pydantic error | Wrong type on a state field | Check the field's declared type; date fields need `date()` not `str` |

---

## Facilitation Addendum

### Observable Mastery Signals

- Learner can explain route selection from typed state fields, not notebook intuition.
- Learner can show which Day 2 fields Day 3 consumes next.
- Learner updates the workflow path without breaking the artifact contract.

### Intervention Cues

- If a learner treats the graph like a linear script, redraw nodes, edges, and state transitions.
- If the artifact is missing downstream state, point them back to the handoff contract before deeper debugging.
- If someone wants the LLM to choose the route, pause and compare determinism vs. explainability.

### Fallback Path

- If LangGraph setup is unavailable, walk through a saved `build/day2/golden_thread_day2.json` and focus on state mutation and route reasoning.

### Exit Ticket Answer Key

1. `current_node` and route/status fields tell you where the workflow is.
2. Deterministic routing is testable, reproducible, and safer for audit.
3. `uv run python scripts/run_day2_workflow.py --day1-artifact build/day1/golden_thread_day1.json --known-vendor` rebuilds the handoff.

### Time-box Guidance

- Keep graph debugging to one branch at a time; do not let learners chase all routes in parallel.
- If route confusion lasts more than 15 minutes, regroup and trace one case end-to-end as a cohort.

---

## Common Misconceptions

| Misconception | Correction |
|---|---|
| "LangGraph is for LLM chains only" | LangGraph is a general state machine; most Day 2 nodes contain no LLM calls |
| "The state object is mutated in place" | Each node returns a new (or updated) state. LangGraph handles merging. |
| "Conditional edges are complex" | They are a dict lookup. The routing function returns a key; the map selects the next node. |
| "Structured logging is optional" | It is the only way to make telemetry queryable in Azure Monitor (Day 8) |

---

## Discussion Prompts

1. "A new business rule requires that invoices from vendors with overdue payments
   get routed to a separate review queue. Where does that rule live in the graph,
   and how do you add it without modifying existing nodes?"

2. "What is the minimum set of fields that `WorkflowState` needs to contain for
   Day 5 to be able to checkpoint and resume this graph?"

3. "Today's routing is 100% deterministic Python. When, if ever, would it be
   appropriate to involve an LLM in a routing decision?"

---

## Expected Q&A

**Q: Can LangGraph nodes be async?**  
A: Yes — `graph.ainvoke()` supports async nodes. AegisAP uses sync nodes in
training for simplicity; the hosted runtime uses async. The graph definition
is identical.

**Q: What's the difference between `WorkflowState` and the Day 5 checkpoint JSON?**  
A: Day 5 serialises `WorkflowState` to JSON for database storage. The state
schema must be JSON-serialisable. If you add a `datetime` or `Decimal` field,
confirm the serialiser handles it correctly.

**Q: Why not use Celery or Temporal instead of LangGraph for workflow orchestration?**  
A: Celery and Temporal are excellent for task queues and distributed durable
workflows at scale. LangGraph fits the AI agent pattern specifically: branching
logic driven by LLM or model outputs. Days 5–10 add the durability layer on top
of LangGraph rather than replacing it.

---

## Next-Day Bridge (5 min)

> "We now have a typed, stateful workflow that produces either a recommendation
> or an escalation for every case. But our routing today only knows about the
> invoice itself — it has no external evidence. Tomorrow we add retrieval:
> we'll connect to Azure AI Search and ground our decisions in policy documents.
> The workflow structure stays the same. What changes is the evidence quality
> available to each node."
