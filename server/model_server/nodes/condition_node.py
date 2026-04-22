from __future__ import annotations

from typing import Any

from server.model_server.nodes.base import NodeResult, PipelineContext, PipelineNode


class ConditionNode(PipelineNode):
    """Node that routes execution based on conditions (if/else branching)."""

    node_type = "condition"

    async def execute(self, inputs: dict[str, Any], context: PipelineContext) -> NodeResult:
        input_template = self.config.get("input", "")
        branches = self.config.get("branches", {})
        default_branch = branches.get("default")

        try:
            value = context.resolve_template(input_template).strip().lower()

            # Check each branch for a match
            for branch_key, target_node in branches.items():
                if branch_key == "default":
                    continue
                if branch_key.lower() in value or value in branch_key.lower():
                    return NodeResult(
                        output=target_node,
                        metadata={"matched_branch": branch_key, "input_value": value},
                    )

            # Fall back to default
            if default_branch:
                return NodeResult(
                    output=default_branch,
                    metadata={"matched_branch": "default", "input_value": value},
                )

            return NodeResult(output=None, metadata={"matched_branch": None, "input_value": value})
        except Exception as e:
            return NodeResult(output=None, success=False, error=str(e))

    def validate_config(self) -> list[str]:
        errors = []
        if not self.config.get("branches"):
            errors.append(f"Node {self.node_id}: 'branches' is required for condition nodes")
        return errors
