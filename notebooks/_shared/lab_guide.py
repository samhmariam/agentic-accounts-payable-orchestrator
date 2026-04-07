from __future__ import annotations

import json
import os
from pathlib import Path


def render_lab_overview(
    mo,
    *,
    prerequisites: list[str],
    required_inputs: list[str],
    required_env_vars: list[str],
    expected_artifact: str,
    pass_criteria: list[str],
    implementation_exercise: str,
):
    sections: list[object] = [
        mo.md("## Lab Contract"),
        mo.md("**Prerequisites**"),
        mo.md("\n".join(f"- {item}" for item in prerequisites)),
        mo.md("**Required inputs**"),
        mo.md("\n".join(f"- {item}" for item in required_inputs)),
        mo.md("**Required env vars**"),
        mo.md(
            "\n".join(f"- `{item}`" for item in required_env_vars)
            if required_env_vars
            else "- None beyond the prior-day artifact and notebook defaults."
        ),
        mo.md("**Expected artifact**"),
        mo.md(f"- `{expected_artifact}`"),
        mo.md("**Pass criteria**"),
        mo.md("\n".join(f"- {item}" for item in pass_criteria)),
        mo.md("**Implementation exercise**"),
        mo.md(f"- {implementation_exercise}"),
    ]
    return mo.vstack(sections)


def render_notebook_learning_context(
    mo,
    *,
    purpose: str,
    prerequisites: list[str],
    resources: list[str],
    setup_sequence: list[str],
    run_steps: list[str],
    output_interpretation: list[str],
    troubleshooting: list[str],
    outside_references: list[str],
):
    def _bullet_block(items: list[str]) -> str:
        return "\n".join(f"- {item}" for item in items)

    _agent_era_lens = [
        "Focus first on system boundaries, authority rules, contracts, and failure modes.",
        "Treat code snippets as reference patterns to inspect and adapt, not as long blocks to transcribe manually.",
        "If an agent drafts code, your responsibility is to review the interfaces, constraints, and evidence the code must preserve.",
        "Look for the tradeoff in each section: what is being optimized, what risk is being accepted, and what proof makes the choice safe.",
    ]

    return mo.vstack(
        [
            mo.callout(
                mo.md(
                    f"""
## Notebook Guide

**Purpose**

{purpose}

**Agent-era working mode**

Use this notebook to understand the design, review the critical abstractions, and verify the evidence chain. Let agents handle routine code drafting; keep human attention on tradeoffs, boundary decisions, and proof that the system behaves safely.
"""
                ),
                kind="info",
            ),
            mo.accordion(
                {
                    "Prerequisites": mo.md(_bullet_block(prerequisites)),
                    "Resources": mo.md(_bullet_block(resources)),
                    "Preparation": mo.md(_bullet_block(setup_sequence)),
                    "Architecture and Tradeoff Lens": mo.md(_bullet_block(_agent_era_lens)),
                    "Run, Review, Verify": mo.md(
                        "Work through the notebook in a way that keeps design intent ahead of implementation detail. "
                        "If a shell script is mentioned, treat it as a rebuild, automation, or live-validation wrapper "
                        "around logic you should already understand from the notebook itself.\n\n"
                        + _bullet_block(run_steps)
                    ),
                    "Verification Signals": mo.md(
                        "Use the outputs below to decide whether the system behavior, artifact shape, and evidence chain match the intended design.\n\n"
                        + _bullet_block(output_interpretation)
                    ),
                    "Troubleshooting": mo.md(_bullet_block(troubleshooting)),
                    "Outside Notebook": mo.md(
                        "Use this notebook as the primary learning surface. Leave it only for deeper theory, infra deep dives, trainer operations, or reusable reference material.\n\n"
                        + _bullet_block(outside_references)
                    ),
                }
            ),
        ]
    )


