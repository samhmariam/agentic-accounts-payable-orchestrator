# Day 5 — Durable State & Human-in-the-Loop · Trainer Guide

> **Session duration:** 3.5 hours (60 min theory + 2.5 h lab)  
> **WAF Pillars:** Reliability · Operational Excellence  
> **Prerequisite:** Day 4 complete; PostgreSQL provisioned (`full` track)

---

## Session Goals

By the end of Day 5, every learner should be able to:
- Explain why in-memory state is insufficient for enterprise workflows
- Define idempotency and write a check-before-act pattern
- Execute the full pause/resume cycle using the CLI tools
- Inspect a checkpoint row in PostgreSQL and map its fields to workflow concepts
- Explain why a resume token is single-use

---

## Preparation Checklist

- [ ] PostgreSQL accessible: `AEGISAP_POSTGRES_DSN` or Entra auth configured
- [ ] Migrations applied: `uv run python scripts/apply_migrations.py`
- [ ] Day 4 artifact present: `build/day4/golden_thread_day4.json`
- [ ] Training runtime API running if using hosted path:
      `uv run uvicorn aegisap.api.app:app --reload`
- [ ] Verify database connection posture:
      `uv run python scripts/verify_env.py --track full --env`

**Expected artifact:** `build/day5/golden_thread_day5_resumed.json`  
Supporting artifact: `build/day5/golden_thread_day5_pause.json`

---

## Theory Segment (60 min)

### Block 1: The In-Memory Problem (15 min)

**Talking points:**
1. Set the scene: "It's 3 AM. A controller was waiting to approve an
   invoice. Your Container App crashes due to an OOM event. When it restarts,
   what happens to the approval state?"
   - Expected: "It's gone."
2. Ask: "What if the crash happened *after* an email notification was sent to
   the controller, but *before* the approval task was written to the database?"
   - Expected: "The controller got a notification but the workflow doesn't know it."
   - Introduce: this is a *duplicate notification* problem — a classic idempotency violation.
3. Draw the timeline of failure:
   ```
   Step 1: send approval email ✓
   Step 2: write approval_task to DB ← CRASH
   Step 3: write checkpoint ← never reached
   ---
   Restart:
   Step 1: send approval email ← DUPLICATE
   Step 2: write approval_task to DB
   ...
   ```
