#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compile a principal-review strategy from review telemetry, with an optional DSPy path."
    )
    parser.add_argument(
        "--dataset",
        default="data/review/principal_review_telemetry.jsonl",
        help="JSONL review telemetry dataset.",
    )
    parser.add_argument(
        "--out-json",
        default="build/review/principal_review_strategy.json",
        help="Path to the compiled strategy JSON.",
    )
    return parser.parse_args()


def load_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        records.append(json.loads(line))
    return records


def _example_from_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "profile": record["profile"],
        "diff_smell": record["diff_smell"],
        "review": record["staff_review"],
        "human_decision": record.get("human_decision"),
    }


def heuristic_strategy(records: list[dict[str, Any]]) -> dict[str, Any]:
    profiles: dict[str, dict[str, Any]] = {}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record["profile"]].append(record)

    for profile, items in grouped.items():
        blocking_patterns = Counter()
        examples: list[dict[str, Any]] = []
        for item in items:
            if item.get("false_positive_label"):
                continue
            blocking_patterns.update(item.get("deterministic_tags", []))
            examples.append(_example_from_record(item))
        profiles[profile] = {
            "examples": examples[:4],
            "style_guidance": (
                "Be terse, strict, and evidence-first. Start with the highest-risk finding, "
                "tie it to the day rubric, and end with a direct fix request."
            ),
            "blocking_patterns": [pattern for pattern, _count in blocking_patterns.most_common(6)],
        }

    global_examples: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for record in records:
        example = _example_from_record(record)
        key = (example["profile"], example["diff_smell"])
        if key in seen:
            continue
        seen.add(key)
        global_examples.append(example)

    return {
        "compiled_at": os.environ.get("GITHUB_RUN_ID", "") or "local",
        "compiler": "heuristic",
        "llm_blocking_enabled": False,
        "profiles": profiles,
        "examples": global_examples[:8],
    }


def maybe_compile_with_dspy(records: list[dict[str, Any]], heuristic: dict[str, Any]) -> dict[str, Any] | None:
    if os.environ.get("PRINCIPAL_REVIEW_USE_DSPY", "").strip() != "1":
        return None

    try:
        import dspy
    except Exception:
        return None

    model_name = os.environ.get("PRINCIPAL_REVIEW_DSPY_MODEL", "").strip()
    if not model_name:
        return None

    class StrategyCompiler(dspy.Signature):
        telemetry_summary = dspy.InputField()
        baseline_strategy = dspy.InputField()
        strategy_json = dspy.OutputField()

    try:
        lm_kwargs: dict[str, Any] = {"model": model_name}
        api_key = os.environ.get("PRINCIPAL_REVIEW_DSPY_API_KEY", "").strip()
        api_base = os.environ.get("PRINCIPAL_REVIEW_DSPY_API_BASE", "").strip()
        if api_key:
            lm_kwargs["api_key"] = api_key
        if api_base:
            lm_kwargs["api_base"] = api_base

        dspy.configure(lm=dspy.LM(**lm_kwargs))
        predictor = dspy.Predict(StrategyCompiler)
        telemetry_summary = json.dumps(records, indent=2)[:24000]
        response = predictor(
            telemetry_summary=telemetry_summary,
            baseline_strategy=json.dumps(heuristic, indent=2),
        )
        payload = json.loads(response.strategy_json)
        if isinstance(payload, dict):
            payload["compiler"] = "dspy"
            payload["llm_blocking_enabled"] = True
            return payload
    except Exception:
        return None

    return None


def main() -> int:
    args = parse_args()
    dataset_path = Path(args.dataset)
    out_path = Path(args.out_json)

    records = load_records(dataset_path)
    strategy = heuristic_strategy(records)
    dspy_strategy = maybe_compile_with_dspy(records, strategy)
    if dspy_strategy is not None:
        strategy = dspy_strategy

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(strategy, indent=2), encoding="utf-8")
    print(json.dumps(strategy, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
