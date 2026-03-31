# Day 4 — Explicit Planning · Trainee Pre-Reading

> **WAF Pillars:** Operational Excellence · Reliability  
> **Time to read:** 20 min  
> **Lab notebook:** `notebooks/day4_explicit_planning.py`

---

## Learning Objectives

By the end of Day 4 you will be able to:

1. Explain the *planner–executor* pattern and contrast it with a reactive agent.
2. Describe why plans should be typed JSON validated before execution.
3. Explain the role of a policy overlay and why it outranks the LLM planner.
4. Interpret a plan schema and identify which fields are deterministic decisions.
5. Describe how a plan can *fail closed* before any downstream work proceeds.

---

## 1. Reactive Agents vs. Plan-First Agents

### Reactive agent

A reactive agent takes an action, observes the result, then decides its next
action — repeating until some terminal condition.

```
Observe ──► Think ──► Act ──► Observe (loop)
```

Reactive agents are flexible but unpredictable. In enterprise workflows this
means:
- Non-deterministic execution paths — hard to audit
- No pre-flight validation — the system discovers problems mid-execution
- Hard to estimate time or cost before starting

### Plan-first agent

A plan-first agent generates a **complete plan** before executing any action.
The plan is validated, the policy overlay is applied, and only then does
execution begin.

```
Observe ──► Plan ──► Validate ──► Execute ──► Report
  (LLM)              (Python)     (Python)
```

The plan is a **typed JSON contract** between the LLM and the executor. The
executor only processes plans that pass validation — it never interprets
ambiguous or malformed instructions.

---

## 2. Structured Outputs and Azure OpenAI

Azure OpenAI supports **structured outputs**: you provide a JSON Schema and the
model guarantees its response matches that schema (no extra fields, no missing
required fields, correct types).

```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "InvoicePlan",
            "strict": True,
            "schema": InvoicePlan.model_json_schema(),
        },
    },
)
plan_dict = json.loads(response.choices[0].message.content)
```

### Azure best practice
- Always use `strict: True` in `json_schema` response format. Without it, the
  model may produce JSON that satisfies the schema structurally but not logically.
- Use Pydantic `BaseModel` to define your schema — `model_json_schema()` generates
  the JSON Schema automatically and stays in sync with your Python types.
- Log the raw model response before parsing it. If parsing fails, you want the
  raw output for debugging.

---

## 3. Plan Schema Design

A good plan schema has these properties:

| Property | What it means | Why it matters |
|---|---|---|
| **Typed fields** | Every field has a declared type | Catches wrong types before execution |
| **Enum for task types** | Task names are from a fixed set | Prevents the model from inventing unknown tasks |
| **Explicit ordering** | Tasks have a `sequence` or `depends_on` field | Executor knows the dependency graph |
| **No free-text instructions** | Tasks are parameterised, not instruction strings | Executor logic is deterministic |

### Example minimal plan

```json
{
  "plan_id": "plan-abc-001",
  "case_id": "INV-3001",
  "tasks": [
    { "sequence": 1, "task_type": "validate_po", "po_number": "PO-9001" },
    { "sequence": 2, "task_type": "check_vendor_auth", "vendor_id": "VEND-001" },
    { "sequence": 3, "task_type": "compute_recommendation", "depends_on": [1, 2] }
  ],
  "escalation_if_failed": true
}
```

The executor handles each `task_type` with a dedicated Python handler — the LLM
never writes executable code.

---

## 4. The Policy Overlay

The planner may generate a valid plan, but business policy can still prohibit
execution. The **policy overlay** is a set of deterministic rules applied after
plan generation but before execution.

Policy overlay rules might include:
- If `amount > 50 000`, require `check_director_authority` task in plan
- If `vendor_id` is on the sanctions list, reject plan entirely
- If plan contains a `skip_po_check` task, reject with `POLICY_VIOLATION`

The overlay runs in Python, not via the LLM. This means:
- Policy changes are code reviews, not prompt engineering
- Policy enforcement is independently testable
- Policy violations are auditable with precise reason codes

### Azure best practice
Store policy rules in a structured format (e.g., YAML loaded at startup or
Azure App Configuration entries) so they can be updated without a code
deployment. Tag each rule with a policy ID so violations can reference the
exact rule violated.

