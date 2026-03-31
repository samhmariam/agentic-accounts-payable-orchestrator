# Day 9 — Cost Governance, Model Routing & Caching · Trainer Guide

> **Session duration:** 3.5 hours (60 min theory + 2.5 h lab)  
> **WAF Pillars:** Cost Optimization · Performance Efficiency  
> **Prerequisite:** Day 8 complete; traces and eval baselines present

---

## Session Goals

By the end of Day 9, every learner should be able to:
- Explain the trade-offs between PTU and PAYG Azure OpenAI billing
- Trace a request through the task class routing table and predict which tier it hits
- Describe the semantic cache bypass policy and when each bypass condition fires
- Read a cost ledger entry and compute the per-case spend
- Articulate why aggregate evaluation scores can mask slice-level regressions

---

## Preparation Checklist

- [ ] `AZURE_OPENAI_ENDPOINT` set to a PTU deployment if available; otherwise note fallback
- [ ] Redis instance available (or in-process cache for training mode)
- [ ] Cost ledger table exists; Day 4–8 runs have populated it
- [ ] `uv run pytest tests/day9 -q` passes
- [ ] Eval baseline from Day 8 present
- [ ] Optionally: Azure Cost Management + Budgets open in portal to show alert setup

**Expected artifact:** `build/day9/routing_report.json`

---

## Theory Segment (60 min)

### Block 1: Azure OpenAI Billing and the PTU Decision (20 min)

**Talking points:**
1. Open with the question: "If Azure OpenAI PAYG costs $0.002/1K tokens, and
   you're running 10,000 invoice cases a month, what's your monthly bill?"
   Walk through the calculation (varies by model). Then ask: "Under what
   conditions does PTU become cheaper?"
2. Draw the PTU vs PAYG comparison:
   ```
   PAYG                          PTU
   ─────────────────────        ─────────────────────────
   Pay per token                Fixed commitment
   Latency varies               Consistent p99
   Auto-scales                  Capped at PTU units
   No commitment                Requires forecasting
   Good for dev/test            Good for steady baseline
   ```
3. Introduce the AegisAP hybrid model: PTU handles the high-volume baseline
   (extraction, classification). PAYG handles bursts and complex cases.
   APIM manages the overflow routing between the two.
4. Show `infra/apim/` policies that route between PTU and PAYG based on
   utilisation. Ask: "What metric should trigger the switch from PTU to PAYG?"
   (PTU utilisation > 90%.)

---

### Block 2: Task Class Routing (20 min)

**Talking points:**
1. Show the five task classes in AegisAP and their routing decisions:
   ```
   Task class              Examples              Model tier
   ─────────────────────   ───────────────────   ─────────────────────
   extraction              parse invoice PDF     gpt-4o-mini / PTU
   classification          route query type      gpt-4o-mini / PAYG
   planning                build action plan     gpt-4o / PTU
   complex_reasoning       compliance check      gpt-4o / PTU
   utility                 summarise, reformat   gpt-4o-mini / PAYG
   ```
2. Ask: "Why does the planning task use gpt-4o on PTU rather than a cheaper
   model?" Walk through the failure scenario: gpt-4o-mini produces a
   well-structured plan that misses the mandatory authority boundary check.
   The error is not visible until a human reviewer catches it. The cost of
   that review is higher than the saved token cost.
3. Introduce the routing function in `src/aegisap/routing/`. Show how task
   class is determined (Pydantic model, explicit annotation on each node).
4. **Live walkthrough:** trace an extraction call and a planning call through
   the router. Show the different `model_deployment` attribute on each span.

---

### Block 3: Semantic Caching and the Cost Ledger (20 min)

**Talking points:**
1. Explain semantic caching: instead of an exact key match, compute the
   embedding of the prompt, find the nearest neighbour in cache, and serve
   the cached response if similarity > threshold.
2. Show the bypass policy (four conditions that skip cache):
   - `ADVERSARIAL_FLAG`: any previously flagged content pattern
   - `HIGH_VALUE`: invoice above authority threshold
   - `FRESH_RETRIEVAL_REQUIRED`: case involves regulatory expiry dates
   - `HUMAN_REVIEW`: decision has HITL routing
3. Ask: "Why do we bypass cache for HIGH_VALUE cases even if the prompt
   content looks identical to a cached case?" Expected: the invoice amount and
   vendor are data-plane content. A similar-looking cached response may have
   been for a $500 invoice from a known vendor. Serving it for a $50,000 case
   from a new vendor is incorrect.
4. Walk through the cost ledger. Show each field and its source:
   - `prompt_tokens`, `completion_tokens` → from the Azure OpenAI response
   - `model_deployment` → from the routing decision
   - `task_class` → from the node annotation
   - `estimated_cost_usd` → computed from public Azure pricing table
5. Show how the ledger is queried to produce per-case and per-tenant totals.
   Show how these totals are compared to the budget ceiling in `check_cost_gates.py`.

---

## Lab Walkthrough Notes

### Key cells to call out in `day9_cost_routing.py`:

1. **Routing decision cell** — send a planning request and show the routing
   decision object. Ask learners to change the `task_class` to `extraction`
   and show the different deployment selected.

2. **Cache demo cell** — run the same retrieval query twice. On the second
   run, show `cached: true` and `latency_ms: 1` in the response attributes.
   Then modify one word in the query and show the cache miss.

