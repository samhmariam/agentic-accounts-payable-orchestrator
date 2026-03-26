from __future__ import annotations

import argparse
import runpy
import sys

from aegisap.common.paths import repo_root


COMMANDS = {
    "evals": "evals/run_eval_suite.py",
    "smoke": "scripts/smoke_test.py",
    "check-traces": "scripts/check_traces.py",
    "check-cost": "scripts/check_cost_gates.py",
    "check-resume": "scripts/check_resume_replay.py",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="AegisAP worker entrypoint.")
    parser.add_argument("command", choices=sorted(COMMANDS))
    args, remaining = parser.parse_known_args()

    script_path = repo_root(__file__) / COMMANDS[args.command]
    sys.argv = [str(script_path), *remaining]
    runpy.run_path(str(script_path), run_name="__main__")


if __name__ == "__main__":
    main()
