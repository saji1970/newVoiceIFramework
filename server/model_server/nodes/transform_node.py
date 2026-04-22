from __future__ import annotations

import json
from typing import Any

from jinja2 import Template

from server.model_server.nodes.base import PipelineNode, NodeResult, PipelineContext


class TransformNode(PipelineNode):
    """Node that transforms data using Jinja2 templates."""

    node_type = "transform"

    async def execute(self, inputs: dict[str, Any], context: PipelineContext) -> NodeResult:
        template_str = self.config.get("template", "")
        output_format = self.config.get("output_format", "text")  # text, json

        try:
            rendered = context.resolve_template(template_str)

            if output_format == "json":
                try:
                    output = json.loads(rendered)
                except json.JSONDecodeError:
                    output = rendered
            else:
                output = rendered

            return NodeResult(output=output)
        except Exception as e:
            return NodeResult(output=None, success=False, error=str(e))

    def validate_config(self) -> list[str]:
        errors = []
        if not self.config.get("template"):
            errors.append(f"Node {self.node_id}: 'template' is required for transform nodes")
        return errors
