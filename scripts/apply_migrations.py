#!/usr/bin/env python3
from __future__ import annotations

import argparse

from aegisap.common.paths import repo_root
from aegisap.training.postgres import apply_migration_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply the Day 5 PostgreSQL migration.")
    parser.add_argument(
        "--migration",
        default=str(repo_root(__file__) / "src" / "migrations" / "005_day_05_durable_state.sql"),
        help="Path to a SQL migration file.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    apply_migration_file(args.migration)
    print(f"Applied migration: {args.migration}")


if __name__ == "__main__":
    main()
