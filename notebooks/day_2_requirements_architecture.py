import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell
def _bootstrap():
    import sys
    import marimo as mo
    import json

    from pathlib import Path
    _root = Path(__file__).resolve().parents[1]
    for _p in [str(_root / "src"), str(_root / "notebooks")]:
        if _p not in sys.path:
            sys.path.insert(0, _p)
    return (mo,)


@app.cell
def _title(mo):
    mo.md("""
    # Day 2 — Requirements Gathering, Scoping & Architecture Blueprints

    > **Framework lenses:** Azure Well-Architected Framework · Cloud Adoption Framework for Azure (AI adoption)
    > **Estimated time:** 2.5 hours
    > **Sources:** `docs/curriculum/trainee/DAY_00_TRAINEE.md` §3-6,
    > `docs/curriculum/trainer/DAY_00_TRAINER.md`, and the 14-lesson notebook sequence under `notebooks/`
    > **Prerequisite:** Day 1 conceptual foundation.

    ---

    ## Learning Objectives

    By the end of this notebook you will be able to:

    1. Run a structured FDE discovery session to turn a vague brief into a scoped MVP.
    2. Write non-functional requirements (NFRs) specific to agentic AI workloads.
    3. Produce an Architecture Decision Record (ADR) that a team can act on.
    4. Read and explain the full AegisAP architecture blueprint.
    5. Describe the AegisAP data-flow narrative end-to-end.
    6. Identify and defend scoping boundaries — what is Day 4 MVP, what is Day 10 production, and what is Day 14 enterprise scale.
    7. Map discovery outputs to business ownership, adoption readiness, and enterprise governance.

    ---

    ## Where Day 2 Sits in the Full Arc

    ```
    Day 1 ──►[Day 2]──► Day 3 ──► Day 4 ──► Day 5 ──►
    Fund.    ARCH     Services  Agent    Multi-Agent
    ─────────────────────────────────────────────────
             ──► Day 6 ──► Day 7 ──► Day 8 ──► Day 9 ──► Day 10
                Data/ML   Evals    CI/CD    Observ.   Ops
    ──────────────────────────────────────────────────────────────
    Day 11 ──► Day 12 ──► Day 13 ──► Day 14
    OBO       Networking  Integration  Elite Ops
    ```

    Decisions made today govern every subsequent lesson. A weak scoping decision
    here creates technical debt that is expensive to fix by Day 8 and governance
    debt that becomes obvious by Days 12–14.
    """)
    return


@app.cell
def _full_day_agenda(mo):
    from _shared.curriculum_scaffolds import render_full_day_agenda

    render_full_day_agenda(
        mo,
        day_label="Day 2 requirements, scope, and architecture",
        core_outcome="turn a vague AI idea into a scoped architecture with named boundaries, ownership, and measurable NFRs",
    )
    return


@app.cell
def _day2_lineage_map(mo):
    mo.callout(
        mo.md(
            """
    ## Visual Guide — Architecture Lineage Map

    ```
    Day 1 problem framing
        └─► Day 2 discovery notes, NFRs, ADR, stakeholder map
              ├─► Day 3 service and framework choices
              ├─► Day 4-6 workflow and data-boundary design
              ├─► Day 8 deployment and release model
              └─► Days 12-14 governance, networking, and elite-ops constraints
    ```

    Day 2 is where the programme stops being a sequence of interesting tools and
    becomes one architecture with enforceable boundaries.

    | Day 2 artifact | Later dependency |
    |---|---|
    | NFR register | Day 8 gate thinking, Day 12 private-only posture, Day 14 data residency |
    | ADR-001 scope and boundaries | Day 3 service fit, Day 13 integration boundary design |
    | Stakeholder map / RACI | Day 10 release authority, Day 14 incident command |
    """
        ),
        kind="info",
    )
    return


@app.cell
def _day2_mastery_checkpoint(mo):
    mo.callout(
        mo.md(
            """
    ## Mastery Checkpoint — Before You Leave Discovery

    You are not ready to move on if you cannot answer:
    - which requirement here will become a hard gate later
    - which boundary is protecting auditability rather than convenience
    - which role owns a bad scoping decision when it fails in production
    - what you deliberately deferred from MVP and what evidence would justify bringing it forward
    """
        ),
        kind="warn",
    )
    return


@app.cell
def _s1_header(mo):
    mo.md("""
    ## 1. The FDE Discovery Process
    """)
    return


@app.cell
def _s1_body(mo):
    mo.md("""
    A **Forward Deployed Engineer** is not handed a spec sheet. You arrive with
    a vague directive: *"We need to do something with AI for invoices."*

    Your job is to convert that into a buildable, achievable, scoped system
    in under two hours of structured conversation. Here is the framework:

    ### Discovery in Five Phases

    | Phase | Question to answer | Output |
    |---|---|---|
    | **1. Problem framing** | What pain are we solving, for whom, measured how? | Problem statement + success metric |
    | **2. Data inventory** | What inputs exist, in what formats, at what volume? | Data asset list with quality notes |
    | **3. System boundaries** | What is in scope for this agent? What calls what? | Context diagram |
    | **4. Trust and compliance** | What data is sensitive? What decisions must be auditable? | Trust boundary + compliance flags |
    | **5. NFR elicitation** | Latency, cost, availability, accuracy targets — from the business | NFR table with numerical targets |

    ### Applying Discovery to AegisAP

    The original brief was: *"Our AP team spends too much time on manual invoice processing.
    Can we use AI?"*

    After a 90-minute discovery session:

    | Phase | AegisAP result |
    |---|---|
    | Problem framing | Reduce AP processing time from 45 min to < 2 min per invoice; error rate from 12% to < 1%; decision audit trail required |
    | Data inventory | Invoice PDFs (OCR available), ERP PO registry (REST API), vendor contracts (SharePoint PDFs), AP policy rulebook (Word doc) |
    | System boundaries | Agent handles extraction + routing + low-value auto-approval; humans handle approvals > £10k |
    | Trust and compliance | Invoice PDFs may contain PII (contact names, bank fragments); approval decisions are legally binding and must be auditable |
    | NFRs | Extraction p99 < 15 s, auto-approve accuracy ≥ 99.5%, mandatory escalation recall = 100%, cost per invoice < £0.10 |
    """)
    return


@app.cell
def _discovery_simulator(mo):
    mo.md("""
    ### Discovery Question Simulator
    """)
    return


@app.cell
def _disc_sim(mo):
    phase = mo.ui.dropdown(
        options=[
            "1. Problem Framing",
            "2. Data Inventory",
            "3. System Boundaries",
            "4. Trust & Compliance",
            "5. NFR Elicitation",
        ],
        value="1. Problem Framing",
        label="Select a discovery phase to see key questions:",
    )
    phase
    return (phase,)


