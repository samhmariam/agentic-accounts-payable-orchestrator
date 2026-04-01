# Daily Artifact Pack — Standard Structure

Every training day produces **four outputs**. This file describes the standard
directory structure and naming convention for the artifact pack submitted at
end-of-day.

The **exact artifact filenames** for each day are defined in
`docs/curriculum/CURRICULUM_MANIFEST.yaml` under `artifact_files`. This template
describes folder structure and content intent only.

---

## Directory Layout

```
dayNN_<trainee_id>/
├── LAB_OUTPUT/          # Technical build artifacts (code, config, diagrams)
├── DECISION_MEMOS/      # Design defense memos (ADRs and trade-off writeups)
├── PROCESS_ARTIFACTS/   # Corporate process artifacts (RACI, CAB packet, etc.)
├── RUBRIC/              # Self-assessment against the daily rubric criteria
└── ORAL_DEFENSE/        # Prep notes (not scored; submitted for completeness check)
```

---

## Output 1 — Technical Build (`LAB_OUTPUT/`)

**What goes here:** Code, configuration, diagrams, or analysis directly produced
by the lab exercise. File formats vary by day (`.py`, `.bicep`, `.json`, `.md`).

**Acceptance criteria:**
- Runnable or parseable in the format specified by the day's lab instructions
- Named exactly as specified in `CURRICULUM_MANIFEST.yaml artifact_files`
- No placeholder content (TODO stubs count as incomplete)

**Common failures:**
- Notebook screenshots instead of actual code files
- Renaming files to avoid overwriting previous day's work

---

## Output 2 — Design Defense Memo (`DECISION_MEMOS/`)

**What goes here:** One or more Architecture Decision Records (ADRs) or
trade-off writeups produced during the day.

**Minimum required sections per memo:**
1. Decision title and date
2. Status (proposed / accepted / superseded)
3. Context (what forced a decision)
4. Options considered (at least two)
5. Decision and rationale
6. Consequences (including downside of the chosen option)
7. Decision rights (who can reverse this and under what condition)

**Acceptance criteria:**
- At least one rejected alternative documented with specific rejection rationale
- Consequences section must name a blast radius scenario
- Decision rights section must name an approval role

---

## Output 3 — Corporate Process Artifact (`PROCESS_ARTIFACTS/`)

**What goes here:** Enterprise governance artifacts. Examples: RACI matrix,
CAB packet, approval authority model, risk register entry, SLA/OLA clause,
data authority chart, change classification record.

**Acceptance criteria:**
- Uses realistic enterprise role names (not "the team", "engineering")
- Approval chain is complete end-to-end
- Any zero-tolerance NFR touched that day appears in the artifact

**Common failures:**
- RACI matrices where every cell is "Responsible" (ownership not differentiated)
- CAB packets with no evidence section (assertions not evidence)

---

## Output 4 — Scored Oral Defense (`ORAL_DEFENSE/`)

**Trainee submits:** Prep notes only. These are checked for completeness (present
/ absent) but not scored. Oral performance is scored live by the panel using
`templates/ORAL_DEFENSE_SCORECARD.md`.

**Prep notes should contain:**
- Trainee's own answer sketch for each of the three standard prompts
- Any additional notes on rejected alternatives and blast radius

**What trainees must NOT include in prep notes:**
- Final answers written out verbatim (defeats the defense purpose)
- Content copied from the lab instructions

---

## Completeness Gate

The pack is only accepted if all four output folders are present and non-empty.
A missing folder counts as an incomplete submission. An incomplete submission
blocks progression per the zero-tolerance policy on Days 7, 10, 11, 12, and 14.

The `RUBRIC/` folder must contain the trainee's self-assessment against the
daily rubric. Self-assessment scores are not binding but are reviewed during
assessor calibration for disconnect patterns.
