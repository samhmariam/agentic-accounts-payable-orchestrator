# Day 9 — Cost Governance & Model Routing · Trainee Pre-Reading

> **WAF Pillars:** Cost Optimization · Performance Efficiency  
> **Time to read:** 25 min  
> **Lab notebook:** `notebooks/day9_cost_routing.py`

---

## Learning Objectives

By the end of Day 9 you will be able to:

1. Explain Azure OpenAI's two billing models and when to use each.
2. Define task class routing and describe why routing decisions must be explicit.
3. Explain semantic caching, its policy constraints, and when to bypass it.
4. Describe the cost ledger pattern and what a per-run cost record contains.
5. Explain why aggregate metrics can hide per-slice regressions.

---

## 1. Azure OpenAI Billing Models

| Model | How you pay | Best for |
|---|---|---|
| **Pay-as-you-go (PAYG)** | Per token consumed | Unpredictable load, development, low volume |
| **Provisioned Throughput Units (PTU)** | Reserved capacity per hour regardless of usage | Predictable high-throughput production workloads |

### Key implication: PTU vs. PAYG trade-offs

| Concern | PAYG | PTU |
|---|---|---|
| Cost at low utilisation | Low | Fixed (expensive if underused) |
| Cost at high utilisation | High (can spike) | Predictable cap |
| Latency | Variable; may queue | Consistent; bounded |
| Overflow behaviour | Throttled (429) | Can spill to PAYG via APIM |

### Azure best practice
- Use PTU for your highest-traffic tasks (e.g., Day 4 planning) once you have
  three months of baseline utilisation data.
- Configure **APIM** as the gateway so overflow from PTU automatically routes to
  a PAYG deployment. Never hardcode the endpoint to a specific deployment.
- Monitor `Utilization` and `Queued Requests` metrics on your PTU deployment to
  detect when to scale or adjust routing.

---

## 2. Task Class Routing

Not every LLM call needs the same model. AegisAP defines **task classes** that
describe the capability and latency requirements of each model invocation:

| Task class | Example use | Recommended model tier |
|---|---|---|
| `extraction_standard` | Day 1 invoice extraction, low OCR noise | `gpt-4o-mini` |
| `extraction_complex` | Day 1 with heavy OCR noise, foreign characters | `gpt-4o` |
| `planning_low_risk` | Day 4 planning for auto-approve cases | `gpt-4o-mini` |
| `planning_high_risk` | Day 4 planning for high-value or flagged cases | `gpt-4o` |
| `review_compliance` | Day 6 policy review | `gpt-4o` (never mini — compliance critical) |

### Why routing must be explicit

Implicit routing ("just always use the best model") produces:
- Unnecessary cost on low-complexity tasks
- No visibility into which model handled which decision
- No ability to A/B test model tiers on specific task classes

Explicit routing produces:
- Traceable routing decisions in every span
- Cost attribution by task class and case class
- Controlled experiments: swap the model for `extraction_standard` without
  touching `review_compliance`

---

## 3. Semantic Caching

**Semantic caching** stores the result of prior LLM calls and reuses them when a
new request is semantically similar enough.

```
New request embedding
    │
    ▼
[ Cache lookup ] ── cosine similarity ──► score
    │
    ├── score ≥ threshold → return cached response (no LLM call)
    │
    └── score < threshold → call LLM, store result
```

### Benefits and risks

| Benefit | Risk |
|---|---|
| Reduces PAYG cost on repetitive queries | Stale cache may return outdated policy answers |
| Reduces p99 latency on cache hits | Semantically similar ≠ actually equivalent |
| Predictable cost on high-repetition workloads | Compliance-sensitive decisions must never be cached |

### Cache bypass policy

AegisAP bypasses the cache in the following situations:

| Condition | Why |
|---|---|
| Task class is `review_compliance` | Policy compliance decisions must always use current context |
| Evidence freshness flag is set | Retrieved documents may have changed since cache entry was created |
| Case risk score is HIGH | High-risk cases require fresh model inference |
| Time-to-live expired | All cache entries have a configurable TTL |

### Azure best practice
Use **Azure Cache for Redis** as the cache backend if deploying beyond a single
replica. In-memory caches do not survive process restarts and do not function
correctly with multiple Container App replicas.

---

## 4. The Cost Ledger

Every model call that completes successfully writes a **cost ledger entry**:

