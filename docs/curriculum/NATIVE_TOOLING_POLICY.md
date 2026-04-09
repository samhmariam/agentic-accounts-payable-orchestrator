# Native Tooling Policy

This policy governs the raw-operator evidence contract for Wave 3 and Wave 4.

## Purpose

The curriculum stops rewarding wrapper memorization on Day 04. From Day 04 onward,
learners must prove they can find, interpret, and defend production signals with
native tooling before they rely on any lab helper flow.

## Day Bands

- Day 04: save at least 1 native command tied to the policy or posture failure domain.
- Days 05-08: save at least 1 native command and 1 raw KQL query.
- Days 09-14: save at least 2 native commands and 1 raw KQL query.
- Days 08-14: also save `diagnostic_timeline.md` and enough pre-patch proof to
  establish diagnostic independence.
- Days 12 and 14: the live-demo witness fields are mandatory.
- Day 10 CAB review: the release packet is incomplete unless Days 05-09 native and
  KQL evidence are structurally valid and replay-ready.

## Machine-Readable Diagnostic Hygiene

- Azure CLI diagnostics must append `-o json` unless the day explicitly documents another machine-readable output format.
- `observed_excerpt` is graded as diagnostic output, not as a free-form note.
- Day contracts may enforce required command and output signal families; generic commands such as `az account show` do not count unless the day explicitly allows them.

## Allowed Tools

- Azure Portal
- `az`
- `az rest`
- raw KQL in Log Analytics or the Azure Portal query surface
- `curl`
- `git`
- `nslookup`
- `Resolve-DnsName`

## Banned During Investigation And Evidence Capture

- `aegisap-lab` helper commands used to discover the answer
- canned verification wrappers
- step-by-step answer keys
- any replay flow that hides the literal command, request, or query text the learner
  actually relied on

## Wrapper Use After Evidence Capture

Once both raw evidence files are complete, wrappers may be used again only for:

- artifact rebuild flows
- mastery validation
- drill reset or incident reset flows

They may not be used retroactively to discover the answer and then backfill the
saved command text.

## Evidence Artifacts

Each day from 04-14 must preserve:

- `build/dayX/native_operator_evidence.json`
- `build/dayX/kql_evidence.json` on Days 05-14
- `build/dayX/diagnostic_timeline.md` on Days 08-14

Those files must contain the literal commands and literal query text the learner
used, plus the operator interpretation that explains why the evidence mattered.

For Days 08-14, the evidence must also prove ordering:

- pre-patch telemetry must be captured before the repair is applied
- repo search before first telemetry capture forces `Diagnostic Independence = 0`
- hint-ladder intervention forces `Diagnostic Independence = 0`

## Live Audit Rule

Facilitators may randomly require the learner to clear recent terminal-history
context, rerun one saved native command or KQL query live, and explain the result
before mastery is accepted. This is the enforcement mechanism for authenticity in
this tranche.
