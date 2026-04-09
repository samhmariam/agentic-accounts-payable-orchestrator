from __future__ import annotations

import json
import os
import shutil
import tarfile
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .curriculum import normalize_day, resolve_repo_root


ASSET_PROVIDER_ENV = "AEGISAP_ASSET_PROVIDER"
ASSET_BASE_URL_ENV = "AEGISAP_ASSET_BASE_URL"
ASSET_TOKEN_ENV = "AEGISAP_ASSET_TOKEN"

ASSET_PROVIDER_LOCAL = "local"
ASSET_PROVIDER_REMOTE = "remote"

ASSET_CACHE_ROOT = Path(".aegisap-lab") / "cache" / "assets"
DAY_BUNDLE_ROOT = ASSET_CACHE_ROOT / "days"
DAY_BUNDLE_ARCHIVE_DIR = ASSET_CACHE_ROOT / "archives"
BUNDLE_METADATA_NAME = "bundle.json"
REMOTE_OVERLAY_FILE = "overlay.yaml"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def configured_asset_provider() -> str:
    provider = os.environ.get(ASSET_PROVIDER_ENV, ASSET_PROVIDER_LOCAL).strip().lower() or ASSET_PROVIDER_LOCAL
    if provider not in {ASSET_PROVIDER_LOCAL, ASSET_PROVIDER_REMOTE}:
        raise ValueError(
            f"Unsupported asset provider `{provider}`. Expected `{ASSET_PROVIDER_LOCAL}` or `{ASSET_PROVIDER_REMOTE}`."
        )
    return provider


def asset_base_url() -> str:
    return os.environ.get(ASSET_BASE_URL_ENV, "").strip()


def asset_token() -> str:
    return os.environ.get(ASSET_TOKEN_ENV, "").strip()


def asset_cache_dir(repo_root: str | Path | None = None) -> Path:
    return resolve_repo_root(repo_root) / ASSET_CACHE_ROOT


def day_bundle_cache_dir(day: str | int, repo_root: str | Path | None = None) -> Path:
    return asset_cache_dir(repo_root) / "days" / f"day{normalize_day(day)}"


def day_bundle_archive_path(day: str | int, repo_root: str | Path | None = None) -> Path:
    return asset_cache_dir(repo_root) / "archives" / f"day{normalize_day(day)}.tar.gz"


def day_bundle_metadata_path(day: str | int, repo_root: str | Path | None = None) -> Path:
    return day_bundle_cache_dir(day, repo_root) / BUNDLE_METADATA_NAME


def remote_bundle_url(day: str | int, *, base_url: str | None = None) -> str:
    normalized_day = normalize_day(day)
    root = (base_url or asset_base_url()).strip()
    if not root:
        raise ValueError(
            f"Remote asset provider requires `{ASSET_BASE_URL_ENV}` to be set."
        )
    if "{" in root:
        return root.format(day=normalized_day, day_slug=f"day{normalized_day}")
    return f"{root.rstrip('/')}/days/day{normalized_day}.tar.gz"


def _download_bundle(url: str, destination: Path, *, token: str = "") -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request: urllib.request.Request | str
    if token:
        request = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/gzip, application/x-tar, application/octet-stream",
            },
        )
    else:
        request = url
    with urllib.request.urlopen(request) as response, destination.open("wb") as handle:
        shutil.copyfileobj(response, handle)


