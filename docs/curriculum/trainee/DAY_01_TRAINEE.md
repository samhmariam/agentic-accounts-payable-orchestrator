# Day 1 — Intake & Canonicalization · Trainee Pre-Reading

> **WAF Pillars:** Security · Reliability  
> **Time to read:** 20 min  
> **Lab notebook:** `notebooks/day1_intake_canonicalization.py`

---

## Learning Objectives

By the end of Day 1 you will be able to:

1. Explain why **extraction** and **normalization** must be kept separate from each other.
2. Define a *trust boundary* and identify where it sits in AegisAP.
3. Describe how Azure OpenAI Service is used as an extractor, not a decision-maker.
4. Read a `CanonicalInvoice` schema and explain what makes each field mandatory.
5. Explain why a rejected invoice is a successful system outcome, not a failure.

---

## 1. The Role of the Trust Boundary

Enterprise AI systems must decide, at a single point, what data is trustworthy
enough to enter the processing pipeline. Everything upstream of that point is
**untrusted input**. Everything downstream is a **controlled artefact** that the
system stands behind.

Without a trust boundary:
- Malformed data propagates deep into business logic before failing.
- Errors become expensive to diagnose because the corruption is hidden.
- Audit trails cannot pinpoint where bad data entered the system.

**AegisAP's trust boundary is day 1.** An invoice package arrives as raw bytes.
It leaves Day 1 as a `CanonicalInvoice` object or it is **explicitly rejected**.
There is no third outcome.

```
Raw invoice package
      │
      ▼
[ Extraction — Azure OpenAI ]    ← probabilistic, ML, uncertain
      │
      ▼
[ Normalization — Python ]       ← deterministic, strict, typed
      │
      ▼
[ Validation — Python ]          ← reject or pass
      │
    ┌─┴─┐
 Rejected  CanonicalInvoice      ← only these two outcomes exist
```

---

## 2. Extraction vs. Normalization vs. Validation

These three steps are conceptually distinct and should never be mixed:

| Step | Tool | Output | Nature |
|---|---|---|---|
| **Extraction** | Azure OpenAI (few-shot prompt) | `InvoiceCandidate` | Probabilistic — may contain nulls, wrong types, ambiguous values |
| **Normalization** | Deterministic Python | Typed fields, canonical currency codes, ISO dates | Deterministic — given the same input, always the same output |
| **Validation** | Python (Pydantic/custom rules) | Pass or explicit rejection | Deterministic — binary decision with a reason code |

### Why keep them separate?

If normalization and validation logic live inside the LLM prompt, the system
cannot test them independently. A prompt change might silently break a rule that
was previously reliable. By keeping normalization in Python, you can write unit
tests that never call the API.

### Azure best practice
Use Azure OpenAI `structured outputs` (JSON mode + `response_format`) to
constrain extraction output to a JSON schema. This reduces hallucinated field
names and type mismatches but **does not substitute for Python validation** — the
model can still produce logically invalid values that satisfy the schema.

---

## 3. Azure OpenAI Service as an Extractor

### What Azure OpenAI does in Day 1

The LLM reads the raw invoice text and fills in an `InvoiceCandidate` template.
It is doing the job a human would do if asked "read this PDF and fill in this
form." The LLM does **not**:

- Apply business rules
- Make approval decisions
- Persist any data
- Call any other service

### Model selection guidance

| Model | Use for extraction? | Why |
|---|---|---|
| `gpt-4o` | Yes (default) | Strong JSON adherence, fast enough for synchronous intake |
| `gpt-4o-mini` | Yes, for cost-sensitive bulk | Slightly lower accuracy on noisy OCR; test before deployment |
| `o1` / `o3` | Overkill | Reasoning models add latency and cost with no measurable accuracy gain for structured extraction |

### Azure best practice
- Deploy one model per **named deployment** (e.g., `gpt-4o-intake`).
- Pin the deployment name in the environment variable (`AZURE_OPENAI_DEPLOYMENT`),
  not in source code, so you can swap model versions via config without a code change.
- Set `temperature=0` for extraction — you want deterministic, not creative.

---

## 4. The CanonicalInvoice Contract

A `CanonicalInvoice` is a **typed, validated, immutable record** that the rest of
the system depends on. Its fields are:

