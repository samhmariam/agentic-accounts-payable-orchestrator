import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _bootstrap():
    import sys
    from pathlib import Path
    _root = Path(__file__).resolve().parents[1]
    for _p in [str(_root / "src"), str(_root / "notebooks"), str(_root)]:
        if _p not in sys.path:
            sys.path.insert(0, _p)
    return


@app.cell
def _imports():
    import marimo as mo
    import json
    import os
    from pathlib import Path
    return json, mo, os, Path


# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------
@app.cell
def _title(mo):
    mo.md("""
    # Day 9 — Scaling, Monitoring & Cost Optimisation

    > **WAF Pillars covered:** Cost Optimisation · Performance Efficiency · Operational Excellence
    > **Estimated time:** 2.5 hours
    > **Sources:** `docs/curriculum/trainee/DAY_08_TRAINEE.md` (observability, OTEL, KQL, eval regression),
    > `docs/curriculum/trainee/DAY_09_TRAINEE.md` (billing models, task routing, cost ledger, semantic caching)
    > **Prerequisites:** Day 8 complete; `build/day8/regression_baseline.json` exists.

    ---

    ## Learning Objectives

    1. Explain the three pillars of observability and which questions each one answers uniquely.
    2. Describe the OpenTelemetry data model: traces, spans, metrics, and logs.
    3. Write KQL queries for diagnosing latency outliers, error rates, and escalation spikes.
    4. Explain how evaluation baselines become regression tests and why slice-level breakdown matters.
    5. Compare Azure OpenAI PAYG and PTU billing models and identify when each is appropriate.
    6. Define task-class routing and explain why routing decisions must be explicit and traceable.
    7. Describe the cost ledger pattern and build a `routing_report.json` artifact for Day 10.
    8. Enumerate the four conditions under which AegisAP bypasses the semantic cache.

    ---

    ## Where Day 9 Sits in the Full Arc

    ```
    Day 7  ── Day 8 ──►[Day 9]──► Day 10
    Testing  CI/CD &   Scaling  Production
    & Safety  IaC      & Cost   Operations
    ```

    Day 9 answers: **"Once AegisAP is deployed, how do we observe what it is doing,
    control what models it uses, and ensure it stays within budget?"**
    The deployment pipeline was proven in Day 8; now we operate it at scale.
    """)
    return


@app.cell
def _full_day_agenda(mo):
    from _shared.curriculum_scaffolds import render_full_day_agenda

    render_full_day_agenda(
        mo,
        day_label="Day 9 observability, scaling, and cost control",
        core_outcome="show how telemetry, routing, and budget controls keep agentic systems operable at enterprise scale",
    )
    return


# ---------------------------------------------------------------------------
# Section 1 – Three Pillars of Observability
# ---------------------------------------------------------------------------
@app.cell
def _s1_header(mo):
    mo.md("## 1. The Three Pillars of Observability")
    return


@app.cell
def _s1_body(mo):
    mo.md("""
    **Observability** means being able to understand what is happening inside a
    running system from its external outputs alone.  Three complementary signal
    types each answer a different question:

    | Pillar | What it captures | The question it answers |
    |---|---|---|
    | **Logs** | Discrete events with context | "What happened, and when?" |
    | **Metrics** | Numeric measurements over time | "How fast, how often, how much?" |
    | **Traces** | End-to-end journey of a request across components | "Why was this specific invoice slow?" |

    No single pillar is sufficient:

    - **Logs only** cannot answer "how slow is it today compared to last Tuesday?"
    - **Metrics only** cannot answer "which exact invoice triggered the p99 regression?"
    - **Traces only** do not alert on sustained error-rate spikes without aggregation.

    A production AI workload needs all three.

    ### Why this matters for AegisAP

    AegisAP's workflow spans at least six processing nodes across two processes
    (API server and resume worker).  A user complaint about "the invoice was slow"
    could be caused by:

    - LLM latency regression (metrics + traces)
    - Retrieval quality drop causing extra reflection loops (traces)
    - A silent failure in checkpoint writing delaying resume (logs + metrics)
    - A cost gate triggering escalation unexpectedly (logs + traces)

    Only a combination of all three pillars narrows the diagnosis to one root cause.

    ### Silent failures — the most dangerous mode

    A silent failure is a system degradation that produces **no errors** but
    degrades output quality.  Common examples in AegisAP:

    | Failure | Observable symptom | Signal type needed |
    |---|---|---|
    | LLM latency regression | p99 extraction time > 2× baseline | Metric |
    | Retrieval quality drop | Rising `INSUFFICIENT_EVIDENCE` refusal rate | Metric + Trace attribute |
    | Spurious escalations | `needs_human_review` rate rising without cause | Metric |
    | Checkpoint write latency | Growing resume times | Metric + Trace |

    Without metrics, none of these produce an alert.  Without traces, none of
    them can be attributed to a specific workflow node.
    """)
    return


@app.cell
def _pillar_explorer(mo):
    _pillar_data = {
        "Logs": {
            "description": "Discrete, structured events with timestamp and context. Best for 'what happened?'",
            "example": '`{"timestamp": "2024-03-26T14:32:05Z", "event": "workflow.node_completed", "node": "day3.retrieve", "case_id": "INV-3001", "duration_ms": 340, "result": "OK"}`',
            "azure_service": "Log Analytics — query with KQL `traces` table",
            "limitation": "Cannot aggregate to answer 'what is p99 latency ACROSS all nodes today?'",
            "aegisap_use": "Audit trail for each workflow node, compliance events, refusal decisions",
        },
        "Metrics": {
            "description": "Numeric measurements sampled over time. Best for 'how often, how fast, how much?'",
            "example": '`workflow_duration_ms{node="day3.retrieve", case_class="high_value"} p99=1800`',
            "azure_service": "Azure Monitor Metrics + App Insights `customMetrics` table",
            "limitation": "Cannot identify WHICH specific invoice caused the p99 spike",
            "aegisap_use": "Latency SLOs, error-rate alerts, cost-per-day dashboards, escalation-rate thresholds",
        },
        "Traces": {
            "description": "A tree of spans representing the complete journey of a single workflow run.",
            "example": '`Root span: workflow.run → child spans: day1.extract, day3.retrieve, day4.plan, day6.review, day5.checkpoint`',
            "azure_service": "App Insights Distributed Tracing blade — `dependencies` + `requests` tables in KQL",
            "limitation": "Requires sampling strategy at high throughput — can't keep every span forever",
            "aegisap_use": "Diagnose which node is slow for a specific invoice, correlate cost ledger entries to spans",
        },
    }

    pillar_picker = mo.ui.radio(
        options=list(_pillar_data.keys()),
        value="Traces",
        label="Explore a pillar:",
    )
    pillar_picker
    return _pillar_data, pillar_picker


@app.cell
def _pillar_detail(mo, _pillar_data, pillar_picker):
    p = _pillar_data[pillar_picker.value]
    mo.callout(
        mo.md(f"""
**{pillar_picker.value}**

{p['description']}

**Example signal:** `{p['example']}`

**Azure service:** {p['azure_service']}

**Limitation (why you need the other pillars too):** {p['limitation']}

**AegisAP use:** {p['aegisap_use']}
        """),
        kind="neutral",
    )
    return


# ---------------------------------------------------------------------------
# Section 2 – OpenTelemetry Data Model
# ---------------------------------------------------------------------------
@app.cell
def _s2_header(mo):
    mo.md("## 2. OpenTelemetry: The CNCF Telemetry Standard")
    return


