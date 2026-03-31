# Day 8 — Observability & Reliability Engineering · Trainee Pre-Reading

> **WAF Pillars:** Operational Excellence · Reliability  
> **Time to read:** 25 min  
> **Lab notebook:** `notebooks/day8_observability.py`

---

## Learning Objectives

By the end of Day 8 you will be able to:

1. Explain the three pillars of observability and how they differ.
2. Describe the OpenTelemetry data model: traces, spans, metrics, and logs.
3. Explain why distributed tracing is essential for multi-step AI workflows.
4. Describe how evaluation datasets become regression tests.
5. Write a KQL query to find latency outliers in Azure Monitor.

---

## 1. The Three Pillars of Observability

Observability means being able to understand what is happening inside a system
from its external outputs. The three pillars are:

| Pillar | What it captures | Example |
|---|---|---|
| **Logs** | Discrete events with context | "Invoice INV-3001 routed to review at 14:32:05" |
| **Metrics** | Numeric measurements over time | `workflow_duration_ms{case_class="high_value"} p99=1800` |
| **Traces** | The journey of a request through multiple components | Span tree showing Day 1→2→3→4→6→5 with timings |

A system with only logs cannot answer "how slow is it?" A system with only
metrics cannot answer "why was this specific invoice slow?" Traces answer both.

---

## 2. OpenTelemetry

**OpenTelemetry (OTEL)** is the CNCF standard for distributed telemetry. It
provides a vendor-neutral API and SDK for producing traces, metrics, and logs —
and exporters that forward data to any compliant backend.

### OTEL data model

```
Trace
└── Root Span: "workflow.run"
    ├── Child Span: "day1.extract"  (duration, status, attributes)
    ├── Child Span: "day3.retrieve"
    │   ├── Child Span: "search.query.vendor_policy"
    │   └── Child Span: "search.query.compliance"
    ├── Child Span: "day4.plan"
    │   └── Child Span: "openai.chat.completions"
    ├── Child Span: "day6.review"
    └── Child Span: "day5.checkpoint_write"
```

Each **span** has:
- A `trace_id` (same for all spans in the trace)
- A `span_id` (unique per span)
- A `parent_span_id` (links child to parent)
- `start_time` and `end_time`
- **Attributes** (key-value metadata)
- **Status** (`OK`, `ERROR`)
- **Events** (point-in-time annotations on the span)

### Azure best practice
Use the **Azure Monitor OpenTelemetry Distro** (`azure-monitor-opentelemetry`)
instead of manually configuring exporters. It wires up the OTLP exporter for
Application Insights, propagates trace context through Azure SDK calls, and
enables correlation between Azure infrastructure metrics and application spans.

---

## 3. Correlation IDs

A single business case in AegisAP touches multiple components, potentially
across multiple processes (API server, worker, resume service). **Correlation IDs**
link all of these together:

| ID | Scope | Persisted? |
|---|---|---|
| `trace_id` | OTEL trace — one HTTP request or workflow run | In spans only |
| `workflow_run_id` | One run of the business workflow | In durable state + spans |
| `thread_id` | The resumable business thread (survives multiple runs) | In durable state |
| `case_id` | The invoice/business identity | In all outputs |

In a production incident, you start with a `case_id` from a complaint, find
the `thread_id` in the database, retrieve the `workflow_run_id`, then look up
the `trace_id` to pivot to the full trace in Application Insights.

```kusto
// Find all spans for a specific workflow run
dependencies
| where customDimensions.workflow_run_id == "run-abc-001"
| order by timestamp asc
| project timestamp, name, duration, resultCode, customDimensions
```

---

## 4. Silent Failures in AI Workflows

Silent failures are the most dangerous failure mode for AI systems. The system
appears to be running but is producing degraded output — higher latency, lower
confidence, more escalations — without raising any error.

Common silent failures in AegisAP:

| Failure | Observable symptom | Alert |
|---|---|---|
| LLM latency regression | p99 extraction time > baseline | `duration_ms > 2× rolling average` |
| Retrieval quality drop | More `INSUFFICIENT_EVIDENCE` refusals | `refusal_rate_by_reason` rising above threshold |
| Spurious escalations | `needs_human_review` rate rising | Review rate metric threshold |
| Checkpoint write latency | Resume times growing | `checkpoint_write_ms` p95 alert |

All of these require **metrics**, not just logs.

---

## 5. Evaluation as Regression Testing

