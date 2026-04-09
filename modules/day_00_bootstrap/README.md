# Day 00 Module Wormhole

## Why This Matters to an FDE

Bootstrap drift is still production drift. Elite FDEs need to recover the environment contract with the same discipline they use later for release, identity, and network failures.

## Customer Context

The cohort's Azure bootstrap contract is broken. You must recover the Day 0 state file, explain the identity and environment boundary, and prove the repo can reload the environment deterministically.

## Cost of Failure

If the bootstrap contract drifts, every later day starts from a false premise and learners lose the ability to separate Azure truth from local shell luck.

## Persistent Constraints

- `bootstrap_contract_reproducibility`: The Day 0 environment must be restorable from repo-tracked automation rather than remembered shell state.
- `keyless_runtime_identity`: Azure access must remain explainable through `DefaultAzureCredential`, RBAC, and managed identity rather than hard-coded secrets.

## FDE Implementation Cycle

- Incident first: start with the broken bootstrap contract, not the happy-path tutorial.
- Portal second: inspect the Azure control plane only after you can name what contract broke locally.
- Bootstrap doc third: use the Day 0 doc to connect the broken state to the provisioning and env-loading surfaces.
- Automation last: restore the Day 0 state file and verify the environment with the repeatable command path.

## Mastery Gate

- `uv run aegisap-lab mastery --day 00 --track core`
- `uv run aegisap-lab mastery --day 00 --track full`

## Chaos Gate

- Failure signal: the Day 0 state file no longer matches the bootstrap track, so `setup-env.sh` plus `verify_env.py` cannot re-establish the environment contract.
- Starting signal: a bootstrap state value is missing or corrupted, and the environment reload fails before the cohort can trust Foundry, Search, or PostgreSQL access.
- Expected recovery artifact: `.day0/core.json` or `.day0/full.json`
- Time box: 20 minutes

## Day X File Manifest

Do not edit code in this module folder.

- Diagnostic Notebook: `notebooks/day_0_bootstrap_incident.py`
- Primary Day Doc: `docs/DAY_00_AZURE_BOOTSTRAP.md`
- Rosetta Stone Bridge: `notebooks/bridges/day00_bootstrap_contract.md`
- Repair Domain: `Day 0 State Contract`
- Repair Domain: `Bootstrap Incident`
- Incident Asset Ref: `incident.day00`
- Verification Command: `bash -lc "source ./scripts/setup-env.sh core && uv run python scripts/verify_env.py --track core"`
- Verification Command: `bash -lc "source ./scripts/setup-env.sh full && uv run python scripts/verify_env.py --track full"`
- Process Artifact: `docs/curriculum/artifacts/day00/BOOTSTRAP_RECOVERY_NOTE.md`

## Automated Drill

- List drills: `uv run aegisap-lab drill list --day 00`
- Inject default drill: `uv run aegisap-lab drill inject --day 00`
- Reset active drill: `uv run aegisap-lab drill reset --day 00`
