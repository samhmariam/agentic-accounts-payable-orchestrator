from __future__ import annotations

from aegisap.security.config import SecurityConfig


def validate_security_posture(config: SecurityConfig) -> None:
    if config.forbidden_env_vars_present:
        joined = ", ".join(config.forbidden_env_vars_present)
        raise RuntimeError(
            "forbidden runtime secrets detected in environment: "
            f"{joined}. Remove secret-based fallback paths before startup."
        )

    if not config.is_local_like and not config.key_vault_uri:
        raise RuntimeError("AZURE_KEY_VAULT_URI is required outside local/test environments.")

