from __future__ import annotations

from typing import Any

import httpx

from server.model_server.connectors.base import Connector


class HTTPConnector(Connector):
    """REST API connector."""

    connector_type = "http"

    def __init__(self, name: str, config: dict):
        super().__init__(name, config)
        self.base_url = config.get("base_url", "")
        self.default_headers = config.get("headers", {})
        self.auth_type = config.get("auth_type")  # bearer, api_key, basic
        self.auth_value = config.get("auth_value", "")
        self.timeout = config.get("timeout", 30)

    def _build_headers(self, extra_headers: dict | None = None) -> dict:
        headers = dict(self.default_headers)
        if self.auth_type == "bearer":
            headers["Authorization"] = f"Bearer {self.auth_value}"
        elif self.auth_type == "api_key":
            key_name = self.config.get("api_key_header", "X-API-Key")
            headers[key_name] = self.auth_value
        if extra_headers:
            headers.update(extra_headers)
        return headers

    async def execute(self, params: dict[str, Any]) -> Any:
        method = params.get("method", "GET").upper()
        path = params.get("path", "")
        headers = self._build_headers(params.get("headers"))
        body = params.get("body")
        query_params = params.get("params")

        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}" if path else self.base_url

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=body if method in ("POST", "PUT", "PATCH") else None,
                params=query_params,
            )
            response.raise_for_status()
            try:
                return response.json()
            except Exception:
                return response.text

    async def test(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    self.base_url,
                    headers=self._build_headers(),
                )
                return response.status_code < 500
        except Exception:
            return False

    def validate_config(self) -> list[str]:
        errors = []
        if not self.base_url:
            errors.append("'base_url' is required for HTTP connectors")
        return errors
