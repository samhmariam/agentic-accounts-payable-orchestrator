# Trainee Preflight Checklist

Use this checklist before the cohort starts so Day 1 begins with learning, not
environment triage.

## Purpose

Confirm that your local environment, Azure access, and repo checkout are ready
for the notebook-led 14-day curriculum.

This is not a tutorial. You are expected to work from broken states, telemetry,
and incomplete operator evidence rather than step-by-step answers.

## One Week Before Cohort Start

- Confirm you can access the training repository and pull the current branch.
- Confirm you have a working shell (`bash`, `zsh`, or PowerShell) and Python on
  your machine.
- Confirm you can sign in to the target Azure tenant with the account you will
  use during training.
- Confirm you can use the Azure CLI: `az version`
- Confirm you have enough local disk space for dependencies, notebook outputs,
  and build artifacts.

## 24 Hours Before Day 1

1. Sync the repo and install dependencies:

```bash
uv sync --extra dev --extra day9
```

2. Sign in to Azure:

```bash
az login
az account show
```

3. Run the lightweight environment verification:

```bash
uv run python scripts/verify_env.py --track core --env
```

4. If your facilitator has already provisioned a `.day0` state file for later
   labs, load it and verify the matching track:

```bash
source ./scripts/setup-env.sh core
uv run python scripts/verify_env.py --track core --env
```

PowerShell:

```powershell
. .\scripts\setup-env.ps1 -Track core
uv run python scripts/verify_env.py --track core --env
```

5. If you are scheduled to use the `full` track during the cohort, repeat the
   same process with `full`.

## Morning Of Day 1

- Pull the latest curriculum changes.
- Re-run `uv sync --extra dev --extra day9` if anything changed.
- Confirm your Azure session is still valid with `az account show`.
- Close stale shells that might still hold old environment variables.
- Wait to open notebooks until the facilitator gives the start signal for the day.

## Minimum Ready State

You are ready to begin the live cohort if all of the following are true:

- `uv sync --extra dev --extra day9` completes without error
- `az account show` returns the expected tenant and subscription context
- `uv run python scripts/verify_env.py --track core --env` succeeds or your
  facilitator has explicitly approved a local-only fallback for the day
- You know which shell you will use for the full cohort
- You know how to capture terminal output if you need help

## Native Tooling Readiness By Day 5

By the time the cohort reaches Day 5, you should also be ready for:

- `full` track environment loading with `scripts/setup-env.sh` or `scripts/setup-env.ps1`
- Azure resource access for deployment, identity, and later verification steps
- Running live verification scripts where the facilitator expects authoritative evidence
- Producing raw `az`, DNS, Git, and KQL proofs without relying on helper commands

See `docs/curriculum/NATIVE_TOOLING_POLICY.md` for the governing rules.

Native Azure and Git fluency is assessed by Week 2.
Native Azure and Git fluency is assessed from Day 5 onward. Days 05-14 require
saved native operator evidence and saved KQL evidence, and Days 12 and 14
require live replay on request.
Every submission should run
`uv run aegisap-lab rubric-check --day XX` before review prep so your declared
weak spots are visible in the PR.

## If You Get Blocked

Do these three things before asking for help:

1. Copy the exact command you ran.
2. Copy the last 20-30 lines of terminal output.
3. State whether the failure happened during `uv sync`, `az login`, `setup-env`,
   `verify_env`, or notebook execution.

That is the minimum context a facilitator needs to unblock you quickly.
