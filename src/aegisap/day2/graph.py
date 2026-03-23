from __future__ import annotations

from typing import Any

from aegisap.day2.nodes import (
    clean_path_finalize,
    finalize_workflow,
    high_value_review,
    init_workflow,
    new_vendor_review,
    route_invoice,
)
from aegisap.day2.router import route_selector
from aegisap.day2.state import WorkflowState


def build_graph() -> Any:
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError as exc:
        raise ImportError(
            "LangGraph is required for Day 2. Install dependencies from requirements-day2.txt."
        ) from exc

    graph = StateGraph(WorkflowState)
    graph.add_node("init_workflow", init_workflow)
    graph.add_node("route_invoice", route_invoice)
    graph.add_node("high_value_review", high_value_review)
    graph.add_node("new_vendor_review", new_vendor_review)
    graph.add_node("clean_path_finalize", clean_path_finalize)
    graph.add_node("finalize_workflow", finalize_workflow)

    graph.add_edge(START, "init_workflow")
    graph.add_edge("init_workflow", "route_invoice")
    graph.add_conditional_edges(
        "route_invoice",
        route_selector,
        {
            "high_value": "high_value_review",
            "new_vendor": "new_vendor_review",
            "clean_path": "clean_path_finalize",
        },
    )
    graph.add_edge("high_value_review", "finalize_workflow")
    graph.add_edge("new_vendor_review", "finalize_workflow")
    graph.add_edge("clean_path_finalize", "finalize_workflow")
    graph.add_edge("finalize_workflow", END)
    return graph.compile()
