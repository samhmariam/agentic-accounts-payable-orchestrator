# INCIDENT COMMAND PLAYBOOK

<!-- CAPSTONE_B: This artifact applies to both AP and claims intake transfer domain -->

## Purpose

Provide the incident commander with a structured decision framework for the
war-game and production incidents, covering triage, communication, and authority.

## Required Headings

1. Incident severity classification — with observable signals and first-response actions per severity
2. Command structure — incident commander, technical lead, communications lead, and their handoff protocol
3. Triage order — the mental model for prioritising simultaneous failures
4. Communication cadence — who is briefed, how often, and in what format at each severity
5. Partial service continuation rules — conditions where partial operation is safe vs conditions where full stop is required
6. Stand-down procedure — what must happen before the incident is declared resolved

## Guiding Questions

- If three failures occur simultaneously, what is the decision framework for first action?
- What is the blast radius of continuing partial service when a binary gate is failing?
- Who declares the incident resolved and what evidence do they require?
- What does the post-incident report look like, and who receives it?

## Acceptance Criteria

- Severity classes have observable signals — not descriptions like "major outage"
- Triage order is a numbered priority list with the model behind it
- Partial service continuation rules are binary conditions — not judgement calls described as judgement calls
- Communication cadence specifies an update interval and a format for each severity
- Stand-down requires evidence — not just the incident commander's decision
