# Day 4 — Explicit Planning · Trainer Guide

> **Session duration:** 3 hours (50 min theory + 2 h lab + 10 min wrap-up)  
> **WAF Pillars:** Operational Excellence · Reliability  
> **Prerequisite:** Day 3 complete; Azure OpenAI responding with structured output support

---

## Session Goals

By the end of Day 4, every learner should be able to:
- Explain the planner–executor pattern and contrast it with a reactive agent
- Use Azure OpenAI structured outputs with a Pydantic schema
- Write a policy overlay rule and show how it blocks a plan before execution
- Trace a plan execution result back through the planning and validation steps
- Explain what "fail closed" means and verify that AegisAP implements it

---

## Preparation Checklist

- [ ] Day 3 artifact present: `build/day3/`
- [ ] Azure OpenAI supports structured outputs (`gpt-4o` or later)
- [ ] `scripts/run_day4_case.py --planner-mode fixture` runs cleanly
- [ ] Have the plan schema open in the editor: `src/aegisap/day4/planning/`
- [ ] Prepare one deliberately invalid plan JSON for the policy overlay demo

**Expected artifact:** `build/day4/golden_thread_day4.json`

---

## Theory Segment (50 min)

### Block 1: Reactive vs. Plan-First Agents (20 min)

**Talking points:**
1. Start with a live demo of a simple ReAct-style loop (pseudocode or real):
   ```
   Observe: invoice INV-3001, amount GBP 12,500
   Think: I should check the PO first
   Act: check_po(PO-9001)
   Observe: PO found, amount matches
   Think: I should check vendor authority
   Act: check_vendor_authority(VEND-001)
   ...
   ```
   Ask: "What can go wrong here?" Expected answers:
   - The LLM might skip a mandatory step
   - The LLM might invent a task that doesn't exist
   - There's no pre-flight check — problems are discovered mid-execution

2. Now show the plan-first approach: "Before any task runs, the planner produces
   a complete typed plan. The plan is validated. The policy overlay is applied.
   Only then does execution start."

3. Draw the flow:
   ```
   LLM planner ──► raw plan JSON
       │
       ▼
   Pydantic validation ──► TypeError / ValueError if invalid
       │
       ▼
   Policy overlay ──► policy rejection if rule violated
       │
       ▼
   Executor ──► task results
       │
       ▼
   Recommendation or Escalation
   ```

4. Ask: "What is the earliest point in this flow where we can fail closed?"
   Answer: during plan validation — before a single task has run.

**Key message:** "The plan is the contract. If the contract is bad, nothing runs."

---

### Block 2: Structured Outputs with Pydantic (15 min)

**Talking points:**
1. Open the plan schema in the editor. Show the Pydantic `BaseModel`:
   - Task type is an `Enum` — not a free-text string
   - `sequence` is an `int` — not a string
   - `depends_on` is a `list[int]` — explicit dependency graph
2. Show `model_json_schema()` output. Explain: "This JSON Schema is what we
   send to Azure OpenAI as `response_format`."
3. Live demo: call `client.chat.completions.create()` with `strict=True` and
   the plan schema. Show the raw JSON that comes back. Then parse it:
   ```python
   plan_dict = json.loads(response.choices[0].message.content)
   plan = InvoicePlan.model_validate(plan_dict)
   ```
4. Deliberately introduce an error: change `strict=True` to `strict=False`
   and modify the prompt to ask for an unrecognised task type. Show what
   happens without strict mode.

---

### Block 3: Policy Overlay and Fail Closed (15 min)

**Talking points:**
1. Show a policy rule in action:
   ```
   Rule: if amount > 50,000 → plan must include "check_director_authority"
   ```
   Demonstrate a plan for INV-3001 (GBP 12,500) that does NOT include this
   task — correctly. Then push the threshold down to GBP 10,000 — the rule
   now triggers. The plan is rejected.
2. Emphasise: "The policy overlay is Python code. It is tested, versioned,
   and reviewed in PRs. We do not encode business rules in prompts."
3. Walk through the `EscalationPackage` that gets emitted when a plan
   fails validation or policy check. Show its `escalation_reason` field.
4. Ask: "Is an escalation a failure?" Expected: No — it is a correct outcome
   produced by the system deliberately.

---

## Lab Walkthrough Notes

### Key cells to call out in `day4_explicit_planning.py`:

1. **`_generate_plan` cell** — shows raw planner output. Ask learners to
   identify the task types and verify they match the allowed enum values.