@app.cell
def _disc_questions(mo, phase):
    questions_db = {
        "1. Problem Framing": [
            "What is the outcome you are trying to change? How do you measure it today?",
            "Who experiences the pain most? What is their exact workflow step that is broken?",
            "What does 'success' look like in 3 months? In 12 months?",
            "What has been tried before? Why did it fail?",
            "What is the cost of *not* solving this?",
        ],
        "2. Data Inventory": [
            "What are the raw inputs? PDF, email, API, database table?",
            "What is the volume? Per day, per month, in what distribution?",
            "What is the data quality like? OCR errors? Missing fields? Multiple formats?",
            "Who owns the source data? Is it accessible programmatically today?",
            "How fresh must the data be? Is a day-old vendor policy document acceptable?",
        ],
        "3. System Boundaries": [
            "What does this agent do, and what does it explicitly NOT do?",
            "What external systems does it need to call? Which ones can call it?",
            "Who initiates a workflow? Who receives its outputs?",
            "What is the human role in the loop? When must a human be involved?",
            "What is out of scope for this MVP that we will defer to a later phase?",
        ],
        "4. Trust & Compliance": [
            "What data is PII or commercially sensitive? What must never appear in logs?",
            "Which decisions require a legal audit trail?",
            "Are there regulatory obligations (GDPR, SOX, VAT compliance)?",
            "What happens if the agent makes a wrong decision? What is the recovery?",
            "Who is accountable when the agent recommends an approval that turns out wrong?",
        ],
        "5. NFR Elicitation": [
            "What latency is acceptable to the end user for a response?",
            "What accuracy rate is the minimum viable product? What is the target?",
            "What is the per-transaction cost budget?",
            "What availability SLA is required? (99.9% means ≈8.7 hours downtime/year)",
            "What is the maximum tolerable data loss? (RPO) What is the max recovery time? (RTO)",
        ],
    }
    qs = questions_db[phase.value]
    mo.callout(
        mo.vstack([mo.md(f"**Key questions for phase {phase.value}:**")] +
                  [mo.md(f"- {q}") for q in qs]),
        kind="info",
    )
    return


@app.cell
def _stakeholder_sim_header(mo):
    mo.md("""
    ### Stakeholder Interview Simulation
    """)
    return


@app.cell
def _stakeholder_question(mo):
    sq_question = mo.ui.dropdown(
        options=[
            "How many invoices do you process each week?",
            "What is the most common reason an invoice fails validation?",
            "What happens when an invoice amount exceeds your approval limit?",
            "How long does it take to resolve a disputed invoice today?",
            "Which suppliers cause the most processing problems?",
            "What data quality issues do you encounter most often?",
            "What would 'good' look like in six months?",
        ],
        value="How many invoices do you process each week?",
        label="You are the FDE. Select a question to ask the AP Manager:",
    )
    sq_question
    return (sq_question,)


@app.cell
def _stakeholder_response(mo, sq_question):
    _ap_responses = {
        "How many invoices do you process each week?": {
            "response": (
                "On average about 240 per week, but it spikes to 400+ at month-end. "
                "We have three clerks — Sarah, Tom, and Priya — and they each handle around 80. "
                "Month-end is brutal. We sometimes have to bring in a temp."
            ),
            "fde_note": (
                "**Volume signal:** 240/week nominal, 400+ at peak. Month-end spike "
                "means batch processing pressure — durable state (Day 5) matters here. "
                "Three-person team means any automation that removes manual entry "
                "frees roughly 45 min × 240 = 180 hours/month."
            ),
        },
        "What is the most common reason an invoice fails validation?": {
            "response": (
                "Missing PO numbers — that's the number one problem. Maybe 15% of invoices "
                "arrive without a PO. Then wrong amounts — the supplier totals don't match "
                "the line items. And sometimes the currency is wrong: we had a US supplier "
                "send USD amounts but label them as GBP last month."
            ),
            "fde_note": (
                "**Three validation failure modes:** missing PO (15%), arithmetic mismatch, "
                "currency mislabel. These become your first `CanonicalInvoice` "
                "validation rules in the Day 4 canonicaliser. "
                "Currency detection is a trust-boundary concern — Decimal arithmetic required."
            ),
        },
        "What happens when an invoice amount exceeds your approval limit?": {
            "response": (
                "Anything over £10,000 has to go to the finance manager — that's James. "
                "He usually approves within a day but sometimes it takes three days if he's "
                "travelling. We don't have a way to track those: we just send an email and wait. "
                "Sometimes invoices get lost in his inbox."
            ),
            "fde_note": (
                "**Amount threshold: £10,000.** Manual async approval path with no tracking. "
                "Lost emails → zero `mandatory_escalation_recall` guarantee. "
                "This is your most important NFR row (recall must = 1.0). "
                "Durable HITL with PostgreSQL resume (Day 5) is the architectural response."
            ),
        },
        "How long does it take to resolve a disputed invoice today?": {
            "response": (
                "It depends. If it's a simple PO mismatch and the supplier is a regular, "
                "maybe two days. If it's a new vendor with a contract dispute, it can take "
                "two weeks. And then sometimes we have to put a payment on hold and the "
                "supplier relationship manager gets involved. That's messy."
            ),
            "fde_note": (
                "**Happy path: 2 days for known vendors. Exception path: 2 weeks for new vendor disputes.** "
                "This data feeds your `new_vendor` routing flag in LangGraph (Day 5). "
                "Supplier relationship escalation is out of scope for MVP — "
                "document this as a deferred capability in the scoping matrix."
            ),
        },
        "Which suppliers cause the most processing problems?": {
            "response": (
                "The international ones, honestly. We have three EU suppliers who send invoices "
                "in their own format — one even sends in German. And there's a US company that "
                "always sends PDFs that are basically scanned paper — very poor OCR quality."
            ),
            "fde_note": (
                "**International and low-OCR-quality invoices are harder inputs.** "
                "Language detection and OCR quality score are good candidate fields "
                "for `InvoiceCandidate.confidence`. "
                "This maps to your `input_variability` Decision Tool signal — score upward. "
                "Locale mismatch is the `fixtures/locale_mismatch/` fixture."
            ),
        },
        "What data quality issues do you encounter most often?": {
            "response": (
                "The big one is dates. We get dates in US format, UK format, also written out "
                "like 'fifteenth of January 2024'. And amounts sometimes have commas as "
                "thousand separators and sometimes as decimal separators depending on the country."
            ),
            "fde_note": (
                "**Date format and locale-aware decimal parsing are critical.** "
                "These become deterministic normalisation rules in the Day 4 canonicaliser — "
                "NOT LLM reasoning. The LLM extracts what it sees; Python normalises it. "
                "This is the trust-boundary pattern: structured validation post-LLM output."
            ),
        },
        "What would 'good' look like in six months?": {
            "response": (
                "Honestly? I'd like to hand invoices to the system in the morning and have "
                "everything under £10,000 with a valid PO just processed automatically — "
                "no manual entry at all. And for the ones that need approval, I want James "
                "to get a clear summary: not just a forwarded email, but something that says "
                "'here is the invoice, here is why it needs approval, here is the policy that applies.'"
            ),
            "fde_note": (
                "**Success definition:** auto-approve all invoices under £10k with valid PO. "
                "For escalations: structured approval package (not raw forwarded email). "
                "This is your `RecommendationPackage` + `HumanApprovalPackage` design goal — "
                "the two terminal output types of the AegisAP workflow."
            ),
        },
    }
    _r = _ap_responses[sq_question.value]
    mo.vstack([
        mo.callout(
            mo.md(f"**AP Manager says:** *\"{_r['response']}\"*"),
            kind="neutral",
        ),
        mo.callout(
            mo.md(f"**FDE insight:** {_r['fde_note']}"),
            kind="info",
        ),
    ])
    return


@app.cell
def _stakeholder_map_header(mo):
    mo.md("""
    ### Stakeholder Ownership & Sign-Off Map
    """)
    return


