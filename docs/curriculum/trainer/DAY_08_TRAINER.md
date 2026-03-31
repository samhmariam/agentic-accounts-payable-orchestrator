# Day 8 — Observability & Reliability Engineering · Trainer Guide

> **Session duration:** 4 hours (70 min theory + 2.5 h lab + 20 min wrap-up)  
> **WAF Pillars:** Operational Excellence · Reliability  
> **Prerequisite:** Day 7 complete; Azure Monitor / App Insights connection string in env

---

## Session Goals

By the end of Day 8, every learner should be able to:
- Explain what OpenTelemetry traces, spans, metrics, and logs are
- Add a custom span to an existing workflow node
- Write a KQL query to find latency outliers in Azure Monitor
- Explain why evaluation suites must run as regression tests, not ad-hoc checks
- Identify three categories of silent failure that AegisAP's monitoring detects

---

## Preparation Checklist

- [ ] `APPLICATIONINSIGHTS_CONNECTION_STRING` set in `.env`
- [ ] `LANGSMITH_API_KEY` secret present in Key Vault (or `LANGCHAIN_API_KEY` env var for local)
- [ ] Evaluation baseline exists: `data/day8/eval/baseline.json`
- [ ] `uv run pytest tests/day8 -q` passes
- [ ] Run a golden thread case to generate traces: `uv run python scripts/run_day4_case.py --planner-mode fixture`
- [ ] Optionally: Azure Monitor workbook open showing trace data

**Expected artifact:** `build/day8/regression_baseline.json`

---

## Theory Segment (70 min)

### Block 1: The Three Pillars of Observability (20 min)

**Talking points:**
1. Open with a scenario: "Production incident at 11 PM. Alert: error rate
   spiked. You have 30 minutes to find the cause. What do you look for first?"
   Walk through what each pillar tells you:
   - **Logs**: "What events happened? For which case?" → Discrete events
   - **Metrics**: "How bad is it? Which percentile?" → Numeric aggregates
   - **Traces**: "Which step caused it, and how long did each step take?" → Request journey
2. Emphasise: you need all three. Logs without metrics can't tell you how
   widespread the issue is. Metrics without traces can't tell you *which*
   invocation failed. Traces without logs miss the edge cases.
3. Introduce OTEL as the standard. Ask: "Why do we prefer a standard over
   vendor-specific SDKs?" Key answers:
   - Vendor portability: traces go to Azure Monitor today, LangSmith tomorrow
   - Consistent context propagation across service boundaries
   - One SDK, not three

---

### Block 2: OTEL Traces and Spans in Depth (30 min)

**Talking points:**
1. Draw a trace tree for the AegisAP golden thread:
   ```
   workflow.run (root span)
   ├── day1.extract        [12ms]
   ├── day3.retrieve       [45ms]
   │   ├── search.vendor   [18ms]
   │   └── search.compl    [22ms]
   ├── day4.plan           [230ms]
   │   └── openai.chat     [220ms]
   ├── day6.review         [180ms]
   │   └── openai.chat     [175ms]
   └── day5.checkpoint     [8ms]
   ```
2. Explain each span field: `trace_id`, `span_id`, `parent_span_id`.
   Draw how the parent-child chain works. Show that ALL spans share the
   same `trace_id`.
3. Show the correlation IDs: `workflow_run_id`, `thread_id`, `case_id`.
   Map each to the span attributes layer and to the database fields where
   they are persisted.
4. Live demo: open Application Insights in Azure Portal, find the golden
   thread trace, and navigate the span tree. Show the "End-to-end transaction"
   view.

**Code walkthrough — adding a custom span:**
```python
from opentelemetry import trace

tracer = trace.get_tracer("aegisap.day4.executor")

with tracer.start_as_current_span("plan.task.validate_po") as span:
    span.set_attribute("task.po_number", po_number)
    span.set_attribute("task.vendor_id", vendor_id)
    result = validate_po(po_number, vendor_id)
    span.set_attribute("task.result", result.status)
```

Have learners add this to one of the executor cells and verify the span
appears in the next trace.

---

### Block 3: Silent Failures and Evaluation Regression (20 min)

**Talking points:**
1. Ask: "What does a silent failure look like?" Expected: no exceptions,
   system appears healthy, but output quality has degraded.
2. Show three AegisAP silent failure modes:
   - **Latency regression**: Day 4 planning takes 2× longer post model update.
     Error rate: 0%. Latency: +150ms p99. How do you detect this without
     alerting on errors?
   - **Retrieval drift**: the search index hasn't been refreshed. Hit rate
     for compliance searches is dropping.
   - **Spurious escalations**: the `needs_human_review` rate is slowly
     climbing. No error. But human reviewers are spending double the time.
3. For each, show the metric or alert that would catch it.
4. Bridge to evaluation: "Eval scores are also metrics. If compliance
   accuracy drops from 0.92 to 0.85, that's a regression. It should block
   a release the same way a 5% error rate would."
5. Show `evals/score_thresholds.yaml` and `evals/run_eval_suite.py`.
   Explain that these run in CI as a normal part of the release pipeline
   in Day 10.

---

## Lab Walkthrough Notes

### Key cells to call out in `day8_observability.py`:

1. **`_otel_status` cell** — confirms OTEL exporter is running and traces
   are being sent. If this shows "not configured", stop and fix the
   connection string before proceeding.

2. **`_kql_viewer` cell** — runs a live KQL query against the workspace.
   Walk through the query structure. Show how to filter by `workflow_run_id`.

