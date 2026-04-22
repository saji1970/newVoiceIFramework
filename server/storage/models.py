from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


def _utcnow():
    return datetime.now(timezone.utc)


def _new_id():
    return uuid.uuid4().hex


class ConversationRecord(Base):
    __tablename__ = "conversations"

    id = Column(String(32), primary_key=True, default=_new_id)
    system_prompt = Column(Text, nullable=True)
    provider = Column(String(50), nullable=True)
    model = Column(String(100), nullable=True)
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    messages = relationship("MessageRecord", back_populates="conversation", cascade="all, delete-orphan")


class MessageRecord(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(32), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    conversation = relationship("ConversationRecord", back_populates="messages")


class PipelineRecord(Base):
    __tablename__ = "pipelines"

    id = Column(String(32), primary_key=True, default=_new_id)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    config = Column(JSON, nullable=False)
    version = Column(String(20), default="1.0")
    enabled = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class ProviderConfig(Base):
    __tablename__ = "provider_configs"

    id = Column(String(32), primary_key=True, default=_new_id)
    name = Column(String(50), unique=True, nullable=False)
    provider_type = Column(String(50), nullable=False)
    config = Column(JSON, default=dict)
    enabled = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
