# Assessor Calibration Guide

This guide prevents inter-assessor scoring drift on the oral defense component.
It provides anchor descriptions — **not answer keys** — for each scoring band
across the five dimensions.

Anchor descriptions describe the *quality of reasoning*, not the presence of
specific keywords. Two sentences per anchor maximum. Read the anchor, then listen
to the trainee. Do not look for the anchor sentence verbatim.

---

## Panel Composition and Tie-Breaking

**Panel size:** 2 assessors per session (1 lead, 1 shadow). For Days 10 and 14
final defenses, 3 assessors (1 lead, 2 shadows).

**Scoring:** Each assessor scores independently. The lead records the final score.
For each dimension where the two scores differ by more than 3 points, assessors
must verbally confer before the lead finalises.

**Tie-breaking:** If assessors still disagree after conferring, the lower of the
two scores applies. Trainees should not benefit from assessor uncertainty.

**Declaration:** Any assessor who coached the trainee on a capstone or worked
directly with them on Day 13–14 artifacts must declare a conflict. A replacement
assessor must be appointed.

---

## Dimension 1 — Technical Accuracy and Build Quality

*Scored 0–35 on full rubric. Oral defense contribution assessed here as: does the
trainee's explanation reveal understanding or reveal memorisation?*

| Band | What it looks like |
|---|---|
| **Exceptional (32–35)** | Trainee identifies the failure mode that would surface first in production, and explains why their implementation prevents or surfaces it earlier than alternatives. |
| **Proficient (26–31)** | Trainee explains trade-offs correctly but stays at the happy-path level; edge cases are acknowledged but not deeply analysed. |
| **Developing (18–25)** | Trainee describes what the implementation does but falls back on "it works in tests" without connecting to production risk. |
| **Beginning (0–17)** | Trainee cannot explain why key implementation choices were made, or contradicts the artifact they submitted. |

---

## Dimension 2 — Design Defense and Trade-Off Clarity

*Assessed primarily through oral defense prompt 1 (rejected alternative).*

| Band | What it looks like |
|---|---|
| **Exceptional (18–20)** | Trainee articulates the winning alternative's weakest point and the condition under which they would have chosen differently; demonstrates real decision ambiguity was resolved. |
| **Proficient (14–17)** | Trainee names a credible alternative, gives a reason for rejection, but does not identify conditions under which that decision reverses. |
| **Developing (9–13)** | Trainee names an alternative but the rejection reason is vague ("it was more complex") without specifying the specific downside relative to requirements. |
| **Beginning (0–8)** | Trainee names no credible alternative or states the chosen approach was obviously correct; reasoning is circular. |

---

## Dimension 3 — Enterprise Process Fluency

*Assessed primarily through oral defense prompt 3 (who must approve / what evidence).*

| Band | What it looks like |
|---|---|
| **Exceptional (14–15)** | Trainee names the approval role, the artefact that role would sign, and what would cause that role to reject the submission. |
| **Proficient (11–13)** | Trainee names the approval role and a plausible artefact but cannot specify what would trigger rejection. |
| **Developing (7–10)** | Trainee knows approval is required but conflates roles (e.g., "legal or compliance") or names an artefact that does not match the governance step. |
| **Beginning (0–6)** | Trainee treats approval as a formality with no specific role, artefact, or criteria named. |

---

## Dimension 4 — Risk Articulation and Safety Reasoning

*Assessed primarily through oral defense prompt 2 (blast radius) and any
zero-tolerance condition.*

| Band | What it looks like |
|---|---|
| **Exceptional (14–15)** | Trainee scopes the blast radius precisely: which users or processes are affected, by what mechanism, and what the recovery timeline would be. |
| **Proficient (11–13)** | Trainee identifies the primary failure mode and affected component but does not trace the downstream cascade or quantify recovery cost. |
| **Developing (7–10)** | Trainee identifies that something could go wrong but stays at the level of "it would break" without naming the affected component, users, or recovery action. |
| **Beginning (0–6)** | Trainee dismisses risk ("it would just fail safely") or conflates risk with inconvenience. |

---

## Dimension 5 — Communication Fitness for Role

*Assessed across the whole defense. Would a CISO, CAB chair, finance controller,
or external auditor find this explanation sufficient?*

| Band | What it looks like |
|---|---|
| **Exceptional (14–15)** | Trainee frames answers at the appropriate altitude for the role named in the prompt; does not need prompting to adjust register. |
| **Proficient (11–13)** | Trainee communicates accurately but at uniform technical depth regardless of the role implied by the prompt. |
| **Developing (7–10)** | Trainee's answer would need translation before reaching a business or audit audience; technical framing dominates throughout. |
| **Beginning (0–6)** | Trainee cannot adjust the framing even when explicitly asked to explain "as if to the board" or "as if to external audit". |

---

## Common Scoring Errors to Avoid

1. **Keyword credit.** Do not award points because the trainee used the right
   word (e.g., "blast radius"). Award points based on quality of reasoning.

2. **Confidence credit.** Fluent confident delivery does not raise a score.
   Hesitant but structurally correct reasoning does not lower a score.

3. **Artifact rescue.** If the trainee's artifact was weak, a brilliant oral
   defense cannot rescue it. The oral defense dimension scores oral performance
   only; artifact quality is scored under dimensions 1–4 on the submitted artifact.

4. **Questions as hints.** Panel members may ask one clarifying follow-up per
   dimension. Do not reframe or lead — ask only "Can you say more about that?"
   or "What would change if X were different?"

5. **Capstone B scoring.** For Day 12–14 defenses, the transfer domain
   (customer onboarding) is the primary scoring domain, not accounts payable.
   A trainee who answers only in AP terms scores as Developing on dimensions 2–5.

6. **Rubber-stamping peer review.** A peer who asks weak questions or accepts
   claims without evidence is underperforming as a reviewer. Record
   `peer_reviewer_challenge_quality` explicitly; weak challenge quality blocks
   Top Talent until reviewer remediation is complete.

## Peer Reviewer Accountability

For Day 10 and capstone `cab_board` sessions, the facilitator also scores the
peer reviewers.

- `peer_reviewer_challenge_quality = 5`: reviewer asks probing role-appropriate questions, requests concrete evidence, and tests the native proof live when needed
- `peer_reviewer_challenge_quality = 5` also requires replaying saved KQL proof and challenging Revert Proof when Day 10 or capstone evidence depends on them
- `peer_reviewer_challenge_quality = 3`: reviewer is credible but misses one major evidence gap
- `peer_reviewer_challenge_quality = 1`: reviewer rubber-stamps, avoids skepticism, or never asks for evidence

Scores below `3` require remediation and block `Top Talent` even if the learner's
own technical defense is strong.