Days 3 and 6 produce evaluation scores. Day 8 turns those scores into
**executable regression tests** that run in CI and on a deployed sentinel.

### Evaluation dimensions for AegisAP

| Dimension | What it measures | Target |
|---|---|---|
| **Faithfulness** | Do claims reference retrieved evidence? | ≥ 0.85 |
| **Compliance accuracy** | Are compliance-sensitive decisions correct? | ≥ 0.90 |
| **Mandatory escalation recall** | Are all must-escalate cases escalated? | = 1.0 (zero tolerance) |
| **Refusal precision** | Of refusals, what fraction were correct? | ≥ 0.80 |

### Why mandatory escalation recall must be 1.0

A missed mandatory escalation means a high-risk invoice was processed
automatically when it should have been reviewed. This is the highest-severity
failure mode. Any regression below 1.0 on mandatory escalation recall must
block release.

### Azure best practice
Store evaluation baselines in `data/day8/eval/baseline.json` in source control.
Run evaluation using a **dedicated Azure Container App job** on a schedule (not
on the primary API path). Alert on any score degradation greater than the
threshold defined in `evals/score_thresholds.yaml`.

---

## 6. KQL Fundamentals for AI Workflows

Azure Monitor queries use **Kusto Query Language (KQL)**. Essential patterns:

```kusto
// p99 latency by workflow node
traces
| where customDimensions.span_name startswith "day"
| summarize p99 = percentile(duration, 99) by customDimensions.span_name
| order by p99 desc

// Error rate by case class in the last 24h
exceptions
| where timestamp > ago(24h)
| summarize errors = count() by customDimensions.case_class
| join kind=inner (
    traces | where customDimensions.event == "workflow.started"
    | summarize total = count() by customDimensions.case_class
) on customDimensions.case_class
| project error_rate = errors / total, case_class = customDimensions.case_class
```

---

## Glossary

| Term | Definition |
|---|---|
| **Observability** | The ability to understand internal system state from external outputs: logs, metrics, traces |
| **OpenTelemetry (OTEL)** | CNCF standard for vendor-neutral distributed telemetry |
| **Trace** | A tree of spans representing the end-to-end journey of one request or workflow run |
| **Span** | A named, timed unit of work within a trace, with attributes and status |
| **Correlation ID** | A shared identifier that links related records across multiple systems |
| **Silent failure** | A system degradation that produces no errors but degrades output quality |
| **Evaluation regression** | A change in eval scores that indicates model or system behaviour has degraded |
| **KQL** | Kusto Query Language — the query language for Azure Monitor and Log Analytics |

---

## Check Your Understanding

1. What are the three pillars of observability, and what question does each answer that the others cannot?
2. What is a span, and what is the relationship between `trace_id`, `span_id`, and `parent_span_id`?
3. Why is the `azure-monitor-opentelemetry` distro preferred over manually configuring OTEL exporters?
4. Why does mandatory escalation recall have a target of 1.0, not 0.95?
5. Write a KQL query that shows the count of `not_authorised_to_continue` outcomes per hour over the last 7 days.

---

## Lab Readiness

- **Lab duration:** 2.5 hours
- **Required inputs:** prior-day artifacts, optional Application Insights connection string, and `notebooks/day8_observability.py`
- **Expected artifacts:** `build/day8/regression_baseline.json`, `build/day8/checkpoint_trace_extension.json`

### Pass Criteria

- The notebook writes a usable regression baseline.
- The mandatory checkpoint artifact records the trace extension contract and query.
- You can explain which metric would block Day 10 release and where you would inspect it.

### Common Failure Signals

- A learner treats “no exceptions” as proof that the system is healthy.
- The baseline is overwritten without explaining what changed.
- The trace extension exists only in prose and not in an artifact or queryable attribute.

### Exit Ticket

1. Which metric on Day 8 is zero-tolerance and why?
2. What new span or attribute did the checkpoint add, and where would you query it?
3. What command or notebook step would you use to regenerate the baseline if the artifact was missing?

### Remediation Task

Re-run the notebook and checkpoint flow with:

```bash
marimo edit notebooks/day8_observability.py
```

Then inspect `build/day8/checkpoint_trace_extension.json` and explain how it
proves the trace extension is visible to release review.

### Stretch Task

Design one alert that combines a trace symptom with an eval regression symptom
and explain why that combination is more actionable than either signal alone.
