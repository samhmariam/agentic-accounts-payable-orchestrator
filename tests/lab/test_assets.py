from __future__ import annotations

import json
import subprocess
import sys
import tarfile
import textwrap
from pathlib import Path

import yaml

from aegisap.lab import drills
from aegisap.lab.assets import hydrate_remote_bundle
from aegisap.lab.engine import reset_incident, start_incident
from aegisap.lab.overlay import overlay_day, overlay_status


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _build_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "remote-lab-repo"
    repo.mkdir()
    _write(
        repo / "pyproject.toml",
        textwrap.dedent(
            """
            [project]
            name = "remote-mini-lab"
            version = "0.0.1"
            """
        ).strip()
        + "\n",
    )
    _write(repo / "app.txt", "healthy\n")
    _write(
        repo / "scripts" / "check_failure.py",
        textwrap.dedent(
            """
            from pathlib import Path
            import sys

            text = Path("app.txt").read_text(encoding="utf-8").strip()
            raise SystemExit(1 if text == "broken" else 0)
            """
        ).strip()
        + "\n",
    )
    _write(
        repo / "scripts" / "check_success.py",
        textwrap.dedent(
            """
            from pathlib import Path
            import sys

            text = Path("app.txt").read_text(encoding="utf-8").strip()
            raise SystemExit(0 if text == "healthy" else 1)
            """
        ).strip()
        + "\n",
    )
    _write(
        repo / "scripts" / "mark_azure.py",
        textwrap.dedent(
            """
            import json
            import sys
            from pathlib import Path

            action = sys.argv[1]
            receipt_dir = Path(".aegisap-lab") / "receipts"
            receipt_dir.mkdir(parents=True, exist_ok=True)
            (receipt_dir / f"{action}.json").write_text(json.dumps({"action": action}), encoding="utf-8")
            """
        ).strip()
        + "\n",
    )
    _write(
        repo / "scripts" / "baseline.py",
        textwrap.dedent(
            """
            import json
            from pathlib import Path

            Path("app.txt").write_text("healthy\\n", encoding="utf-8")
            receipt_dir = Path(".aegisap-lab") / "baseline"
            receipt_dir.mkdir(parents=True, exist_ok=True)
            (receipt_dir / "baseline.json").write_text(json.dumps({"status": "rebuilt"}), encoding="utf-8")
            """
        ).strip()
        + "\n",
    )
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "initial state")
    _git(repo, "branch", "-M", "main")
    return repo


def _bundle_root(server_root: Path, day: str) -> Path:
    normalized = f"{int(day):02d}"
    root = server_root / "staging" / f"day{normalized}"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _write_remote_bundle(server_root: Path, *, day: str, files: dict[str, str]) -> Path:
    normalized = f"{int(day):02d}"
    staging_root = _bundle_root(server_root, normalized)
    for rel_path, content in files.items():
        _write(staging_root / rel_path, content)
    archive_path = server_root / "days" / f"day{normalized}.tar.gz"
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "w:gz") as tar:
        for path in staging_root.rglob("*"):
            tar.add(path, arcname=str(path.relative_to(staging_root)))
    return archive_path


def _scenario_yaml(day: str) -> str:
    payload = {
        "day": day,
        "title": "Remote incident",
        "phase": "phase_1_trust_boundary",
        "baseline_track": "core",
        "baseline_reprovision_command": f"{sys.executable} scripts/baseline.py",
        "setup": {
            "apply_diff": "seed/incident.patch",
            "azure_script": f"{sys.executable} scripts/mark_azure.py break",
            "customer_drop": "customer_artifact.md",
        },
        "validation": {
            "reproduce_command": f"{sys.executable} scripts/check_failure.py",
            "ci_command": f"{sys.executable} scripts/check_success.py",
        },
        "teardown": {
            "revert_diff": "seed/incident.patch",
            "azure_script": f"{sys.executable} scripts/mark_azure.py restore",
            "cleanup": ["customer_artifact.md"],
        },
        "review": {
            "evaluator_profile": "remote-test-profile",
            "human_required": True,
        },
    }
    return yaml.safe_dump(payload, sort_keys=False)


def _overlay_yaml(day: str) -> str:
    normalized = f"{int(day):02d}"
    payload = {
        "schema_version": 1,
        "phase1_limits": {
            "max_cohorts": 2,
            "max_age_days": 60,
        },
        "days": {
            normalized: {
                "incident_asset_ref": f"incident.day{normalized}",
                "scenario_dir": f"scenarios/day{normalized}",
                "oral_defense_prompt_pool": [
                    "What would a hostile release board reject here?",
                    "What evidence would change your rollback decision?",
                    "Which approval role would block this?",
                ],
            }
        },
    }
    return yaml.safe_dump(payload, sort_keys=False)


