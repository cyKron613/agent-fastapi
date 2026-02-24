from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.main.core.orm.model.base import BaseModel as Base, generate_uuid
from src.main.config.manager import settings

POSTGRES_SCHEMA = settings.POSTGRES_SCHEMA


class AgentChatSession(Base):
    """会话表 - 记录每个对话会话"""
    __tablename__ = "agent_chat_sessions"
    __table_args__ = {"schema": POSTGRES_SCHEMA}

    id = Column(UUID, primary_key=True, default=generate_uuid)
    user_id = Column(String(64), index=True, comment="用户ID")
    title = Column(String(255), comment="会话标题")
    model = Column(String(100), nullable=True, comment="使用的模型名称")
    system_prompt = Column(Text, nullable=True, comment="会话级系统提示词")
    metadata_ = Column("metadata", JSON, nullable=True, comment="会话元数据(JSON)")
    is_deleted = Column(Boolean, default=False, comment="软删除标记")
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    messages = relationship("AgentChatMessage", back_populates="session", cascade="all, delete-orphan",
                            order_by="AgentChatMessage.created_at")


class AgentChatMessage(Base):
    """消息表 - 记录每条对话消息"""
    __tablename__ = "agent_chat_messages"
    __table_args__ = {"schema": POSTGRES_SCHEMA}

    id = Column(UUID, primary_key=True, default=generate_uuid)
    session_id = Column(UUID, ForeignKey(f"{POSTGRES_SCHEMA}.agent_chat_sessions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(64), comment="用户ID")
    role = Column(String(20), nullable=False, comment="角色: system/user/assistant/tool")
    content = Column(Text, nullable=False, comment="消息内容")
    token_count = Column(String(20), nullable=True, comment="token消耗数量")
    metadata_ = Column("metadata", JSON, nullable=True, comment="消息元数据(JSON)")
    is_deleted = Column(Boolean, default=False, comment="软删除标记")
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    session = relationship("AgentChatSession", back_populates="messages")
