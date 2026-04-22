from __future__ import annotations

import asyncio
import importlib
import logging
from typing import Any

from server.config import settings
from server.model_server.nodes.base import PipelineNode, NodeResult, PipelineContext

logger = logging.getLogger(__name__)


class ToolNode(PipelineNode):
    """Node that calls a registered tool/function from an allowed module."""

    node_type = "tool"

    async def execute(self, inputs: dict[str, Any], context: PipelineContext) -> NodeResult:
        tool_name = self.config.get("tool")
        tool_module = self.config.get("module")
        tool_function = self.config.get("function")
        args_template = self.config.get("args", {})

        try:
            # Resolve argument templates
            resolved_args = {}
            for key, val in args_template.items():
                if isinstance(val, str):
                    resolved_args[key] = context.resolve_template(val)
                else:
                    resolved_args[key] = val

            # Load and execute the tool function
            if tool_module and tool_function:
                # Security: validate module against whitelist
                allowed = set(settings.allowed_tool_modules)
                if not allowed:
                    return NodeResult(
                        output=None,
                        success=False,
                        error="No allowed_tool_modules configured. "
                              "Add modules to ALLOWED_TOOL_MODULES in your .env to enable tool nodes.",
                    )

                if tool_module not in allowed:
                    logger.warning(
                        f"ToolNode '{self.node_id}' blocked: module '{tool_module}' "
                        f"not in allowed list: {allowed}"
                    )
                    return NodeResult(
                        output=None,
                        success=False,
                        error=f"Module '{tool_module}' is not in the allowed_tool_modules whitelist",
                    )

                mod = importlib.import_module(tool_module)
                func = getattr(mod, tool_function)

                if asyncio.iscoroutinefunction(func):
                    result = await func(**resolved_args)
                else:
                    result = func(**resolved_args)

                return NodeResult(
                    output=result,
                    metadata={"tool": f"{tool_module}.{tool_function}"},
                )

            return NodeResult(
                output=None,
                success=False,
                error=f"Tool '{tool_name}' not found. Provide 'module' and 'function'.",
            )
        except Exception as e:
            logger.error(f"ToolNode '{self.node_id}' execution failed: {e}")
            return NodeResult(output=None, success=False, error=str(e))

    def validate_config(self) -> list[str]:
        errors = []
        if not self.config.get("module") or not self.config.get("function"):
            errors.append(f"Node {self.node_id}: 'module' and 'function' are required for tool nodes")
        return errors
