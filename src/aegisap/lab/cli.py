from __future__ import annotations

import argparse
import json
from typing import Any

from .mastery import SKIP as MASTERY_SKIP
from .mastery import run_mastery
from .engine import (
    IncidentError,
    InterruptedIncident,
    nuke_incident,
    reset_incident,
    start_incident,
    status_incident,
)
from .overlay import hydrate_instructor_bundle, import_instructor_overlay, overlay_status, record_hint_usage


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AegisAP incident-driven training CLI.")
    parser.add_argument("--repo-root", help=argparse.SUPPRESS, default=None)

    subparsers = parser.add_subparsers(dest="command", required=True)
    incident = subparsers.add_parser("incident", help="Manage hidden lab incidents.")
    incident_subparsers = incident.add_subparsers(dest="incident_command", required=True)

    for name in ("start", "reset", "status", "nuke"):
        sub = incident_subparsers.add_parser(name, help=f"{name.capitalize()} an incident.")
        sub.add_argument("--day", required=True, help="Two-digit day number, for example 01.")
        sub.add_argument(
            "--track",
            choices=("core", "full"),
            default=None,
            help="Bootstrap track for day 00 incident flows. Ignored for days 01-14.",
        )

    artifact = subparsers.add_parser("artifact", help="Rebuild day artifacts from the fixed reference path.")
    artifact_subparsers = artifact.add_subparsers(dest="artifact_command", required=True)
    rebuild = artifact_subparsers.add_parser("rebuild", help="Rebuild a day artifact from the fixed reference path.")
    rebuild.add_argument("--day", required=True, help="Two-digit day number, for example 01.")

    drill = subparsers.add_parser("drill", help="Manage Phase 2 automated drills.")
    drill_subparsers = drill.add_subparsers(dest="drill_command", required=True)
    drill_list = drill_subparsers.add_parser("list", help="List available drills.")
    drill_list.add_argument("--day", default=None, help="Optional day filter, for example 12.")
    drill_inject = drill_subparsers.add_parser("inject", help="Inject the default or selected drill for a day.")
    drill_inject.add_argument("--day", required=True, help="Two-digit day number, for example 12.")
    drill_inject.add_argument("--drill-id", default=None, help="Optional explicit drill id for days with multiple drills.")
    drill_reset = drill_subparsers.add_parser("reset", help="Reset the active drill for a day.")
    drill_reset.add_argument("--day", required=True, help="Two-digit day number, for example 12.")

    audit = subparsers.add_parser("audit-production", help="Audit live Azure posture and write a production-readiness artifact.")
    audit.add_argument("--out", default=None, help="Optional output path for the audit artifact JSON.")
    audit.add_argument("--day", default=None, help="Optional day number for manifest-driven cloud-truth checks.")
    audit.add_argument(
        "--strict",
        action="store_true",
        help="Fail if the audit runs in preview mode or any live check fails.",
    )

    mastery = subparsers.add_parser("mastery", help="Run the manifest-backed mastery gates for a curriculum day.")
    mastery.add_argument("--day", required=True, help="Two-digit day number, for example 08, or 00 for bootstrap.")
    mastery.add_argument(
        "--track",
        choices=("core", "full"),
        default="core",
        help="Bootstrap track for day 00. Ignored for days 01-14.",
    )
    mastery.add_argument(
        "--strict",
        action="store_true",
        help="Fail on skipped preview gates in addition to blocking failures.",
    )

    rubric = subparsers.add_parser("rubric-check", help="Write a learner self-score artifact for the current day.")
    rubric.add_argument("--day", required=True, help="Two-digit day number, for example 10.")
    rubric.add_argument("--learner-name", default=None, help="Optional learner name. Prompts if omitted.")
    rubric.add_argument(
        "--confidence",
        choices=("low", "medium", "high"),
        default=None,
        help="Optional self-declared confidence level. Prompts if omitted.",
    )
    rubric.add_argument("--weakness", default=None, help="Optional declared weakness. Prompts if omitted.")
    rubric.add_argument("--remediation", default=None, help="Optional remediation action. Prompts if omitted.")
    rubric.add_argument(
        "--score",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Optional rubric score override, for example technical_correctness=28.",
    )
    rubric.add_argument(
        "--rationale",
        action="append",
        default=[],
        metavar="KEY=TEXT",
        help="Optional rubric rationale override, for example technical_correctness=Green gates after fix.",
    )

    overlay = subparsers.add_parser("overlay", help="Manage facilitator-only instructor overlay assets.")
    overlay_subparsers = overlay.add_subparsers(dest="overlay_command", required=True)
    overlay_import = overlay_subparsers.add_parser("import", help="Import an instructor overlay into the local cache.")
    overlay_import.add_argument("--file", required=True, help="Path to the secure overlay bundle to cache locally.")
    overlay_import.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing cached overlay if one is already present.",
    )
    overlay_hydrate = overlay_subparsers.add_parser(
        "hydrate",
        help="Fetch and cache the remote instructor bundle for a day when using the remote asset provider.",
    )
    overlay_hydrate.add_argument("--day", required=True, help="Two-digit day number, for example 08.")
    overlay_hydrate.add_argument(
        "--force",
        action="store_true",
        help="Re-fetch and replace any cached bundle for the selected day.",
    )
    overlay_subparsers.add_parser("status", help="Show whether a cached instructor overlay is available.")
    overlay_hint = overlay_subparsers.add_parser("hint", help="Record hint-ladder usage for a learner day.")
    overlay_hint.add_argument("--day", required=True, help="Two-digit day number, for example 08.")
    overlay_hint.add_argument("--level", required=True, help="Hint-ladder level such as T+30 or T+60.")
    overlay_hint.add_argument("--prompt", default="", help="Prompt or command shared with the learner.")
    overlay_hint.add_argument("--note", default="", help="Optional facilitator note.")

    return parser