@app.cell
def _stakeholder_select(mo):
    stakeholder = mo.ui.dropdown(
        options=[
            "Process owner (AP manager)",
            "Security / compliance lead",
            "Finance approver",
            "Platform / cloud engineering",
            "Operations / support",
        ],
        value="Process owner (AP manager)",
        label="Select a stakeholder to inspect their decision rights:",
    )
    stakeholder
    return (stakeholder,)


@app.cell
def _stakeholder_detail(mo, stakeholder):
    stakeholders = {
        "Process owner (AP manager)": {
            "cares_about": "Cycle time, error rate, manual effort removed, exception handling realism",
            "must_sign_off": "Problem statement, KPI targets, in-scope vs out-of-scope workflow steps, human approval thresholds",
            "evidence_needed": "Current-state pain data, volume analysis, success metrics, scoping matrix",
            "when": "Discovery and MVP scope approval",
        },
        "Security / compliance lead": {
            "cares_about": "PII handling, auditability, network posture, identity model, regulatory exposure",
            "must_sign_off": "Trust boundary, zero-tolerance NFRs, logging policy, network posture decision",
            "evidence_needed": "Data classification notes, threat assumptions, RBAC model, ADR with network posture",
            "when": "Before production design is accepted",
        },
        "Finance approver": {
            "cares_about": "Delegation of authority, approval controls, escalation recall, financial blast radius",
            "must_sign_off": "Approval thresholds, escalation policy, override model, audit evidence expectations",
            "evidence_needed": "Authority matrix, failure-mode analysis, sample approval package, zero-tolerance NFRs",
            "when": "Before auto-approval is enabled",
        },
        "Platform / cloud engineering": {
            "cares_about": "Deployability, supportability, identity, networking, environment consistency",
            "must_sign_off": "Runtime topology, CI/CD expectations, hosting model, operational ownership boundaries",
            "evidence_needed": "Architecture blueprint, NFR targets, IaC expectations, environment plan",
            "when": "Before platform onboarding and production rollout",
        },
        "Operations / support": {
            "cares_about": "Alertability, runbooks, incident response, rollback criteria, ownership clarity",
            "must_sign_off": "Monitoring coverage, release gates, on-call boundaries, failure recovery expectations",
            "evidence_needed": "Runbook outline, observability plan, zero-tolerance gate list, rollback triggers",
            "when": "Before go-live readiness review",
        },
    }
    d = stakeholders[stakeholder.value]
    mo.callout(
        mo.md(f"""
    **Cares about:** {d['cares_about']}

    **Must sign off:** {d['must_sign_off']}

    **Evidence needed:** {d['evidence_needed']}

    **Primary timing:** {d['when']}
        """),
        kind="info",
    )
    return


@app.cell
def _caf_bridge_header(mo):
    mo.md("""
    ### Discovery Outputs as Adoption Artifacts
    """)
    return


@app.cell
def _caf_bridge_body(mo):
    mo.md("""
    Discovery is not just a workshop activity. It feeds the enterprise adoption process.

    | Discovery output | Immediate architecture use | Adoption question it answers | Typical owner |
    |---|---|---|---|
    | Problem statement + KPI | Defines the MVP and success criteria | Why are we doing this and what value proves adoption? | Process owner |
    | Data inventory | Constrains retrieval, normalization, and integration design | Are our data sources ready and trustworthy enough? | Data owner + engineering |
    | System boundary | Prevents over-scoping and unclear interfaces | What belongs in this workload vs surrounding systems? | Solution architect |
    | Trust boundary + compliance flags | Drives identity, logging, and network decisions | What controls are mandatory before production? | Security / compliance |
    | NFR register | Drives model, platform, and gate choices | What must be true before pilot, production, and enterprise scale? | Engineering + ops |

    ### Excellence standard

    A strong Day 2 outcome produces five artifacts, not one:

    1. A scoped MVP recommendation.
    2. A production-ready NFR register.
    3. At least one ADR with explicit alternatives.
    4. Named stakeholders and sign-off boundaries.
    5. A clear path from prototype to enterprise operation across Days 3–14.
    """)
    return


@app.cell
def _s2_header(mo):
    mo.md("""
    ## 2. Non-Functional Requirements for Agentic AI Workloads
    """)
    return


@app.cell
def _s2_body(mo):
    mo.md("""
    NFRs for AI systems are different from traditional software because:

    - **Accuracy is probabilistic** — you cannot guarantee 100%; you set thresholds and measure
    - **Cost has two components** — infrastructure (ACA, PostgreSQL) *and* model tokens
    - **Latency includes warm-up** — cold-starting a model deployment adds unpredictable latency
    - **Safety NFRs are hard constraints** — mandatory escalation recall must be 1.0, not "best effort"

    ### AegisAP NFR Table

    | NFR | Metric | Target | Monitoring | Consequence of breach |
    |---|---|---|---|---|
    | Extraction latency | p99 end-to-end | < 15 s | App Insights trace | SLA breach; user complaint |
    | Auto-approve accuracy | Precision on approved cases | ≥ 99.5% | Weekly eval run | Financial exposure |
    | **Mandatory escalation recall** | Recall on must-escalate cases | **= 1.0** | CI gate | **Release blocked** |
    | Cost per invoice | Token cost + infra amortised | < £0.10 | Cost ledger daily alert | Budget overrun |
    | Availability | System uptime | 99.5% | ACA health probe | SLA breach |
    | Durable state recovery | RTO after process crash | < 2 min | Resume smoke test | Approvals lost |
    | Audit completeness | Audit rows per decision | 100% | Append-only table row count | Compliance failure |
    | **Private networking posture** | No public endpoint reachable from internet | All AI services: `publicNetworkAccess=Disabled` + Private Endpoint | Gate `gate_private_network_static` in CI | **Release blocked** (Days 12, 14) |
    | **Data residency** | ARM `.location` of all AI resources | Single approved region (e.g., `uksouth`) | Gate `gate_data_residency` reading ARM API | **Release blocked** (Day 14) |

    > **Zero-tolerance NFRs** are those where *any* breach is a production incident,
    > regardless of frequency. Mandatory escalation recall is zero-tolerance because
    > a missed escalation means an unauthorised payment could be processed.
    > Private networking posture and data residency are equally zero-tolerance in
    > regulated-sector deployments — a misconfigured public endpoint is an immediate audit finding.

    > **ADR requirement (added Day 12):** Every ADR produced in this workshop must include
    > a **"Network Posture Decision"** field with one of: `public_endpoint`, `vnet_injected`,
    > or `air_gapped`. The decision drives which acceptance gates apply at Day 14.
    """)
    return


@app.cell
def _nfr_trade_off(mo):
    mo.md("""
    ### NFR Trade-Off Explorer
    """)
    return


@app.cell
def _nfr_slider(mo):
    latency_target = mo.ui.slider(
        start=1, stop=30, step=1, value=15,
        label="Extraction latency target (seconds, p99)",
    )
    accuracy_target = mo.ui.slider(
        start=90, stop=100, step=0.5, value=99.5,
        label="Auto-approve accuracy target (%)",
    )
    cost_target = mo.ui.slider(
        start=0.01, stop=0.50, step=0.01, value=0.10,
        label="Cost per invoice ceiling (£)",
    )
    mo.vstack([
        mo.md("Slide to explore how NFR targets drive architectural decisions:"),
        latency_target, accuracy_target, cost_target,
    ])
    return accuracy_target, cost_target, latency_target


