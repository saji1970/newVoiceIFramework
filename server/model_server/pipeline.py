from __future__ import annotations

import logging
from typing import Any

from server.model_server.config_loader import NodeConfig, PipelineConfig
from server.model_server.nodes.api_node import APINode
from server.model_server.nodes.base import NodeResult, PipelineContext, PipelineNode
from server.model_server.nodes.condition_node import ConditionNode
from server.model_server.nodes.llm_node import LLMNode
from server.model_server.nodes.loop_node import LoopNode
from server.model_server.nodes.tool_node import ToolNode
from server.model_server.nodes.transform_node import TransformNode

logger = logging.getLogger(__name__)

NODE_TYPES: dict[str, type[PipelineNode]] = {
    "llm": LLMNode,
    "api": APINode,
    "transform": TransformNode,
    "condition": ConditionNode,
    "loop": LoopNode,
    "tool": ToolNode,
}


class PipelineExecutionError(Exception):
    def __init__(self, node_id: str, message: str):
        self.node_id = node_id
        super().__init__(f"Node '{node_id}': {message}")


class PipelineEngine:
    """Executes pipelines defined by PipelineConfig."""

    def __init__(self):
        self._node_types = dict(NODE_TYPES)

    def register_node_type(self, type_name: str, cls: type[PipelineNode]):
        """Register a custom node type."""
        self._node_types[type_name] = cls

    def _create_node(self, node_config: NodeConfig) -> PipelineNode:
        cls = self._node_types.get(node_config.type)
        if cls is None:
            raise ValueError(f"Unknown node type: {node_config.type}")
        return cls(node_id=node_config.id, config=node_config.config)

    def validate(self, config: PipelineConfig) -> list[str]:
        """Validate a pipeline config. Returns list of errors."""
        errors = []
        for node_config in config.nodes:
            if node_config.type not in self._node_types:
                errors.append(f"Node '{node_config.id}': unknown type '{node_config.type}'")
                continue
            node = self._create_node(node_config)
            errors.extend(node.validate_config())
        return errors

    async def execute(
        self,
        config: PipelineConfig,
        input_data: dict[str, Any],
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a pipeline and return all node outputs."""
        context = PipelineContext(
            variables={
                **config.variables,
                **(variables or {}),
                "input": input_data.get("input", ""),
            },
        )
        # Also make all input data available
        context.variables.update(input_data)

        # Build node lookup
        nodes: dict[str, tuple[NodeConfig, PipelineNode]] = {}
        for nc in config.nodes:
            nodes[nc.id] = (nc, self._create_node(nc))

        # Provide node executor callback for LoopNode
        async def _execute_node(node_id: str, inputs: dict, ctx: PipelineContext) -> NodeResult:
            if node_id not in nodes:
                return NodeResult(output=None, success=False, error=f"Node '{node_id}' not found")
            _, node = nodes[node_id]
            return await node.execute(inputs, ctx)

        context.node_executor = _execute_node

        # Execute nodes in order, following condition routing
        executed: set[str] = set()
        execution_order = [nc.id for nc in config.nodes]

        i = 0
        while i < len(execution_order):
            node_id = execution_order[i]
            if node_id in executed:
                i += 1
                continue

            if node_id not in nodes:
                logger.warning(f"Node '{node_id}' referenced but not defined, skipping")
                i += 1
                continue

            nc, node = nodes[node_id]
            logger.info(f"Executing node: {node_id} (type={nc.type})")

            result = await node.execute(input_data, context)
            context.set_output(node_id, result.output)
            executed.add(node_id)

            if not result.success:
                logger.error(f"Node '{node_id}' failed: {result.error}")
                raise PipelineExecutionError(node_id, result.error or "Unknown error")

            # Handle condition routing: jump to the target node
            if nc.type == "condition" and result.output:
                target = result.output
                if target in nodes and target not in executed:
                    # Insert the target as the next node to execute
                    if target not in execution_order[i + 1 :]:
                        execution_order.insert(i + 1, target)

            i += 1

        return {
            "outputs": context.node_outputs,
            "variables": context.variables,
            "final_output": context.node_outputs.get(config.nodes[-1].id) if config.nodes else None,
        }


# Singleton
pipeline_engine = PipelineEngine()
