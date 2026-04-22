from __future__ import annotations

from typing import Any

import httpx

from server.model_server.connectors.base import Connector


class GraphQLConnector(Connector):
    """GraphQL API connector."""

    connector_type = "graphql"

    def __init__(self, name: str, config: dict):
        super().__init__(name, config)
        self.endpoint = config.get("endpoint", "")
        self.headers = config.get("headers", {})
        self.auth_token = config.get("auth_token")
        self.timeout = config.get("timeout", 30)

    def _build_headers(self) -> dict:
        headers = {"Content-Type": "application/json", **self.headers}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    async def execute(self, params: dict[str, Any]) -> Any:
        query = params.get("query", "")
        variables = params.get("variables", {})
        operation_name = params.get("operation_name")

        payload = {"query": query, "variables": variables}
        if operation_name:
            payload["operationName"] = operation_name

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.endpoint,
                headers=self._build_headers(),
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            if "errors" in data:
                raise RuntimeError(f"GraphQL errors: {data['errors']}")

            return data.get("data")

    async def test(self) -> bool:
        try:
            result = await self.execute(
                {
                    "query": "{ __typename }",
                }
            )
            return result is not None
        except Exception:
            return False

    def validate_config(self) -> list[str]:
        errors = []
        if not self.endpoint:
            errors.append("'endpoint' is required for GraphQL connectors")
        return errors
