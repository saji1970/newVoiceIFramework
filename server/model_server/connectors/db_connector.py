from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from server.model_server.connectors.base import Connector


class DBConnector(Connector):
    """Database connector using SQLAlchemy async."""

    connector_type = "db"

    def __init__(self, name: str, config: dict):
        super().__init__(name, config)
        self.connection_string = config.get("connection_string", "")
        self._engine: AsyncEngine | None = None

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            self._engine = create_async_engine(self.connection_string)
        return self._engine

    async def execute(self, params: dict[str, Any]) -> Any:
        query = params.get("query", "")
        query_params = params.get("params", {})

        async with self.engine.connect() as conn:
            result = await conn.execute(text(query), query_params)
            if result.returns_rows:
                rows = result.fetchall()
                columns = list(result.keys())
                return [dict(zip(columns, row)) for row in rows]
            await conn.commit()
            return {"affected_rows": result.rowcount}

    async def test(self) -> bool:
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                return True
        except Exception:
            return False

    def validate_config(self) -> list[str]:
        errors = []
        if not self.connection_string:
            errors.append("'connection_string' is required for DB connectors")
        return errors
