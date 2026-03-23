from pathlib import Path

import pytest

from aegisap.day_01.service import IntakeReject
from aegisap.day2.run_workflow import run_from_fixture
from aegisap.day2.state import WorkflowState


class _FakeGraph:
    def invoke(self, state: WorkflowState) -> WorkflowState:
        return state


def test_run_from_fixture_infers_known_vendor_from_registry(monkeypatch) -> None:
    monkeypatch.setattr("aegisap.day2.run_workflow.build_graph", lambda: _FakeGraph())

    fixture_dir = Path("fixtures/day2/clean_path")
    state = run_from_fixture(fixture_dir)

    assert state.vendor.is_known_vendor is True


def test_run_from_fixture_allows_explicit_vendor_override(monkeypatch) -> None:
    monkeypatch.setattr("aegisap.day2.run_workflow.build_graph", lambda: _FakeGraph())

    fixture_dir = Path("fixtures/day2/clean_path")
    state = run_from_fixture(fixture_dir, known_vendor=False)

    assert state.vendor.is_known_vendor is False


def test_run_from_fixture_rejects_missing_po_before_day_2(monkeypatch) -> None:
    monkeypatch.setattr("aegisap.day2.run_workflow.build_graph", lambda: _FakeGraph())

    fixture_dir = Path("fixtures/missing_po")

    with pytest.raises(IntakeReject, match="po_reference_text is required"):
        run_from_fixture(fixture_dir)
