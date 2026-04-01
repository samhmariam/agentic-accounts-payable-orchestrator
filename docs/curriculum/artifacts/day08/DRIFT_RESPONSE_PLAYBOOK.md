# DRIFT RESPONSE PLAYBOOK

## Purpose

Provide step-by-step response procedures for configuration drift events in IaC,
identity, and pipeline components — before they become incidents.

## Required Headings

1. Drift detection inventory — what is monitored for drift and by what mechanism
2. Drift severity classification — how severity is determined and what response each severity triggers
3. Response procedure per drift class — step-by-step for each class
4. Escalation criteria — when drift response escalates to an incident
5. Post-drift review — what must be documented after a drift event is resolved

## Guiding Questions

- Which drift class is most likely to go undetected for more than one hour?
- If pipeline identity drift causes a deployment failure at 02:00, who is the first call and what is the first command?
- What distinguishes a drift event from a deliberate approved change that was not reflected in IaC?
- What is the minimum evidence that an auditor would require after a drift event in a financial system?

## Acceptance Criteria

- Minimum 4 drift classes (IaC, pipeline identity, secrets, network/firewall are starting points)
- Each class has a specific detection mechanism (not "monitored")
- Each high-severity response procedure is step-by-step, not descriptive
- Escalation criteria are observable signals, not subjective judgements
- Post-drift review names required fields in the incident record
