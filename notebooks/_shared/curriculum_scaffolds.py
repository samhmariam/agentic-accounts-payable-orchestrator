from __future__ import annotations

import importlib
import sys
from pathlib import Path

import yaml


def deep_reload_modules(*module_prefixes: str) -> list[str]:
    removed: list[str] = []
    prefixes = tuple(prefix.strip() for prefix in module_prefixes if prefix and prefix.strip())
    if not prefixes:
        return removed

    # Remove deepest modules first so re-imports do not inherit stale transitive state.
    for name in sorted(sys.modules, key=lambda item: (item.count("."), item), reverse=True):
        if any(name == prefix or name.startswith(f"{prefix}.") for prefix in prefixes):
            sys.modules.pop(name, None)
            removed.append(name)

    importlib.invalidate_caches()
    return removed


def render_full_day_agenda(
    mo,
    *,
    day_label: str,
    core_outcome: str,
    afternoon_focus: str | None = None,
    deliverables_note: str | None = None,
):
    afternoon_focus = afternoon_focus or (
        "Work one bounded problem without notebook-adjacent hints and turn the "
        "result into something you could defend to an assessor."
    )
    deliverables_note = deliverables_note or (
        "Notebook outputs, artifact drafts, and oral defense notes are updated "
        "before you stop."
    )
    return mo.callout(
        mo.md(
            f"""
## Full-Day Agenda

| Block | Focus | Success signal |
|---|---|---|
| Morning concept block | Build the mental model for {day_label} | You can explain the core ideas without reading from the notebook |
| Guided build block | Follow the notebook labs and inspect the evidence chain | You can reproduce the main artifact flow |
| Afternoon independent block | {afternoon_focus} | You can solve one bounded problem without step-by-step scaffolding |
| Artifact writing block | Turn today's work into assessor-ready notes, memos, or packets | {deliverables_note} |
| Oral defense prep | Rehearse the hardest tradeoff in business and engineering language | You can defend why the day's decisions matter later |

### AM checkpoint

- You can state the day's core outcome clearly: {core_outcome}
- You know which upstream artifact, decision, or operating model this day depends on

### PM checkpoint

- You can complete at least one bounded task without notebook-adjacent hints
- You can point to the artifact or evidence this day should leave behind

### End-of-day deliverables

- Core notebook completed or consciously time-boxed
- Artifact drafts updated to assessor-ready quality
- Oral defense notes written in your own words
"""
        ),
        kind="info",
    )


def render_unscaffolded_block(
    mo,
    *,
    title: str,
    brief: str,
    done_when: tuple[str, ...],
):
    done_lines = "\n".join(f"- {line}" for line in done_when)
    return mo.callout(
        mo.md(
            f"""
## {title}

{brief}

### Done when

{done_lines}
"""
        ),
        kind="warn",
    )


def render_daily_rubric_callout(
    mo,
    *,
    day: str,
    repo_root: str | Path | None = None,
):
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[2]
    manifest_path = root / "docs" / "curriculum" / "CURRICULUM_MANIFEST.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    day_id = f"{int(day):02d}"
    day_entry = next(item for item in manifest.get("days", []) if str(item["id"]) == day_id)
    weights = day_entry.get("rubric_weights", {})
    rows = "\n".join(f"| `{key}` | {value} |" for key, value in weights.items())
    rubric_path = root / "docs" / "curriculum" / "ASSESSMENT_RUBRIC.md"
    manifest_link = root / "docs" / "curriculum" / "CURRICULUM_MANIFEST.yaml"
    return mo.callout(
        mo.md(
            f"""
## How You'll Be Scored Today

| Dimension | Points |
|---|---:|
{rows}

See [ASSESSMENT_RUBRIC.md]({rubric_path}) for band descriptors and
[CURRICULUM_MANIFEST.yaml]({manifest_link}) for the authoritative day contract.
"""
        ),
        kind="info",
    )
