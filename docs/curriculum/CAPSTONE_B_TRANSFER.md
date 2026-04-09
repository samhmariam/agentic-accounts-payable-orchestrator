# Capstone B — Transfer Domain Specification

<!-- CAPSTONE_B -->

## Purpose

Capstone B tests whether the trainee can apply every AegisAP pattern to an
unfamiliar domain with different schema, different compliance constraints, and
different stakeholder vocabulary — without template drift into familiar territory.

## Transfer Domains

### Primary: Claims Intake (Medical Supplier)

A medical equipment supplier submits insurance claims for durable medical
equipment (DME) supplied to patients. The claims intake workflow receives
structured claim packages, validates them against authorisation records, checks
medical codes, and routes high-value or exception claims for human review.

**Key differences from AegisAP invoices:**

| Dimension | Invoices (AP) | Claims (DME) |
|---|---|---|
| Primary identifier | Invoice number | Claim number |
| Approval authority | Finance Controller | Claims Adjudicator |
| Compliance regime | Procurement policy | Healthcare billing regulation |
| Zero-tolerance failure | Wrong supplier paid | Upcoding or unbundling |
| HITL trigger | High-value threshold | Medical necessity exception |
| Data authority | ERP system of record | Insurance payer portal |

**Use this domain for:** Days 12, 13, 14 primary deliverables and all oral
defense prompts at Capstone B.

### Secondary: Customer Onboarding (Product Extension)

A software vendor onboards enterprise customers through a multi-step approval
workflow: contract review, identity provisioning, environment setup, and
compliance attestation. The agent automates the process from signed contract
through activated account.

**Use this domain for:** corroboration questions in Days 12/13 oral defenses
where the assessor wants to stress-test breadth of transfer.

---

## Trainee Fixture Access

Trainee-visible fixtures are in `fixtures/capstone_b/claims_intake/`. The
trainee is told that a sixth "assessor-only" case exists but they have not
seen it. The purpose of this case is to test whether their implementation
handles adversarial input from outside their training distribution.

Trainee-visible fixtures cover:

| Case | Description |
|---|---|
| `claim_001_routine.json` | Routine low-value DME claim, all fields present and valid |
| `claim_002_high_value.json` | High-value claim above authorisation threshold — triggers HITL |
| `claim_003_missing_auth.json` | Missing prior-authorisation reference inside nested supportingInfo — must escalate or refuse |
| `claim_004_code_mismatch.json` | Procedure code inconsistent with diagnosis — must flag |
| `claim_005_duplicate.json` | Duplicate claim number — idempotency and deduplication test |

---

## Assessor-Only Case

`fixtures/capstone_b/_assessor_only/claims_intake/claim_006_assessor_only.json`

This case contains a subtle encoding inconsistency designed to test whether the
trainee's pipeline handles an unfamiliar but structurally valid nested Claim
payload without silently passing incorrect data downstream. Assessors provide
this case after the trainee has demonstrated their pipeline with the five
trainee cases.

**Do not distribute this file to trainees at any point before the defense.**

---

## Capstone B Scoring Model

Capstone B uses the same 100-point rubric as every other day. The key difference:

- Scoring is in the **claims intake domain**, not accounts payable
- A trainee who answers oral defense prompts using AP examples without
  connecting explicitly to claims intake scores as **Developing** on dimensions
  2–5 regardless of technical correctness
- The CAPSTONE_B marker must appear in the primary doc for Days 12, 13, 14

**Transfer adequacy test:** The assessor presents the assessor-only case after
the five trainee cases. The trainee must explain what their implementation would
do with this case and why. This is scored under dimension 1 (technical accuracy).

---

## Customer Onboarding Fixtures

`fixtures/capstone_b/customer_onboarding/`

| Case | Description |
|---|---|
| `onboarding_001_standard.json` | Standard enterprise onboarding — all required fields |
| `onboarding_002_compliance_hold.json` | Onboarding blocked on compliance attestation — requires HITL |
