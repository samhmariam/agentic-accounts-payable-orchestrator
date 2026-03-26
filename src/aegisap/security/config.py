from __future__ import annotations

import os
from typing import Literal

from pydantic import BaseModel, Field


EnvironmentName = Literal["local", "test", "staging", "production", "cloud"]
CredentialMode = Literal["entra_developer_identity", "managed_identity"]

DEFAULT_RESUME_TOKEN_SECRET_NAME = "aegisap-resume-token-secret"
DEFAULT_LANGSMITH_API_KEY_SECRET_NAME = "aegisap-langsmith-api-key"
FORBIDDEN_ENV_VARS = {
    "SEARCH_ADMIN_KEY",
    "SEARCH_QUERY_KEY",
    "AZURE_SEARCH_ADMIN_KEY",
    "AZURE_SEARCH_QUERY_KEY",
    "AZURE_OPENAI_API_KEY",
    "OPENAI_API_KEY",
    "AZURE_STORAGE_KEY",
    "AZURE_STORAGE_CONNECTION_STRING",
    "LANGSMITH_API_KEY",
}
FORBIDDEN_CONNECTION_STRING_VARS = {
    "AZURE_SEARCH_CONNECTION_STRING",
    "AZURE_OPENAI_CONNECTION_STRING",
}
ALLOWED_CONNECTION_STRING_VARS = {
    "APPLICATIONINSIGHTS_CONNECTION_STRING",
}


class SecurityConfig(BaseModel):
    environment: EnvironmentName = "local"
    credential_mode: CredentialMode = "entra_developer_identity"
    service_name: str = "aegisap-api"
    git_sha: str = "dev"
    image_tag: str = "dev"
    key_vault_uri: str = ""
    application_insights_connection_string: str = ""
    deployment_revision: str = "dev"
    tracing_enabled: bool = True
    trace_sample_ratio: float = 1.0
    light_model_deployment: str = ""
    strong_model_deployment: str = ""
    cache_enabled: bool = False
    cache_ttl_seconds: int = 300
    backpressure_enabled: bool = True
    cheap_model_max_concurrency: int = 8
    strong_model_max_concurrency: int = 2
    compiled_prompt_version: str = "baseline"
    langsmith_project: str = ""
    langsmith_endpoint: str = ""
    langsmith_api_key_secret_name: str = DEFAULT_LANGSMITH_API_KEY_SECRET_NAME
    langsmith_api_key: str = ""
    postgres_dsn: str = ""
    resume_token_secret_name: str = DEFAULT_RESUME_TOKEN_SECRET_NAME
    resume_token_secret: str = ""
    forbidden_env_vars_present: list[str] = Field(default_factory=list)

    @property
    def is_local_like(self) -> bool:
        return self.environment in {"local", "test"}


