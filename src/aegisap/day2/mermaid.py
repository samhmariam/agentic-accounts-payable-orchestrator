"""
Mermaid diagram generation for the Day 2 LangGraph workflow.

Converts the compiled LangGraph to a Mermaid flowchart string that
marimo can render with mo.mermaid().
"""
from __future__ import annotations


def generate_mermaid(graph=None) -> str:  # noqa: ANN001
    """
    Return a Mermaid flowchart string for the AegisAP Day 2 workflow.

    The ``graph`` parameter is accepted for future extension (e.g. extracting
    edges dynamically) but the topology is currently static because LangGraph's
    compiled graph does not expose a public edge-listing API.
    """
    return """\
flowchart TD
    START([START]) --> init_workflow
    init_workflow --> route_invoice

    route_invoice -->|high_value| high_value_review
    route_invoice -->|new_vendor| new_vendor_review
    route_invoice -->|clean_path| clean_path_finalize

    high_value_review --> finalize_workflow
    new_vendor_review --> finalize_workflow
    clean_path_finalize --> finalize_workflow

    finalize_workflow --> END([END])

    style high_value_review fill:#f9c74f,stroke:#f3722c
    style new_vendor_review fill:#90be6d,stroke:#43aa8b
    style clean_path_finalize fill:#4cc9f0,stroke:#4361ee
"""
