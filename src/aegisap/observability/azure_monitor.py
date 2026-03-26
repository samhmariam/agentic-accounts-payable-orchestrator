from __future__ import annotations

import logging

from aegisap.security.config import SecurityConfig

logger = logging.getLogger("aegisap.observability.azure_monitor")


def configure_azure_monitor_exporter(config: SecurityConfig) -> bool:
    if not config.application_insights_connection_string or not config.tracing_enabled:
        return False

    try:
        from azure.monitor.opentelemetry import configure_azure_monitor

        configure_azure_monitor(connection_string=config.application_insights_connection_string)
        return True
    except Exception as exc:  # pragma: no cover - defensive startup guard
        logger.warning("azure_monitor_configuration_failed: %s", exc)
        return False
