import typing
from sqlalchemy.ext.asyncio import (
    AsyncSession as SQLAlchemyAsyncSession,
)
from src.main.core.orm.db.base import async_db
from loguru import logger


async def get_async_session() -> (
    typing.AsyncGenerator[SQLAlchemyAsyncSession, None]
):
    """
    获取异步数据库连接会话
    为每个请求创建独立的会话，避免并发冲突
    """
    # 为每个请求创建新的会话实例
    async_session = SQLAlchemyAsyncSession(bind=async_db.async_engine)

    try:
        yield async_session
    except Exception as e:
        # 只有在会话还有效时才执行回滚
        if async_session.is_active:
            try:
                await async_session.rollback()
                logger.warning("数据库会话已回滚")
            except Exception as rollback_error:
                # 记录回滚错误但不重新抛出，避免掩盖原始异常
                logger.warning(f"数据库会话回滚失败: {rollback_error}")
        raise e  # 重新抛出原始异常
    finally:
        # 安全关闭会话
        try:
            # AsyncSession没有is_closed属性，直接调用close()
            # close()方法是幂等的，多次调用不会出错
            await async_session.close()
            logger.warning("数据库会话已关闭")
        except Exception as close_error:
            # 记录关闭错误但不抛出异常
            logger.warning(f"数据库会话关闭失败: {close_error}")


async def get_async_another_session() -> (
    typing.AsyncGenerator[SQLAlchemyAsyncSession, None]
):
    """
    获取异步数据库连接会话
    为每个请求创建独立的会话，避免并发冲突
    """
    # 为每个请求创建新的会话实例
    async_session_another = SQLAlchemyAsyncSession(bind=async_db.another_async_engine)
    
    try:
        yield async_session_another
    except Exception as e:
        # 只有在会话还有效时才执行回滚
        if async_session_another.is_active:
            try:
                await async_session_another.rollback()
                logger.warning("数据库会话已回滚")
            except Exception as rollback_error:
                # 记录回滚错误但不重新抛出，避免掩盖原始异常
                logger.warning(f"数据库会话回滚失败: {rollback_error}")
        raise e  # 重新抛出原始异常
    finally:
        # 安全关闭会话
        try:
            # AsyncSession没有is_closed属性，直接调用close()
            # close()方法是幂等的，多次调用不会出错
            await async_session_another.close()
            logger.warning("数据库会话已关闭")
        except Exception as close_error:
            # 记录关闭错误但不抛出异常
            logger.warning(f"数据库会话关闭失败: {close_error}")
