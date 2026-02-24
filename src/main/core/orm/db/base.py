from typing import Union, Optional
import pydantic
import asyncio
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    AsyncEngine as SQLAlchemyAsyncEngine,
    create_async_engine as create_sqlalchemy_async_engine,
)
from sqlalchemy.pool import (
    Pool as SQLAlchemyPool,
    AsyncAdaptedQueuePool as SQLAlchemyAsyncAdaptedQueuePool,
)
from sqlalchemy import text
from loguru import logger
import pathlib
import sys
ROOT_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent.parent.parent.parent.parent.resolve()
sys.path.append(str(ROOT_DIR))
from src.main.config.manager import settings

class AsyncDatabase:
    """
    异步数据库连接
    """

    def __init__(self):
        self.postgres_uri: pydantic.PostgresDsn = pydantic.PostgresDsn(
            url=f"{settings.POSTGRES_CONNECT}://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )
        self.another_postgres_uri: pydantic.PostgresDsn = pydantic.PostgresDsn(
            url=f"{settings.POSTGRES_CONNECT_ANOTHER}://{settings.POSTGRES_USERNAME_ANOTHER}:{settings.POSTGRES_PASSWORD_ANOTHER}@{settings.POSTGRES_HOST_ANOTHER}:{settings.POSTGRES_PORT_ANOTHER}/{settings.POSTGRES_DB_ANOTHER}"
        )
        self.async_engine: SQLAlchemyAsyncEngine = (
            create_sqlalchemy_async_engine(
                url=self.gset_async_db_uri,
                echo=settings.IS_DB_ECHO_LOG,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_POOL_OVERFLOW,
                poolclass=SQLAlchemyAsyncAdaptedQueuePool,
                pool_timeout=settings.DB_POOL_TIMEOUT,
                pool_recycle=settings.DB_POOL_RECYCLE,
                pool_reset_on_return=settings.DB_POOL_RESET_ON_RETURN,
                connect_args={
                    "server_settings": {
                        "application_name": "ai-empower",
                    }
                }
            )
        )
        self.another_async_engine: SQLAlchemyAsyncEngine = (
            create_sqlalchemy_async_engine(
                url=self.gset_async_another_db_uri,
                echo=settings.IS_DB_ECHO_LOG,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_POOL_OVERFLOW,
                poolclass=SQLAlchemyAsyncAdaptedQueuePool,
                pool_timeout=settings.DB_POOL_TIMEOUT,
                pool_recycle=settings.DB_POOL_RECYCLE,
                pool_reset_on_return=settings.DB_POOL_RESET_ON_RETURN,
                connect_args={
                    "server_settings": {
                        "application_name": "ai-empower",
                    }
                }
            )
        )
        self.pool: SQLAlchemyPool = self.async_engine.pool
        self.another_pool: SQLAlchemyPool = self.another_async_engine.pool


    @property
    def gset_async_db_uri(
        self,
    ) -> Union[str, pydantic.PostgresDsn]:
        """
        Set the synchronous database driver into asynchronous version by utilizing AsyncPG:

            `postgresql://` => `postgresql+asyncpg://`
        """
        return (
            str(self.postgres_uri).replace(
                "postgresql://",
                "postgresql+asyncpg://",
            )
            if self.postgres_uri
            else self.postgres_uri
        )

    @property
    def gset_async_another_db_uri(
        self,
    ) -> Union[str, pydantic.PostgresDsn]:
        """
        Set the synchronous database driver into asynchronous version by utilizing AsyncPG:

            `postgresql://` => `postgresql+asyncpg://`
        """
        return (
            str(self.another_postgres_uri).replace(
                "postgresql://",
                "postgresql+asyncpg://",
            )
            if self.another_postgres_uri
            else self.another_postgres_uri
        )   
    

    async def close_all_connections(self):
        """
        关闭所有数据库连接，用于应用程序关闭时清理
        """
        if self.async_engine:
            await self.async_engine.dispose()
    
        if self.another_async_engine:
            await self.another_async_engine.dispose()



# 全局实例

async_db: AsyncDatabase = AsyncDatabase()
# print(async_db.gset_async_db_uri, 1111111111)
# print(async_db.gset_async_another_db_uri, 2222222222)
