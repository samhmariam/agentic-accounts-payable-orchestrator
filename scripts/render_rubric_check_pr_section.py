#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

from aegisap.common.paths import repo_root
from aegisap.lab.rubric_check import copy_tracked_rubric_check_to_build, render_rubric_check_markdown


RUBRIC_CHECK_PATTERN = re.compile(r"^docs/curriculum/submissions/day([0-9]{2})/rubric_check\.json$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a rubric-check PR body section from tracked learner submissions.")
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--head-ref", default="HEAD")
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", required=True)
    return parser.parse_args()


def _changed_files(*, root: Path, base_ref: str, head_ref: str) -> list[str]:
    output = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...{head_ref}"],
        cwd=root,
        check=True,
        text=True,
        capture_output=True,
    ).stdout
    return [line.strip() for line in output.splitlines() if line.strip()]


def main() -> int:
    args = parse_args()
    root = repo_root(__file__)
    changed = _changed_files(root=root, base_ref=args.base_ref, head_ref=args.head_ref)
    rubric_files = [path for path in changed if RUBRIC_CHECK_PATTERN.match(path)]
    if len(rubric_files) > 1:
        raise SystemExit("Expected at most one rubric_check.json handoff per PR.")

    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    if not rubric_files:
        payload = {"found": False, "changed_files": changed}
        out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        out_md.write_text("", encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 0

    rel_path = rubric_files[0]
    match = RUBRIC_CHECK_PATTERN.match(rel_path)
    assert match is not None
    day = match.group(1)
    tracked_path = root / rel_path
    payload = json.loads(tracked_path.read_text(encoding="utf-8"))
    copy_result = copy_tracked_rubric_check_to_build(repo_root=root, day=day)
    markdown = render_rubric_check_markdown(payload)
    response = {
        "found": True,
        "day": day,
        "tracked_path": rel_path,
        "build_path": str(Path(copy_result["build_path"]).relative_to(root)),
        "markdown": markdown,
    }
    out_json.write_text(json.dumps(response, indent=2), encoding="utf-8")
    out_md.write_text(markdown, encoding="utf-8")
    print(json.dumps(response, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
