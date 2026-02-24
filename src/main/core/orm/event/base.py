import fastapi
from loguru import logger
from sqlalchemy import event
from sqlalchemy.dialects.postgresql.asyncpg import (
    AsyncAdapt_asyncpg_connection,
)
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.pool.base import _ConnectionRecord

from src.main.core.orm.db.base import async_db


@event.listens_for(
    target=async_db.async_engine.sync_engine,
    identifier="connect",
)
def inspect_db_server_on_connection(
    db_api_connection: AsyncAdapt_asyncpg_connection,
    connection_record: _ConnectionRecord,
) -> None:
    """
    新建连接监听器
    """
    logger.info(f"New DB API Connection ---\n {db_api_connection}")
    logger.info(f"Connection Record ---\n {connection_record}")


@event.listens_for(
    target=async_db.async_engine.sync_engine,
    identifier="close",
)
def inspect_db_server_on_close(
    db_api_connection: AsyncAdapt_asyncpg_connection,
    connection_record: _ConnectionRecord,
) -> None:
    """
    关闭连接监听器
    """
    logger.info(f"Closing DB API Connection ---\n {db_api_connection}")
    logger.info(f"Closed Connection Record ---\n {connection_record}")


async def initialize_db_tables(
    connection: AsyncConnection,
) -> None:
    """
    初始化数据库连接
    """
    logger.info("Database Need Do Something --- Initializing . . .")

    # await connection.run_sync(BaseModel.metadata.drop_all)
    # await connection.run_sync(BaseModel.metadata.create_all)
    # resut = await connection.exec_driver_sql("select current_schema()")
    # first = resut.first()

    logger.info("Database Need Do Something --- Successfully Initialized!")


async def initialize_db_connection(
    backend_app: fastapi.FastAPI,
) -> None:
    """
    初始化数据库连接
    """
    logger.info("Database Connection --- Establishing . . .")

    backend_app.state.db = async_db

    async with backend_app.state.db.async_engine.begin() as connection:
        await initialize_db_tables(connection=connection)

    logger.info("Database Connection --- Successfully Established!")


async def dispose_db_connection(
    backend_app: fastapi.FastAPI,
) -> None:
    """
    断开数据库连接
    """
    logger.info("Database Connection --- Disposing . . .")

    await backend_app.state.db.close_all_connections()

    logger.info("Database Connection --- Successfully Disposed!")


# 其他数据库连接
async def initialize_another_db_connection(
    backend_app: fastapi.FastAPI,
) -> None:
    """
    初始化其他数据库连接
    """
    logger.info("Another Database Connection --- Establishing . . .")

    backend_app.state.another_db = async_db

    async with backend_app.state.another_db.another_async_engine.begin() as connection:
        await initialize_db_tables(connection=connection)

    logger.info("Another Database Connection --- Successfully Established!")

async def dispose_another_db_connection(
    backend_app: fastapi.FastAPI,
) -> None:
    """
    断开其他数据库连接
    """
    logger.info("Another Database Connection --- Disposing . . .")

    await backend_app.state.another_db.close_all_connections()

    logger.info("Another Database Connection --- Successfully Disposed!")   
