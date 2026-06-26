from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

try:  # pragma: no cover - exercised when langgraph is installed.
    from langgraph.graph import END, StateGraph
except ModuleNotFoundError:  # pragma: no cover - fallback is covered by tests in minimal envs.
    END = "__end__"

    NodeFn = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]

    class _CompiledGraph:
        def __init__(self, entry_point: str, nodes: dict[str, NodeFn], edges: dict[str, str]) -> None:
            self.entry_point = entry_point
            self.nodes = nodes
            self.edges = edges

        async def ainvoke(self, state: dict[str, Any]) -> dict[str, Any]:
            current = self.entry_point
            while current != END:
                state = await self.nodes[current](state)
                current = self.edges.get(current, END)
            return state

    class StateGraph:  # type: ignore[no-redef]
        def __init__(self, _state_type: Any) -> None:
            self.nodes: dict[str, NodeFn] = {}
            self.edges: dict[str, str] = {}
            self.entry_point: str | None = None

        def add_node(self, name: str, fn: NodeFn) -> None:
            self.nodes[name] = fn

        def set_entry_point(self, name: str) -> None:
            self.entry_point = name

        def add_edge(self, source: str, target: str) -> None:
            self.edges[source] = target

        def compile(self) -> _CompiledGraph:
            if not self.entry_point:
                raise ValueError("Graph entry point is required.")
            return _CompiledGraph(self.entry_point, self.nodes, self.edges)