@app.cell
def _s2_body(mo):
    mo.md("""
    **OpenTelemetry (OTEL)** is the CNCF standard for vendor-neutral distributed
    telemetry.  It provides a unified API and SDK for producing traces, metrics, and
    logs — and exporters that forward data to any compliant backend (Azure Monitor,
    Jaeger, Grafana, etc.) without changing application code.

    ### The OTEL data model

    ```
    Trace
    └── Root Span: "workflow.run"  (trace_id=abc, span_id=001, parent=none)
        ├── Child Span: "day1.extract"          (span_id=002, parent=001)
        ├── Child Span: "day3.retrieve"         (span_id=003, parent=001)
        │   ├── Child Span: "search.vendor_policy"  (span_id=004, parent=003)
        │   └── Child Span: "search.compliance"     (span_id=005, parent=003)
        ├── Child Span: "day4.plan"             (span_id=006, parent=001)
        │   └── Child Span: "openai.chat"       (span_id=007, parent=006)
        ├── Child Span: "day6.review"           (span_id=008, parent=001)
        └── Child Span: "day5.checkpoint_write" (span_id=009, parent=001)
    ```

    Each **span** carries:

    | Field | Type | Description |
    |---|---|---|
    | `trace_id` | 128-bit hex | Same for all spans in one workflow run |
    | `span_id` | 64-bit hex | Unique per span |
    | `parent_span_id` | 64-bit hex | Links child to parent |
    | `start_time` + `end_time` | Timestamps | Duration computed from these |
    | `attributes` | Key-value map | Domain metadata — `aegis.case_id`, `aegis.outcome_type`, etc. |
    | `status` | `OK` / `ERROR` | Whether this span succeeded |
    | `events` | List of timestamped annotations | Point-in-time markers within the span |

    ### Azure Monitor OpenTelemetry Distro

    Use `azure-monitor-opentelemetry` instead of manually wiring the OTEL SDK:

    ```python
    from azure.monitor.opentelemetry import configure_azure_monitor

    configure_azure_monitor(
        connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"],
    )
    # All Azure SDK calls (OpenAI, Search, Storage) now auto-instrument spans
    # Correlation context propagates through HTTP headers automatically
    ```

    **Why the distro, not raw OTEL?**

    - Wires the OTLP exporter to App Insights automatically
    - Propagates W3C `traceparent` headers through Azure SDK calls
    - Correlates infrastructure metrics (CPU, memory) with application spans
    - AegisAP-specific attributes (`aegis.*`) appear in `customDimensions` in KQL

    ### Correlation IDs in AegisAP

    | ID | Scope | Where persisted |
    |---|---|---|
    | `trace_id` | One OTEL trace (one HTTP request or workflow run) | Span context only |
    | `workflow_run_id` | One execution of the business workflow | Durable state + span attributes |
    | `thread_id` | The resumable business thread (survives multiple runs) | Durable state |
    | `case_id` | The invoice business identity | All outputs + audit log |

    Incident response workflow:
    1. Start with `case_id` from a complaint
    2. Look up `thread_id` in the audit log
    3. Find the `workflow_run_id` for the failing run
    4. Look up `trace_id` to pivot to the full distributed trace in App Insights
    """)
    return


# ---------------------------------------------------------------------------
# Section 3 – KQL for AI Workflow Incident Response
# ---------------------------------------------------------------------------
@app.cell
def _s3_header(mo):
    mo.md("## 3. KQL Fundamentals for AI Workflow Incident Response")
    return


@app.cell
def _s3_kql_gallery(mo):
    _kql_queries = {
        "p99 latency by workflow node": {
            "query": """\
traces
| where customDimensions.span_name startswith "day"
| summarize p99 = percentile(duration, 99) by tostring(customDimensions.span_name)
| order by p99 desc""",
            "use_case": "Identify which workflow node is the latency bottleneck. Run in App Insights → Logs.",
            "alert_on": "Any node where `p99 > 2 × rolling 7-day baseline`"
        },
        "Error rate by case class (last 24 h)": {
            "query": """\
exceptions
| where timestamp > ago(24h)
| summarize errors = count() by tostring(customDimensions.case_class)
| join kind=inner (
    traces | where customDimensions.event == "workflow.started"
    | summarize total = count() by tostring(customDimensions.case_class)
) on $left.customDimensions_case_class == $right.customDimensions_case_class
| project case_class = customDimensions_case_class,
          error_rate = todouble(errors) / totalCount""",
            "use_case": "Detect case classes with elevated error rates — useful for incident triage.",
            "alert_on": "Any case class with `error_rate > 0.02` (2%)"
        },
        "Escalation spike detection": {
            "query": """\
traces
| where customDimensions.outcome_type in ("needs_human_review", "not_authorised_to_continue")
| summarize escalations = count() by bin(timestamp, 1h)
| extend rolling_avg = avg(escalations)
    over (order by timestamp asc rows between 24 preceding and current row)
| where escalations > 2 * rolling_avg
| project timestamp, escalations, rolling_avg""",
            "use_case": "Detect when escalation volume rises unexpectedly — could indicate data drift or prompt regression.",
            "alert_on": "Any hour where `escalations > 2 × rolling 24-hour average`"
        },
        "Find all spans for a workflow run": {
            "query": """\
dependencies
| where customDimensions.workflow_run_id == "run-abc-001"
| order by timestamp asc
| project timestamp, name, duration,
          resultCode, customDimensions""",
            "use_case": "Full trace reconstruction for a specific invoice complaint. Start with the `workflow_run_id` from the audit log.",
            "alert_on": "N/A — diagnostic query, not an alert"
        },
        "Mandatory escalation recall regression": {
            "query": """\
customEvents
| where name == "eval.result"
| where customDimensions.metric == "mandatory_escalation_recall"
| summarize latest = max(todouble(customDimensions.value)) by bin(timestamp, 1d)
| where latest < 1.0
| project timestamp, recall = latest""",
            "use_case": "Detect any day where mandatory escalation recall drops below 1.0. Zero-tolerance regression.",
            "alert_on": "`recall < 1.0` — any miss blocks release"
        },
        "Cost per task class (last 7 days)": {
            "query": """\
customEvents
| where name == "cost_ledger.entry"
| where timestamp > ago(7d)
| summarize
    total_cost = sum(todouble(customDimensions.estimated_cost)),
    call_count = count()
  by tostring(customDimensions.task_class)
| order by total_cost desc""",
            "use_case": "Break down model spend by task class to find cost reduction opportunities.",
            "alert_on": "Any task class exceeding its weekly cost ceiling"
        },
    }

    kql_picker = mo.ui.dropdown(
        options=list(_kql_queries.keys()),
        value="p99 latency by workflow node",
        label="Select a KQL pattern:",
    )
    mo.vstack([
        mo.md("Explore the six recurring KQL patterns for AegisAP incident response:"),
        kql_picker,
    ])
    return _kql_queries, kql_picker


@app.cell
def _kql_detail(mo, _kql_queries, kql_picker):
    q = _kql_queries[kql_picker.value]
    mo.vstack([
        mo.md(f"```sql\n{q['query']}\n```"),
        mo.callout(
            mo.md(
                f"**Use case:** {q['use_case']}\n\n**Alert on:** {q['alert_on']}"),
            kind="neutral",
        ),
    ])
    return


# ---------------------------------------------------------------------------
# Section 4 – Evaluation as Regression Testing (Slice-based)
# ---------------------------------------------------------------------------
@app.cell
def _s4_header(mo):
    mo.md("## 4. Evaluation as Regression Testing: Aggregate vs. Slice")
    return


@app.cell
def _s4_body(mo):
    mo.md("""
    Day 8 turned evaluation scores into a baseline.  Day 9 introduces the critical
    nuance: **aggregate scores can hide per-slice regressions**.

    ### Why aggregate evaluation is not enough

    Consider a model update that improves average faithfulness from 0.87 → 0.89.
    That looks like a win.  But broken down by slice:

    | Slice | Before | After | Delta |
    |---|---|---|---|
    | `extraction_standard / auto_approve` | 0.92 | 0.94 | +0.02 ✅ |
    | `planning_low_risk / auto_approve` | 0.88 | 0.91 | +0.03 ✅ |
    | **`review_compliance / high_value`** | **0.91** | **0.83** | **−0.08 ❌** |
    | `extraction_complex / high_risk` | 0.80 | 0.81 | +0.01 ✅ |

    The aggregate improved because three out of four slices improved.  But the
    **most critical slice** — compliance review on high-value invoices — regressed
    significantly.  A pure aggregate evaluation would have shipped this regression.

    ### Why this is catastrophic for AegisAP

    `review_compliance / high_value` is the slice that decides whether a large
    invoice bypasses human review.  A faithfulness drop from 0.91 → 0.83 means
    the model is increasingly making claims that are not grounded in the retrieved
    evidence.  On a high-value invoice, an unsupported claim that "all vendor checks
    passed" is a compliance failure — not just an accuracy metric.

    ### The four evaluation dimensions for AegisAP

    | Dimension | What it measures | Target |
    |---|---|---|
    | **Faithfulness** | Do claims reference retrieved evidence? | ≥ 0.85 |
    | **Compliance accuracy** | Are compliance-sensitive decisions correct? | ≥ 0.90 |
    | **Mandatory escalation recall** | Are ALL must-escalate cases escalated? | = 1.0 (zero tolerance) |
    | **Refusal precision** | Of refusals, what fraction were correct? | ≥ 0.80 |

    Mandatory escalation recall is the only zero-tolerance metric.  Any drop below
    1.0 means a high-risk invoice was processed automatically without human review.
    This is the highest-severity failure mode and always blocks release.

    ### Azure best practice

    Store baselines in `build/day8/regression_baseline.json` in source control.
    Run slice-level evaluation in a dedicated Container App Job on a schedule —
    never on the primary API path.  Alert on any per-slice degradation greater than
    the threshold in `evals/score_thresholds.yaml`.
    """)
    return


