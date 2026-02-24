"""
ChatRepository - 对话数据访问层

提供会话和消息的 CRUD 操作。所有数据库操作集中在此层，
上层 Service 不直接操作 ORM 对象。
"""

from typing import Optional, List
from src.main.models.chat import AgentChatSession, AgentChatMessage
from src.main.core.orm.repository.base import BaseRepository
from sqlalchemy import select, update, asc, desc, func, delete


class ChatRepository(BaseRepository):

    # ====================== Session 操作 ======================

    async def create_session(
        self,
        user_id: Optional[str] = None,
        title: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> AgentChatSession:
        """创建新会话"""
        session = AgentChatSession(
            user_id=user_id,
            title=title,
            model=model,
            system_prompt=system_prompt,
            metadata_=metadata,
        )
        self.async_session.add(session)
        await self.async_session.flush()
        return session

    async def get_session(self, session_id: str) -> Optional[AgentChatSession]:
        """获取指定会话(排除已删除)"""
        result = await self.async_session.execute(
            select(AgentChatSession).where(
                AgentChatSession.id == session_id,
                AgentChatSession.is_deleted == False,  # noqa: E712
            )
        )
        return result.scalar_one_or_none()

    async def get_all_sessions(
        self,
        limit: int = 20,
        offset: int = 0,
        user_id: Optional[str] = None,
    ) -> List[AgentChatSession]:
        """获取会话列表(排除已删除)"""
        query = select(AgentChatSession).where(AgentChatSession.is_deleted == False)  # noqa: E712
        if user_id:
            query = query.where(AgentChatSession.user_id == user_id)
        query = query.order_by(desc(AgentChatSession.updated_at)).offset(offset).limit(limit)
        result = await self.async_session.execute(query)
        return list(result.scalars().all())

    async def count_sessions(self, user_id: Optional[str] = None) -> int:
        """统计会话总数(排除已删除)"""
        query = select(func.count(AgentChatSession.id)).where(AgentChatSession.is_deleted == False)  # noqa: E712
        if user_id:
            query = query.where(AgentChatSession.user_id == user_id)
        result = await self.async_session.execute(query)
        return result.scalar() or 0

    async def update_session(self, session_id: str, **kwargs) -> Optional[AgentChatSession]:
        """更新会话字段"""
        session = await self.get_session(session_id)
        if not session:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(session, key):
                setattr(session, key, value)
        self.async_session.add(session)
        await self.async_session.flush()
        return session

    async def rename_session(self, session_id: str, title: str) -> Optional[AgentChatSession]:
        """重命名会话"""
        return await self.update_session(session_id, title=title)

    async def soft_delete_session(self, session_id: str) -> bool:
        """软删除会话"""
        session = await self.get_session(session_id)
        if not session:
            return False
        session.is_deleted = True
        self.async_session.add(session)
        await self.async_session.flush()
        return True

    async def hard_delete_session(self, session_id: str) -> bool:
        """硬删除会话(同时级联删除关联消息)"""
        session = await self.get_session(session_id)
        if not session:
            return False
        await self.async_session.delete(session)
        await self.async_session.flush()
        return True

    # ====================== Message 操作 ======================

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        user_id: Optional[str] = None,
        token_count: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> AgentChatMessage:
        """新增消息"""
        message = AgentChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            user_id=user_id,
            token_count=token_count,
            metadata_=metadata,
        )
        self.async_session.add(message)
        await self.async_session.flush()
        return message

    async def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = None,
    ) -> List[AgentChatMessage]:
        """获取会话消息列表(排除已删除)"""
        query = (
            select(AgentChatMessage)
            .where(
                AgentChatMessage.session_id == session_id,
                AgentChatMessage.is_deleted == False,  # noqa: E712
            )
            .order_by(asc(AgentChatMessage.created_at))
        )
        if limit:
            query = query.limit(limit)
        result = await self.async_session.execute(query)
        return list(result.scalars().all())

    async def get_message(self, message_id: str) -> Optional[AgentChatMessage]:
        """获取指定消息"""
        result = await self.async_session.execute(
            select(AgentChatMessage).where(
                AgentChatMessage.id == message_id,
                AgentChatMessage.is_deleted == False,  # noqa: E712
            )
        )
        return result.scalar_one_or_none()

    async def soft_delete_message(self, message_id: str) -> bool:
        """软删除消息"""
        message = await self.get_message(message_id)
        if not message:
            return False
        message.is_deleted = True
        self.async_session.add(message)
        await self.async_session.flush()
        return True

    async def count_messages(self, session_id: str) -> int:
        """统计会话消息数"""
        result = await self.async_session.execute(
            select(func.count(AgentChatMessage.id)).where(
                AgentChatMessage.session_id == session_id,
                AgentChatMessage.is_deleted == False,  # noqa: E712
            )
        )
        return result.scalar() or 0

    async def get_last_message(self, session_id: str, role: Optional[str] = None) -> Optional[AgentChatMessage]:
        """获取最后一条消息"""
        query = (
            select(AgentChatMessage)
            .where(
                AgentChatMessage.session_id == session_id,
                AgentChatMessage.is_deleted == False,  # noqa: E712
            )
            .order_by(desc(AgentChatMessage.created_at))
        )
        if role:
            query = query.where(AgentChatMessage.role == role)
        result = await self.async_session.execute(query.limit(1))
        return result.scalar_one_or_none()

    async def delete_messages_after(self, session_id: str, message_id: str) -> int:
        """删除指定消息之后的所有消息(用于重新生成)"""
        target = await self.get_message(message_id)
        if not target:
            return 0
        stmt = (
            update(AgentChatMessage)
            .where(
                AgentChatMessage.session_id == session_id,
                AgentChatMessage.created_at > target.created_at,
            )
            .values(is_deleted=True)
        )
        result = await self.async_session.execute(stmt)
        await self.async_session.flush()
        return result.rowcount