def _print_payload(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        if args.command == "incident" and args.incident_command == "start":
            journal = start_incident(day=args.day, repo_path=args.repo_root, track=args.track)
            _print_payload(journal.model_dump(mode="json"))
            return 0
        if args.command == "incident" and args.incident_command == "reset":
            journal = reset_incident(day=args.day, repo_path=args.repo_root, track=args.track)
            _print_payload(journal.model_dump(mode="json"))
            return 0
        if args.command == "incident" and args.incident_command == "nuke":
            journal = nuke_incident(day=args.day, repo_path=args.repo_root, track=args.track)
            _print_payload(journal.model_dump(mode="json"))
            return 0
        if args.command == "incident" and args.incident_command == "status":
            journal = status_incident(day=args.day, repo_path=args.repo_root, track=args.track)
            if journal is None:
                _print_payload({"day": f"{int(args.day):02d}", "status": "idle"})
            else:
                _print_payload(journal.model_dump(mode="json"))
            return 0
        if args.command == "artifact" and args.artifact_command == "rebuild":
            from .artifacts import rebuild_day_artifact

            _print_payload(rebuild_day_artifact(day=args.day))
            return 0
        if args.command == "drill" and args.drill_command == "list":
            from .drills import list_drills

            _print_payload(list_drills(repo_root=args.repo_root, day=args.day))
            return 0
        if args.command == "drill" and args.drill_command == "inject":
            from .drills import inject_drill

            _print_payload(inject_drill(day=args.day, repo_root=args.repo_root, drill_id=args.drill_id))
            return 0
        if args.command == "drill" and args.drill_command == "reset":
            from .drills import reset_drill

            _print_payload(reset_drill(day=args.day, repo_root=args.repo_root))
            return 0
        if args.command == "audit-production":
            from .audit import FAIL, SKIP, run_production_audit

            payload = run_production_audit(repo_root=args.repo_root, out_path=args.out, day=args.day)
            _print_payload(payload)
            checks = payload.get("checks", [])
            if any(check.get("status") == FAIL for check in checks):
                return 1
            if args.strict and (
                not payload.get("authoritative_evidence")
                or any(check.get("status") == SKIP for check in checks)
            ):
                return 1
            return 0
        if args.command == "mastery":
            payload = run_mastery(
                day=args.day,
                strict=args.strict,
                repo_root=args.repo_root,
                track=args.track,
            )
            print(f"Mastery Gates: Day {payload['day']} - {payload['title']}")
            for constraint in payload["constraint_lineage"]["active_constraints"]:
                gate_ids = ", ".join(item["gate_id"] for item in constraint["covered_by"]) or "uncovered"
                print(
                    f"  constraint {constraint['id']} ({constraint['type']}, day {constraint['introduced_on']}): {gate_ids}"
                )
            for result in payload["results"]:
                print(f"[{result['status']}] {result['gate_id']} ({result['mode']}): {result['detail']}")
            if not payload["results"]:
                print(f"[{MASTERY_SKIP}] no_manifest_gates: No mastery gates were declared for this day.")
            if payload.get("constraint_lineage_path"):
                print(f"Constraint lineage artifact: {payload['constraint_lineage_path']}")
            return 0 if payload["overall_ok"] else 1
        if args.command == "rubric-check":
            from .rubric_check import run_rubric_check

            def _parse_pairs(items: list[str], *, cast_int: bool) -> dict[str, Any]:
                parsed: dict[str, Any] = {}
                for item in items:
                    if "=" not in item:
                        raise ValueError(f"Expected KEY=VALUE pair, got `{item}`.")
                    key, value = item.split("=", 1)
                    key = key.strip()
                    if not key:
                        raise ValueError(f"Expected KEY=VALUE pair, got `{item}`.")
                    parsed[key] = int(value) if cast_int else value.strip()
                return parsed

            payload = run_rubric_check(
                day=args.day,
                repo_root=args.repo_root,
                learner_name=args.learner_name,
                confidence=args.confidence,
                weakness=args.weakness,
                remediation=args.remediation,
                scores=_parse_pairs(args.score, cast_int=True),
                rationales=_parse_pairs(args.rationale, cast_int=False),
                prompt_for_missing=True,
            )
            _print_payload(
                {
                    "day": payload["day"],
                    "build_path": payload["build_path"],
                    "tracked_path": payload["tracked_path"],
                    "self_score_total": payload["payload"]["self_score_total"],
                }
            )
            print()
            print(payload["markdown"])
            return 0
        if args.command == "overlay" and args.overlay_command == "import":
            _print_payload(import_instructor_overlay(source=args.file, repo_root=args.repo_root, force=args.force))
            return 0
        if args.command == "overlay" and args.overlay_command == "hydrate":
            _print_payload(hydrate_instructor_bundle(day=args.day, repo_root=args.repo_root, force=args.force))
            return 0
        if args.command == "overlay" and args.overlay_command == "status":
            _print_payload(overlay_status(repo_root=args.repo_root))
            return 0
        if args.command == "overlay" and args.overlay_command == "hint":
            _print_payload(
                record_hint_usage(
                    day=args.day,
                    level=args.level,
                    prompt=args.prompt,
                    note=args.note,
                    repo_root=args.repo_root,
                )
            )
            return 0
    except IncidentError as exc:
        print(str(exc))
        return 1
    except InterruptedIncident as exc:
        print(str(exc))
        return 130
    except ValueError as exc:
        print(str(exc))
        return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
