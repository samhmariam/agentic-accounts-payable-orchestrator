from __future__ import annotations

import json
import logging
from typing import Any

from aegisap.security.redaction import redact_value


def configure_application_logging() -> None:
    logging.basicConfig(level=logging.INFO)


def log_structured(logger: logging.Logger, event: str, **fields: Any) -> None:
    sanitized, _changed = redact_value(fields)
    logger.info("%s %s", event, json.dumps(sanitized, sort_keys=True, default=str))