def load_security_config(env: dict[str, str] | None = None) -> SecurityConfig:
    source = env or dict(os.environ)
    environment = _environment_name(source)
    credential_mode: CredentialMode = (
        "entra_developer_identity" if environment in {"local", "test"} else "managed_identity"
    )
    forbidden_present = _forbidden_env_vars(source, environment)
    return SecurityConfig(
        environment=environment,
        credential_mode=credential_mode,
        service_name=source.get("AEGISAP_SERVICE_NAME", "aegisap-api").strip() or "aegisap-api",
        git_sha=source.get("AEGISAP_GIT_SHA", "dev").strip() or "dev",
        image_tag=source.get("AEGISAP_IMAGE_TAG", source.get("AEGISAP_GIT_SHA", "dev")).strip()
        or source.get("AEGISAP_GIT_SHA", "dev").strip()
        or "dev",
        key_vault_uri=source.get("AZURE_KEY_VAULT_URI", "").strip(),
        application_insights_connection_string=source.get(
            "APPLICATIONINSIGHTS_CONNECTION_STRING", ""
        ).strip(),
        deployment_revision=source.get("AEGISAP_DEPLOYMENT_REVISION", "dev").strip() or "dev",
        tracing_enabled=_bool_env(source.get("AEGISAP_TRACING_ENABLED"), default=True),
        trace_sample_ratio=_sample_ratio(source.get("AEGISAP_TRACE_SAMPLE_RATIO")),
        light_model_deployment=source.get("AEGISAP_LIGHT_MODEL_DEPLOYMENT", "").strip(),
        strong_model_deployment=source.get("AEGISAP_STRONG_MODEL_DEPLOYMENT", "").strip(),
        cache_enabled=_bool_env(source.get("AEGISAP_CACHE_ENABLED"), default=False),
        cache_ttl_seconds=_int_env(source.get("AEGISAP_CACHE_TTL_SECONDS"), default=300, minimum=30),
        backpressure_enabled=_bool_env(source.get("AEGISAP_BACKPRESSURE_ENABLED"), default=True),
        cheap_model_max_concurrency=_int_env(
            source.get("AEGISAP_CHEAP_MODEL_MAX_CONCURRENCY"),
            default=8,
            minimum=1,
        ),
        strong_model_max_concurrency=_int_env(
            source.get("AEGISAP_STRONG_MODEL_MAX_CONCURRENCY"),
            default=2,
            minimum=1,
        ),
        compiled_prompt_version=source.get("AEGISAP_COMPILED_PROMPT_VERSION", "baseline").strip()
        or "baseline",
        langsmith_project=source.get("LANGSMITH_PROJECT", "").strip(),
        langsmith_endpoint=source.get("LANGSMITH_ENDPOINT", "").strip(),
        langsmith_api_key_secret_name=source.get(
            "AEGISAP_LANGSMITH_API_KEY_SECRET_NAME",
            DEFAULT_LANGSMITH_API_KEY_SECRET_NAME,
        ).strip()
        or DEFAULT_LANGSMITH_API_KEY_SECRET_NAME,
        langsmith_api_key=source.get("LANGSMITH_API_KEY", "").strip(),
        postgres_dsn=source.get("AEGISAP_POSTGRES_DSN", "").strip(),
        resume_token_secret_name=source.get(
            "AEGISAP_RESUME_TOKEN_SECRET_NAME",
            DEFAULT_RESUME_TOKEN_SECRET_NAME,
        ).strip()
        or DEFAULT_RESUME_TOKEN_SECRET_NAME,
        resume_token_secret=source.get("AEGISAP_RESUME_TOKEN_SECRET", "").strip(),
        forbidden_env_vars_present=forbidden_present,
    )


def _environment_name(env: dict[str, str]) -> EnvironmentName:
    if env.get("PYTEST_CURRENT_TEST"):
        return "test"
    value = env.get("AEGISAP_ENVIRONMENT", "").strip().lower()
    if value in {"local", "test", "staging", "production", "cloud"}:
        return value  # type: ignore[return-value]
    return "local"


def _forbidden_env_vars(env: dict[str, str], environment: EnvironmentName) -> list[str]:
    present: list[str] = []
    for name in FORBIDDEN_ENV_VARS:
        if env.get(name, "").strip():
            present.append(name)

    for name, value in env.items():
        if not value or not value.strip():
            continue
        upper = name.upper()
        if upper in ALLOWED_CONNECTION_STRING_VARS:
            continue
        if upper in FORBIDDEN_CONNECTION_STRING_VARS:
            present.append(name)
        if upper == "AEGISAP_POSTGRES_DSN" and environment not in {"local", "test"}:
            present.append(name)
        if upper == "AEGISAP_RESUME_TOKEN_SECRET" and environment not in {"local", "test"}:
            present.append(name)
    return sorted(set(present))


def _bool_env(value: str | None, *, default: bool) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


def _sample_ratio(value: str | None) -> float:
    if value is None or not value.strip():
        return 1.0
    try:
        ratio = float(value)
    except ValueError:
        return 1.0
    return max(0.0, min(1.0, ratio))


def _int_env(value: str | None, *, default: int, minimum: int = 0) -> int:
    if value is None or not value.strip():
        return default
    try:
        parsed = int(value)
    except ValueError:
        return default
    return max(minimum, parsed)
