# Day 1 — Intake & Canonicalization · Trainer Guide

> **Session duration:** 2.5–3 hours (40 min theory + 2 h lab)  
> **WAF Pillars:** Security · Reliability  
> **Prerequisite:** Day 0 complete; Foundry OpenAI-compatible deployment responding

---

## Session Goals

By the end of Day 1, every learner should be able to:
- Explain the separation between extraction (LLM), normalization (Python), and validation (Python)
- Run `run_day1_intake.py` in both `fixture` and `live` modes
- Read the `golden_thread_day1.json` artifact and interpret each field
- Articulate why a rejected invoice is a correct outcome, not a system failure

---

## Preparation Checklist

- [ ] Day 0 complete: `verify_env.py --track core` exits 0
- [ ] `fixtures/golden_thread/package.json` and `candidate.json` present
- [ ] OpenAI-compatible deployment name matches `AZURE_OPENAI_CHAT_DEPLOYMENT` in the loaded Day 0 state
- [ ] Run `scripts/run_day1_intake.py --mode fixture` yourself before the session
      to confirm `build/day1/golden_thread_day1.json` is generated correctly

---

## Theory Segment (40 min)

### Block 1: Trust Boundaries in AI Systems (15 min)

**Talking points:**
1. Draw the intake pipeline on the whiteboard:
   ```
   Raw invoice bytes
        │
        ▼
   [ Extraction — probabilistic ]
        │
        ▼
   [ Normalization — deterministic ]
        │
        ▼
   [ Validation — binary decision ]
        │
      ┌─┴─┐
   Rejected  CanonicalInvoice
   ```
2. Emphasise: "The LLM's only job is to *extract*. Once the data enters
   Python, it is deterministic Python all the way down."
3. Ask: "What would happen if we let routing decisions happen in the same
   prompt as extraction?" (Answer: untestable, un-auditable, non-deterministic.)
4. Contrast with a naive "send everything to the LLM and get back a decision"
   approach. Show the failure mode: the LLM may make up a vendor ID if the
   document is unclear.

**Key message:** "LLMs are extractors. Python is the authority."

---

### Block 2: The CanonicalInvoice Contract (15 min)

**Talking points:**
1. Open `src/aegisap/day_01/` in the editor. Walk through:
   - The `InvoiceCandidate` schema (raw extraction output, may have nulls)
   - The `CanonicalInvoice` schema (validated, typed, no nulls on required fields)
2. Point out `Decimal` vs `float` for the `amount` field. Show a live demo:
   ```python
   0.1 + 0.2  # Python float: 0.30000000000000004
   from decimal import Decimal
   Decimal("0.1") + Decimal("0.2")  # Decimal: 0.3
   ```
3. Explain that `invoice_date` must be ISO 8601 and not in the future.
   Ask: "Why 'not in the future'? What business rule does that enforce?"
4. Walk through one rejection example. Show the `IntakeRejectionError` class
   and explain why the `reason` field is an enum, not a free-text string.

---

### Block 3: Azure OpenAI Extraction in Practice (10 min)

**Talking points:**
1. Show the extraction prompt in `src/aegisap/day_01/agent.py`.
   Point out:
   - `temperature=0` (no creativity in extraction)
   - `response_format` with JSON schema mode (`strict=True`)
   - System message vs. human message content separation
2. Explain `fixture` vs `live` mode — why all learners always start with fixture
   mode to decouple from network and quota variability.
3. Briefly explain that Day 9 will add routing logic that decides *which*
   model deployment is used for which task class.

---

## Lab Walkthrough Notes

### Key cells to call out in `day1_intake_canonicalization.py`:

1. **`_extract` cell** — shows the raw `InvoiceCandidate` from fixture mode.
   Point out the optional fields that *might* have been null in a live extraction.

2. **`_canonicalize` cell** — apply the normaliser. Show step by step what each
   normalisation does: currency uppercasing, date parsing, rounding.

3. **`_validate` cell** — run validation against the business rules. Ask
   learners to introduce a deliberate error (wrong currency code) and observe
   the rejection.