@app.cell
def _nfr_implications(accuracy_target, cost_target, latency_target, mo):
    implications = []

    if latency_target.value < 5:
        implications.append(
            "⚡ **Latency < 5s:** Requires GPT-4o-mini or PTU deployment to avoid queuing. No sequential tool chains — parallelise search queries.")
    elif latency_target.value < 10:
        implications.append(
            "✅ **Latency 5–10s:** GPT-4o PAYG is achievable in most regions. Semantic caching helps at high volume.")
    else:
        implications.append(
            "🟦 **Latency 10–30s:** Any model tier works. Allows sequential retrieval and richer planning prompts.")

    if accuracy_target.value >= 99.5:
        implications.append(
            "🔒 **Accuracy ≥ 99.5%:** Requires GPT-4o (not mini) for planning/compliance tasks. Slice-based eval must pass Day 10 release gates and remain stable through Day 14 enterprise gates.")
    elif accuracy_target.value >= 97:
        implications.append(
            "⚠️ **Accuracy 97–99.5%:** GPT-4o-mini may suffice for lower-risk task classes; GPT-4o required for compliance review.")
    else:
        implications.append(
            "⚠️ **Accuracy < 97%:** Below enterprise threshold for financial systems. Re-examine scope — are you automating the right tasks?")

    if cost_target.value < 0.05:
        implications.append(
            "💰 **Cost < £0.05:** Requires heavy caching + GPT-4o-mini for most tasks. PTU only if volume > 5,000 invoices/day.")
    elif cost_target.value < 0.15:
        implications.append(
            "✅ **Cost £0.05–0.15:** Balanced tier routing (mini for extraction, 4o for compliance). Semantic cache for repeat vendors.")
    else:
        implications.append(
            "🟦 **Cost > £0.15:** Budget allows GPT-4o everywhere. Still worth routing by task class for traceability.")

    mo.callout(
        mo.vstack([mo.md("**Architectural implications of your NFR choices:**")] +
                  [mo.md(impl) for impl in implications]),
        kind="info",
    )
    return


@app.cell
def _s3_header(mo):
    mo.md("""
    ## 3. Architecture Decision Records (ADRs)
    """)
    return


@app.cell
def _s3_body(mo):
    mo.md("""
    An **Architecture Decision Record** documents a single, significant architectural
    choice so that future engineers (including yourself at 3am) understand:
    - What was decided
    - Why it was decided (context + rationale)
    - What alternatives were considered
    - What the consequences are

    ADRs are stored in source control alongside the code. They are not RFCs or
    approval documents — they are factual records of decisions already made.

    ### ADR Template

    ```markdown
    # ADR-NNN: [Short title]

    **Date:** YYYY-MM-DD
    **Status:** Accepted | Deprecated | Superseded by ADR-NNN
    **Deciders:** [Names / roles]
    **Decision type:** Strategy | Architecture | Governance
    **Operational owner:** [Team / role]
    **Network posture decision:** public_endpoint | vnet_injected | air_gapped

    ## Context
    [What situation or problem prompted this decision?]

    ## Decision
    [What was decided, in one or two sentences?]

    ## Rationale
    [Why this option over the alternatives?]

    ## Alternatives considered
    - [Option A] — rejected because [reason]
    - [Option B] — rejected because [reason]

    ## Consequences
    - [Positive consequence]
    - [Constraint or trade-off introduced]

    ## Review trigger
    [What future condition would cause this ADR to be revisited?]
    ```

    > For this programme, great ADRs are not just technically correct. They also
    > make ownership, network posture, and review triggers explicit so later
    > lessons can attach the right production and enterprise gates.
    """)
    return


@app.cell
def _adr_examples(mo):
    adr_selector = mo.ui.dropdown(
        options=[
            "ADR-001: LangGraph for workflow orchestration",
            "ADR-002: PostgreSQL for durable state (not Cosmos DB)",
            "ADR-003: DefaultAzureCredential over API keys",
            "ADR-004: Structured outputs (JSON schema) for extraction",
        ],
        value="ADR-001: LangGraph for workflow orchestration",
        label="Browse AegisAP ADRs:",
    )
    adr_selector
    return (adr_selector,)


@app.cell(hide_code=True)
def _adr_content(adr_selector, mo):
    adrs = {
        "ADR-001: LangGraph for workflow orchestration": """
    **Date:** 2024-01-15 | **Status:** Accepted

    **Context:** AegisAP requires a multi-step approval workflow with branching logic
    (auto-approve vs. human review), durable state, and the ability to pause and resume.
    We needed an orchestration layer that could represent conditional transitions as
    inspectable code, not as a black-box agent loop.

    **Decision:** Use LangGraph as the workflow orchestration layer.

    **Rationale:** LangGraph represents workflows as a directed graph with typed state —
    every node is a testable Python function, every edge is an explicit transition.
    This makes the workflow auditable, debuggable, and independently testable.

    **Alternatives considered:**
    - **Vanilla ReAct agent loop** — rejected because it is non-deterministic and
      hard to audit. Each run may take a different path.
    - **Temporal.io** — rejected because it requires a separate Temporal server,
      adds operational complexity, and LangGraph is sufficient for our scale.
    - **Azure Durable Functions** — rejected because it binds us to C#/.NET heritage
      patterns and is harder to integrate with the Python ML/AI ecosystem.

    **Consequences:**
    - (+) Workflow is fully inspectable as a state graph
    - (+) Each node is independently unit-testable
    - (-) LangGraph adds a dependency; team must learn its API
    - (-) Persistence requires custom checkpointing (PostgreSQL) beyond LangGraph's in-memory default
        """,
        "ADR-002: PostgreSQL for durable state (not Cosmos DB)": """
    **Date:** 2024-01-20 | **Status:** Accepted

    **Context:** From Day 5, AegisAP needs a durable store for workflow checkpoints,
    approval tasks, and the idempotency ledger. The store must be ACID-compliant
    and support structured queries (e.g., "all pending approval tasks for thread X").

    **Decision:** Use Azure Database for PostgreSQL — Flexible Server.

    **Rationale:** PostgreSQL provides ACID guarantees needed for the idempotency
    ledger (duplicate prevention). It supports structured queries across the four
    related tables. Azure Flexible Server supports Entra authentication natively
    (Day 7 requirement).

    **Alternatives considered:**
    - **Azure Cosmos DB** — rejected for workflow state because eventual consistency
      is incompatible with the idempotency ledger's requirements. Cosmos DB is
      appropriate for unstructured agent memory (Day 6 discussion).
    - **Azure Table Storage** — rejected because it lacks transactions across rows.
    - **SQLite (in-process)** — rejected because it does not survive process
      restarts across Container App replicas.

    **Consequences:**
    - (+) Full ACID compliance; no duplicate side effects
    - (+) Entra auth support eliminates password management
    - (-) Additional Azure service to provision and manage
    - (-) Requires schema migrations on updates (tracked in `scripts/apply_migrations.py`)
        """,
        "ADR-003: DefaultAzureCredential over API keys": """
    **Date:** 2024-01-10 | **Status:** Accepted

    **Context:** All Azure SDK calls require authentication. The choice is between
    API keys/connection strings (simple but risky) and managed identity
    (`DefaultAzureCredential`).

    **Decision:** All Azure SDK calls use `DefaultAzureCredential`. API keys are
    forbidden in application code and environment variables in staging/production.

    **Rationale:** API keys do not expire, are stored as secrets, and have been the
    source of multiple high-profile credential leaks. Managed Identity issues
    short-lived tokens automatically — there is nothing to rotate, nothing to leak.
    The `DefaultAzureCredential` chain degrades gracefully: `az login` in dev,
    Managed Identity in production — no code change at promotion.

    **Alternatives considered:**
    - **API keys in Azure Key Vault** — rejected for services that support RBAC
      because Key Vault access itself requires a credential; managed identity removes
      the bootstrap problem entirely.
    - **Service Principal + secret** — rejected because the secret must be stored
      somewhere (GitHub Actions, Key Vault) and has a rotation burden.

    **Consequences:**
    - (+) Zero stored secrets for Azure-native services
    - (+) Credential source changes automatically between dev and prod
    - (-) `az login` required in local dev — slight friction for new engineers
    - (-) Services that do not support Managed Identity still need Key Vault
        """,
        "ADR-004: Structured outputs (JSON schema) for extraction": """
    **Date:** 2024-01-18 | **Status:** Accepted

    **Context:** Day 4 extraction requires the LLM to produce a JSON object matching
    `InvoiceCandidate`. Without format constraints, the model may produce freeform JSON,
    wrong field names, or refuse to populate optional fields.

    **Decision:** Use Azure OpenAI `response_format` with `json_schema` and `strict: true`
    for all extraction calls.

    **Rationale:** Structured outputs guarantee the model's response matches the
    declared JSON Schema. This eliminates field-name hallucination, wrong type
    coercion, and missing required fields at the JSON level — leaving only logical
    validation to Python. `strict: true` is essential; without it the guarantee is weaker.

    **Alternatives considered:**
    - **Prompt-only JSON instruction** — rejected because compliance is inconsistent
      and parsing failures are silent in production.
    - **Tool calling / function calling** — acceptable but JSON schema is more direct
      for extraction use cases; function calling adds unnecessary wrapping overhead.

    **Consequences:**
    - (+) Eliminated JSON parse failures in extraction
    - (-) `strict: true` does not allow `additionalProperties`; schema must be
      complete upfront — a schema change requires a prompt + schema change together
    - (-) Not all model versions support `strict: true`; must pin deployment version
        """,
    }
    mo.md(f"```markdown\n{adrs[adr_selector.value].strip()}\n```")
    return


