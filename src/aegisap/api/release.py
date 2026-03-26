from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aegisap.api.models import DecisionEnvelope, HealthResponse, StructuredRefusalResponse, VersionResponse
from aegisap.observability.azure_monitor import azure_monitor_configured
from aegisap.security.config import SecurityConfig, load_security_config
from aegisap.security.key_vault import get_resume_token_secret, get_secret_value
from aegisap.training.postgres import build_connection_factory_from_env


@dataclass(slots=True)
class ReleaseMetadata:
    service_name: str
    environment: str
    deployment_revision: str
    git_sha: str
    image_tag: str

    @classmethod
    def from_config(cls, config: SecurityConfig | None = None) -> "ReleaseMetadata":
        resolved = config or load_security_config()
        return cls(
            service_name=resolved.service_name,
            environment=resolved.environment,
            deployment_revision=resolved.deployment_revision,
            git_sha=resolved.git_sha,
            image_tag=resolved.image_tag,
        )

    def version_payload(self) -> VersionResponse:
        return VersionResponse(
            service_name=self.service_name,
            environment=self.environment,
            deployment_revision=self.deployment_revision,
            git_sha=self.git_sha,
            image_tag=self.image_tag,
        )


def health_live_payload(config: SecurityConfig | None = None) -> HealthResponse:
    metadata = ReleaseMetadata.from_config(config)
    return HealthResponse(
        status="ok",
        service_name=metadata.service_name,
        environment=metadata.environment,
        deployment_revision=metadata.deployment_revision,
        git_sha=metadata.git_sha,
        image_tag=metadata.image_tag,
        checks={"process": "ok"},
    )


def health_ready_payload(config: SecurityConfig | None = None) -> HealthResponse:
    resolved = config or load_security_config()
    metadata = ReleaseMetadata.from_config(resolved)
    checks: dict[str, str] = {
        "app_loaded": "ok",
        "tracing": "ok" if (resolved.tracing_enabled and azure_monitor_configured()) or not resolved.tracing_enabled else "not_ready",
    }

    checks["secrets"] = _check_secrets(resolved)
    checks["database"] = _check_database(resolved)
    status = "ok" if all(value == "ok" for value in checks.values()) else "not_ready"
    return HealthResponse(
        status=status,
        service_name=metadata.service_name,
        environment=metadata.environment,
        deployment_revision=metadata.deployment_revision,
        git_sha=metadata.git_sha,
        image_tag=metadata.image_tag,
        checks=checks,
    )


def decision_envelope(day6_review: dict[str, Any] | None) -> DecisionEnvelope:
    if not day6_review:
        return DecisionEnvelope(decision_class="unknown", outcome="unknown")

    outcome = day6_review.get("outcome", "unknown")
    reasons = day6_review.get("reasons", [])
    reason_codes = [reason["code"] for reason in reasons if "code" in reason]
    primary_reason_code = reason_codes[0] if reason_codes else None
    if outcome == "approved_to_proceed":
        return DecisionEnvelope(
            decision_class="approved",
            outcome=outcome,
            primary_reason_code=primary_reason_code,
            reason_codes=reason_codes,
            blocking=False,
        )
    if outcome == "needs_human_review":
        return DecisionEnvelope(
            decision_class="manual_review",
            outcome=outcome,
            primary_reason_code=primary_reason_code,
            reason_codes=reason_codes,
            blocking=True,
        )
    refusal = StructuredRefusalResponse(
        primary_reason_code=primary_reason_code or "POLICY_CONFLICT",
        reason_codes=reason_codes or ["POLICY_CONFLICT"],
        review_stage=day6_review.get("review_stage", "policy_tax_compliance_review"),
        policy_version=((day6_review.get("model_trace") or {}).get("policy_version")),
        citations_count=len(day6_review.get("citations") or []),
    )
    return DecisionEnvelope(
        decision_class="structured_refusal",
        outcome=outcome,
        primary_reason_code=refusal.primary_reason_code,
        reason_codes=refusal.reason_codes,
        blocking=True,
        structured_refusal=refusal,
    )


def _check_database(config: SecurityConfig) -> str:
    required_present = bool(config.postgres_dsn) or all(
        (
            _env("AZURE_POSTGRES_HOST"),
            _env("AZURE_POSTGRES_PORT"),
            _env("AZURE_POSTGRES_DB"),
            _env("AZURE_POSTGRES_USER"),
        )
    )
    if config.is_local_like and not required_present:
        return "ok"
    try:
        connect = build_connection_factory_from_env()
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return "ok"
    except Exception:
        return "not_ready"


def _check_secrets(config: SecurityConfig) -> str:
    try:
        get_resume_token_secret(config)
        if config.langsmith_project:
            if config.langsmith_api_key:
                return "ok"
            if config.key_vault_uri:
                get_secret_value(config.langsmith_api_key_secret_name)
            else:
                return "not_ready"
        return "ok"
    except Exception:
        return "not_ready"


def _env(name: str) -> str:
    import os

    return os.getenv(name, "").strip()