def _safe_extract_tar(archive_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    destination_root = destination.resolve()
    with tarfile.open(archive_path, "r:*") as tar:
        for member in tar.getmembers():
            member_path = (destination / member.name).resolve()
            if destination_root not in member_path.parents and member_path != destination_root:
                raise ValueError(
                    f"Remote asset bundle contains an unsafe path outside the cache root: {member.name}"
                )
        tar.extractall(destination, filter="data")


def hydrate_remote_bundle(
    *,
    day: str | int,
    repo_root: str | Path | None = None,
    force: bool = False,
) -> dict[str, Any]:
    if configured_asset_provider() != ASSET_PROVIDER_REMOTE:
        raise ValueError(
            f"`hydrate_remote_bundle` requires `{ASSET_PROVIDER_ENV}={ASSET_PROVIDER_REMOTE}`."
        )
    root = resolve_repo_root(repo_root)
    normalized_day = normalize_day(day)
    bundle_dir = day_bundle_cache_dir(normalized_day, root)
    metadata_path = day_bundle_metadata_path(normalized_day, root)
    archive_path = day_bundle_archive_path(normalized_day, root)
    url = remote_bundle_url(normalized_day)
    asset_cache_dir(root).mkdir(parents=True, exist_ok=True)

    if bundle_dir.exists() and not force and (bundle_dir / REMOTE_OVERLAY_FILE).exists():
        cached = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
        return {
            "status": "cached",
            "provider": ASSET_PROVIDER_REMOTE,
            "day": normalized_day,
            "bundle_dir": str(bundle_dir),
            "archive_path": str(archive_path),
            "url": url,
            "metadata": cached,
        }

    if force:
        shutil.rmtree(bundle_dir, ignore_errors=True)
        archive_path.unlink(missing_ok=True)

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=str(asset_cache_dir(root))) as temp_root:
        temp_root_path = Path(temp_root)
        temp_archive = temp_root_path / f"day{normalized_day}.tar.gz"
        temp_bundle_dir = temp_root_path / f"day{normalized_day}"
        _download_bundle(url, temp_archive, token=asset_token())
        _safe_extract_tar(temp_archive, temp_bundle_dir)
        if not (temp_bundle_dir / REMOTE_OVERLAY_FILE).exists():
            raise ValueError(
                f"Remote bundle for day {normalized_day} is missing `{REMOTE_OVERLAY_FILE}`."
            )
        bundle_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.rmtree(bundle_dir, ignore_errors=True)
        shutil.move(str(temp_bundle_dir), str(bundle_dir))
        shutil.move(str(temp_archive), str(archive_path))

    metadata = {
        "provider": ASSET_PROVIDER_REMOTE,
        "day": normalized_day,
        "url": url,
        "fetched_at": _utc_now_iso(),
        "token_configured": bool(asset_token()),
        "overlay_path": str(bundle_dir / REMOTE_OVERLAY_FILE),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")
    return {
        "status": "hydrated",
        "provider": ASSET_PROVIDER_REMOTE,
        "day": normalized_day,
        "bundle_dir": str(bundle_dir),
        "archive_path": str(archive_path),
        "url": url,
        "metadata": metadata,
    }


def ensure_day_bundle(day: str | int, repo_root: str | Path | None = None) -> Path:
    root = resolve_repo_root(repo_root)
    if configured_asset_provider() == ASSET_PROVIDER_LOCAL:
        return root
    bundle_dir = day_bundle_cache_dir(day, root)
    if bundle_dir.exists() and (bundle_dir / REMOTE_OVERLAY_FILE).exists():
        return bundle_dir
    hydrate_remote_bundle(day=day, repo_root=root)
    return bundle_dir


def resolve_day_asset_path(
    *,
    day: str | int,
    relative_path: str,
    repo_root: str | Path | None = None,
) -> Path:
    root = ensure_day_bundle(day, repo_root)
    return (root / relative_path).resolve()


def bundle_overlay_path(day: str | int, repo_root: str | Path | None = None) -> Path:
    return resolve_day_asset_path(day=day, relative_path=REMOTE_OVERLAY_FILE, repo_root=repo_root)


def cached_remote_days(repo_root: str | Path | None = None) -> list[str]:
    root = asset_cache_dir(repo_root) / "days"
    if not root.exists():
        return []
    return sorted(
        path.name.removeprefix("day")
        for path in root.iterdir()
        if path.is_dir() and path.name.startswith("day")
    )


def asset_provider_status(repo_root: str | Path | None = None) -> dict[str, Any]:
    provider = configured_asset_provider()
    root = resolve_repo_root(repo_root)
    status = {
        "provider": provider,
        "cache_root": str(asset_cache_dir(root)),
    }
    if provider == ASSET_PROVIDER_LOCAL:
        return status
    status.update(
        {
            "base_url": asset_base_url(),
            "token_configured": bool(asset_token()),
            "cached_days": cached_remote_days(root),
        }
    )
    return status