---

## 5. Fail Closed

A system **fails closed** when it refuses to proceed in the presence of
uncertainty. A system fails *open* when it proceeds anyway, hoping things work out.

In accounts payable, failing open means processing an invoice that shouldn't be
processed. Failing closed means stopping and escalating.

AegisAP always fails closed:
- If the plan fails validation → escalation package, no execution
- If the policy overlay rejects the plan → escalation package, no execution
- If a plan task raises an unhandled exception → escalation package, no partial result

```
Plan generation
  │
  ├── Validation fails ──────────────────────────────► EscalationPackage
  │
  ├── Policy overlay rejects ─────────────────────────► EscalationPackage
  │
  └── Validation passes + policy passes
          │
          ▼
       Execution
          │
          ├── Task exception ──────────────────────────► EscalationPackage
          │
          └── All tasks succeed
                  │
                  ▼
           RecommendationPackage
```

---

## 6. Execution Tracing

Every plan execution emits structured timing data:

```python
{
  "plan_id": "plan-abc-001",
  "tasks": [
    { "task_type": "validate_po", "started_at": "...", "elapsed_ms": 12, "status": "ok" },
    { "task_type": "check_vendor_auth", "elapsed_ms": 8, "status": "ok" },
    { "task_type": "compute_recommendation", "elapsed_ms": 45, "status": "ok" }
  ],
  "total_elapsed_ms": 65,
  "outcome": "recommendation_ready"
}
```

This trace is persisted with the workflow state and available in Day 8's
observability dashboard.

---

## Glossary

| Term | Definition |
|---|---|
| **Planner** | The LLM component that generates a typed plan JSON from the invoice context |
| **Executor** | The deterministic Python component that runs the tasks in the plan |
| **Structured outputs** | Azure OpenAI feature constraining model output to a declared JSON schema |
| **Policy overlay** | Post-planning deterministic rules that can reject or modify a plan before execution |
| **Fail closed** | Refusing to proceed when a required condition is not met |
| **Plan schema** | The Pydantic model (and its JSON Schema representation) that defines a valid plan |
| **Task type** | An enum value representing a known, executable workflow step |

---

## Check Your Understanding

1. What is the difference between a reactive agent and a plan-first agent? Why does the plan-first pattern favour auditability?
2. What does `strict: True` do in Azure OpenAI structured outputs, and why should you always set it?
3. Why are task types defined as enums rather than free-text strings in the plan schema?
4. What is the policy overlay, and why does it run in Python rather than in the LLM?
5. Define "fail closed" and give two examples of conditions under which AegisAP fails closed in Day 4.

---

## Lab Readiness

- **Lab duration:** 2.5 hours
- **Required inputs:** `build/day3/golden_thread_day3.json`, planner fixture or Azure OpenAI access, and `notebooks/day4_explicit_planning.py`
- **Expected artifacts:** `build/day4/golden_thread_day4.json`, `build/day4/checkpoint_policy_overlay.json`

### Pass Criteria

- The notebook produces a valid plan and a deterministic execution outcome.
- The policy overlay blocks the seeded high-risk case when required evidence is missing.
- The mandatory checkpoint artifact proves the fail-closed rule and blocked case.

### Common Failure Signals

- The planner is trusted without a validator or policy overlay review.
- The case proceeds even though a required precondition or evidence check is missing.
- The learner can describe the plan but not the blocking condition that forced escalation.

### Exit Ticket

1. Which part of Day 4 owns the final authority to block a plan: the LLM or Python?
2. What exact condition made the checkpoint case fail closed?
3. What command would you run to rebuild the Day 4 artifact in fixture mode?

### Remediation Task

Re-run the deterministic planner flow with:

```bash
uv run python scripts/run_day4_case.py --planner-mode fixture
marimo edit notebooks/day4_explicit_planning.py
```

Then regenerate `build/day4/checkpoint_policy_overlay.json` and explain which
evidence gap triggered the block.

### Stretch Task

Design one additional policy-overlay rule for supplier-bank changes that keeps
the executor deterministic and explain how you would test it without live model calls.
