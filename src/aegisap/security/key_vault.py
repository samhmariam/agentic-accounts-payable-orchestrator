from __future__ import annotations

from functools import lru_cache

from aegisap.observability.tracing import node_span_attributes, start_observability_span
from aegisap.security.config import SecurityConfig, load_security_config
from aegisap.security.credentials import get_key_vault_secret_client
from aegisap.security.policy import validate_security_posture


@lru_cache(maxsize=64)
def get_secret_value(secret_name: str, *, version: str | None = None) -> str:
    config = load_security_config()
    validate_security_posture(config)
    with start_observability_span(
        "dep.key_vault.secret_get",
        attributes=node_span_attributes(node_name="key_vault_secret_get", idempotent=True),
    ):
        secret = get_key_vault_secret_client(vault_url=config.key_vault_uri).get_secret(
            secret_name,
            version=version,
        )
    return secret.value


def get_resume_token_secret(config: SecurityConfig | None = None) -> str:
    resolved = config or load_security_config()
    validate_security_posture(resolved)
    if resolved.resume_token_secret:
        return resolved.resume_token_secret
    if resolved.key_vault_uri:
        return get_secret_value(resolved.resume_token_secret_name)
    raise RuntimeError(
        "No resume token secret available. Provide AEGISAP_RESUME_TOKEN_SECRET locally "
        "or configure Key Vault access for non-local environments."
    )
