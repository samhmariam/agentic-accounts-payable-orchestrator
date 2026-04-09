from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .curriculum import get_day, load_manifest, normalize_day, resolve_repo_root


DEFAULT_RUBRIC_DIMENSIONS: tuple[tuple[str, str, int], ...] = (
    ("technical_correctness", "Technical Correctness", 35),
    ("trade_off_reasoning", "Trade-off Reasoning", 20),
    ("process_fluency", "Process Fluency", 15),
    ("artifact_quality", "Artifact Quality", 15),
    ("oral_defense", "Oral Defense", 15),
)
VALID_CONFIDENCE = {"low", "medium", "high"}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_rubric_check_path(*, repo_root: str | Path | None = None, day: str | int) -> Path:
    root = resolve_repo_root(repo_root)
    day_id = normalize_day(day)
    return root / "build" / f"day{int(day_id)}" / "rubric_check.json"


def tracked_rubric_check_path(*, repo_root: str | Path | None = None, day: str | int) -> Path:
    root = resolve_repo_root(repo_root)
    day_id = normalize_day(day)
    return root / "docs" / "curriculum" / "submissions" / f"day{day_id}" / "rubric_check.json"


def render_rubric_check_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "## Rubric Check",
        f"- Day: `{payload['day']}`",
        f"- Learner: `{payload['learner_name']}`",
        f"- Confidence: `{payload['confidence']}`",
        f"- Declared weakness: {payload['declared_weakness']}",
        f"- Remediation action: {payload['remediation_action']}",
        f"- Self-score total: `{payload['self_score_total']}` / 100",
        "",
        "### Dimension Scores",
    ]
    for item in payload["dimensions"]:
        lines.append(
            f"- `{item['label']}`: `{item['score']}` / {item['max_points']} | {item['rationale']}"
        )
    return "\n".join(lines)


def copy_tracked_rubric_check_to_build(
    *, repo_root: str | Path | None = None, day: str | int
) -> dict[str, str]:
    tracked_path = tracked_rubric_check_path(repo_root=repo_root, day=day)
    build_path = build_rubric_check_path(repo_root=repo_root, day=day)
    if not tracked_path.exists():
        raise ValueError(f"Tracked rubric-check artifact missing: {tracked_path}")
    payload = json.loads(tracked_path.read_text(encoding="utf-8"))
    build_path.parent.mkdir(parents=True, exist_ok=True)
    build_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return {"tracked_path": str(tracked_path), "build_path": str(build_path)}


def _prompt_score(label: str, max_points: int) -> tuple[int, str]:
    while True:
        raw = input(f"{label} score (0-{max_points}): ").strip()
        try:
            value = int(raw)
        except ValueError:
            print("Enter an integer score.")
            continue
        if 0 <= value <= max_points:
            break
        print(f"Score must be between 0 and {max_points}.")
    rationale = input(f"{label} rationale: ").strip()
    return value, rationale


def _label_for_dimension(key: str) -> str:
    return key.replace("_", " ").title().replace("Obo", "OBO").replace("Iac", "IaC")


def _dimension_contracts(*, day_id: str, repo_root: str | Path | None = None) -> list[tuple[str, str, int]]:
    try:
        day_entry = get_day(load_manifest(repo_root), day_id)
    except Exception:
        return list(DEFAULT_RUBRIC_DIMENSIONS)
    weights = day_entry.get("rubric_weights", {})
    if not isinstance(weights, dict) or not weights:
        return list(DEFAULT_RUBRIC_DIMENSIONS)
    return [(key, _label_for_dimension(key), int(points)) for key, points in weights.items()]


def _normalize_scores(
    scores: dict[str, int] | None,
    rationales: dict[str, str] | None,
    *,
    day_id: str,
    repo_root: str | Path | None = None,
    prompt_for_missing: bool,
) -> list[dict[str, Any]]:
    score_map = scores or {}
    rationale_map = rationales or {}
    normalized: list[dict[str, Any]] = []
    for key, label, max_points in _dimension_contracts(day_id=day_id, repo_root=repo_root):
        score = score_map.get(key)
        rationale = rationale_map.get(key, "").strip()
        if score is None and prompt_for_missing:
            score, rationale = _prompt_score(label, max_points)
        if score is None:
            raise ValueError(f"Missing rubric-check score for `{key}`.")
        if not 0 <= int(score) <= max_points:
            raise ValueError(f"Rubric-check score for `{key}` must be between 0 and {max_points}.")
        if not rationale and prompt_for_missing:
            rationale = input(f"{label} rationale: ").strip()
        if not rationale:
            rationale = "Self-assessed without additional notes."
        normalized.append(
            {
                "key": key,
                "label": label,
                "score": int(score),
                "max_points": max_points,
                "rationale": rationale,
            }
        )
    return normalized


def run_rubric_check(
    *,
    day: str | int,
    repo_root: str | Path | None = None,
    learner_name: str | None = None,
    confidence: str | None = None,
    weakness: str | None = None,
    remediation: str | None = None,
    scores: dict[str, int] | None = None,
    rationales: dict[str, str] | None = None,
    prompt_for_missing: bool = True,
) -> dict[str, Any]:
    day_id = normalize_day(day)
    root = resolve_repo_root(repo_root)

    if not learner_name and prompt_for_missing:
        learner_name = input("Learner name: ").strip()
    if not learner_name:
        raise ValueError("Learner name is required.")

    if not confidence and prompt_for_missing:
        confidence = input("Confidence (low/medium/high): ").strip().lower()
    confidence = (confidence or "").strip().lower()
    if confidence not in VALID_CONFIDENCE:
        raise ValueError("Confidence must be one of: low, medium, high.")

    if not weakness and prompt_for_missing:
        weakness = input("One declared weakness: ").strip()
    if not remediation and prompt_for_missing:
        remediation = input("One remediation action: ").strip()
    if not weakness:
        raise ValueError("A declared weakness is required.")
    if not remediation:
        raise ValueError("A remediation action is required.")

    dimensions = _normalize_scores(
        scores,
        rationales,
        day_id=day_id,
        repo_root=root,
        prompt_for_missing=prompt_for_missing,
    )
    payload = {
        "day": day_id,
        "learner_name": learner_name,
        "generated_at": _utc_now_iso(),
        "confidence": confidence,
        "declared_weakness": weakness,
        "remediation_action": remediation,
        "self_score_total": sum(item["score"] for item in dimensions),
        "dimensions": dimensions,
    }

    build_path = build_rubric_check_path(repo_root=root, day=day_id)
    tracked_path = tracked_rubric_check_path(repo_root=root, day=day_id)
    for path in (build_path, tracked_path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "day": day_id,
        "build_path": str(build_path),
        "tracked_path": str(tracked_path),
        "payload": payload,
        "markdown": render_rubric_check_markdown(payload),
    }