@app.cell
def _adr_exercise_header(mo):
    mo.md("""
    ### ✏️ Practice: Write an ADR

    Now you produce one. Using the template above as a guide, write the ADR for
    the decision to use **LangGraph** as AegisAP's workflow orchestration layer.

    Do not look at ADR-001 in the selector above yet. Use only what you know
    from Day 1 (agent loops, identity, WAF) and the AegisAP brief. When you are
    done, click **Show model answer** to compare against the actual ADR-001.
    """)
    return


@app.cell
def _adr_exercise_form(mo):
    _adr_context_input = mo.ui.text_area(
        placeholder="What situation or problem prompted this decision?",
        label="Context (2–3 sentences)",
    )
    _adr_decision_input = mo.ui.text_area(
        placeholder="What was decided, in one or two sentences?",
        label="Decision",
    )
    _adr_rationale_input = mo.ui.text_area(
        placeholder="Why this option over the alternatives? (2–4 bullet points)",
        label="Rationale",
    )
    _adr_alternatives_input = mo.ui.text_area(
        placeholder="Option A — rejected because ...\nOption B — rejected because ...",
        label="Alternatives considered (at least two)",
    )
    _adr_consequences_input = mo.ui.text_area(
        placeholder="(+) Positive consequence\n(-) Constraint or trade-off introduced",
        label="Consequences",
    )
    adr_reveal_btn = mo.ui.run_button(label="Show model answer (ADR-001)")
    mo.vstack([
        mo.md("**Fill in each field, then click the button below to compare:**"),
        _adr_context_input,
        _adr_decision_input,
        _adr_rationale_input,
        _adr_alternatives_input,
        _adr_consequences_input,
        adr_reveal_btn,
    ])
    return (adr_reveal_btn,)


@app.cell
def _adr_model_answer(adr_reveal_btn, mo):
    if adr_reveal_btn.value:
        _out = mo.callout(
            mo.md("""
    ```markdown
    # ADR-001: LangGraph for workflow orchestration

    **Date:** 2024-01-15 | **Status:** Accepted

    ## Context
    AegisAP requires a multi-step approval workflow with branching logic
    (auto-approve vs. human review), durable state, and the ability to pause and resume
    while awaiting human approval. We needed an orchestration layer that could represent
    conditional transitions as inspectable code, not as a black-box agent loop.

    ## Decision
    Use LangGraph as the workflow orchestration layer.

    ## Rationale
    - LangGraph represents workflows as a directed graph with typed state — every node is
      a testable Python function, every edge is an explicit transition.
    - The workflow is auditable, debuggable, and independently testable at the node level.
    - `StateGraph` handles the pause/resume requirement natively with custom checkpointers.

    ## Alternatives considered
    - **Vanilla ReAct agent loop** — rejected because it is non-deterministic and hard
      to audit; each run may take a different path.
    - **Temporal.io** — rejected because it requires a separate Temporal server and adds
      operational complexity beyond what this use case needs.
    - **Azure Durable Functions** — rejected because it binds to C#/.NET heritage patterns
      and is harder to integrate with the Python ML/AI ecosystem.

    ## Consequences
    - (+) Workflow is fully inspectable as a state graph
    - (+) Each node is independently unit-testable
    - (-) LangGraph adds a dependency; team must learn its API
    - (-) Persistence requires custom checkpointing (PostgreSQL) beyond the in-memory default
    ```
            """),
            kind="neutral",
        )
    else:
        _out = mo.callout(
            mo.md(
                "Fill in all five fields above, then click "
                "**Show model answer (ADR-001)** to compare your ADR to the actual one."
            ),
            kind="info",
        )
    _out
    return


@app.cell
def _s4_header(mo):
    mo.md("""
    ## 4. AegisAP Full Architecture Blueprint
    """)
    return


