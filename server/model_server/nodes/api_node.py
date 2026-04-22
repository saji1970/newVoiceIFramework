from __future__ import annotations

import json
from typing import Any

import httpx

from server.model_server.nodes.base import PipelineNode, NodeResult, PipelineContext


class APINode(PipelineNode):
    """Node that makes HTTP API calls."""

    node_type = "api"

    async def execute(self, inputs: dict[str, Any], context: PipelineContext) -> NodeResult:
        url_template = self.config.get("url", "")
        method = self.config.get("method", "GET").upper()
        headers = self.config.get("headers", {})
        body_template = self.config.get("body")
        timeout = self.config.get("timeout", 30)

        url = context.resolve_template(url_template)

        # Resolve header templates
        resolved_headers = {}
        for k, v in headers.items():
            resolved_headers[k] = context.resolve_template(str(v))

        # Resolve body template
        body = None
        if body_template:
            if isinstance(body_template, str):
                body = context.resolve_template(body_template)
            else:
                body = json.dumps(body_template)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=resolved_headers,
                    content=body if method in ("POST", "PUT", "PATCH") else None,
                )
                response.raise_for_status()

                # Try to parse as JSON, fall back to text
                try:
                    data = response.json()
                except Exception:
                    data = response.text

                return NodeResult(
                    output=data,
                    metadata={"status_code": response.status_code, "url": url},
                )
        except Exception as e:
            return NodeResult(output=None, success=False, error=str(e))

    def validate_config(self) -> list[str]:
        errors = []
        if not self.config.get("url"):
            errors.append(f"Node {self.node_id}: 'url' is required for API nodes")
        return errors