4. **Rejection cell** — walk through the rejection path. Emphasise the
   `rejection_reason` field and how it maps to an auditable enum.

5. **Output cell** — open `build/day1/golden_thread_day1.json` and compare
   with the notebook display.

### Expected lab friction points

| Issue | Likely cause | Resolution |
|---|---|---|
| `ModuleNotFoundError: aegisap` | `.venv` not active or `pip install -e .` not run | `pip install -e .` in the root |
| Live mode 401 error | Missing OpenAI RBAC role | Verify Day 0; re-run role assignments Bicep |
| `golden_thread_day1.json` empty | Exception during canonicalization | Check the rejection reason in the notebook output |

---

## Facilitation Addendum

### Observable Mastery Signals

- Learner can show why the rejection happened from the artifact rather than notebook prose.
- Learner keeps extraction, normalization, and validation separate in their explanation.
- Learner treats malformed input as a first-class product outcome, not a failure to be hidden.

### Intervention Cues

- If a learner wants to push validation rules into the prompt, stop and restate the trust-boundary ownership model.
- If money handling drifts toward `float`, force a quick precision demo before proceeding.
- If the malformed fixture passes, have the learner compare the artifact to the schema instead of editing prompts blindly.

### Fallback Path

- If Azure OpenAI is unavailable, run the lab in fixture mode and keep the discussion focused on deterministic validation.

### Exit Ticket Answer Key

1. Validation is the authority layer; the LLM only extracts.
2. Structured rejections remain queryable and auditable.
3. `uv run python scripts/run_day1_intake.py --mode fixture` is the correct deterministic rebuild command.

### Time-box Guidance

- Limit live prompt discussion to 10 minutes; the core objective is schema and boundary reasoning.
- If learners are blocked on a malformed case for more than 12 minutes, switch them to artifact inspection and targeted comparison.

---

## Common Misconceptions

| Misconception | Correction |
|---|---|
| "The LLM validates the invoice" | The LLM only extracts. Python runs every validation rule. |
| "A rejection means the system failed" | A rejection means the system correctly identified an untrusted input |
| "`strict=True` in structured outputs means the data is valid" | It means the *schema* is structurally satisfied. Business logic validation still runs in Python. |
| "`float` is fine for money — it's just a display" | Rounding errors accumulate. In line-item reconciliation, `float` will fail the sum check on valid invoices. |

---

## Discussion Prompts

1. "What if a vendor OCRs their invoice in a non-English locale — would the
   extraction prompt need to change? Should normalization change?"

2. "At what point should we enrich the `CanonicalInvoice` with vendor master
   data? Before or after the trust boundary? Why?"

3. "A junior engineer suggests putting the validation rules in the LLM prompt
   to save on code. What are three problems with that approach?"

---

## Expected Q&A

**Q: What happens if Azure OpenAI returns a `null` for a required field in structured output mode?**  
A: `strict=True` prevents null on required fields — the model must include the
field. But the model can still produce logically invalid values (e.g., a valid
string for `currency` that isn't an ISO 4217 code). That's why Python
validation is always the second line of defence.

**Q: Why not use a database to deduplicate invoice IDs at the extraction step?**  
A: Day 1 sits at the very edge of the system — its job is to produce a
canonical shape. Deduplication against a live database is a Day 5 responsibility
(idempotency at the checkpoint level), not a trust boundary concern.

**Q: Can we handle multiple invoices in one API call for efficiency?**  
A: Batch extraction is possible with structured output arrays, but it complicates
per-invoice rejection logic (what do you do if two of three are valid?). For
the training, single-invoice extraction keeps the logic clean. Batching is a
valid day-2 optimisation after the pattern is established.

---

## Next-Day Bridge (5 min)

> "Today we established the trust boundary. We have one reliable, typed
> `CanonicalInvoice` object. Tomorrow it becomes the input to a stateful
> workflow — and we'll see for the first time what explicit state management
> buys us. The canonical invoice won't change, but the system around it will
> become dramatically more observable."
