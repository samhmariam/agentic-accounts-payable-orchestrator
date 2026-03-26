# Day 5 - Durable State and Resumption

Day 5 turns AegisAP into a workflow that survives interruption. The learner
persists a Day 4 case to PostgreSQL, creates an approval task, and later
resumes that thread without duplicating side effects.

## Prerequisite

Use the `full` Day 0 track or provide `AEGISAP_POSTGRES_DSN`. Day 5 requires a
reachable PostgreSQL database before any checkpoints can be written.

## Lab Sequence

1. Apply the Day 5 schema:

```bash
uv run python scripts/apply_migrations.py
```

2. Create a Day 4 artifact if needed:

```bash
uv run python scripts/run_day4_case.py --planner-mode fixture
```

3. Pause at the approval boundary:

```bash
uv run python scripts/run_day5_pause_resume.py
```

4. Resume the approval:

```bash
uv run python scripts/resume_day5_case.py --status approved
```

## Training Artifacts

- `build/day5/golden_thread_day5_pause.json`
- `build/day5/golden_thread_day5_resumed.json`

The pause artifact includes the thread ID, checkpoint ID, approval task ID, and
resume token used by the API and deployment smoke tests.

## Exit Check

Day 5 succeeds when:

- a checkpoint is written to PostgreSQL
- an approval task is bound to that checkpoint
- resume loads the latest checkpoint
- side effects are deduplicated across retries

## Hosted Path

The same logic is exposed through the training runtime:

- `GET /healthz`
- `POST /api/day4/cases/run`
- `GET /api/day5/threads/{thread_id}`
- `POST /api/day5/approvals/{approval_task_id}/resume`

Deploy this runtime through Azure Container Apps after building the image and
deploying the `infra/modules/container_app.bicep` module.

## Key Files

- `src/migrations/005_day_05_durable_state.sql`
- `src/aegisap/day5/workflow/training_runtime.py`
- `src/aegisap/day5/workflow/resume_service.py`
- `scripts/apply_migrations.py`
- `scripts/run_day5_pause_resume.py`
- `scripts/resume_day5_case.py`