3. **Cache bypass cell** — set the invoice amount above the HIGH_VALUE threshold
   and re-run. Show the bypass flag being set and the cache not consulted.

4. **Cost ledger cell** — query the ledger aggregated by day and task class.
   Show the cost breakdown and which task class is most expensive per case.

5. **Slice evaluation cell** — run the evaluation suite and compare aggregate
   vs. per-slice scores. Demonstrate that a model change that improves the
   aggregate score can degrade the high-value-case slice.

### Expected lab friction points

| Issue | Likely cause | Resolution |
|---|---|---|
| All requests routing to PAYG | PTU deployment not provisioned | Expected in training env; show routing code and explain how it would change |
| Cache always missing | Redis not running or wrong connection string | Check redis connection; training env can use in-process mock |
| Cost ledger empty | Previous day runs not recorded cost | Run a case first; verify `record_cost()` call is present in Day 4 executor |
| Slice evaluation unavailable | Missing `data/day8/eval/` slices | Run `evals/run_eval_suite.py --create-slices` |

---

## Facilitation Addendum

### Observable Mastery Signals

- Learner can defend a routing decision with both cost and quality implications.
- Learner knows when cache bypass is required even if the semantic match is strong.
- Learner can connect the routing report to the Day 10 budget gate.

### Intervention Cues

- If “use the best model” shows up without cost framing, stop and ask for the missing budget argument.
- If aggregate scores are used to justify release, redirect to slice-level evidence.
- If cache discussion ignores freshness or risk, force a bypass example before moving on.

### Fallback Path

- If optional APIM or external routing dependencies are unavailable, keep the lab on the in-repo routing report and cost-ledger evidence.
- This is an approved day to run one unsignposted failure drill from [INCIDENT_DRILL_RUNBOOK.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/INCIDENT_DRILL_RUNBOOK.md), especially the altered-threshold or stale-checkpoint scenario.

### Exit Ticket Answer Key

1. `build/day9/routing_report.json` becomes the Day 10 budget evidence.
2. Strong answers cite freshness, regulatory change, high-risk slices, or low-confidence similarity as cache-bypass triggers.
3. Reopening `notebooks/day9_cost_routing.py` is acceptable as the rebuild path if the learner can still explain the routing contract.

### Time-box Guidance

- Limit PTU vs PAYG debate to 10 minutes unless it is grounded in the actual routing report.
- Reserve the final 20 minutes for Day 10 handoff: budget evidence, routing rationale, and release implications.
- Reserve the final 15 minutes of the day for the capstone design brief and PR-style review kickoff from [CAPSTONE_PR_REVIEW.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/CAPSTONE_PR_REVIEW.md).

---

## Common Misconceptions

| Misconception | Correction |
|---|---|
| "Semantic cache is equivalent to memoisation" | Memoisation is exact key match. Semantic cache is approximate nearest-neighbour. The threshold matters enormously for safety — too low = wrong responses served. |
| "PTU is always cheaper at scale" | PTU is cheaper if your utilisation is consistently high. Spiky workloads waste reserved PTU capacity. |
| "Aggregate eval score passing = release safe" | Aggregates can hide regressions in critical slices (high-value cases, locale edge cases). Gate on slice scores too. |
| "Routing by cost is the only factor" | Routing is by task class, which encodes both cost AND quality requirements. High-risk tasks use premium models regardless of cost. |

---

## Discussion Prompts

1. "The aggregate compliance accuracy score passes the 0.90 threshold. But
   the 'invoices > £20,000' slice has a recall of 0.71. Do you release?
   What process change does this suggest?"

2. "You are caching answers to vendor compliance queries. A vendor's
   compliance status changes between two requests that are nearly
   semantically identical. How does AegisAP handle this? Is the current
   policy sufficient?"

3. "You want to add a new task class for 'regulatory policy lookup.' What
   model tier do you assign it to? What are the criteria for that decision?"

---

## Expected Q&A

**Q: Can we use Redis Cache on Azure for the semantic cache in production?**  
A: Yes — Azure Cache for Redis Enterprise supports vector search, which is
required for semantic caching. For production, Redis is multi-replica and
consistent across Container App instances. The in-process mock used in
training is single-instance only and is unsuitable for production.

**Q: What happens when PTU capacity is exhausted (429)?**  
A: APIM's retry policy with round-robin overflow routes the request to PAYG.
The cost is higher, but the request succeeds. The PTU utilisation metric
triggers an alert so the team knows to increase PTU units at the next
commitment renewal.

**Q: How is DSPy used in AegisAP?**  
A: DSPy is referenced as a future optimisation path. The prompt templates
in Day 4 and Day 6 are currently hand-crafted. DSPy's `BootstrapFewShot`
optimiser can improve them by compiling against the evaluation dataset. This
is gated behind the Day 10 acceptance suite to prevent regressions.

---

## Next-Day Bridge (5 min)

> "We have a fully instrumented, cost-governed, tested system. The last step
> is to deploy it in a way that's safe, auditable, and reversible. Tomorrow
> we apply all of the system's own acceptance gates to the act of deploying
> the system itself. If the gates pass, traffic shifts incrementally. If
> anything fails, an automated rollback fires within minutes."
