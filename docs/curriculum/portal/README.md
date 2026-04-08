# Portal-First Bootstrap Guide

This folder now exists only for the Day 0 bootstrap exception.

Use it when learners need to build the Azure mental model from the control
plane before IaC, incident injection, and notebook-led repair become the normal
delivery path.

## Working Order

Use this sequence for Day 0 only:

1. Open `docs/curriculum/portal/DAY_00_PORTAL.md`.
2. Complete the manual Azure bootstrap step.
3. Capture the evidence listed in the guide.
4. Return to the primary bootstrap doc.
5. Only then use scripts or modules to see how the repo abstracts the same work.

This preserves the learner's attention on Azure concepts before they are hidden
behind automation.

## Later Days

Days 1-14 no longer use standalone portal guides. Those days begin with:

```bash
uv run aegisap-lab incident start --day XX
```

The learner still inspects Azure surfaces, but the exact portal investigation
now lives inside the day notebook under `Portal Investigation`, followed by the
`Codification Bridge` step that maps Azure state to permanent code.

## Evidence Rule

Every portal-first pass should leave behind concrete evidence:

- the exact Azure blade or object inspected
- the state observed there
- the notebook section that interprets that state
- the script or module that later automates or verifies it

If a learner cannot explain that chain, the bootstrap pass did not do its job.

## Navigation

- Use [DELIVERY_MAP.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/DELIVERY_MAP.md) for the day-by-day repo map.
- Use [README.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/README.md) for the full curriculum contract.
- Use `DAY_00_PORTAL.md` in this folder as the Day 0 entrypoint.