@app.cell
def _arch_diagram(mo):
    mo.md("""
    The diagram below shows the complete AegisAP system as it exists by Day 14.
    Day 10 gives us a production-ready workload; Days 11–14 add enterprise
    delegation, network constraints, integration boundaries, and elite operations.

    ```
    ┌─────────────────────────── AZURE SUBSCRIPTION ────────────────────────────────┐
    │                                                                                 │
    │  ┌──────────────────────────── Resource Group ─────────────────────────────┐   │
    │  │                                                                          │   │
    │  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
    │  │  │              AZURE CONTAINER APPS ENVIRONMENT                   │    │   │
    │  │  │                                                                  │    │   │
    │  │  │  ┌──────────────────┐      ┌────────────────────────────────┐   │    │   │
    │  │  │  │  aegisap-api     │      │       aegisap-worker           │   │    │   │
    │  │  │  │  (FastAPI)       │      │ (LangGraph workflow runner)    │   │    │   │
    │  │  │  │                  │      │                                │   │    │   │
    │  │  │  │  POST /cases/run │─────►│  Day 4: extract + validate    │   │    │   │
    │  │  │  │  GET  /threads/  │      │  Day 5: route + checkpoint     │   │    │   │
    │  │  │  │  POST /approvals/│      │  Day 3: retrieve evidence      │   │    │   │
    │  │  │  └─────────┬────────┘      │  Day 4: plan + execute         │   │    │   │
    │  │  │            │               │  Day 7: policy review          │   │    │   │
    │  │  │            │  Managed      │  Day 5: durable resume         │   │    │   │
    │  │  │            │  Identity     └─────────┬────────────┬─────────┘   │    │   │
    │  │  └────────────┼─────────────────────────┼────────────┼─────────────┘    │   │
    │  │               │                         │            │                  │   │
    │  │  ┌────────────▼──────┐   ┌──────────────▼──┐ ┌──────▼────────────┐    │   │
    │  │  │  Azure OpenAI     │   │ Azure AI Search  │ │  Azure PostgreSQL │    │   │
    │  │  │  gpt-4o (extract) │   │ Vendor policies  │ │  workflow_threads │    │   │
    │  │  │  gpt-4o (plan)    │   │ Compliance rules │ │  checkpoints      │    │   │
    │  │  │  gpt-4o (review)  │   │ Hybrid search    │ │  approval_tasks   │    │   │
    │  │  └───────────────────┘   └─────────────────┘ │  side_effect_     │    │   │
    │  │                                               │    ledger         │    │   │
    │  │  ┌───────────────────┐   ┌─────────────────┐ └───────────────────┘    │   │
    │  │  │  Azure Key Vault  │   │ Azure Monitor /  │                          │   │
    │  │  │  LangSmith key    │   │ App Insights     │                          │   │
    │  │  │  webhook tokens   │   │ (OTEL traces)    │                          │   │
    │  │  └───────────────────┘   └─────────────────┘                          │   │
    │  │                                                                          │   │
    │  │  ┌───────────────────┐   ┌─────────────────┐                           │   │
    │  │  │ Entra OBO / Auth  │   │ Private Endpoints│                           │   │
    │  │  │ Day 11 delegation │   │ Day 12 network   │                           │   │
    │  │  └───────────────────┘   └─────────────────┘                           │   │
    │  │                                                                          │   │
    │  │  ┌──────────────────────────────────────────────────────────────────┐   │   │
    │  │  │ IDENTITY PLANES                                                  │   │   │
    │  │  │  Runtime: system-assigned MI  •  CI/CD: OIDC federation          │   │   │
    │  │  │  Admin (one-time): human SP   •  Dev/Ops: Reader role            │   │   │
    │  │  └──────────────────────────────────────────────────────────────────┘   │   │
    │  └──────────────────────────────────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────────────────────────────────┘

    External: Azure Container Registry (ACR) — image source for ACA
              Azure API Management (APIM) — Day 9 PTU overflow gateway
              MCP / enterprise connectors — Day 13 integration boundary
              Acceptance + change gates — Day 14 operating controls
    ```
    """)
    return


@app.cell
def _day_by_day_build(mo):
    mo.md("""
    ### Which Day Adds Which Component?
    """)
    return


@app.cell
def _build_timeline(mo):
    try:
        import plotly.graph_objects as go

        components = [
            ("Azure AI Search", 3, 14),
            ("Azure OpenAI extraction/planning", 4, 14),
            ("LangGraph workflow", 5, 14),
            ("Durable state (PostgreSQL)", 5, 14),
            ("Approval gate (HITL)", 5, 14),
            ("ADF + Search indexing", 6, 14),
            ("PII redaction + eval harness", 7, 14),
            ("Bicep IaC + ACA", 8, 14),
            ("OIDC federation", 8, 14),
            ("OTEL + cost governance", 9, 14),
            ("Acceptance gates", 10, 14),
            ("Delegated identity / OBO", 11, 14),
            ("Private networking", 12, 14),
            ("MCP integration boundary", 13, 14),
            ("Change-control / elite ops", 14, 14),
        ]

        fig = go.Figure()
        for i, (name, start, end) in enumerate(components):
            fig.add_trace(go.Bar(
                orientation="h",
                x=[end - start + 1],
                y=[name],
                base=[start - 1],
                marker_color=f"hsl({(start * 25) % 360},60%,55%)",
                name=f"Day {start}",
                showlegend=False,
                text=f"Day {start}",
                textposition="inside",
                hovertemplate=f"<b>{name}</b><br>Added: Day {start}<extra></extra>",
            ))
        fig.update_layout(
            title="AegisAP Component Build Timeline",
            xaxis=dict(tickvals=list(range(1, 15)), ticktext=[f"Day {d}" for d in range(1, 15)],
                       title="Programme Day"),
            height=500,
            margin=dict(t=60, l=220, b=40),
            barmode="overlay",
        )
        _out = mo.ui.plotly(fig)
    except ImportError:
        mo.callout(mo.md("Install `plotly` to see this chart."), kind="warn")

    _out
    return


@app.cell
def _s5_header(mo):
    mo.md("""
    ## 5. End-to-End Data Flow Narrative
    """)
    return


@app.cell
def _data_flow_step(mo):
    mo.md("""
    ### Step through the data flow
    """)
    return


@app.cell
def _step_select(mo):
    step = mo.ui.slider(start=1, stop=8, step=1, value=1,
                        label="Data flow step (1–8):")
    step
    return (step,)


@app.cell
def _step_detail(mo, step):
    steps = {
        1: {
            "title": "Invoice arrives as raw bytes",
            "what": "An API call `POST /api/cases/run` delivers the invoice as multipart/form-data (PDF bytes + metadata).",
            "data_state": "Raw bytes — completely untrusted. No field extraction has occurred.",
            "where": "ACA API container, `aegisap-api`",
            "day": "Day 8 (API); Day 4 (intake logic)",
        },
        2: {
            "title": "Extraction: bytes → InvoiceCandidate",
            "what": "Azure OpenAI `gpt-4o` receives the text (post-OCR) and produces an `InvoiceCandidate` JSON using structured outputs.",
            "data_state": "`InvoiceCandidate` — probabilistic. Fields may be None, wrong type, or logically invalid. Not yet trusted.",
            "where": "Worker container, `intake.extractor`",
            "day": "Day 4",
        },
        3: {
            "title": "Normalization + Validation: InvoiceCandidate → CanonicalInvoice",
            "what": "Deterministic Python: currency codes normalised to ISO 4217, amounts to Decimal, dates to ISO 8601. Pydantic validation checks mandatory fields, sums, and PO presence.",
            "data_state": "`CanonicalInvoice` — typed, immutable, validated. **Trust boundary crossed.** If validation fails, `IntakeRejectionError` is raised with a reason code.",
            "where": "Worker container, `intake.canonicaliser`",
            "day": "Day 4",
        },
        4: {
            "title": "Routing: CanonicalInvoice → routing decision",
            "what": "Python rules evaluate amount thresholds, vendor authorisation status, and PO presence. The LLM is NOT involved.",
            "data_state": "`routing: Literal['auto_approve', 'review_required']` — binary, deterministic.",
            "where": "Worker container, `workflow.routing_node`",
            "day": "Day 5 (LangGraph)",
        },
        5: {
            "title": "Evidence retrieval: Azure AI Search",
            "what": "If routing requires review: `VendorPolicyAgent` and `ComplianceAgent` query Azure AI Search with hybrid search. Each chunk carries a citation ID.",
            "data_state": "`List[EvidenceChunk]` — retrieved but not yet assessed. Still data-plane content.",
            "where": "Worker container, `retrieval` agents",
            "day": "Day 3 (retrieval); Day 5 (workflow step)",
        },
        6: {
            "title": "Planning: CaseFacts → ExecutionPlan",
            "what": "Azure OpenAI `gpt-4o` receives the `CaseFacts` (canonical invoice + evidence) and generates a typed `ExecutionPlan` using JSON schema structured output. The policy overlay runs next.",
            "data_state": "`ExecutionPlan` — typed JSON; validated by `PlanValidator`; policy overlay applied. If either fails: `EscalationPackage`.",
            "where": "Worker container, `planning.planner`",
            "day": "Day 4",
        },
        7: {
            "title": "Policy review: Day 7 safety gate",
            "what": "The Day 7 policy reviewer evaluates evidence sufficiency, authority satisfaction, and injection indicators. Produces one of three typed outcomes: `approved_to_proceed`, `needs_human_review`, `not_authorised_to_continue`.",
            "data_state": "`PolicyReviewDecision` — typed, includes reason codes, evidence IDs, policy IDs. Durable: persisted to checkpoint.",
            "where": "Worker container, `review.policy_reviewer`",
            "day": "Day 7",
        },
        8: {
            "title": "Checkpoint + HITL: durable pause/resume",
            "what": "LangGraph state is serialised and written to `workflow_checkpoints` in PostgreSQL. If human approval is needed, an `approval_task` row is created. On approval, the workflow resumes from the checkpoint.",
            "data_state": "Terminal outputs: `RecommendationPackage` (auto) or `HumanApprovalPackage` (pending). After resume: `RecommendationPackage`.",
            "where": "Worker container + PostgreSQL",
            "day": "Day 5",
        },
    }
    _d = steps[step.value]
    mo.callout(
        mo.md(f"""
    **Step {step.value}: {_d['title']}**

    **What happens:** {_d['what']}

    **Data state:** {_d['data_state']}

    **Where it runs:** `{_d['where']}`

    **Covered in depth:** {_d['day']}
        """),
        kind="success" if step.value in [3, 7, 8] else "info",
    )
    return


