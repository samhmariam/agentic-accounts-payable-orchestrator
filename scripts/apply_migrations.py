#!/usr/bin/env python3
from __future__ import annotations

import argparse

from aegisap.common.paths import repo_root
from aegisap.training.postgres import apply_migration_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply AegisAP PostgreSQL migrations.")
    parser.add_argument(
        "--migration",
        default=str(repo_root(__file__) / "src" / "migrations"),
        help="Path to a SQL migration file or a directory of ordered SQL migrations.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    applied = apply_migration_path(args.migration)
    print("Applied migrations:")
    for migration in applied:
        print(f"- {migration}")


if __name__ == "__main__":
    main()
