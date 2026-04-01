"""Starter scaffold for a new AegisAP MCP server (Day 13).

Copy this file when creating a new domain-specific MCP server that extends
or replaces the default AegisAP MCP server.

Steps:
1. Copy to a new location: ``cp aegisap/mcp/_scaffold/server_scaffold.py my_mcp/server.py``
2. Rename ``MyDomainAdapter`` and add your tool handlers.
3. Register each tool with ``@app.post("/tools/<tool-name>")``.
4. Set required env vars: AZURE_TENANT_ID, AEGISAP_MCP_AUDIENCE.
5. Start with: ``uvicorn my_mcp.server:app --host 0.0.0.0 --port 8080``
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# 1. Define your request/response schemas
# ---------------------------------------------------------------------------
class MyToolRequest(BaseModel):
    """Replace with your actual request fields."""
    input_text: str
    requester_oid: str | None = None


class MyToolResponse(BaseModel):
    """Replace with your actual response fields."""
    result: str
    tool: str = "my_tool"
    citation_ids: list[str] = []


# ---------------------------------------------------------------------------
# 2. Implement your domain adapter
# ---------------------------------------------------------------------------
class MyDomainAdapter:
    """Replace with your actual LOB integration logic."""

    def my_tool(self, req: MyToolRequest) -> MyToolResponse:
        # Implement real logic here
        return MyToolResponse(result=f"Processed: {req.input_text}")


# ---------------------------------------------------------------------------
# 3. Wire up the FastAPI app
# ---------------------------------------------------------------------------
_adapter = MyDomainAdapter()

app = FastAPI(
    title="My MCP Server",
    version="1.0.0",
    description="Domain-specific MCP server built on the AegisAP scaffold.",
)


@app.get("/capabilities")
async def capabilities() -> dict[str, Any]:
    return {
        "protocol_version": "2024-11-05",
        "server_name": "my-mcp-server",
        "server_version": "1.0.0",
        "tools": ["my_tool"],
    }


@app.post("/tools/my_tool", response_model=MyToolResponse)
async def my_tool(req: MyToolRequest) -> MyToolResponse:
    """Replace this with your tool implementation."""
    return _adapter.my_tool(req)


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})
