# Day 5 — Durable State & Human-in-the-Loop · Trainee Pre-Reading

> **WAF Pillars:** Reliability · Operational Excellence  
> **Time to read:** 25 min  
> **Lab notebook:** `notebooks/day5_durable_state.py`

---

## Learning Objectives

By the end of Day 5 you will be able to:

1. Generate a Day 5 pause artifact and a Day 5 resumed artifact from the training runtime.
2. Inspect the checkpoint and approval-task rows created for a parked workflow thread.
3. Explain how idempotency and the side-effect ledger prevent duplicate effects after resume.
4. Trace how a resume token and approval task map to the hosted runtime API.
5. Explain why AegisAP uses PostgreSQL + Entra auth for durable workflow control state.

---

## 1. The Problem with In-Memory State

Days 1–4 make great demos but have a critical production gap: if the process
crashes after step 3 of a 5-step workflow, all intermediate state is lost and
the workflow must restart from the beginning.

Problems this causes:
- **Duplicate side effects**: an email or payment instruction emitted in step 2
  may be re-emitted on restart
- **Data loss**: partially constructed recommendation packages are discarded
- **User frustration**: the approver who was waiting for a notification that was
  already sent now gets it again — or never receives the resume prompt

---

## 2. Durable State with PostgreSQL

**Durable state** means persisting the workflow's intermediate state to an
external store so the workflow can be resumed after any failure.

AegisAP uses **Azure Database for PostgreSQL — Flexible Server** for durable state
because:
- It is ACID-compliant (writes are durable once committed)
- It supports structured queries needed for the approval queue
- It is natively available in Azure with managed backup and high availability
- The Day 7 security model covers it: Entra auth, no password auth

### Durable-state model

AegisAP persists four related tables:

| Table | Purpose | Key fields |
|---|---|---|
| `workflow_threads` | One row per business thread | `thread_id`, `case_id`, `status`, `current_checkpoint_seq` |
| `workflow_checkpoints` | Immutable saved states | `checkpoint_id`, `thread_id`, `checkpoint_seq`, `node_name`, `state_json` |
| `approval_tasks` | Human approval queue | `approval_task_id`, `thread_id`, `checkpoint_id`, `status`, `assigned_to` |
| `side_effect_ledger` | Idempotency ledger for replay-safe effects | `effect_key`, `thread_id`, `checkpoint_id`, `effect_type`, `status` |

`workflow_run_id` is still important, but it lives inside the serialised
workflow state and audit records rather than as a top-level checkpoint column.
On resume, the system loads the latest checkpoint for the `thread_id`,
deserialises the saved state, and continues from that exact control point.

### Azure best practice
- Enable **geo-redundant backup** on the PostgreSQL Flexible Server.
- Use **Entra authentication** instead of password authentication. The application
  connects via `DefaultAzureCredential` — no password in env vars.
- Set `connection_timeout` and `connect_retries` in the connection string so
  transient network blips don't cause unrecoverable failures before the workflow
  reaches a checkpoint.

---

## 3. Idempotency

A function is **idempotent** if calling it multiple times with the same input
produces the same result and does not create duplicate side effects.

In a durable workflow, every step that produces a side effect (sending a
notification, creating an approval task, writing to an external system) **must
be idempotent**. If the step completes but the checkpoint write fails, the step
will be re-run on next resume — and only idempotent steps can survive that.

### Pattern: check-before-act

```python
# Idempotent approval task creation
existing = cursor.execute(
    "SELECT task_id FROM approval_tasks WHERE thread_id = %s",
    (thread_id,)
).fetchone()

if existing:
    return existing["task_id"]    # already created; return the existing ID
else:
    task_id = create_approval_task(thread_id, amount, currency)
    return task_id
```

### AegisAP idempotency keys

| Entity | Key used |
|---|---|
| Checkpoint | `(thread_id, checkpoint_seq)` |
| Approval task | `thread_id` (one per thread) |
| Resume token | `checkpoint_id` (single-use) |

---

## 4. The Pause/Resume Flow

```
[ Day 4 recommendation ] ──► Day 6 review gate
                                    │
                        ┌───────────┴───────────┐
                approved_to_proceed        needs_human_review
                        │                       │
                        ▼                       ▼
              write checkpoint          write checkpoint
              create approval_task      create review_task
              │                               │
              ▼                               ▼
         PAUSED ◄─────────────────────── PAUSED
              │
    (approver acts via API)
              │
              ▼
         resume_service.resume(thread_id, approval_decision)
              │
              ▼
         load latest checkpoint
              │
              ▼
         continue from Day 5 resume node
              │
              ▼
         write terminal checkpoint
```