4. Introduce the fix: idempotent step 1 ("check if email was already sent
   before sending") + checkpoint between steps.

---

### Block 2: Checkpoints and Durable Resumption (25 min)

**Talking points:**
1. Walk through the `checkpoints` table schema. Draw it on the board:
   ```
   workflow_threads:    thread_id | case_id | status | current_checkpoint_seq
   workflow_checkpoints: checkpoint_id | thread_id | checkpoint_seq | node_name | state_json
   approval_tasks:      approval_task_id | thread_id | checkpoint_id | status | assigned_to
   side_effect_ledger:  effect_key | thread_id | checkpoint_id | effect_type | status
   ```
2. Explain the distinction between `thread_id` and `workflow_run_id`:
   - `thread_id` = the business case (survives forever)
   - `workflow_run_id` = one execution attempt stored inside workflow state and audit rows
3. Show the resume logic: "On resume, load the row with the highest `checkpoint_seq`
   for this `thread_id`. Deserialise `state_json` into
   `WorkflowState`. Continue from the resume node."
4. Ask: "What happens if we resume from a checkpoint that was written mid-plan?
   Could we re-run tasks that already completed?"
   - Walk through the check-before-act pattern in `resume_service.py`.

**Azure best practice moment:** Explain Entra authentication for PostgreSQL.
Show the connection code: no password in the DSN. Ask: "Why does the training
allow `AEGISAP_POSTGRES_DSN` with a password?" Answer: "Local dev escape hatch.
Day 7 forbids it in staging/production. Show the `verify_env.py` check that
enforces this."

---

### Block 3: Human-in-the-Loop Patterns (20 min)

**Talking points:**
1. Map the four HITL patterns to real accounts payable scenarios:
   - **Approval gate**: high-value invoice needs controller sign-off
   - **Review queue**: insufficient evidence; human inspects and supplements
   - **Escalation**: prompt injection detected; human security review
   - **Breakglass** (not in AegisAP): emergency override — introduce as a
     risk discussion, not a feature to build
2. Show the Day 5 API:
   - `POST /api/day4/cases/run` — starts the workflow
   - `GET /api/day5/threads/{id}` — inspects current state
   - `POST /api/day5/approvals/{id}/resume` — submits approval decision
3. Discuss the **resume token**: a short-lived, single-use credential bound to
   one `checkpoint_id`. If the training token is missing or stale, regenerate
   the Day 5 pause artifact or create a new handoff through `POST /api/day4/cases/run`.
4. Ask: "Why is the resume token single-use?" Expected: replay attack prevention.
   An attacker who intercepts a resume URL should not be able to approve the
   same invoice twice.

---

## Lab Walkthrough Notes

### Key cells to call out in `day5_durable_state.py`:

1. **`_db_config` cell** — shows the database connection configuration.
   Confirm Entra vs. password auth based on track.

2. **`_run_to_pause` cell** — executes through Day 4 and pauses at the
   approval gate. Show the pause artifact written to `build/day5/`.

3. **`_view_checkpoint` cell** — directly queries PostgreSQL and shows the
   `state_json`. Have learners identify the `routing` and `review_outcome`
   fields inside the JSON blob.

4. **`_pending_approvals` cell** — shows all outstanding approval tasks.
   Encourage learners to run this before and after the resume step to see
   the task status change.

5. **`_idempotency_check` cell** — run the resume step twice. Show that the
   second run produces the same output without duplicating any side effect.

6. **`_resume` cell** — resume with `approved`. Walk through the resumed
   state and compare with the pre-pause checkpoint.

### Expected lab friction points

| Issue | Likely cause | Resolution |
|---|---|---|
| `psycopg2.OperationalError` | PostgreSQL not reachable | Check `AEGISAP_POSTGRES_DSN` or Entra auth; verify network |
| Migrations not applied | Old schema | `uv run python scripts/apply_migrations.py` |
| Checkpoint not found on resume | `thread_id` mismatch | Use the `thread_id` from the pause artifact, not a hand-typed value |
| Resume produces duplicate email | Idempotency check incomplete | Show the `SELECT ... WHERE thread_id` check pattern |

---

## Facilitation Addendum

### Observable Mastery Signals

- Learner can point to the exact thread row, checkpoint row, and approval task row for the same case
- Learner can explain why `duplicate_side_effects = 0` is the acceptance signal for safe replay
- Learner uses the pause artifact and resume artifact as evidence rather than only notebook output

### Intervention Cues

- If a learner confuses `thread_id` with `workflow_run_id`, pause and redraw the table relationships
- If a learner reaches for portal edits or manual DB fixes, redirect them to the exact recovery commands
- If a learner gets blocked by a stale Day 4 artifact, have them regenerate it with `uv run python scripts/run_day4_case.py --planner-mode fixture`

### Fallback Path

- If PostgreSQL or Azure auth is unavailable, switch to a whiteboard walkthrough of the four-table durable-state model and use saved artifacts from `build/day5/`

### Exit Ticket Answer Key

1. `workflow_threads` tells you where the thread is currently parked.
2. `workflow_checkpoints` are immutable history; `workflow_threads` is the mutable head pointer.
3. Inspect `side_effect_ledger` first to determine whether replay protection failed or the upstream task used the wrong effect key.

### Time-box Guidance

- Spend no more than 15 minutes on connection or auth debugging before switching to a saved-artifact walkthrough.
- Protect the final 20 minutes for pause/resume evidence review and rubric scoring.

### Scoring And Remediation Trigger

- Immediate remediation is required if `duplicate_side_effects` is non-zero or if the learner cannot produce the exact pause/resume recovery command.
- A learner who can run the notebook but cannot explain `thread_id` vs `workflow_run_id` does not pass without follow-up coaching.

---

## Common Misconceptions

| Misconception | Correction |
|---|---|
| "Checkpoints are backups" | Checkpoints are resumption points. They capture workflow state, not raw data backups. |
| "thread_id = workflow_run_id" | A thread can have many runs. thread_id is the business identity; run_id is an execution attempt. |
| "Idempotency means doing nothing on retry" | It means producing the same *result* on retry, which may involve detecting the prior result rather than re-running. |
| "Resume token = API key" | Resume tokens are short-lived, single-use, and bound to a specific checkpoint. They are not credentials. |

---

## Discussion Prompts

1. "If a workflow is in the `needs_human_review` state and nobody acts on it
   for 30 days, what should happen? Where would you implement that escalation?"

2. "A controller approves an invoice at exactly the same second that a fraud
   flag is raised by another system. The approval wins. How would you add a
   'post-approval safety check' without changing the resume API?"

3. "PostgreSQL is the durable state store today. What would you need to change
   if we moved to Azure Cosmos DB? Would the workflow code change?"

---

## Expected Q&A

**Q: Can we use Azure Durable Functions instead of custom PostgreSQL checkpoints?**  
A: Yes — Azure Durable Functions (Durable Task Framework) is a strong
alternative. It provides built-in checkpointing, replay, and orchestration
history. AegisAP uses PostgreSQL to keep the implementation transparent and
portable (no Azure Functions dependency). Either approach achieves the same
durability guarantee.

**Q: What happens if the checkpoint write fails after business logic completes?**  
A: The operation must be retried completely. The idempotency checks on each
step ensure that retrying does not duplicate side effects. This is why every
state-changing step must be check-before-act, not act-then-check.

**Q: How long should we keep checkpoints?**  
A: Depends on business retention requirements. AegisAP sets `is_terminal=true`
on the final checkpoint. Non-terminal checkpoints can be pruned after a
configurable retention window (e.g., 90 days). Terminal checkpoints should
follow the business record retention policy (often 7 years for financial data).

---

## Next-Day Bridge (5 min)

> "Today we persisted the workflow safely and added human approval gates.
> But we haven't asked a hard question: what if the recommendation itself
> is wrong? What if an adversarial email in the case material tried to
> influence the outcome? Tomorrow we add the policy review layer — a hard
> safety gate that examines every recommendation before it is persisted,
> and that can refuse to proceed with a structured, auditable decision."
