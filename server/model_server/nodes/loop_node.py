from __future__ import annotations

import json
import logging
from typing import Any

from server.model_server.nodes.base import NodeResult, PipelineContext, PipelineNode

logger = logging.getLogger(__name__)


class LoopNode(PipelineNode):
    """Node that iterates over a list, executing a sub-node for each item."""

    node_type = "loop"

    async def execute(self, inputs: dict[str, Any], context: PipelineContext) -> NodeResult:
        items_template = self.config.get("items", "")
        item_var = self.config.get("item_variable", "item")
        target_node = self.config.get("execute_node")
        max_iterations = self.config.get("max_iterations", 100)

        try:
            items_raw = context.resolve_template(items_template)

            # Parse items: try JSON list, or split by newline/comma
            try:
                items = json.loads(items_raw)
                if not isinstance(items, list):
                    items = [items]
            except (json.JSONDecodeError, TypeError):
                items = [i.strip() for i in str(items_raw).split(",") if i.strip()]

            items = items[:max_iterations]
            results = []

            for i, item in enumerate(items):
                context.variables[item_var] = item
                context.variables[f"{item_var}_index"] = i

                # Execute the target sub-node if specified and executor is available
                if target_node and context.node_executor:
                    sub_result = await context.node_executor(target_node, inputs, context)
                    results.append(sub_result.output)
                    if not sub_result.success:
                        logger.warning(
                            f"Loop iteration {i} failed on node '{target_node}': {sub_result.error}"
                        )
                else:
                    results.append(item)

            return NodeResult(
                output=results,
                metadata={
                    "item_count": len(items),
                    "target_node": target_node,
                },
            )
        except Exception as e:
            logger.error(f"LoopNode '{self.node_id}' failed: {e}")
            return NodeResult(output=None, success=False, error=str(e))

    def validate_config(self) -> list[str]:
        errors = []
        if not self.config.get("items"):
            errors.append(f"Node {self.node_id}: 'items' is required for loop nodes")
        return errors