def render_azure_mastery_guide(
    mo,
    *,
    focus: str,
    portal_tasks: str,
    cli_verification: str,
    sdk_snippet: str,
    proof_in_azure: str,
):
    return mo.vstack(
        [
            mo.callout(
                mo.md(
                    f"""
## Azure Mastery Loop

{focus}

Work the day across four surfaces: inspect the live resource in the portal, reproduce or verify it from the command line, recognise the minimal SDK pattern in code, and gather proof that separates a training preview from authoritative Azure evidence.
"""
                ),
                kind="info",
            ),
            mo.accordion(
                {
                    "Portal Inspection Tasks": mo.md(portal_tasks),
                    "CLI Verification Blocks": mo.md(cli_verification),
                    "Short Azure SDK Snippet": mo.md(sdk_snippet),
                    "How to Prove It in Azure": mo.md(proof_in_azure),
                }
            ),
        ]
    )


def render_surface_linkage(
    mo,
    *,
    portal_guide: str,
    portal_activity: str,
    notebook_activity: str,
    automation_steps: list[str],
    evidence_checks: list[str],
):
    def _bullet_block(items: list[str]) -> str:
        return "\n".join(f"- {item}" for item in items)

    return mo.vstack(
        [
            mo.callout(
                mo.md(
                    f"""
## Three-Surface Linkage

Treat today's work as one chain, not three detached activities:

1. **Portal first** — inspect or operate the Azure surface directly.
2. **Notebook second** — reinforce the logic, boundary, or decision path in code.
3. **Automation third** — use the script or module only after the first two surfaces make sense.
4. **Evidence last** — prove the same story appears in the artifact and the Azure state.

When the three surfaces disagree, resolve the mismatch explicitly rather than trusting the wrapper script by default.
"""
                ),
                kind="warn",
            ),
            mo.accordion(
                {
                    "1. Portal First": mo.md(
                        f"- Guide: `{portal_guide}`\n"
                        f"- Task: {portal_activity}"
                    ),
                    "2. Notebook Reinforcement": mo.md(
                        f"- Manual step: {notebook_activity}"
                    ),
                    "3. Automation Handoff": mo.md(_bullet_block(automation_steps)),
                    "4. Evidence To Compare": mo.md(_bullet_block(evidence_checks)),
                }
            ),
        ]
    )


def load_day0_environment(
    *,
    track: str = "core",
    outputs_file: str | Path | None = None,
    overwrite: bool = False,
) -> tuple[dict[str, str], Path | None]:
    repo_root = Path(__file__).resolve().parents[2]
    state_path = Path(outputs_file) if outputs_file is not None else repo_root / ".day0" / f"{track}.json"
    if not state_path.exists():
        return {}, None

    payload = json.loads(state_path.read_text())
    environment = payload.get("environment", {})
    loaded: dict[str, str] = {}

    for key, value in environment.items():
        text = str(value).strip() if value is not None else ""
        if not text:
            continue
        if overwrite or not os.environ.get(key, "").strip():
            os.environ[key] = text
            loaded[key] = text

    defaults = {
        "AEGISAP_ENVIRONMENT": "local",
        "AEGISAP_RESUME_TOKEN_SECRET_NAME": "aegisap-resume-token-secret",
    }
    for key, value in defaults.items():
        if overwrite or not os.environ.get(key, "").strip():
            os.environ[key] = value
            loaded[key] = value

    return loaded, state_path


def render_readiness_check(
    mo,
    *,
    artifact_relpath: str,
    next_day: str,
    recovery_command: str,
):
    artifact_path = Path(__file__).resolve().parents[2] / artifact_relpath
    if artifact_path.exists():
        return mo.callout(
            mo.md(
                f"Ready for **{next_day}**. Verified artifact: `{artifact_relpath}`"
            ),
            kind="success",
        )
    return mo.callout(
        mo.md(
            f"Artifact missing: `{artifact_relpath}`.\n\n"
            f"Recovery command:\n\n```bash\n{recovery_command}\n```"
        ),
        kind="warn",
    )