3. **`_eval_results` cell** — shows evaluation scores from the latest run.
   Ask learners: "Which score is closest to its threshold? What would push
   it below the threshold?"

4. **`_regression_check` cell** — compares current scores to the baseline.
   Have learners deliberately degrade a score by modifying a system prompt
   comment, then run the regression check to see it fail.

5. **`_persist` cell** — show the evaluation results being persisted for
   the next regression comparison.

### Expected lab friction points

| Issue | Likely cause | Resolution |
|---|---|---|
| No traces in App Insights | Connection string missing or SDK not initialised | Check `APPLICATIONINSIGHTS_CONNECTION_STRING`; verify OTEL distro init |
| KQL query returns 0 rows | Data ingestion lag (2–5 min) | Wait, then re-run query |
| Eval scores not found | `data/day8/eval/` empty | Run `scripts/run_day4_case.py` to generate a case, then re-run eval suite |
| LangSmith traces missing | API key not in Key Vault or `LANGCHAIN_TRACING_V2` not set | Check Key Vault; set `LANGCHAIN_TRACING_V2=true` |

---

## Facilitation Addendum

### Observable Mastery Signals

- Learner can explain why a trace or eval signal would block release, not just describe the dashboard.
- Learner produces both `build/day8/regression_baseline.json` and `build/day8/checkpoint_trace_extension.json`.
- Learner can point to the exact attribute or query added by the checkpoint.

### Intervention Cues

- If a learner treats “tests passed” as equivalent to “release is safe,” reconnect them to regression and silent-failure concepts.
- If the checkpoint artifact is missing, do not count the day as complete.
- If KQL becomes the blocker, anchor on one known-good query and one attribute rather than teaching the entire language.

### Fallback Path

- If live Application Insights is unavailable, use the checkpoint artifact and saved queries to teach the release-blocking logic offline.
- This is an approved day to run one unsignposted failure drill from [INCIDENT_DRILL_RUNBOOK.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/INCIDENT_DRILL_RUNBOOK.md), especially the missing Day 8 baseline scenario.

### Exit Ticket Answer Key

1. Mandatory escalation recall remains zero-tolerance because missing a required escalation is a material production risk.
2. Strong answers name the new span or attribute and where it appears in KQL or Azure Monitor.
3. Reopening `notebooks/day8_observability.py` is the expected rebuild path when the baseline or checkpoint artifact is missing.

### Time-box Guidance

- Save at least 25 minutes for the mandatory checkpoint and KQL evidence review.
- If live telemetry setup exceeds 15 minutes, switch the cohort to saved artifacts and continue.
- Reserve 15-20 minutes if you are injecting the incident drill.

---

## Common Misconceptions

| Misconception | Correction |
|---|---|
| "Logging is enough for observability" | Logs answer 'what happened'. Metrics answer 'how often / how bad'. Traces answer 'which path'. All three are needed. |
| "OTEL is just another logging library" | OTEL is a data model standard with vendor-neutral exporters. It produces structured trace trees, not log strings. |
| "Evaluation runs once, before release" | Evaluation runs continuously in CI AND on a production sentinel. Silent degradation appears between releases. |
| "trace_id = workflow_run_id" | trace_id is an OTEL concept tied to one HTTP request or process invocation. workflow_run_id is a business concept that persists in the database. They are correlated but distinct. |

---

## Discussion Prompts

1. "A model update is released. Aggregate faithfulness improves from 0.87 to
   0.89. But mandatory escalation recall drops from 1.0 to 0.97 on
   high-value cases. Should the release proceed?"
   (Answer: No. Mandatory escalation recall = 1.0 is a zero-tolerance gate.
   Three missed escalations out of 100 = three unreviewed high-risk invoices.)

2. "An invoice is processed successfully and the trace shows all spans as OK.
   An hour later the controller says 'I never got the approval email.' How
   do you diagnose this using OTEL data?"

3. "You're on call. An alert fires: p99 latency for `day4.plan` exceeded
   1000ms (threshold: 800ms). Write the KQL query you'd run first."

---

## Expected Q&A

**Q: Should we create one tracer per class, one per module, or one global tracer?**  
A: One per logical component (e.g., `aegisap.day4.executor`, `aegisap.day6.reviewer`).
This gives useful `instrumentationScope` grouping in traces without excessive
granularity. Never use one global tracer — it loses the component context.

**Q: What's the difference between a span event and a span attribute?**  
A: An **attribute** is metadata that describes the span (e.g., `invoice_id`,
`model_deployment`, `task_type`). An **event** is a timestamped annotation
inside the span (e.g., "plan validation completed", "cache miss"). Use
attributes for stable metadata; use events for significant moments during
the span's execution.

**Q: Can we use Application Insights and LangSmith at the same time?**  
A: Yes — AegisAP uses both. Azure Monitor receives all spans via the OTLP
exporter. LangSmith receives LLM-specific spans via the LangChain callback.
Both use the same `trace_id` for correlation. The Day 10 trace correlation
gate verifies that a run is discoverable in both sinks.

---

## Next-Day Bridge (5 min)

> "We can now see exactly what the system is doing, at what cost, and when
> it's regressing. Tomorrow we take that cost visibility and make it
> actionable: model calls will be explicitly routed by task class and risk,
> caching will be governed by policy, and the cost of each case will be
> ledgered so we can enforce spending ceilings before they become surprises
> on the monthly bill."