@app.cell
def _s6_header(mo):
    mo.md("""
    ## 6. Scoping Decisions: MVP, Production & Enterprise Scale
    """)
    return


@app.cell
def _s6_body(mo):
    mo.md("""
    One of the most valuable skills an FDE has is knowing what to defer.
    Shipping a scoped, working Day 4 MVP creates more real-world value than
    an overengineered system that takes three months to deploy.

    ### AegisAP Scoping Matrix

    | Capability | MVP (Day 4) | Production (Day 10) | Enterprise scale (Day 14) | Deferred rationale |
    |---|---|---|---|---|
    | Invoice extraction | ✅ In scope | ✅ In scope | ✅ In scope | Foundation capability |
    | Trust boundary validation | ✅ Canonical schema + deterministic normalization | ✅ In scope | ✅ In scope | Must exist before anything else scales |
    | Routing rules | ✅ Hardcoded thresholds | ✅ Config-driven + tested | ✅ Governed with approval ownership | Hardcoded is fine until rule change velocity rises |
    | Human approval | ❌ Sync placeholder | ✅ Durable HITL + resume | ✅ Delegated authority + actor verification | Requires workflow state and authority model |
    | Evidence retrieval | ❌ Mocked | ✅ Azure AI Search | ✅ Integrated enterprise evidence sources | Requires index provisioning and boundary control |
    | PII redaction | ❌ Not implemented | ✅ Boundary-level redaction | ✅ Audited redaction policy + evidence retention controls | No external sinks in MVP |
    | OTEL traces | ❌ `print()` logging | ✅ Azure Monitor + App Insights | ✅ SLO-driven ops + change gates | OTEL adds boilerplate before infra exists |
    | Cost governance | ❌ None | ✅ Cost ledger + gates | ✅ Budget ownership + exception process | No PAYG baseline data in MVP |
    | Multi-model routing | ❌ One model | ✅ Task-class routing | ✅ Portfolio optimization by workload class | Cannot optimise without baseline data |
    | IaC deployment | ❌ Manual ACA | ✅ Bicep + GitHub Actions | ✅ Policy-guarded multi-env promotion | Manual is fine for dev iteration |
    | Private networking | ❌ Not required for local learning | ⚠️ Design decided, may still be public in lower envs | ✅ Private endpoints + public access disabled | Enterprise constraint appears after platform maturity |
    | Integration boundary | ❌ Direct mocks only | ✅ Stable internal APIs | ✅ MCP / connector contracts + protocol governance | Avoid premature protocol design in MVP |
    | Change management | ❌ Manual judgment | ✅ Acceptance gates | ✅ Breaking-change review + elite ops traceability | Needs stable baseline before governance can bite |

    ### The Scoping Principle

    > **Build the trust boundary first.** Everything else can be deferred.
    >
    > If Day 4 does not have a clean `InvoiceCandidate → CanonicalInvoice` boundary,
    > every subsequent day inherits technical debt. The structure of the validated contract
    > dictates the schema of the database, the fields in the audit log, and the shape of
    > the evaluation dataset.

    ### Excellence principle

    Great Day 2 scoping separates three horizons clearly:

    1. **MVP:** prove the workflow and trust boundary.
    2. **Production:** prove reliability, safety, and operational readiness.
    3. **Enterprise scale:** prove delegated authority, network posture, protocol boundaries, and controlled change.
    """)
    return


@app.cell
def _exercises_header(mo):
    mo.md("""
    ## Exercises
    """)
    return


@app.cell
def _exercise_1(mo):
    mo.accordion({
        "Exercise 1 — Write NFRs for a New Agent Use Case": mo.vstack([
            mo.md("""
    **Scenario:** You are designing an agent that automatically triages IT support
    tickets — classifying severity, estimating resolution time, and routing to the
    appropriate team. The system handles ≈3,000 tickets/day.

    Write a complete NFR table with at least five rows, including:
    - One zero-tolerance NFR (hard constraint, not a best-effort target)
    - The metric name, numerical target, monitoring approach, and consequence of breach
            """),
            mo.accordion({
                "Show solution": mo.md("""
    | NFR | Metric | Target | Monitoring | Consequence |
    |---|---|---|---|---|
    | **P1/P2 ticket escalation recall** | Recall on high-severity tickets | **= 1.0** | Eval gate on each release | Release blocked; any miss is a P1 incident |
    | Classification latency | p99 end-to-end triage | < 10 s | App Insights trace | SLA breach; user complaint; fallback to manual |
    | Classification accuracy | Precision on auto-routed tickets | ≥ 97% | Weekly eval run against labelled test set | Rerouting cost; analyst complaint |
    | Cost per ticket | Token + infra cost | < £0.03 | Daily cost ledger alert | Budget overrun; requires model-tier review |
    | Availability | System uptime | 99.5% | ACA health probe + alert | Tickets queue up; manual fallback activated |
    | PII compliance | No ticket body text in traces | 100% | Log sampling + PII regex scan | GDPR breach; audit finding |
                """),
            }),
        ]),
    })
    return