def test_hydrate_remote_bundle_caches_day_bundle(monkeypatch, tmp_path: Path) -> None:
    repo = _build_repo(tmp_path)
    server_root = tmp_path / "asset-server"
    _write_remote_bundle(
        server_root,
        day="01",
        files={
            "overlay.yaml": _overlay_yaml("01"),
            "scenarios/day01/scenario.yaml": _scenario_yaml("01"),
        },
    )
    monkeypatch.setenv("AEGISAP_ASSET_PROVIDER", "remote")
    monkeypatch.setenv("AEGISAP_ASSET_BASE_URL", server_root.as_uri())
    monkeypatch.delenv("AEGISAP_ASSET_TOKEN", raising=False)

    payload = hydrate_remote_bundle(day="01", repo_root=repo)

    assert payload["status"] == "hydrated"
    assert (repo / ".aegisap-lab" / "cache" / "assets" / "days" / "day01" / "overlay.yaml").exists()
    status = overlay_status(repo)
    assert status["provider"] == "remote"
    assert status["cached_days"] == ["01"]


def test_overlay_day_reads_remote_bundle_overlay(monkeypatch, tmp_path: Path) -> None:
    repo = _build_repo(tmp_path)
    server_root = tmp_path / "asset-server"
    _write_remote_bundle(
        server_root,
        day="01",
        files={
            "overlay.yaml": _overlay_yaml("01"),
            "scenarios/day01/scenario.yaml": _scenario_yaml("01"),
        },
    )
    monkeypatch.setenv("AEGISAP_ASSET_PROVIDER", "remote")
    monkeypatch.setenv("AEGISAP_ASSET_BASE_URL", server_root.as_uri())

    entry = overlay_day("01", repo)

    assert entry["incident_asset_ref"] == "incident.day01"
    assert entry["scenario_dir"] == "scenarios/day01"
    assert len(entry["oral_defense_prompt_pool"]) == 3


def test_start_incident_uses_remote_bundle_assets(monkeypatch, tmp_path: Path) -> None:
    repo = _build_repo(tmp_path)
    server_root = tmp_path / "asset-server"
    _write_remote_bundle(
        server_root,
        day="01",
        files={
            "overlay.yaml": _overlay_yaml("01"),
            "scenarios/day01/scenario.yaml": _scenario_yaml("01"),
            "scenarios/day01/customer_artifact.md": "# Remote customer escalation\n",
            "scenarios/day01/seed/incident.patch": textwrap.dedent(
                """
                diff --git a/app.txt b/app.txt
                --- a/app.txt
                +++ b/app.txt
                @@ -1 +1 @@
                -healthy
                +broken
                """
            ).strip()
            + "\n",
        },
    )
    monkeypatch.setenv("AEGISAP_ASSET_PROVIDER", "remote")
    monkeypatch.setenv("AEGISAP_ASSET_BASE_URL", server_root.as_uri())

    journal = start_incident(day="01", repo_path=repo)

    assert journal.status == "ready"
    assert (repo / "app.txt").read_text(encoding="utf-8").strip() == "broken"
    assert (repo / "customer_artifact.md").exists()

    reset = reset_incident(day="01", repo_path=repo)
    assert reset.status == "reset"
    assert (repo / "app.txt").read_text(encoding="utf-8").strip() == "healthy"


def test_load_drill_metadata_reads_remote_bundle_source_file(monkeypatch, tmp_path: Path) -> None:
    repo = _build_repo(tmp_path)
    server_root = tmp_path / "asset-server"
    _write_remote_bundle(
        server_root,
        day="12",
        files={
            "overlay.yaml": _overlay_yaml("12"),
            "evals/failure_drills/drill_03_dns_misconfiguration.json": json.dumps(
                {"severity": "high", "signal": "private DNS broke"},
                indent=2,
            ),
        },
    )
    monkeypatch.setenv("AEGISAP_ASSET_PROVIDER", "remote")
    monkeypatch.setenv("AEGISAP_ASSET_BASE_URL", server_root.as_uri())

    payload = drills._load_drill_metadata(
        repo,
        "12",
        {
            "id": "drill_03_dns_misconfiguration",
            "source_file": "evals/failure_drills/drill_03_dns_misconfiguration.json",
        },
    )

    assert payload["severity"] == "high"
    assert payload["signal"] == "private DNS broke"
