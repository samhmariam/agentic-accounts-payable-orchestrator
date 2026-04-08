from __future__ import annotations

import argparse
import json
from typing import Any

from .engine import (
    IncidentError,
    InterruptedIncident,
    nuke_incident,
    reset_incident,
    start_incident,
    status_incident,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AegisAP incident-driven training CLI.")
    parser.add_argument("--repo-root", help=argparse.SUPPRESS, default=None)

    subparsers = parser.add_subparsers(dest="command", required=True)
    incident = subparsers.add_parser("incident", help="Manage hidden lab incidents.")
    incident_subparsers = incident.add_subparsers(dest="incident_command", required=True)

    for name in ("start", "reset", "status", "nuke"):
        sub = incident_subparsers.add_parser(name, help=f"{name.capitalize()} an incident.")
        sub.add_argument("--day", required=True, help="Two-digit day number, for example 01.")

    artifact = subparsers.add_parser("artifact", help="Rebuild day artifacts from the fixed reference path.")
    artifact_subparsers = artifact.add_subparsers(dest="artifact_command", required=True)
    rebuild = artifact_subparsers.add_parser("rebuild", help="Rebuild a day artifact from the fixed reference path.")
    rebuild.add_argument("--day", required=True, help="Two-digit day number, for example 01.")

    return parser


def _print_payload(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        if args.command == "incident" and args.incident_command == "start":
            journal = start_incident(day=args.day, repo_path=args.repo_root)
            _print_payload(journal.model_dump(mode="json"))
            return 0
        if args.command == "incident" and args.incident_command == "reset":
            journal = reset_incident(day=args.day, repo_path=args.repo_root)
            _print_payload(journal.model_dump(mode="json"))
            return 0
        if args.command == "incident" and args.incident_command == "nuke":
            journal = nuke_incident(day=args.day, repo_path=args.repo_root)
            _print_payload(journal.model_dump(mode="json"))
            return 0
        if args.command == "incident" and args.incident_command == "status":
            journal = status_incident(day=args.day, repo_path=args.repo_root)
            if journal is None:
                _print_payload({"day": f"{int(args.day):02d}", "status": "idle"})
            else:
                _print_payload(journal.model_dump(mode="json"))
            return 0
        if args.command == "artifact" and args.artifact_command == "rebuild":
            from .artifacts import rebuild_day_artifact

            _print_payload(rebuild_day_artifact(day=args.day))
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
