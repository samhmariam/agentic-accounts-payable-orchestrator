"""Starter scaffold for an Azure Functions HTTP trigger (Day 13).

Copy this file to your function app project and rename the class.
This scaffold provides:
- Managed Identity token acquisition (no function keys)
- Structured JSON request/response
- Correlation ID propagation
- Basic input validation

To use:
    cp src/aegisap/integration/_scaffold/function_app_host.py \
       <your-function-project>/function_app.py
    # Then implement handle_invoice_event()
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from typing import Any

import azure.functions as func

# Uncomment when azure-identity is in your function app requirements.txt
# from azure.identity import DefaultAzureCredential

log = logging.getLogger(__name__)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


def _get_correlation_id(req: func.HttpRequest) -> str:
    """Extract or generate a correlation ID for tracing."""
    return req.headers.get("x-correlation-id") or str(uuid.uuid4())


def _validate_body(body: dict[str, Any]) -> list[str]:
    """Return a list of validation errors (empty = valid)."""
    errors: list[str] = []
    if "invoice_id" not in body:
        errors.append("Missing required field: invoice_id")
    if "amount" not in body:
        errors.append("Missing required field: amount")
    return errors


@app.route(route="invoice-event", methods=["POST"])
def invoice_event(req: func.HttpRequest) -> func.HttpResponse:
    """HTTP trigger: receive an invoice event and enqueue for processing."""
    correlation_id = _get_correlation_id(req)
    log.info("invoice-event received  correlation_id=%s", correlation_id)

    try:
        body: dict[str, Any] = req.get_json()  # type: ignore[assignment]
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON body"}),
            status_code=400,
            mimetype="application/json",
        )

    errs = _validate_body(body)
    if errs:
        return func.HttpResponse(
            json.dumps({"error": "Validation failed", "details": errs}),
            status_code=422,
            mimetype="application/json",
        )

    # TODO: replace with your processing logic
    result = handle_invoice_event(body, correlation_id=correlation_id)

    headers = {"x-correlation-id": correlation_id}
    return func.HttpResponse(
        json.dumps(result),
        status_code=200,
        mimetype="application/json",
        headers=headers,
    )


def handle_invoice_event(
    body: dict[str, Any],
    correlation_id: str,
) -> dict[str, Any]:
    """Implement your invoice-event processing logic here.

    Must return a JSON-serialisable dict.
    """
    # --- scaffold placeholder ---
    log.info(
        "handle_invoice_event  invoice_id=%s  correlation_id=%s",
        body.get("invoice_id"),
        correlation_id,
    )
    return {
        "status": "accepted",
        "invoice_id": body.get("invoice_id"),
        "correlation_id": correlation_id,
    }