2. **`_validate_plan` cell** — walk through the Pydantic validation step
   and the policy overlay. Introduce a deliberate policy violation and
   show the escalation output.

3. **`_execute` cell** — show the executor running each task in sequence.
   Walk through the `_exec_elapsed_ms` timing field and explain why
   it uses the underscore prefix (cell-private in Marimo).

4. **Result cell** — show `RecommendationPackage` for the golden thread.
   Open the plan trace inside it and match each task to its elapsed time.

5. **Escalation scenario cell** — switch planner mode to fixture mode with
   a broken plan and show the escalation path end-to-end.

### Expected lab friction points

| Issue | Likely cause | Resolution |
|---|---|---|
| `ValidationError` on plan parse | Enum value not in schema | Check the planner prompt — add enum values to the instruction |
| Policy overlay never fires | Threshold too high for golden thread amount | Lower threshold in `.env` or policy YAML for demo |
| Planner returns extra fields | `strict=False` or schema was not sent correctly | Verify `response_format` includes `json_schema` with `strict: True` |

---

## Facilitation Addendum

### Observable Mastery Signals

- Learner can explain why the validator and policy overlay, not the planner, have final blocking authority.
- Learner produces both `build/day4/golden_thread_day4.json` and `build/day4/checkpoint_policy_overlay.json`.
- Learner can name the exact evidence gap that caused the checkpoint case to fail closed.

### Intervention Cues

- If a learner treats the plan JSON as self-authorizing, stop and revisit the fail-closed overlay.
- If the checkpoint artifact is missing, do not let the learner mark the day complete.
- If execution succeeds on a case that should block, compare the overlay preconditions before debugging the executor.

### Fallback Path

- If live planner mode is unreliable, switch the room to fixture mode and focus on validator, overlay, and checkpoint reasoning.

### Exit Ticket Answer Key

1. Python owns the final authority to block or escalate a plan.
2. Strong answers name the missing precondition or evidence check, not just “the policy overlay.”
3. `uv run python scripts/run_day4_case.py --planner-mode fixture` is the deterministic rebuild path.

### Time-box Guidance

- Reserve the final 25 minutes for the mandatory checkpoint and artifact review.
- If a learner has not reached execution by the midpoint, move them to fixture mode immediately.

---

## Common Misconceptions

| Misconception | Correction |
|---|---|
| "Structured outputs mean valid business logic" | Structural validity ≠ business validity. The model can produce a structurally valid plan that violates policy. |
| "The policy overlay is optional for simple cases" | The overlay runs on every plan, regardless of complexity. Simplicity is not a reason to skip safety checks. |
| "Fail closed means the system breaks" | Fail closed means the system produces an escalation rather than proceeding on bad input. It is a correct outcome. |
| "The planner decides the execution path" | The executor decides how to run tasks. The planner declares what tasks to run. |

---

## Discussion Prompts

1. "A planner generates a plan with tasks in the wrong order — it tries to
   compute a recommendation before completing the PO check. How does the
   executor detect and handle this?"

2. "A policy rule says all high-value invoices need director authority. How
   would you test this rule without calling Azure OpenAI? What would a
   unit test for the policy overlay look like?"

3. "Today's planner uses `gpt-4o`. For simple auto-approve cases, would a
   smaller model work? What would you need to measure to answer that question?"
   (Bridge to Day 9.)

---

## Expected Q&A

**Q: Can the policy overlay modify a plan rather than reject it?**  
A: Yes — it can add mandatory tasks that the planner omitted. AegisAP returns
a rejection in its current form, but the same overlay function could inject
the missing task and re-validate. The decision of whether to reject or auto-
correct is a business policy choice.

**Q: Why use LangGraph for the executor if the plan already defines the task sequence?**  
A: The executor uses LangGraph nodes for each task type. This keeps the same
observability, state management, and conditional edge infrastructure as Days 2–3.
The plan drives *which* subgraph to execute, not the subgraph's internal logic.

**Q: What if the LLM refuses to produce a plan for a valid invoice?**  
A: The planner should never refuse a valid invoice — structured outputs prevent
non-JSON responses. If the model returns valid schema JSON with an empty tasks
list, the validator catches it (tasks must be non-empty) and escalates.

---

## Next-Day Bridge (5 min)

> "Today we have explicit plans, validated before execution. But all of this
> state still lives in memory. If the process crashes after the plan executes
> but before the recommendation is delivered, the work is lost. Tomorrow we
> add durability: the state is written to PostgreSQL at every significant step,
> and the workflow can be resumed after any failure — even a human approval
> pause that lasts three weeks."
