from __future__ import annotations

import logging

from aegisap.security.config import SecurityConfig

logger = logging.getLogger("aegisap.observability.azure_monitor")
_AZURE_MONITOR_CONFIGURED = False


def configure_azure_monitor_exporter(config: SecurityConfig) -> bool:
    global _AZURE_MONITOR_CONFIGURED
    if not config.application_insights_connection_string or not config.tracing_enabled:
        _AZURE_MONITOR_CONFIGURED = False
        return False

    try:
        from azure.monitor.opentelemetry import configure_azure_monitor

        configure_azure_monitor(connection_string=config.application_insights_connection_string)
        _AZURE_MONITOR_CONFIGURED = True
        return True
    except Exception as exc:  # pragma: no cover - defensive startup guard
        logger.warning("azure_monitor_configuration_failed: %s", exc)
        _AZURE_MONITOR_CONFIGURED = False
        return False


def azure_monitor_configured() -> bool:
    return _AZURE_MONITOR_CONFIGURED