| Field | Type | Rule |
|---|---|---|
| `invoice_id` | `str` | Normalised to uppercase; must be unique in this pipeline run |
| `vendor_id` | `str` | Must match a known vendor; rejected if unknown |
| `amount` | `Decimal` | Normalised to two decimal places; never `float` (rounding errors) |
| `currency` | `str` | ISO 4217 three-letter code (e.g., `GBP`) |
| `invoice_date` | `date` | ISO 8601 format; must not be in the future |
| `po_number` | `str \| None` | Optional; if present, validated against PO registry |
| `line_items` | `list[LineItem]` | At least one item; amounts must sum to `amount` |

`Decimal` is mandatory for monetary amounts because `float` in Python (and in
JSON) cannot represent all currency values exactly.

---

## 5. Rejection as a First-Class Outcome

A well-designed system expresses its refusals as clearly as its successes.

Bad pattern:
```python
return None  # nobody knows why
```

Good pattern:
```python
raise IntakeRejectionError(
    reason=RejectionReason.AMOUNT_MISMATCH,
    detail="Line items sum to 12400.00 but header claims 12500.00",
)
```

The rejection is **logged, structured, and auditable**. Downstream systems (and
human reviewers) see exactly why a case was rejected without debugging logs.

### Azure best practice
Emit every rejection as a structured Application Insights event with the
`rejection_reason` dimension. This makes it queryable: "how many invoices were
rejected for `AMOUNT_MISMATCH` in the last 30 days?"

---

## 6. Determinism in Fixture Mode

AegisAP supports two intake modes:

| Mode | Calls Azure OpenAI? | Use for |
|---|---|---|
| `fixture` | No — loads pre-extracted `candidate.json` | CI/CD, local dev, training labs |
| `live` | Yes | Testing against real model endpoints |

In training, **fixture mode** ensures that every learner works with the same
`InvoiceCandidate` values, so the focus is on normalization and validation logic
rather than prompt variability.

---

## Glossary

| Term | Definition |
|---|---|
| **Trust boundary** | The point in a system where untrusted input is validated and either accepted or explicitly rejected |
| **InvoiceCandidate** | Raw extraction output from the LLM — may have null fields or wrong types |
| **CanonicalInvoice** | Validated, typed, immutable record that downstream components can trust |
| **Structured outputs** | Azure OpenAI feature that constrains the model to produce valid JSON for a given schema |
| **Rejection reason code** | A machine-readable enum value that explains *why* a case was rejected |
| **Fixture mode** | Replaces a live service call with a static pre-recorded response |

---

## Check Your Understanding

1. What is the difference between an `InvoiceCandidate` and a `CanonicalInvoice`? Which one does the LLM produce?
2. Why should normalization logic live in Python rather than in the LLM prompt?
3. What Azure OpenAI setting do you use to reduce hallucinated field names during extraction?
4. Why is `Decimal` used instead of `float` for monetary amounts?
5. Give an example of a well-structured rejection and explain what makes it better than returning `None`.

---

## Lab Readiness

- **Lab duration:** 2.5 hours
- **Required inputs:** `build/day0/env_report.json`, golden-thread fixture package, and `notebooks/day1_intake_canonicalization.py`
- **Expected artifact:** `build/day1/golden_thread_day1.json`

### Pass Criteria

- The notebook emits either a valid canonical invoice or an explicit rejection.
- A seeded malformed case is rejected deterministically with the correct reason code.
- You can explain which logic lived in the LLM and which logic stayed deterministic in Python.

### Common Failure Signals

- The acceptance or rejection changes based on prompt wording instead of deterministic validation.
- Money is handled with `float` instead of `Decimal`.
- A malformed case is accepted without a machine-readable rejection reason.

### Exit Ticket

1. Which layer owns schema truth: extraction, normalization, or validation?
2. Why is a structured rejection better than returning `None`?
3. What exact command would you use to regenerate the Day 1 artifact in fixture mode?

### Remediation Task

Re-run the deterministic intake path with:

```bash
uv run python scripts/run_day1_intake.py --mode fixture
marimo edit notebooks/day1_intake_canonicalization.py
```

Then inspect `build/day1/golden_thread_day1.json` and explain why the result is
safe to hand off to Day 2.

### Stretch Task

Describe one additional rejection reason you would add for malformed supplier
identity and how you would keep that reason code queryable in downstream metrics.
