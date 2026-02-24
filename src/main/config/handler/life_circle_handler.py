import typing

import fastapi
import loguru

from src.main.core.orm.event.base import (
    dispose_db_connection, initialize_db_connection, dispose_another_db_connection, initialize_another_db_connection
)

def execute_backend_server_event_handler(backend_app: fastapi.FastAPI) -> typing.Any:
    async def launch_backend_server_events() -> None:
        await initialize_db_connection(backend_app=backend_app)
    return launch_backend_server_events

def terminate_backend_server_event_handler(backend_app: fastapi.FastAPI) -> typing.Any:
    @loguru.logger.catch
    async def stop_backend_server_events() -> None:
        await dispose_db_connection(backend_app=backend_app)
    return stop_backend_server_events


# 其他数据库连接
def execute_another_db_connection_event_handler(backend_app: fastapi.FastAPI) -> typing.Any:
    async def launch_another_db_connection_events() -> None:
        await initialize_another_db_connection(backend_app=backend_app)
    return launch_another_db_connection_events

def terminate_another_db_connection_event_handler(backend_app: fastapi.FastAPI) -> typing.Any:
    @loguru.logger.catch
    async def stop_another_db_connection_events() -> None:
        await dispose_another_db_connection(backend_app=backend_app)
    return stop_another_db_connection_events
