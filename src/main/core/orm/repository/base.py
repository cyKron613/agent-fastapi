from sqlalchemy.ext.asyncio import (
    AsyncSession as SQLAlchemyAsyncSession,
)


class BaseRepository:
    """
    数据库持久层
    """

    def __init__(
        self,
        async_session: SQLAlchemyAsyncSession,
        async_another_session: SQLAlchemyAsyncSession | None = None,
    ):
        self.async_session = async_session
        self.async_another_session = async_another_session