```json
{
  "entry_id": "ledger-abc-001",
  "thread_id": "thread-inv-3001",
  "workflow_run_id": "run-xyz-789",
  "task_class": "planning_high_risk",
  "model_deployment": "gpt-4o-planning",
  "prompt_tokens": 1240,
  "completion_tokens": 312,
  "total_tokens": 1552,
  "estimated_cost_usd": 0.0047,
  "cache_hit": false,
  "created_at": "2024-03-26T14:32:00Z"
}
```

The ledger is queryable by `thread_id`, `task_class`, `case_class`, and date
range. It answers questions like:
- "What is the average cost per invoice class?"
- "How much did we save with caching this month?"
- "Is the `planning_high_risk` task class exceeding its cost ceiling?"

---

## 5. Cost Governance Gates

Day 9 introduces **cost gates** — thresholds that block a case's progression
if it has exceeded a per-run cost ceiling:

```
Per-run cost ceiling for standard cases: $0.10
Per-run cost ceiling for high-value cases: $0.25

If accumulated_cost > ceiling:
    → emit cost gate exception
    → escalate to human review (do not abort silently)
```

Cost gates prevent runaway spending from model loops, infinite retries, or
unexpectedly expensive plans.

---

## 6. Slice-Based Evaluation

Aggregate metrics can hide per-slice regressions. AegisAP tracks evaluation
scores by **slice** — a combination of case class and task class.

Example: a model change improves average faithfulness from 0.87 to 0.89.
But broken down by slice:

| Slice | Before | After | Delta |
|---|---|---|---|
| `extraction_standard / auto_approve` | 0.92 | 0.94 | +0.02 ✅ |
| `planning_low_risk / auto_approve` | 0.88 | 0.91 | +0.03 ✅ |
| **`review_compliance / high_value`** | **0.91** | **0.83** | **−0.08 ❌** |
| `extraction_complex / high_risk` | 0.80 | 0.81 | +0.01 ✅ |

The aggregate improved, but the most critical slice — compliance review on
high-value cases — regressed significantly. **Aggregate-only evaluation would
have missed this.**

---

## Glossary

| Term | Definition |
|---|---|
| **PTU** | Provisioned Throughput Units — reserved Azure OpenAI capacity committed per hour |
| **PAYG** | Pay-As-You-Go — Azure OpenAI billing based on tokens consumed |
| **Task class** | A named category of model invocation with defined capability and latency requirements |
| **Semantic caching** | Reusing prior LLM responses when a new request is semantically similar |
| **Cost ledger** | A durable per-call record of token usage and estimated cost, queryable by case and task |
| **Cost gate** | A threshold that escalates a case if accumulated model cost exceeds the per-run ceiling |
| **Slice evaluation** | Measuring evaluation scores separately for each combination of case class and task class |

---

## Check Your Understanding

1. What is the difference between PAYG and PTU billing for Azure OpenAI? Give one scenario where each is the better choice.
2. Why must routing decisions be explicit rather than "always use the best model"?
3. Under what four conditions does AegisAP bypass the semantic cache?
4. What fields does a cost ledger entry contain, and what business questions can it answer?
5. Explain with an example why slice-based evaluation is more useful than aggregate evaluation for AI systems.

---

## Lab Readiness

- **Lab duration:** 2.5 hours
- **Required inputs:** `build/day8/regression_baseline.json`, task-routing fixtures, and `notebooks/day9_cost_routing.py`
- **Expected artifact:** `build/day9/routing_report.json`

### Pass Criteria

- The routing report shows an explicit deployment choice and justification.
- One routing or cache-bypass decision is changed and defended with cost-quality reasoning.
- The artifact is ready to serve as budget evidence for Day 10.

### Common Failure Signals

- The learner argues for “best model everywhere” without budget or latency justification.
- Cache hits are accepted even when freshness or risk should force a bypass.
- Aggregate score improvements are used to hide slice regressions.

### Exit Ticket

1. Which Day 9 output becomes budget evidence on Day 10?
2. When should AegisAP bypass the semantic cache even if similarity is high?
3. What exact command or notebook path would you use to regenerate the routing report?

### Remediation Task

Re-run the routing lab with:

```bash
marimo edit notebooks/day9_cost_routing.py
```

Then explain which task class you would route differently and what operational
cost or quality tradeoff justifies that decision.

### Stretch Task

Propose a new task class for regulatory lookup and explain how you would decide
whether it belongs on a light, strong, or overflow route.
