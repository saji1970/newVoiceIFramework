from __future__ import annotations

import re

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from server.config import settings

# Ensure PostgreSQL URLs always use the asyncpg driver (belt-and-suspenders with config validator).
_db_url = settings.database_url
if re.match(r"^postgres(ql)?://", _db_url):
    _db_url = re.sub(r"^postgres(ql)?://", "postgresql+asyncpg://", _db_url)

_engine_kwargs: dict = {"echo": settings.debug}

# Add connection-pool settings for PostgreSQL; SQLite uses a single file so pooling is a no-op.
if _db_url.startswith("postgresql"):
    _engine_kwargs.update(pool_size=5, max_overflow=10, pool_pre_ping=True)

engine = create_async_engine(_db_url, **_engine_kwargs)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    from server.storage.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