@app.cell
def _slice_eval_chart(mo):
    try:
        import plotly.graph_objects as go

        slices = [
            "extraction_standard\nauto_approve",
            "planning_low_risk\nauto_approve",
            "review_compliance\nhigh_value",
            "extraction_complex\nhigh_risk",
        ]
        before = [0.92, 0.88, 0.91, 0.80]
        after = [0.94, 0.91, 0.83, 0.81]
        colors_after = ["#27AE60", "#27AE60", "#E74C3C", "#27AE60"]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Before update",
            x=slices,
            y=before,
            marker_color="#95A5A6",
            opacity=0.7,
        ))
        fig.add_trace(go.Bar(
            name="After update",
            x=slices,
            y=after,
            marker_color=colors_after,
            opacity=0.9,
        ))
        fig.add_hline(
            y=0.85, line_dash="dot", line_color="#E74C3C",
            annotation_text="Faithfulness threshold (0.85)",
            annotation_position="top right",
        )
        fig.update_layout(
            title="Slice-level Faithfulness — Aggregate +0.02 Hides Critical Regression",
            barmode="group",
            yaxis=dict(title="Faithfulness score", range=[0.7, 1.0]),
            height=350,
            margin=dict(t=60, b=20),
            legend=dict(orientation="h", y=-0.15),
        )
        mo.ui.plotly(fig)
    except ImportError:
        mo.callout(
            mo.md("Install `plotly` to see the slice evaluation chart."), kind="warn")
    return


# ---------------------------------------------------------------------------
# Section 5 – Azure OpenAI Billing: PAYG vs PTU
# ---------------------------------------------------------------------------
@app.cell
def _s5_header(mo):
    mo.md("## 5. Azure OpenAI Billing: PAYG vs. PTU")
    return


@app.cell
def _s5_body(mo):
    mo.md("""
    Azure OpenAI offers two fundamentally different billing models.  Choosing
    the wrong one at the wrong traffic level is a significant cost lever.

    | Model | How you pay | Latency | Best for |
    |---|---|---|---|
    | **Pay-as-you-go (PAYG)** | Per token consumed | Variable; may queue at peak | Unpredictable load, development, low volume |
    | **Provisioned Throughput Units (PTU)** | Reserved capacity per hour, regardless of usage | Consistent; bounded queue | Predictable high-throughput production workloads |

    ### Trade-offs in detail

    | Concern | PAYG | PTU |
    |---|---|---|
    | Cost at low utilisation | Low — you pay per token | Fixed and expensive (idle capacity wasted) |
    | Cost at high utilisation | Can spike; may throttle (HTTP 429) | Predictable cap; overflow to PAYG via APIM |
    | Latency consistency | Variable — depends on platform load | Bounded — reservation guarantees throughput |
    | Minimum commitment | None | Monthly or annual commitment |
    | Overflow behaviour | System returns 429 | APIM can spill excess to a PAYG deployment |

    ### AegisAP decision rule

    - Use **PAYG** during development, staging, and the first three months of production.
    - Commit to **PTU** for your highest-traffic task classes once you have a stable
      utilisation baseline (typically Day 4 `plan` calls — the most expensive per token).
    - Configure **APIM** as the gateway so overflow from PTU automatically routes to
      PAYG — never hardcode the endpoint to a specific deployment.

    ### Break-even formula

    If your daily PAYG spend for a task class is $P and the PTU reservation costs
    $R per day, PTU is economical when:

    $$P > R \\times \\text{target utilisation}^{-1}$$

    In practice: PTU breaks even when you can sustain ≥ 60–70% utilisation.
    Below that, PAYG is cheaper.

    > **Monitoring:** Watch the `Utilization` and `Queued Requests` metrics on
    > your PTU deployment.  If utilisation drops below 60% for 30 consecutive days,
    > consider reducing the PTU reservation or reverting to PAYG.
    """)
    return


@app.cell
def _payg_ptu_modeller(mo):
    daily_requests = mo.ui.slider(
        start=100, stop=10000, value=1000, step=100,
        label="Daily inference requests (all task classes)",
    )
    avg_cost_per_call_usd = mo.ui.number(
        start=0.001, stop=0.10, step=0.001, value=0.005,
        label="Average PAYG cost per call (USD)",
    )
    ptu_daily_cost_usd = mo.ui.number(
        start=0.50, stop=200.0, step=0.50, value=12.0,
        label="PTU reservation cost per day (USD)",
    )
    mo.vstack([
        mo.md("### PAYG vs. PTU Break-Even Calculator"),
        mo.md("Adjust the sliders to model your workload:"),
        daily_requests,
        avg_cost_per_call_usd,
        ptu_daily_cost_usd,
    ])
    return avg_cost_per_call_usd, daily_requests, ptu_daily_cost_usd


