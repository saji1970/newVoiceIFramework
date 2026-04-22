from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.storage.models import ConversationRecord, MessageRecord, PipelineRecord


class ConversationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> ConversationRecord:
        record = ConversationRecord(**kwargs)
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def get(self, conversation_id: str) -> ConversationRecord | None:
        return await self.session.get(ConversationRecord, conversation_id)

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[ConversationRecord]:
        stmt = (
            select(ConversationRecord)
            .order_by(ConversationRecord.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_message(self, conversation_id: str, role: str, content: str) -> MessageRecord:
        record = MessageRecord(conversation_id=conversation_id, role=role, content=content)
        self.session.add(record)
        await self.session.commit()
        return record

    async def get_messages(self, conversation_id: str) -> list[MessageRecord]:
        stmt = (
            select(MessageRecord)
            .where(MessageRecord.conversation_id == conversation_id)
            .order_by(MessageRecord.id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class PipelineRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> PipelineRecord:
        record = PipelineRecord(**kwargs)
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def get(self, pipeline_id: str) -> PipelineRecord | None:
        return await self.session.get(PipelineRecord, pipeline_id)

    async def list_all(self, limit: int = 50) -> list[PipelineRecord]:
        stmt = select(PipelineRecord).order_by(PipelineRecord.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, pipeline_id: str, **kwargs) -> PipelineRecord | None:
        record = await self.get(pipeline_id)
        if record is None:
            return None
        for k, v in kwargs.items():
            setattr(record, k, v)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def delete(self, pipeline_id: str) -> bool:
        record = await self.get(pipeline_id)
        if record is None:
            return False
        await self.session.delete(record)
        await self.session.commit()
        return True
