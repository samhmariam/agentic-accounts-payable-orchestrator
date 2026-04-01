"""Static Bicep / ARM policy checker for AegisAP private-networking gate (Day 12).

Compiles every ``*.bicep`` file under ``infra/`` to ARM JSON via ``az bicep build``
and verifies that every AI-tier resource has ``publicNetworkAccess`` set to
``"Disabled"``.

Design rationale
----------------
Regex against raw Bicep text is unreliable (parameter references, modules,
conditional expressions).  Compiling to ARM JSON first forces parameter
substitution and produces a deterministic resource list we can inspect directly.

Artifact schema (written to ``build/day12/static_bicep_analysis.json``)::

    {
        "written_by": "check_private_network_static",
        "bicep_files_compiled": [...],
        "resources_checked": 3,
        "violations": [
            {"resource": "my-openai", "type": "Microsoft.CognitiveServices/accounts",
             "violation": "publicNetworkAccess=Enabled"}
        ],
        "all_passed": true,
        "compiled_at": "2025-01-01T00:00:00Z"
    }

Usage::

    checker = BicepPolicyChecker(infra_root=Path("infra"))
    result = checker.run()
"""
from __future__ import annotations

import datetime
import json
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Resource types that must have publicNetworkAccess == "Disabled"
_AI_RESOURCE_TYPES: frozenset[str] = frozenset({
    "microsoft.cognitiveservices/accounts",
    "microsoft.search/searchservices",
    "microsoft.machinelearningservices/workspaces",
    "microsoft.documentdb/databaseaccounts",
    "microsoft.keyvault/vaults",
    "microsoft.storage/storageaccounts",
})


@dataclass
class BicepViolation:
    resource: str
    resource_type: str
    violation: str
    bicep_source: str = ""


@dataclass
class BicepAnalysisResult:
    bicep_files_compiled: list[str] = field(default_factory=list)
    resources_checked: int = 0
    violations: list[BicepViolation] = field(default_factory=list)
    all_passed: bool = True
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "written_by": "check_private_network_static",
            "bicep_files_compiled": self.bicep_files_compiled,
            "resources_checked": self.resources_checked,
            "violations": [
                {
                    "resource": v.resource,
                    "type": v.resource_type,
                    "violation": v.violation,
                    "bicep_source": v.bicep_source,
                }
                for v in self.violations
            ],
            "all_passed": self.all_passed,
            "error": self.error,
            "compiled_at": datetime.datetime.utcnow().isoformat() + "Z",
        }


class BicepPolicyChecker:
    """Compile Bicep templates and enforce network-isolation policy."""

    def __init__(self, infra_root: Path) -> None:
        self._infra_root = infra_root.resolve()

    def _compile_bicep(self, bicep_path: Path) -> dict[str, Any]:
        """Compile a single Bicep file to ARM JSON.

        Uses a temporary output file rather than stdout because some versions
        of the Bicep CLI write diagnostic information to stdout alongside the
        JSON.

        Returns:
            Parsed ARM JSON dict.

        Raises:
            RuntimeError: if ``az bicep build`` fails or output is not JSON.
        """
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            result = subprocess.run(
                ["az", "bicep", "build", "--file", str(bicep_path),
                 "--outfile", str(tmp_path)],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"az bicep build failed for {bicep_path.name}: "
                    f"{result.stderr.strip() or result.stdout.strip()}"
                )
            return json.loads(tmp_path.read_text())
        finally:
            tmp_path.unlink(missing_ok=True)

    def _check_arm_template(
        self, arm: dict[str, Any], bicep_source: str
    ) -> tuple[int, list[BicepViolation]]:
        """Inspect an ARM template's resources[] for network-isolation violations.

        Args:
            arm: Parsed ARM JSON dict.
            bicep_source: Original Bicep filename (for violation metadata).

        Returns:
            Tuple of (resources_checked, violations).
        """
        resources: list[dict[str, Any]] = arm.get("resources", [])
        violations: list[BicepViolation] = []
        checked = 0

        for resource in resources:
            rtype: str = resource.get("type", "").lower()
            if rtype not in _AI_RESOURCE_TYPES:
                continue
            checked += 1
            rname: str = resource.get("name", "<unknown>")
            props: dict[str, Any] = resource.get("properties", {})
            pna: str = props.get("publicNetworkAccess", "Enabled")
            if pna != "Disabled":
                violations.append(
                    BicepViolation(
                        resource=rname,
                        resource_type=resource.get("type", rtype),
                        violation=f"publicNetworkAccess={pna!r} (expected 'Disabled')",
                        bicep_source=bicep_source,
                    )
                )

        return checked, violations

    def run(self) -> BicepAnalysisResult:
        """Compile all ``*.bicep`` files and report policy violations.

        If ``az bicep`` is not available on PATH, returns a failed result with
        a descriptive error rather than crashing.  This ensures the gate degrades
        gracefully in environments without the Azure CLI.
        """
        bicep_files = sorted(self._infra_root.rglob("*.bicep"))
        if not bicep_files:
            return BicepAnalysisResult(
                error=f"No *.bicep files found under {self._infra_root}",
                all_passed=False,
            )

        total_checked = 0
        all_violations: list[BicepViolation] = []
        compiled: list[str] = []

        for bf in bicep_files:
            try:
                arm = self._compile_bicep(bf)
            except FileNotFoundError:
                # az CLI not installed
                return BicepAnalysisResult(
                    error=(
                        "az bicep build failed: Azure CLI not found on PATH. "
                        "Install via: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
                    ),
                    all_passed=False,
                )
            except RuntimeError as exc:
                return BicepAnalysisResult(
                    bicep_files_compiled=compiled,
                    error=str(exc),
                    all_passed=False,
                )

            compiled.append(str(bf.relative_to(self._infra_root.parent)))
            checked, violations = self._check_arm_template(arm, bf.name)
            total_checked += checked
            all_violations.extend(violations)

        return BicepAnalysisResult(
            bicep_files_compiled=compiled,
            resources_checked=total_checked,
            violations=all_violations,
            all_passed=len(all_violations) == 0,
        )
