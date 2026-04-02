from __future__ import annotations


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
