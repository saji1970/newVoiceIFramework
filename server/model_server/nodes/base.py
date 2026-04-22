from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable


@dataclass
class NodeResult:
    output: Any
    metadata: dict = field(default_factory=dict)
    success: bool = True
    error: str | None = None


class PipelineNode(ABC):
    """Abstract base class for all pipeline nodes."""

    node_type: str = "base"

    def __init__(self, node_id: str, config: dict):
        self.node_id = node_id
        self.config = config

    @abstractmethod
    async def execute(self, inputs: dict[str, Any], context: PipelineContext) -> NodeResult:
        """Execute this node with the given inputs and pipeline context."""

    def validate_config(self) -> list[str]:
        """Return a list of validation errors (empty = valid)."""
        return []


# Type alias for node executor callback used by LoopNode
NodeExecutor = Callable[[str, dict[str, Any], "PipelineContext"], Awaitable[NodeResult]]


@dataclass
class PipelineContext:
    """Shared context passed through the pipeline execution."""

    variables: dict[str, Any] = field(default_factory=dict)
    node_outputs: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    node_executor: NodeExecutor | None = None

    def resolve_template(self, template: str) -> str:
        """Resolve Jinja2-style {{variable}} references in a template string."""
        from jinja2 import Template

        tmpl = Template(template)
        render_ctx = {**self.variables, **self.node_outputs}
        return tmpl.render(**render_ctx)

    def set_output(self, node_id: str, output: Any):
        self.node_outputs[node_id] = output
