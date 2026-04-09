# Portal-First Bootstrap Guide

This folder now supports the Day 0 bootstrap incident.

Use it when learners need to inspect the Azure control plane as part of the
bootstrap evidence chain before they repair the Day 0 contract in the repo.

## Working Order

Use this sequence for Day 0 only:

1. Start `uv run aegisap-lab incident start --day 00 --track <core|full>`.
2. Open `docs/curriculum/portal/DAY_00_PORTAL.md`.
3. Capture the evidence listed in the guide.
4. Return to the primary bootstrap doc and notebook.
5. Repair the repo-backed state and verification path.

This preserves the learner's attention on Azure concepts while still keeping the
bootstrap recovery grounded in repo-backed automation.

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
