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