### What makes a resumption safe?

1. **Load from checkpoint, not from re-execution**: resume reads state from the
   database, it does not re-run Days 1–4.
2. **Idempotent side effects**: any step that already ran is skipped (check-before-act).
3. **Resume token**: a short-lived single-use token prevents replay attacks on
   the resume endpoint.

---

## 5. Human-in-the-Loop Patterns

Day 5 implements the most common human-in-the-loop pattern: **approval gate**.

| Pattern | Description | AegisAP use |
|---|---|---|
| **Approval gate** | Workflow pauses and waits for a human yes/no decision | Day 5: controller approval for high-value invoices |
| **Review queue** | Items requiring human inspection are batched for review | Day 5: `needs_human_review` path |
| **Escalation** | Workflow terminates with a human-directed outcome packet | Days 4, 6 |
| **Breakglass** | Emergency human override that bypasses gates | Not implemented — present as a risk discussion topic |

---

## 6. The Training Runtime API

From Day 5, AegisAP is also available as a hosted HTTP service that exposes:

```
POST /api/day4/cases/run              → run a new case and optionally persist the Day 5 handoff
GET  /api/day5/threads/{id}           → inspect the latest durable thread state
POST /api/day5/approvals/{id}/resume  → submit an approval decision with a single-use resume token
```

The hosted path is important: it means the workflow can be initiated by an
external system (e.g., an invoice ingestion pipeline) and resumed by a human
using a browser or mobile approval tool.

If a training token expires or is missing, the supported recovery path is to
re-create the pause artifact or generate a new handoff from the hosted runtime.
AegisAP does not expose a separate `/tokens/refresh` endpoint in this repo.

---

## Glossary

| Term | Definition |
|---|---|
| **Checkpoint** | A durable database record of the workflow's state at a specific point in time |
| **Thread ID** | The persistent business identifier for a resumable case (survives across runs) |
| **Workflow run ID** | Unique identifier for a single execution attempt (a thread may have many runs) |
| **Idempotency** | Property of an operation that can be applied multiple times without producing different results |
| **Resume token** | A short-lived, single-use credential authorising resumption of a specific thread |
| **Approval gate** | A workflow pause point where the process waits for an explicit human decision |
| **Entra authentication** | Azure Active Directory (Microsoft Entra ID) authentication — no passwords |

---

## Check Your Understanding

1. What is lost if a workflow only uses in-memory state and the process crashes?
2. Define idempotency. Why is it required for every side-effecting step in a durable workflow?
3. What three elements make a workflow resumption safe in AegisAP?
4. What columns does AegisAP's `checkpoints` table contain, and what is the difference between `thread_id` and `workflow_run_id`?
5. Why does AegisAP use Entra authentication for PostgreSQL instead of a username/password?

---

## Lab Readiness

- **Lab duration:** 2.5 hours
- **Required inputs:** `build/day4/golden_thread_day4.json` with `workflow_state`
- **Expected artifacts:** `build/day5/golden_thread_day5_pause.json`, `build/day5/golden_thread_day5_resumed.json`

### Pass Criteria

- Pause succeeds and writes the parked-thread artifact.
- Resume succeeds and writes the resumed artifact.
- The side-effect ledger shows no duplicate effect keys.

### Common Failure Signals

- Day 4 artifact is missing `workflow_state`
- PostgreSQL settings are incomplete for `AEGISAP_POSTGRES_DSN` or Entra auth
- Resume fails because the token secret is not available through local env or Key Vault

### Exit Ticket

1. Which table tells you where a thread is currently parked?
2. Why does AegisAP keep both `workflow_threads` and `workflow_checkpoints`?
3. What would you inspect first if a resumed case duplicated an external effect?

### Remediation Task

Re-run the flow using:

```bash
uv run python scripts/run_day4_case.py --planner-mode fixture
uv run python scripts/run_day5_pause_resume.py
uv run python scripts/resume_day5_case.py
```

Then explain which artifact proves the workflow resumed safely.

### Stretch Task

Explain how you would add an SLA-based escalation for approval tasks that sit in
`pending` status for 30 days without breaking idempotency.

### Scoring And Remediation Trigger

- Daily pass requires mostly 3s on the rubric, with no 1 in `Technical Correctness` or `Security Reasoning`.
- Immediate remediation is required if `duplicate_side_effects` is non-zero or the learner cannot name the exact recovery command for the paused thread.
