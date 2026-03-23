from __future__ import annotations

from pathlib import Path

from .models import ExtractedInvoiceCandidate, InvoicePackageInput


def fixture_root() -> Path:
    return Path(__file__).resolve().parents[3] / "fixtures"


def load_fixture_package(case_name: str) -> InvoicePackageInput:
    path = fixture_root() / case_name / "package.json"
    return InvoicePackageInput.model_validate_json(path.read_text(encoding="utf-8"))


def load_fixture_candidate(case_name: str) -> ExtractedInvoiceCandidate:
    path = fixture_root() / case_name / "candidate.json"
    return ExtractedInvoiceCandidate.model_validate_json(path.read_text(encoding="utf-8"))


def list_fixture_cases() -> list[str]:
    return sorted(
        p.name
        for p in fixture_root().iterdir()
        if p.is_dir() and (p / "package.json").exists() and (p / "candidate.json").exists()
    )