@app.cell
def _exercise_2(mo):
    mo.accordion({
        "Exercise 2 — Write an ADR for a Technology Choice": mo.vstack([
            mo.md("""
    **Task:** Write a short ADR for the following decision:

    > *"For the IT ticket triage agent, we will use Azure AI Agent Service rather
    > than LangChain agents for orchestration."*

    Write the ADR using the template from Section 3, including:
    - Context (2–3 sentences)
    - Decision (1 sentence)
    - Rationale (2–3 bullet points)
    - At least two alternatives considered with rejection reasons
    - At least one consequence (positive) and one constraint (negative)
            """),
            mo.accordion({
                "Show solution": mo.md("""
    ```markdown
    # ADR-001: Azure AI Agent Service for ticket triage orchestration

    **Date:** 2026-03-31 | **Status:** Accepted | **Deciders:** Engineering lead, FDE

    ## Context
    The ticket triage agent needs an orchestration layer to manage tool calls (ticket lookup,
    knowledge base search, team routing API) and maintain conversation history per ticket.
    We need native Azure integration and minimal operational overhead.

    ## Decision
    Use Azure AI Agent Service (AIAS) as the orchestration layer.

    ## Rationale
    - AIAS is fully managed — no separate orchestration server to provision or scale
    - Native integration with Azure AI Search (knowledge base retrieval) without custom wrappers
    - Managed thread/memory storage eliminates our need to implement conversation history ourselves

    ## Alternatives considered
    - **LangChain agents** — rejected because they require self-managed state, no native Azure RBAC
      integration, and add a framework dependency with a faster-moving API surface
    - **LangGraph** — rejected for this use case because the triage workflow is linear, not
      graph-shaped; AIAS is simpler and sufficient

    ## Consequences
    - (+) No orchestration infrastructure to manage
    - (+) Native Managed Identity auth throughout
    - (-) Less flexible than LangGraph for future non-linear workflows; may require migration if
      requirements become more complex
    - (-) AIAS API is subject to Azure service versioning; migration effort if API changes
    ```
                """),
            }),
        ]),
    })
    return


@app.cell
def _exercise_3(mo):
    mo.accordion({
        "Exercise 3 — Identify and Defend Three Scoping Decisions": mo.vstack([
            mo.md("""
    **Task:** Review the AegisAP scoping matrix in Section 6. Choose three items
    that are **deferred from MVP** and write a one-paragraph defence for each, including:

    1. Why it is deferred (not just "to save time")
    2. What specific capability or data is missing in the MVP phase that makes it premature
    3. What triggers the decision to build it (the condition that moves it from deferred to in-scope)
            """),
            mo.accordion({
                "Show solution": mo.md("""
    **1. OTEL traces deferred from MVP:**
    Proper OTEL tracing requires an Application Insights connection string, which means
    the Azure Monitor resource must be provisioned and the OTEL distro configured. In the
    Day 4 MVP phase, the focus is on getting the extraction → validation → routing
    pipeline correct — traces would add setup overhead without yet having a system worth
    monitoring in production. The trigger to add OTEL: the first time a case fails in
    staging and `print()` output is insufficient to diagnose why.

    **2. Multi-model routing deferred from MVP:**
    Task-class routing optimises cost by routing low-complexity calls to cheaper models.
    But to know which task classes are low-complexity, you need baseline data: comparison
    of model outputs on real cases. Without a traffic baseline, routing decisions are
    guesses. The trigger to implement routing: 3 months of PAYG usage data showing which
    task classes consistently produce equivalent results on a cheaper model.

    **3. IaC deployment deferred from MVP:**
    Manual Azure Container Apps deployments are adequate for a development iteration cycle.
    IaC (Bicep + GitHub Actions) prevents configuration drift and enables team-wide
    reproducible environments — but writing and testing Bicep adds 1–2 days of scope.
    In the MVP phase, a single developer knows what is deployed because they deployed it.
    The trigger: a second developer joins, or the system needs to be deployed to a second
    environment (staging), at which point manual deployment creates divergence.
                """),
            }),
        ]),
    })
    return


@app.cell
def _reflection(mo):
    mo.md("""
    ## Production Reflection

    1. **Discovery gaps:** In your last project, which of the five discovery phases
       was skipped or rushed? What technical debt resulted?

    2. **Zero-tolerance NFRs:** Name one zero-tolerance NFR in a system you have
       worked on or are considering. What would the consequence of a single breach be,
       and how would you detect it in production?

    3. **Scoping regret:** Describe a capability that was built in the MVP that should
       have been deferred, or vice versa. What was the cost of the wrong scoping call?
    """)
    return


@app.cell
def _day2_unscaffolded_block(mo):
    from _shared.curriculum_scaffolds import render_unscaffolded_block

    render_unscaffolded_block(
        mo,
        title="Unscaffolded Afternoon Block — Scope Defense Without Notebook Hints",
        brief=(
            "Close the architecture diagrams and write a one-page scope defense for a "
            "new enterprise AI workflow. Name the MVP boundary, one zero-tolerance NFR, "
            "one explicit deferral, and the role that can overrule your scope call."
        ),
        done_when=(
            "The scope line is clear enough that another engineer could tell what is out of scope.",
            "At least one future capability is deferred with a named trigger for reconsideration.",
            "The defense uses business, governance, and technical language rather than only architecture jargon.",
        ),
    )
    return


@app.cell
def _summary(mo):
    mo.md("""
    ## Day 2 Summary Checklist

    - [ ] Run a structured discovery session and produce a problem statement with a measurable success metric
    - [ ] Write an NFR table with at least one zero-tolerance row and numerical targets for all rows
    - [ ] Write an ADR for a technology decision, including alternatives considered and consequences
    - [ ] Name the stakeholders who must sign off on scope, trust boundary, and production readiness
    - [ ] Explain how discovery outputs become adoption artifacts for later governance and operations
    - [ ] Explain each component in the AegisAP architecture and which day it is introduced
    - [ ] Trace all eight data-flow steps from raw invoice bytes to `RecommendationPackage`
    - [ ] Defend three scoping decisions across MVP, production, and enterprise-scale horizons
    """)
    return


@app.cell
def _forward(mo):
    mo.callout(
        mo.md("""
    **Tomorrow — Day 3: Azure AI Services & Agent Frameworks**

    Now that we have architecture blueprints and decisions on record, we go hands-on with 
    every Azure AI service in the stack. You will configure service clients with 
    `DefaultAzureCredential`, understand hybrid search and RRF, run a RAG pipeline against 
    mock vendor policy documents, and select the right agent framework for a given use case.
    The choices you make there should now feel anchored to explicit NFRs, ownership, and scope.

    Open `notebooks/day_3_azure_ai_services.py` when ready.
        """),
        kind="success",
    )
    return


@app.cell
def _fde_learning_contract(mo):
    mo.md(r"""
    ---
    ## FDE Learning Contract — Day 02: Discovery, Scoping, NFRs, and Stakeholder Power Mapping


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
    | Discovery Completeness | 20 |
    | NFR Quality With Numeric Targets | 20 |
    | Zero Tolerance NFR Identification | 20 |
    | Stakeholder Ownership Realism | 20 |
    | ADR Tradeoff Defense | 20 |

    Pass bar: **80 / 100**   Elite bar: **90 / 100**

    ### Oral Defense Prompts

    1. Which NFR did you classify as zero-tolerance and why can it not be tuned post-launch without a full change-board review?
    2. If the security stakeholder and the process owner disagree on latency vs control, whose position wins and through what governance mechanism?
    3. Who must approve the scope ADR in production, what evidence section would they challenge first, and what would trigger a rollback?

    ### Artifact Scaffolds

    - `docs/curriculum/artifacts/day02/STAKEHOLDER_MAP.md`
    - `docs/curriculum/artifacts/day02/RACI_MATRIX.md`
    - `docs/curriculum/artifacts/day02/NFR_REGISTER.md`
    - `docs/curriculum/artifacts/day02/ADR_001_SCOPE_AND_BOUNDARIES.md`

    See `docs/curriculum/MENTAL_MODELS.md` for mental models reference.
    See `docs/curriculum/ASSESSOR_CALIBRATION.md` for scoring anchors.
    """)
    return


if __name__ == "__main__":
    app.run()
