# AegisAP Graduation Rubric

Defines the three FDE graduation tiers. All score thresholds and completion
requirements refer to the 100-point daily model in `ASSESSMENT_RUBRIC.md`.
Zero-tolerance conditions are the authoritative list in `CURRICULUM_MANIFEST.yaml`.

---

## Tier 1 — Graduate

**Minimum average score:** 80 / 100

**Requirements:**
- All 14 daily scores ≥ 80
- All zero-tolerance conditions passed across all days
- No hard-fail days remaining (any re-sat days must have passing scores on record)
- Capstone A (AegisAP production defence) submitted and accepted
- No major process-fluency weakness (no day scored < 6 on Process Fluency)

**What this means:**
The engineer can build, deploy, and operate an agentic system on Azure using the
patterns taught in this programme. They meet the minimum bar for production FDE work.

---

## Tier 2 — Strong FDE

**Minimum average score:** 85 / 100

**Additional requirements beyond Graduate:**
- Defends trade-off reasoning across at least three different days without prompting
- Produces artifacts that are reusable by a future cohort without editing
- Handles at least one hostile or adversarial reviewer scenario (documented in
  trainer notes or oral defense record)
- No day scored < 10 on Trade-off Reasoning

**What this means:**
The engineer can lead an agentic solution design, represent it in architecture
reviews, and produce governance artifacts a real enterprise would accept.

---

## Tier 3 — Top Talent

**Minimum average score:** 90 / 100

**Additional requirements beyond Strong FDE:**
- Passes Capstone B (transfer capstone) — applies all programme mental models to
  a domain they have not memorised (claims intake or customer onboarding)
- Can explain technical design to executives without losing precision
- Can explain the same design to auditors, security reviewers, and operators using
  domain-appropriate evidence
- Makes correct go/no-go decisions under pressure using gate evidence, not instinct —
  demonstrated in Day 14 war-game or equivalent incident drill
- No zero-tolerance failures across any day, including transfer capstone days
- No `peer_reviewer_challenge_quality` score below `3` on any Day 10 or capstone
  board assignment; reviewer remediation is required before Top Talent can be awarded

**What this means:**
The engineer operates at elite FDE level. They are capable of leading a production
agentic system through CAB, security review, executive sign-off, and incident
command simultaneously. They transfer skills to new domains without needing domain
pre-loading.

---

## Assessment Chain

1. Daily scores are recorded by trainer in `docs/curriculum/templates/DAILY_SCORECARD.md`
2. Zero-tolerance judgments are logged per day with condition, evidence, and trainer signature
3. Capstone A review is conducted per `capstone/CAPSTONE_A.md`
4. Capstone B is conducted per `capstone/CAPSTONE_B.md`
5. Final tier determination is made by programme lead with evidence from all 14 days
6. Reviewer accountability and any remediation for weak `peer_reviewer_challenge_quality`
   must be resolved before a Top Talent decision is finalized

---

## Re-Sit Policy

- Any day that hard-fails due to zero-tolerance must be re-sat
- Re-sat score replaces original score for graduation average calculation
- A day may only be re-sat once; a second failure requires programme-level review
- Re-sat days count toward the total but are flagged in the graduation record
