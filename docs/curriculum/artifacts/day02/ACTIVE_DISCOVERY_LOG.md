# Day 2 Active Discovery Log

## Interview Context

- Stakeholder interviewed:
- Delivery mode: triad roleplay
- Observer-scribe:

## Required Questions Asked

1. Which reliability or queue-safety control is non-negotiable even under spike traffic?
   Stakeholder Answer: "During end-of-month closing, we get hit with thousands of invoices at once. Even if the agentic system is choking on the volume, it can never bypass the idempotency check against our ERP system. I don't care if invoices sit in the Azure Service Bus queue for 12 hours—we cannot risk the agent issuing a duplicate payment because the system was trying to process items too quickly."  
2. Who owns the decision if throughput and auditability conflict in production?
   Stakeholder Answer: "If the agent is running too slowly because it's generating massive reasoning traces for every invoice (Model Context Protocol logging) and we need to speed it up by cutting back on the logs, that decision does not belong to Engineering. The Chief Risk Officer (CRO) owns that decision. We cannot sacrifice our audit trail for processing speed without compliance sign-off."
3. What evidence would justify a rollback if the throughput change harms safe processing?
   Stakeholder Answer: "If the cost-speed routing controls route complex invoices to a faster, cheaper LLM, and we see the agent hallucinating or skipping the Purchase Order (PO) matching step. Specifically, if the 'PO Mismatch' rejection rate from the downstream ERP hits >2% of agent-approved invoices, we immediately roll back to the slower, highly-accurate model routing."

## Extracted Constraints

- Hidden NFR surfaced:
  LLM Reasoning Retention. The agent's step-by-step reasoning logs (why it approved a specific invoice) must be retained for 7 years for tax audit purposes, not just 30 days. Furthermore, regarding delegated identity, the agent must execute database writes using a restricted Azure Managed Identity, not a shared admin Service Principal.
- Authority boundary surfaced:
  The Chief Risk Officer (CRO) holds veto power over the "Cost-Speed Routing Controls" if optimizing for cheaper/faster LLM inference degrades the auditability of the agent's decisions.
- Rollback trigger surfaced:
  1. A >2% failure rate in downstream ERP PO reconciliation.
  2. Any single detected instance of a duplicate payment attempt slipping past the agent's checks.

## Translation Into Durable Artifacts

- NFR register update:
  * Added NFR-AP-01: "Strict idempotency key validation required for all ERP write operations, enforced at the API gateway level."

  Added NFR-AP-02: "Agent reasoning traces must be routed to Azure Blob Storage (Cold Tier) with a strict 7-year immutable retention policy."
- ADR boundary update:
  Updated ADR-008 (Cost-Speed Routing Controls). The routing logic must now include a hard rule: Any invoice exceeding $50,000 must bypass dynamic routing and be hardcoded to use the most capable (slower/expensive) model available, prioritizing reasoning over latency.
- Open risk or unresolved ambiguity:
  ERP Rate Limiting vs. Agent Speed. If the agent recovers from a downtime event and processes the backlog queue at maximum speed, will it trigger a Denial of Service (DoS) on our own legacy ERP system? We need to schedule a load test on Day 5 to determine the integration boundary limits.