@app.cell
def _payg_ptu_chart(mo, avg_cost_per_call_usd, daily_requests, ptu_daily_cost_usd):
    try:
        import plotly.graph_objects as go

        # Compute PAYG cost across a range of request volumes
        max_requests = max(daily_requests.value * 3, 3000)
        volumes = list(range(100, max_requests + 1,
                       max(50, max_requests // 60)))
        payg_costs = [v * avg_cost_per_call_usd.value for v in volumes]
        ptu_costs = [ptu_daily_cost_usd.value] * len(volumes)

        # Find break-even point
        breakeven_volume: int | None = None
        for v, p in zip(volumes, payg_costs):
            if p >= ptu_daily_cost_usd.value:
                breakeven_volume = v
                break

        current_payg = daily_requests.value * avg_cost_per_call_usd.value
        recommendation = (
            "PTU is economical at your current request volume."
            if current_payg >= ptu_daily_cost_usd.value
            else f"PAYG is cheaper at {daily_requests.value} requests/day. "
            f"PTU breaks even at ~{breakeven_volume or '> ' + str(max_requests)} requests/day."
        )

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=volumes, y=payg_costs, name="PAYG daily cost",
            mode="lines", line=dict(color="#3498DB", width=2),
        ))
        fig.add_trace(go.Scatter(
            x=volumes, y=ptu_costs, name="PTU daily cost (reservation)",
            mode="lines", line=dict(color="#E74C3C", width=2, dash="dash"),
        ))
        # Mark current volume
        fig.add_vline(
            x=daily_requests.value, line_dash="dot", line_color="#27AE60",
            annotation_text=f"Current: {daily_requests.value} req/day",
            annotation_position="top right",
        )
        fig.update_layout(
            title="PAYG vs. PTU Break-Even Curve",
            xaxis=dict(title="Daily requests"),
            yaxis=dict(title="Daily cost (USD)"),
            height=320,
            margin=dict(t=60, b=20),
            legend=dict(orientation="h", y=-0.2),
        )
        mo.vstack([
            mo.ui.plotly(fig),
            mo.callout(
                mo.md(f"**Recommendation:** {recommendation}"),
                kind="success" if current_payg >= ptu_daily_cost_usd.value else "neutral",
            ),
        ])
    except ImportError:
        mo.callout(
            mo.md("Install `plotly` to see the break-even chart."), kind="warn")
    return


# ---------------------------------------------------------------------------
# Section 6 – Task-Class Routing
# ---------------------------------------------------------------------------
@app.cell
def _s6_header(mo):
    mo.md("## 6. Task-Class-Aware Model Routing")
    return


@app.cell
def _s6_body(mo):
    mo.md("""
    Not every LLM call needs the same model.  AegisAP defines **task classes** —
    named categories of model invocation with defined capability and latency
    requirements — and routes each one to the appropriate tier.

    ### AegisAP task classes

    | Task class | Example use | Default tier | Cache allowed? |
    |---|---|---|---|
    | `extract` | Day 1 invoice extraction, standard OCR | Light (`gpt-4.1-mini`) | Yes (when cache enabled) |
    | `extract` + risk flags | Day 1 with `high_value`/`missing_po` escalators | Escalated to Strong | No |
    | `retrieve_summarise` | Day 3 RAG summary | Light | Yes (TTL capped) |
    | `plan` | Day 4 planning — all cases | **Always Strong** (`gpt-4.1`) | No |
    | `compliance_review` | Day 6 policy review | Always Strong | **Never** |
    | `reflection` | Day 6 bounded reflection | Always Strong | No |
    | `final_render` | Final audit output assembly | Light (Strong if sensitive) | Yes (unless sensitive) |

    ### Why routing must be explicit

    Implicit routing ("just always use the best model") produces:

    - **Unnecessary cost** — gpt-4.1 on a simple extraction costs 10–20× more per
      token than gpt-4.1-mini with no quality benefit
    - **No observability** — you cannot attribute cost to specific decisions
    - **No A/B control** — you cannot safely experiment with model tiers without
      touching every task at once

    Explicit routing produces:
    - Traceable routing decisions in every span (`aegis.task_class`, `aegis.deployment_tier`)
    - Cost attribution by task class and case class
    - Safe experiments: swap `extract` tier without touching `compliance_review`

    > **Implementation note:** `plan`, `reflection`, and `compliance_review` always
    > default to the strong tier regardless of risk flags. Risk flags escalate
    > light-tier tasks (e.g. `extract`) to strong; they do not change already-strong tasks.

    ### How `route_task` works

    ```python
    from aegisap.routing.routing_policy import route_task

    # extract with risk flag → escalated to strong
    decision = route_task(
        task_class="extract",
        risk_flags=["high_value", "missing_po"],
    )
    # decision.deployment_tier == "strong"
    # decision.cache_allowed  == False
    # decision.reason         == "risk_escalator_selected_strong_model"

    # plan → always strong (no risk flags needed)
    decision2 = route_task(task_class="plan")
    # decision2.deployment_tier == "strong"
    ```

    The decision is recorded in the span attributes so every KQL query can filter
    by which tier handled which decision.
    """)
    return


@app.cell
def _routing_lab(mo):
    from aegisap.routing.routing_policy import route_task, TaskClass

    _task_options: list[str] = [
        "extract", "classify", "retrieve_summarise",
        "plan", "compliance_review", "reflection", "final_render",
    ]
    _risk_options = [
        "high_value", "missing_po", "bank_details_changed",
        "new_vendor", "cross_border_tax", "reflection_triggered",
    ]

    task_picker = mo.ui.dropdown(
        options=_task_options,
        value="extract",
        label="Task class",
    )
    risk_picker = mo.ui.multiselect(
        options=_risk_options,
        value=[],
        label="Risk flags (optional)",
    )
    mo.vstack([
        mo.md("### Interactive Routing Decision Explorer"),
        mo.md(
            "Select a task class and optional risk flags to see how `route_task` "
            "decides which model deployment to use:"
        ),
        task_picker,
        risk_picker,
    ])
    return TaskClass, risk_picker, route_task, task_picker


@app.cell
def _routing_result(mo, risk_picker, route_task, task_picker):
    decision = route_task(
        task_class=task_picker.value,
        risk_flags=list(risk_picker.value),
    )
    tier_kind = "success" if decision.deployment_tier == "light" else "warn"
    cache_kind = "success" if decision.cache_allowed else "danger"

    mo.vstack([
        mo.hstack([
            mo.stat(label="Deployment", value=decision.deployment_name),
            mo.stat(label="Tier", value=decision.deployment_tier),
            mo.stat(label="Cache allowed",
                    value="Yes" if decision.cache_allowed else "No"),
            mo.stat(label="Max retries", value=str(decision.max_retries)),
        ]),
        mo.callout(
            mo.md(f"**Routing reason:** {decision.reason}"), kind=tier_kind),
        mo.callout(
            mo.md(
                "Cache is allowed for this routing decision. PAYG cost reduced on repeat queries."
                if decision.cache_allowed else
                "Cache is **bypassed** for this task class and/or risk profile. Always uses fresh model inference."
            ),
            kind=cache_kind,
        ),
    ])
    return (decision,)


# ---------------------------------------------------------------------------
# Section 7 – Cost Ledger
# ---------------------------------------------------------------------------
@app.cell
def _s7_header(mo):
    mo.md("## 7. The Cost Ledger Pattern")
    return


@app.cell
def _s7_body(mo):
    mo.md("""
    Every successful model call writes a **cost ledger entry** — a durable, queryable
    record of what was called, what it cost, and whether the cache was hit.

    ### Ledger entry schema

    ```json
    {
      "entry_id":           "ledger-abc-001",
      "thread_id":          "thread-inv-3001",
      "workflow_run_id":    "run-xyz-789",
      "task_class":         "planning_high_risk",
      "model_deployment":   "gpt-4.1",
      "prompt_tokens":      1240,
      "completion_tokens":  312,
      "total_tokens":       1552,
      "estimated_cost":     0.004725,
      "cache_hit":          false,
      "created_at":         "2024-03-26T14:32:00Z"
    }
    ```

    The field `estimated_cost` uses token-rate approximations:
    - Light tier (`gpt-4.1-mini`): ~$0.15/1M input tokens, ~$0.60/1M output tokens
    - Strong tier (`gpt-4.1`): ~$2.00/1M input tokens, ~$8.00/1M output tokens

    ### What the ledger answers

    | Question | KQL / query |
    |---|---|
    | Average cost per invoice class | Group by `case_class`, sum `estimated_cost` |
    | Monthly cache savings | Sum `estimated_cost` where `cache_hit = true` |
    | Which task class is most expensive? | Group by `task_class`, sum `estimated_cost` |
    | Is `planning_high_risk` exceeding its ceiling? | Filter `task_class = planning_high_risk`, sum vs. ceiling |

    ### Cost gate

    If `accumulated_cost` for a single workflow run exceeds the per-run ceiling,
    AegisAP emits a **cost gate exception** and escalates to human review.

    | Case class | Per-run ceiling |
    |---|---|
    | Standard | $0.10 |
    | High-value | $0.25 |

    This prevents runaway spending from model loops, infinite retries, or
    unexpectedly expensive plans.
    """)
    return


@app.cell
def _ledger_simulator(mo):
    _task_classes = [
        "extract",
        "retrieve_summarise",
        "plan",
        "compliance_review",
        "reflection",
    ]
    volume_slider = mo.ui.slider(
        start=1, stop=50, value=10, step=1,
        label="Invoices per hour to simulate",
    )
    cache_rate_slider = mo.ui.slider(
        start=0, stop=80, value=30, step=5,
        label="Cache hit rate on cacheable tasks (%)",
    )
    mo.vstack([
        mo.md("### Cost Ledger Simulator"),
        mo.md("Simulate a batch of invoice executions and see how the ledger builds up:"),
        volume_slider,
        cache_rate_slider,
    ])
    return _task_classes, cache_rate_slider, volume_slider


@app.cell
def _ledger_display(mo, cache_rate_slider, volume_slider):
    import math as _math

    # Representative per-call token and cost model
    _call_specs = {
        "extract":            {"prompt": 420, "completion": 180, "tier": "light",  "cacheable": True},
        "retrieve_summarise": {"prompt": 560, "completion": 210, "tier": "light",  "cacheable": True},
        "plan":               {"prompt": 780, "completion": 250, "tier": "strong", "cacheable": False},
        "compliance_review":  {"prompt": 1240, "completion": 312, "tier": "strong", "cacheable": False},
        "reflection":         {"prompt": 640, "completion": 190, "tier": "strong", "cacheable": False},
    }
    _light_in = 0.00015   # $0.15 / 1M
    _light_out = 0.00060   # $0.60 / 1M
    _strong_in = 0.00200   # $2.00 / 1M
    _strong_out = 0.00800  # $8.00 / 1M

    def _call_cost(spec: dict) -> float:
        if spec["tier"] == "light":
            return round(spec["prompt"] / 1000 * _light_in + spec["completion"] / 1000 * _light_out, 6)
        return round(spec["prompt"] / 1000 * _strong_in + spec["completion"] / 1000 * _strong_out, 6)

    rate = cache_rate_slider.value / 100.0
    rows = []
    total = 0.0
    cache_savings = 0.0

    for _task, _spec in _call_specs.items():
        full_cost = _call_cost(_spec)
        n = volume_slider.value
        n_cache_hit = _math.floor(n * rate) if _spec["cacheable"] else 0
        n_miss = n - n_cache_hit
        cost_this_class = full_cost * n_miss  # cache hits have zero cost
        savings_this_class = full_cost * n_cache_hit
        rows.append({
            "Task class": _task,
            "Tier": _spec["tier"],
            "Calls": n,
            "Cache hits": n_cache_hit,
            "Cost per call ($)": f"{full_cost:.6f}",
            "Total cost ($)": f"{cost_this_class:.4f}",
        })
        total += cost_this_class
        cache_savings += savings_this_class

    total_with_no_cache = sum(_call_cost(
        s) * volume_slider.value for s in _call_specs.values())

    mo.vstack([
        mo.table(rows, selection=None),
        mo.hstack([
            mo.stat(label="Total cost (with cache)", value=f"${total:.4f}"),
            mo.stat(label="Without cache",
                    value=f"${total_with_no_cache:.4f}"),
            mo.stat(label="Cache savings", value=f"${cache_savings:.4f}"),
            mo.stat(label="Savings %",
                    value=f"{100 * cache_savings / max(total_with_no_cache, 1e-9):.0f}%"),
        ]),
    ])
    return cache_savings, rows, total, total_with_no_cache


@app.cell
def _waf_anchor_s7(mo):
    mo.callout(
        mo.md("""
**WAF Anchor — Cost Optimization Pillar**

The cost ledger pattern in this section directly satisfies the
**Cost per invoice** NFR set in Day 2:

> *Cost per invoice < £0.10 (token cost + infrastructure amortised)*

The ledger makes costs observable at the task-class level — not just as a
monthly Azure bill. This granularity is what enables the Day 10 `budget` gate:
the gate reads `routing_report.json` and fails the release if the projected
daily cost exceeds the ceiling *before any code reaches production*.

**The Day 2 scoping decision that enables this:** Multi-model routing was deferred
from MVP precisely because "you cannot optimise without a baseline." The cost ledger
*is* the baseline. You cannot set a task-class routing policy without knowing which
task class is most expensive — and you cannot know that without measuring it first.

**WAF Cost Optimization principle in practice:** The per-invoice cost target (£0.10)
is not a loose guideline. It is a measurable, gate-enforced constraint with a
daily alert that fires *before* the problem appears on the finance dashboard.
        """),
        kind="neutral",
    )
    return


# ---------------------------------------------------------------------------
# Section 8 – Semantic Cache Bypass Policy
# ---------------------------------------------------------------------------
@app.cell
def _s8_header(mo):
    mo.md("## 8. Semantic Cache Bypass Policy")
    return


@app.cell
def _s8_body(mo):
    mo.md("""
    **Semantic caching** stores LLM responses and reuses them when a new request
    is semantically similar enough (cosine similarity ≥ threshold).

    ```
    New request embedding
        │
        ▼
    [ Cache lookup ] ──── cosine similarity score ────►
        │
        ├── score ≥ threshold  →  return cached response (no LLM call)
        │
        └── score < threshold  →  call LLM, store result in cache
    ```

    ### Benefits and risks

    | Benefit | Risk |
    |---|---|
    | Reduces PAYG token cost on repetitive queries | Stale cache may return outdated policy answers |
    | Reduces p99 latency on cache hits | Semantically similar ≠ actually equivalent |
    | Predictable cost on high-repetition workloads | Compliance decisions must never be served from cache |

    ### AegisAP's four cache bypass conditions

    | Condition | Why bypass the cache |
    |---|---|
    | Task class is `compliance_review` | Policy compliance decisions must always use current context and the full evidence set |
    | Evidence freshness flag is set | Retrieved documents may have changed since the cache entry was created |
    | Case risk score is HIGH | High-risk cases require fresh model inference — slight semantic drift is not acceptable |
    | Cache TTL has expired | All cache entries have a configurable TTL; after expiry the entry is treated as a miss |

    ### Azure best practice

    Use **Azure Cache for Redis** as the cache backend if deploying with multiple
    Container App replicas.  In-memory caches:
    - Do not survive process restarts
    - Are not shared across replicas — each replica has its own cold cache
    - Cannot be invalidated centrally when policy documents change

    Redis solves all three problems.
    """)
    return


@app.cell
def _cache_bypass_explorer(mo):
    task_class_cache = mo.ui.dropdown(
        options=["extract", "retrieve_summarise",
                 "plan", "compliance_review", "reflection"],
        value="compliance_review",
        label="Task class",
    )
    evidence_freshness = mo.ui.checkbox(
        label="Evidence freshness flag set?", value=False)
    high_risk = mo.ui.checkbox(label="Case risk score is HIGH?", value=False)
    ttl_expired = mo.ui.checkbox(label="Cache TTL expired?", value=False)

    mo.vstack([
        mo.md("### Cache Bypass Decision Explorer"),
        mo.md("Adjust the conditions to see whether AegisAP bypasses the semantic cache:"),
        task_class_cache,
        evidence_freshness,
        high_risk,
        ttl_expired,
    ])
    return evidence_freshness, high_risk, task_class_cache, ttl_expired


@app.cell
def _cache_bypass_result(mo, evidence_freshness, high_risk, task_class_cache, ttl_expired):
    _bypass_reasons = []
    if task_class_cache.value == "compliance_review":
        _bypass_reasons.append(
            "Task class is `compliance_review` — compliance decisions must never be cached")
    if evidence_freshness.value:
        _bypass_reasons.append(
            "Evidence freshness flag is set — retrieved documents may have changed")
    if high_risk.value:
        _bypass_reasons.append(
            "Case risk score is HIGH — fresh inference required")
    if ttl_expired.value:
        _bypass_reasons.append(
            "Cache TTL has expired — entry treated as a miss")

    if _bypass_reasons:
        mo.callout(
            mo.md(
                "**Cache bypassed.** Fresh LLM inference will be requested.\n\n"
                + "\n".join(f"- {r}" for r in _bypass_reasons)
            ),
            kind="danger",
        )
    else:
        mo.callout(
            mo.md(
                "**Cache eligible.** If a semantically similar entry exists "
                "and similarity ≥ threshold, the cached response will be returned."
            ),
            kind="success",
        )
    return (_bypass_reasons,)


# ---------------------------------------------------------------------------
# Section 9 – ACA Auto-Scaling
# ---------------------------------------------------------------------------
@app.cell
def _s9_header(mo):
    mo.md("## 9. ACA Auto-Scaling for AI Workloads")
    return


@app.cell
def _s9_body(mo):
    mo.md("""
    Azure Container Apps scales replicas based on **scaling rules** — triggers
    that define conditions for adding or removing instances.

    ### Scaling rule types relevant to AegisAP

    | Rule type | Trigger | AegisAP use |
    |---|---|---|
    | **HTTP concurrency** | Active HTTP requests per replica | API server: scale on request queue depth |
    | **Azure Queue** | Messages in a Storage Queue | Worker: scale on pending workflow jobs |
    | **Custom KEDA** | Any external metric via KEDA | Cost-aware: scale-down when budget headroom is low |
    | **CPU / Memory** | Resource utilisation % | Fallback; not recommended as primary trigger for AI workloads |

    ### Recommended AegisAP scaling configuration

    ```yaml
    # containerapp.yaml excerpt
    scale:
      minReplicas: 1
      maxReplicas: 10
      rules:
        - name: http-scaling
          http:
            metadata:
              concurrentRequests: "10"  # scale-out trigger per replica

        - name: queue-scaling
          azureQueue:
            queueName: aegisap-jobs
            queueLength: "5"            # 1 new replica per 5 pending jobs
            auth:
              - secretRef: storage-connection-string
                triggerParameter: connection
    ```

    ### Cost-aware scaling

    ACA is billed per replica-second.  An idle replica in a non-PTU workload
    still costs money but produces no token throughput.

    Best practices:
    - Set `minReplicas: 0` for jobs (eval runs, index ingestion) — zero cost at rest
    - Set `minReplicas: 1` for the API server — avoids cold-start latency on the first request
    - Use a **scale-down stabilisation window** (KEDA default: 5 minutes) to avoid
      thrashing during bursty invoice ingestion

    ### Interaction with PTU

    If you have a PTU reservation and too many replicas, each replica will compete
    for the same throughput budget.  The optimal replica count for a PTU deployment is:

    $$\\text{replicas} = \\left\\lceil \\frac{\\text{PTU capacity (tokens/min)}}{\\text{max tokens/min per replica}} \\right\\rceil$$

    Exceeding this causes queuing at the PTU layer, and under-supplying it wastes
    the reservation.  Monitor `Utilization` on the PTU deployment alongside ACA replica count.
    """)
    return


# ---------------------------------------------------------------------------
# Lab Exercises
# ---------------------------------------------------------------------------
@app.cell
def _exercises_header(mo):
    mo.md("## Exercises")
    return


@app.cell
def _exercise_1(mo):
    mo.accordion({
        "Exercise 1 — Write a KQL Query for Escalation Pattern Detection": mo.vstack([
            mo.md("""
**Task:**

Write a KQL query that:

1. Counts `needs_human_review` outcomes **per vendor** (use `customDimensions.vendor_id`)
   over the last 7 days.
2. Computes a rolling 7-day baseline per vendor.
3. Flags any vendor whose current-day escalation count is more than **2× their baseline**.
4. Orders results by the highest escalation ratio first.

This pattern is useful for detecting a data-quality degradation specific to one
vendor (e.g., a new OCR system upstream that produces noisy invoices).
            """),
            mo.accordion({
                "Show solution": mo.md(r"""
```sql
let baseline_window = ago(7d);
let alert_day = startofday(now());

// Compute per-vendor daily escalation counts for the past 7 days
let daily_escalations = traces
    | where timestamp between(baseline_window .. now())
    | where customDimensions.outcome_type == "needs_human_review"
    | summarize escalations = count()
      by vendor_id = tostring(customDimensions.vendor_id),
         day = startofday(timestamp);

// Baseline: average over the 6 days BEFORE today
let baseline = daily_escalations
    | where day < alert_day
    | summarize baseline_avg = avg(escalations) by vendor_id;

// Today's counts
let today = daily_escalations
    | where day == alert_day
    | project vendor_id, today_count = escalations;

// Join and flag
today
| join kind=inner baseline on vendor_id
| extend ratio = todouble(today_count) / max_of(baseline_avg, 1.0)
| where ratio > 2.0
| order by ratio desc
| project vendor_id, today_count, baseline_avg = round(baseline_avg, 1), ratio = round(ratio, 2)
```

**Key techniques used:**

- `startofday()` — bucket timestamps into calendar days for fair comparison
- `let` KQL variables — split complex logic into readable segments
- `max_of(baseline_avg, 1.0)` — prevent division by zero for new vendors
- `between(start .. end)` — efficient time-range filter
- `join kind=inner` — only vendors present in BOTH the baseline and today trigger the alert

**Alert integration:** Schedule this query every hour as an Azure Monitor alert rule.
Set a threshold of > 0 rows (any flagged vendor) to trigger a PagerDuty notification
for the FDE on-call rotation.
                """),
            }),
        ]),
    })
    return


@app.cell
def _exercise_2(mo):
    mo.accordion({
        "Exercise 2 — Design Routing Thresholds for a New Task Class": mo.vstack([
            mo.md("""
**Scenario:**

The AegisAP product team wants to add a new task class: `regulatory_lookup`.
It will query an external regulatory database from within the Day 6 review node
to verify that a vendor is listed on the approved-supplier register.

**Requirements:**
- The query is straightforward text lookup — low OCR noise, structured input
- The regulatory database changes quarterly — embeddings can be cached with a 90-day TTL
- The risk profile is HIGH for all cases — a missed de-listing is a compliance incident
- Expected volume: ~80% of high-value invoices (approximately 200/day at current load)

**Task:**

1. Which model tier (`light` or `strong`) should `regulatory_lookup` use by default?
2. Should the cache be allowed? If yes, with what TTL policy?
3. Write the routing decision logic (pseudocode or Python) that would extend
   `route_task` in `routing_policy.py` to handle this new task class.
4. What new KQL query would you add to monitor `regulatory_lookup` costs?
            """),
            mo.accordion({
                "Show solution": mo.md(r"""
**1. Model tier:**

`light` (`gpt-4.1-mini`) as the default. The regulatory lookup task is:
- Structured input (approved-supplier register — tabular data)
- Low noise (official database, not OCR output)
- Binary outcome (listed / not listed) — does not require complex reasoning

`strong` is escalated only if `has_escalator` is True (e.g., `bank_details_changed`
combined with a new vendor who is near-match on the register).

**2. Cache policy:**

Cache IS allowed, with a 90-day TTL. Justification:
- The regulatory database changes quarterly — a 90-day TTL ensures cache entries
  don't outlive a database update cycle
- The risk score is HIGH, but the lookup result is deterministic for a given vendor+date;
  caching the binary "listed: true" answer is safe
- Cache bypass is STILL triggered if `evidence_freshness_flag` is set, which the
  workflow sets when a new register publication date is detected

**3. Routing logic extension:**

```python
# In routing_policy.py, extend the TaskClass Literal:
TaskClass = Literal[
    "extract", "classify", "retrieve_summarise", "plan",
    "compliance_review", "reflection", "final_render",
    "regulatory_lookup",   # ← new
]

# In route_task(), add handling before the general light/strong split:
if task_class == "regulatory_lookup":
    # Regulatory lookup: light by default, but escalate on vendor risk flags
    regulatory_escalators = {"new_vendor",
        "bank_details_changed", "cross_border_tax"}
    if bool(regulatory_escalators.intersection(risk_flags)):
        tier = "strong"
        reason = f"regulatory_lookup escalated to strong: risk_flags={sorted(risk_flags)}"
    else:
        tier = "light"
        reason = "regulatory_lookup: structured lookup, light tier"

    deployment = (
        active_policy.strong_model_deployment if tier == "strong"
        else active_policy.light_model_deployment
    )
    # TTL enforcement done in cache layer
    cache_allowed = active_policy.cache_allowed
    return ModelRouteDecision(
        task_class=task_class,
        deployment_name=deployment,
        deployment_tier=tier,
        cache_allowed=cache_allowed,
        cache_mode="semantic",
        max_retries=2,
        timeout_budget_ms=4_000,
        fallback_model_deployment=active_policy.fallback_model_deployment,
        reason=reason,
        risk_flags=risk_flags,
    )
```

**4. KQL monitoring query:**

```sql
customEvents
| where name == "cost_ledger.entry"
| where customDimensions.task_class == "regulatory_lookup"
| summarize
    calls = count(),
    cache_hits = countif(tobool(customDimensions.cache_hit) == true),
    total_cost = sum(todouble(customDimensions.estimated_cost))
  by bin(timestamp, 1d)
| extend cache_hit_rate = todouble(cache_hits) / calls
| order by timestamp desc
```

Alert: if `total_cost > 0.50` in a single day (200 calls × $0.0025 average), the
90-day TTL may need reducing (more cache misses than expected — database may be
updating more frequently).
                """),
            }),
        ]),
    })
    return


@app.cell
def _exercise_3(mo):
    mo.accordion({
        "Exercise 3 — Calculate the PTU Break-Even Point": mo.vstack([
            mo.md("""
**Scenario:**

AegisAP handles:
- 800 `extract` calls/day at average 600 tokens each → light tier at $0.15/$0.60 per 1M tokens
- 500 `plan` calls/day at average 1000 tokens each → light tier at $0.15/$0.60 per 1M tokens
- 300 `compliance_review` calls/day at average 1560 tokens each → strong tier at $2.00/$8.00 per 1M tokens

A PTU reservation for the strong tier costs **$18/day** and supports throughput of
up to 800 strong-tier calls/day.

**Task:**

1. Calculate the current daily PAYG cost for each task class (assume 60% of tokens are prompt, 40% completion).
2. Calculate the total daily PAYG cost.
3. At what daily volume of `compliance_review` calls does PTU break even?
4. Is the current volume above or below break-even?
            """),
            mo.accordion({
                "Show solution": mo.md(r"""
**Token split assumption:** 60% prompt, 40% completion.

**1. Per-task-class PAYG cost:**

`extract` (light tier, $0.15/$0.60 per 1M):
- 800 calls × 600 tokens = 480,000 tokens/day
- Prompt: 480,000 × 0.60 × $0.15/1M = $0.043
- Completion: 480,000 × 0.40 × $0.60/1M = $0.115
- **Daily cost: $0.158**

`plan` (light tier):
- 500 calls × 1,000 tokens = 500,000 tokens/day
- Prompt: 500,000 × 0.60 × $0.15/1M = $0.045
- Completion: 500,000 × 0.40 × $0.60/1M = $0.120
- **Daily cost: $0.165**

`compliance_review` (strong tier, $2.00/$8.00 per 1M):
- 300 calls × 1,560 tokens = 468,000 tokens/day
- Prompt: 468,000 × 0.60 × $2.00/1M = $0.562
- Completion: 468,000 × 0.40 × $8.00/1M = $1.498
- **Daily cost: $2.059**

**2. Total daily PAYG cost:**

$0.158 + $0.165 + $2.059 = **$2.382/day**

**3. Break-even volume for `compliance_review`:**

Cost per `compliance_review` call (PAYG): $2.059 / 300 = $0.00686/call

PTU break-even: $18.00 / $0.00686 = **~2,625 calls/day**

**4. Current volume assessment:**

Current: 300 calls/day.  Break-even: 2,625 calls/day.
The current volume is **far below break-even** — PTU is 7.5× more expensive
than PAYG at current load.

**Recommendation:**

Continue on PAYG.  Revisit when `compliance_review` volume exceeds ~2,600/day
(possible if AegisAP is deployed to more business units or invoice volume grows ~8×).

Note: if latency consistency is required (SLA for compliance review < 2s p99),
PTU may be justified before the cost break-even — write the SLA requirement
explicitly in the architecture decision record.
                """),
            }),
        ]),
    })
    return


@app.cell
def _exercise_4(mo):
    mo.accordion({
        "Exercise 4 — Implement Cost-Aware Cache Bypass Logic": mo.vstack([
            mo.md("""
**Scenario:**

The team wants to add a fifth cache bypass condition: if the accumulated cost
for the current workflow run already exceeds 80% of the per-run ceiling, bypass
the cache — even on cacheable task classes.

The reasoning: if a run is already expensive, it is likely unusual (complex case,
multiple reflection loops). Serving a cached answer for an unusual case increases
the risk of a stale or inappropriate cached response.

**Task:**

1. Where in the AegisAP codebase would you add this check?
2. Write the Python logic (as a function or a conditional block) that implements it.
3. What span attribute would you emit to make this bypass visible in KQL?
4. Would you apply this rule to `compliance_review`? Why or why not?
            """),
            mo.accordion({
                "Show solution": mo.md(r"""
**1. Where to add the check:**

The check belongs in the **model gateway layer** — specifically in
`src/aegisap/routing/model_router.py` inside the `ModelGateway` class,
in the method that builds the `ModelInvocationRequest` before dispatching.

The gateway already has access to the `CostLedger` (its accumulated entries for
the current run) and the routing decision object. It is the right place to
override `cache_allowed` based on runtime cost context.

**2. Implementation:**

```python
from aegisap.cost.budget_gate import check_budget

# Inside ModelGateway.invoke() or build_request():
def _should_bypass_cache_for_cost_risk(
    ledger: list[dict],
    routing_decision: ModelRouteDecision,
    per_run_ceiling_usd: float,
    bypass_threshold_fraction: float = 0.80,
) -> tuple[bool, str]:
    # Returns (bypass_cache, reason_string).
    if not routing_decision.cache_allowed:
        return False, ""  # Already bypassed by routing logic

    # Compute the accumulated cost so far in this run
    accumulated=sum(float(row.get("estimated_cost", 0.0)) for row in ledger)
    threshold=per_run_ceiling_usd * bypass_threshold_fraction

    if accumulated >= threshold:
        return True, (
            f"cost_risk_bypass: accumulated=${accumulated:.4f} "
            f">= {bypass_threshold_fraction:.0%} of ceiling=${per_run_ceiling_usd:.2f}"
        )
    return False, ""
```

Usage inside the gateway:

```python
bypass, bypass_reason=_should_bypass_cache_for_cost_risk(
    ledger=self._current_run_ledger,
    routing_decision=decision,
    per_run_ceiling_usd=self._per_run_ceiling_usd,
)
if bypass:
    decision=replace(decision, cache_allowed=False)  # dataclasses.replace()
    # The bypass_reason will be logged to the span
```

**3. Span attribute: **

```python
span.set_attribute("aegis.cache_bypass_reason", bypass_reason or "none")
span.set_attribute("aegis.cache_allowed_final", str(not bypass))
```

KQL query to find cost-risk bypasses:

```sql
traces
| where customDimensions["aegis.cache_bypass_reason"] startswith "cost_risk_bypass"
| summarize count() by bin(timestamp, 1h)
| order by timestamp desc
```

A spike here means cases are regularly reaching 80 % of the cost ceiling, which
is itself a signal worth alerting on — it suggests model loops or unusually complex invoices.

**4. Compliance_review: **

No — do NOT apply this rule to `compliance_review`. The reason:

`compliance_review` already has `cache_allowed=False` from the routing policy.
This rule is intended as an additional safety net for task classes that are
normally cacheable(`extract`, `retrieve_summarise`). Applying it to a task class
that is already hard-bypassed adds no value and creates misleading span attributes
("cache_risk_bypass" on a span that would never have used the cache anyway).

Keep bypass logic single-responsibility: routing policy handles task-class -level
bypass; the cost-risk check handles run-level bypass only for cacheable tasks.
                """),
            }),
        ]),
    })
    return


# ---------------------------------------------------------------------------
# Artifact — routing_report.json
# ---------------------------------------------------------------------------
@app.cell
def _artifact_write(mo, json, Path):
    import datetime as _dt
    import os
    from aegisap.cost.budget_gate import check_budget as _check_budget

    # Build a representative sample ledger for the Day 10 budget gate.
    # Each entry must contain 'estimated_cost' (field read by check_budget).
    _sample_ledger = [
        {
            "task_class": "extract",
            "model_deployment": "gpt-4.1-mini",
            "deployment_tier": "light",
            "prompt_tokens": 420,
            "completion_tokens": 180,
            "total_tokens": 600,
            "cache_hit": False,
            "estimated_cost": round(420 / 1_000_000 * 0.15 + 180 / 1_000_000 * 0.60, 6),
        },
        {
            "task_class": "retrieve_summarise",
            "model_deployment": "gpt-4.1-mini",
            "deployment_tier": "light",
            "prompt_tokens": 560,
            "completion_tokens": 210,
            "total_tokens": 770,
            "cache_hit": True,
            "estimated_cost": 0.0,  # Cache hit — no cost
        },
        {
            "task_class": "plan",
            "model_deployment": "gpt-4.1",
            "deployment_tier": "strong",  # plan always defaults to strong tier
            "prompt_tokens": 780,
            "completion_tokens": 250,
            "total_tokens": 1030,
            "cache_hit": False,
            "estimated_cost": round(780 / 1_000_000 * 2.00 + 250 / 1_000_000 * 8.00, 6),
        },
        {
            "task_class": "compliance_review",
            "model_deployment": "gpt-4.1",
            "deployment_tier": "strong",
            "prompt_tokens": 1240,
            "completion_tokens": 312,
            "total_tokens": 1552,
            "cache_hit": False,  # Compliance review: cache always bypassed
            "estimated_cost": round(1240 / 1_000_000 * 2.00 + 312 / 1_000_000 * 8.00, 6),
        },
        {
            "task_class": "plan",
            "model_deployment": "gpt-4.1",
            "deployment_tier": "strong",  # second plan call — e.g. reflection-triggered re-plan
            "prompt_tokens": 890,
            "completion_tokens": 205,
            "total_tokens": 1095,
            "cache_hit": False,
            "estimated_cost": round(890 / 1_000_000 * 2.00 + 205 / 1_000_000 * 8.00, 6),
        },
    ]

    _daily_limit = float(os.environ.get("DAILY_BUDGET_USD", "5.0"))
    _budget_status = _check_budget(
        _sample_ledger, daily_limit_usd=_daily_limit)

    _routing_design = {
        "light_tier_tasks": ["extract", "retrieve_summarise", "plan (no risk flags)", "final_render"],
        "strong_tier_tasks": ["compliance_review (always)", "plan (with risk flags)", "reflection"],
        "cache_bypass_conditions": [
            "task_class == compliance_review",
            "evidence_freshness_flag is set",
            "case risk score is HIGH",
            "cache TTL expired",
        ],
        "billing_model": "PAYG (current load below PTU break-even threshold)",
        "ptu_recommended_when": "compliance_review volume > 2600 calls/day OR p99 SLA < 2s required",
        "apim_overflow": "PTU → PAYG overflow configured via APIM policy",
    }

    _artifact = {
        "day": 9,
        "title": "Scaling, Monitoring & Cost Optimisation",
        "completed_at": _dt.datetime.utcnow().isoformat() + "Z",
        "sample_ledger": _sample_ledger,
        "budget_status": _budget_status.as_dict(),
        "routing_design": _routing_design,
        "slice_eval_warning": (
            "Aggregate eval scores can hide per-slice regressions. "
            "Always inspect review_compliance/high_value slice independently."
        ),
        "observability_contract": {
            "otel_distro": "azure-monitor-opentelemetry",
            "span_attributes": [
                "aegis.task_class",
                "aegis.deployment_tier",
                "aegis.cache_allowed",
                "aegis.cache_bypass_reason",
                "aegis.estimated_cost",
            ],
            "kql_patterns": [
                "p99_latency_by_node",
                "error_rate_by_case_class",
                "escalation_spike_detection",
                "cost_per_task_class",
                "mandatory_escalation_recall_regression",
            ],
        },
    }

    out_dir = Path(__file__).resolve().parents[1] / "build" / "day9"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "routing_report.json"
    out_path.write_text(json.dumps(_artifact, indent=2))

    _total_cost = _budget_status.total_cost_usd
    _within = _budget_status.within_budget

    mo.vstack([
        mo.callout(
            mo.md(
                f"Artifact written to `build/day9/routing_report.json`\n\n"
                f"- Sample ledger: {len(_sample_ledger)} entries\n"
                f"- Total cost: ${_total_cost:.6f}\n"
                f"- Daily limit: ${_daily_limit:.2f}\n"
                f"- Budget status: **{'Within budget ✅' if _within else 'OVER BUDGET ❌'}**"
            ),
            kind="success" if _within else "danger",
        ),
        mo.download(
            data=json.dumps(_artifact, indent=2).encode(),
            filename="routing_report.json",
            mimetype="application/json",
            label="Download routing_report.json",
        ),
    ])
    return _artifact, _budget_status, _routing_design, _sample_ledger, out_dir, out_path


# ---------------------------------------------------------------------------
# Production Reflection
# ---------------------------------------------------------------------------
@app.cell
def _reflection(mo):
    mo.md("""
    # Production Reflection

    1. ** Silent failure diagnosis: ** Your incident dashboard shows that `needs_human_review`
       outcomes have increased 40 % this week, but there are no exceptions in the log.
       Walk through the investigation: which metrics do you query first, which KQL
       queries do you run, and what root causes would each query help rule out?

    2. ** Slice regression in production: ** You deploy a new embedding model for the
       retrieval node. The aggregate evaluation score improves by 0.03. Before shifting
       100 % traffic, you run slice-level evaluation and find that
       `review_compliance / high_value` drops from 0.91 → 0.84. What is your decision,
       and how do you document it in the release process?

    3. ** PTU utilisation drift: ** Three months into production, you notice the PTU
       reservation for `compliance_review` is running at 35 % average utilisation.
       What are the three most likely explanations, and what action would you take
       for each?
    """)
    return


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
@app.cell
def _summary(mo):
    mo.md("""
    # Day 9 Summary Checklist

    - [] Name the three pillars of observability and state the unique question each one answers
    - [] Describe the OTEL span data model: `trace_id`, `span_id`, `parent_span_id`, attributes, status
    - [] Explain why the Azure Monitor OpenTelemetry Distro is preferred over raw OTEL SDK wiring
    - [] Write a KQL query for p99 latency by workflow node and one for escalation spike detection
    - [] Explain why aggregate evaluation scores can hide per-slice regressions(use the table example)
    - [] State the mandatory escalation recall target and why it is 1.0 not 0.95
    - [] Compare PAYG and PTU billing: cost profile, latency profile, optimal use case for each
    - [] State the five AegisAP task classes and their default routing tier
    - [] Name the four conditions under which AegisAP bypasses the semantic cache
    - [] Describe a cost ledger entry: all fields and what business questions each answers
    - [] Explain why `minReplicas: 0` is appropriate for ACA Jobs but not for the API server
    - [] Artifact `build/day9/routing_report.json` exists with a `sample_ledger` key
    """)
    return


# ---------------------------------------------------------------------------
# Forward
# ---------------------------------------------------------------------------
@app.cell
def _forward(mo):
    mo.callout(
        mo.md("""
** Tomorrow — Day 10: Production Operations **

The cost governance and observability contracts are now in place.  Tomorrow
brings the full picture together: the six acceptance gates, the release envelope,
ACA rollback procedures, the continuous improvement loop, and how all ten days
of work converge to a production-grade system that meets the WAF pillars.

Open `notebooks/day_10_production_operations.py` when ready.
        """),
        kind="success",
    )
    return



@app.cell
def _fde_learning_contract(mo):
    mo.md(r"""
    ---
    ## FDE Learning Contract — Day 09: Observability, Routing, Cost, and Economic Control
    

    ### Four Daily Outputs

    | # | Output type | Location |
    |---|---|---|
    | 1 | Technical build | `LAB_OUTPUT/` |
    | 2 | Design defense memo | `DECISION_MEMOS/` |
    | 3 | Corporate process artifact | `PROCESS_ARTIFACTS/` |
    | 4 | Oral defense prep notes | `ORAL_DEFENSE/` |

    ### Rubric Weights (100 points total)

    | Dimension | Points |
    |---|---|
    | Routing Correctness | 25 |
| Cost Reasoning | 25 |
| Observability As Control | 20 |
| Finance Communication Quality | 15 |
| Oral Defense | 15 |

    Pass bar: **80 / 100**   Elite bar: **90 / 100**

    ### Oral Defense Prompts

    1. Which capability did you route to the mini model and what is the quality degradation risk if that routing decision is wrong?
2. Finance demands a 30% cost cut. Walk through which lever you would pull first and what zero-tolerance controls you would not touch.
3. Who approves a PTU commitment in your enterprise, and what observability evidence would they require before signing a two-year reservation?

    ### Artifact Scaffolds

    - `docs/curriculum/artifacts/day09/CAPABILITY_ALLOCATION_MEMO.md`
- `docs/curriculum/artifacts/day09/COST_GOVERNANCE_POLICY.md`
- `docs/curriculum/artifacts/day09/PTU_PAYG_DECISION_NOTE.md`

    See `docs/curriculum/MENTAL_MODELS.md` for mental models reference.
    See `docs/curriculum/ASSESSOR_CALIBRATION.md` for scoring anchors.
    """)
    return


if __name__ == "__main__":
    app.run()
