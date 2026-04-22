from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Connector(ABC):
    """Abstract base class for API connectors."""

    connector_type: str = "base"

    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config

    @abstractmethod
    async def execute(self, params: dict[str, Any]) -> Any:
        """Execute a request through this connector."""

    @abstractmethod
    async def test(self) -> bool:
        """Test the connector's connectivity. Returns True if successful."""

    def validate_config(self) -> list[str]:
        """Return validation errors for the config."""
        return []
