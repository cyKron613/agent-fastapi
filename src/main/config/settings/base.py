import logging
from typing import Dict, List, Tuple, Any, Optional

from decouple import config
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)
import pathlib
import sys
import os
from loguru import logger

ROOT_DIR: pathlib.Path = pathlib.Path(
    __file__
).parent.parent.parent.parent.parent.resolve()
sys.path.append(str(ROOT_DIR))



class BackendBaseSettings(BaseSettings):
    """
    后台基础配置
    """

    TITLE: str = "Agent-FastAPI"
    VERSION: str = "1.0.0"
    TIMEZONE: str = "+8"
    DESCRIPTION: str | None = "通用 Agent 开发框架 - 基于 FastAPI"
    DEBUG: bool = True

    BACKEND_SERVER_HOST: str = config("BACKEND_SERVER_HOST", cast=str)  # type: ignore
    BACKEND_SERVER_PORT: int = config("BACKEND_SERVER_PORT", cast=int)  # type: ignore
    BACKEND_SERVER_WORKERS: int = config("BACKEND_SERVER_WORKERS", cast=int)  # type: ignore
    API_PREFIX: str = config("API_PREFIX", cast=str)  # type: ignore
    DOCS_URL: str = config("DOCS_URL", cast=str)  # type: ignore
    OPENAPI_URL: str = config("OPENAPI_URL", cast=str)  # type: ignore
    REDOC_URL: str = config("REDOC_URL", cast=str)  # type: ignore
    OPENAPI_PREFIX: str = ""

    DOCS_AUTH_USERNAME: str = config("DOCS_AUTH_USERNAME", cast=str)  # type: ignore
    DOCS_AUTH_PASSWORD: str = config("DOCS_AUTH_PASSWORD", cast=str)  # type: ignore

    POSTGRES_CONNECT: str = config("POSTGRES_CONNECT", cast=str)  # type: ignore
    POSTGRES_HOST: str = config("POSTGRES_HOST", cast=str)  # type: ignore
    POSTGRES_PORT: int = config("POSTGRES_PORT", cast=int)  # type: ignore
    POSTGRES_DB: str = config("POSTGRES_DB", cast=str)  # type: ignore
    POSTGRES_USERNAME: str = config("POSTGRES_USERNAME", cast=str)  # type: ignore
    POSTGRES_PASSWORD: str = config("POSTGRES_PASSWORD", cast=str)  # type: ignore
    # POSTGRES_SCHEMA: str = config("POSTGRES_SCHEMA", cast=str)  # type: ignore

    # --------------------------------
    #   Production Postgres Config (Another)
    # --------------------------------
    POSTGRES_CONNECT_ANOTHER: str = config("POSTGRES_CONNECT_ANOTHER", cast=str)  # type: ignore
    POSTGRES_HOST_ANOTHER: str = config("POSTGRES_HOST_ANOTHER", cast=str)  # type: ignore
    POSTGRES_PORT_ANOTHER: int = config("POSTGRES_PORT_ANOTHER", cast=int)  # type: ignore
    POSTGRES_DB_ANOTHER: str = config("POSTGRES_DB_ANOTHER", cast=str)  # type: ignore
    POSTGRES_USERNAME_ANOTHER: str = config("POSTGRES_USERNAME_ANOTHER", cast=str)  # type: ignore
    POSTGRES_PASSWORD_ANOTHER: str = config("POSTGRES_PASSWORD_ANOTHER", cast=str)  # type: ignore
    # POSTGRES_SCHEMA_ANOTHER: str = config("POSTGRES_SCHEMA_ANOTHER", cast=str)  # type: ignore

    
    DB_MAX_POOL_CON: int = config("DB_MAX_POOL_CON", cast=int)  # type: ignore
    DB_POOL_SIZE: int = config("DB_POOL_SIZE", cast=int)  # type: ignore
    DB_POOL_OVERFLOW: int = config("DB_POOL_OVERFLOW", cast=int)  # type: ignore
    DB_TIMEOUT: int = config("DB_TIMEOUT", cast=int)  # type: ignore
    DB_POOL_RECYCLE: int = config("DB_POOL_RECYCLE", cast=int)  # type: ignore
    DB_POOL_TIMEOUT: int = config("DB_POOL_TIMEOUT", cast=int)  # type: ignore
    DB_POOL_RESET_ON_RETURN: str = config("DB_POOL_RESET_ON_RETURN", cast=str)  # type: ignore
    DB_RETRY_ATTEMPTS: int = config("DB_RETRY_ATTEMPTS", cast=int)  # type: ignore
    DB_RETRY_DELAY: float = config("DB_RETRY_DELAY", cast=float)  # type: ignore
    DB_RETRY_BACKOFF: float = config("DB_RETRY_BACKOFF", cast=float)  # type: ignore

    IS_DB_ECHO_LOG: bool = config("IS_DB_ECHO_LOG", cast=bool)  # type: ignore
    IS_DB_FORCE_ROLLBACK: bool = config("IS_DB_FORCE_ROLLBACK", cast=bool)  # type: ignore
    IS_DB_EXPIRE_ON_COMMIT: bool = config("IS_DB_EXPIRE_ON_COMMIT", cast=bool)  # type: ignore


    # 修改REDIS_PORT的处理方式
    def parse_redis_port(value):
        if value and "://" in value:
            # 如果是完整的连接字符串，提取端口部分
            return int(value.split(":")[-1])
        return int(value)
        
    # redis
    PROD_REDIS_HOST: str = config("PROD_REDIS_HOST", cast=str)  # type: ignore
    PROD_REDIS_PORT: int = config("PROD_REDIS_PORT", cast=parse_redis_port)  # type: ignore
    PROD_REDIS_PASSWORD: str = config("PROD_REDIS_PASSWORD", cast=str)  # type: ignore
    PROD_REDIS_DB: int = config("PROD_REDIS_DB", cast=int)  # type: ignore
    PROD_REDIS_CLUSTER: bool = config("PROD_REDIS_CLUSTER", cast=bool, default=False)  # type: ignore
    PROD_REDIS_NODES: str = config("PROD_REDIS_NODES", cast=str, default="")  # type: ignore

    TEST_REDIS_HOST: str = config("TEST_REDIS_HOST", cast=str)  # type: ignore
    TEST_REDIS_PORT: int = config("TEST_REDIS_PORT", cast=parse_redis_port)  # type: ignore
    TEST_REDIS_PASSWORD: str = config("TEST_REDIS_PASSWORD", cast=str)  # type: ignore
    TEST_REDIS_DB: int = config("TEST_REDIS_DB", cast=int)  # type: ignore
    TEST_REDIS_CLUSTER: bool = config("TEST_REDIS_CLUSTER", cast=bool, default=False)  # type: ignore

    # LLM 配置 (兼容 OpenAI 格式的 API)
    LLM_API_KEY: str = config("LLM_API_KEY", default="sk-...", cast=str)
    LLM_BASE_URL: str = config("LLM_BASE_URL", default="https://api.openai.com/v1", cast=str)
    LLM_MODEL_NAME: str = config("LLM_MODEL_NAME", default="gpt-4o", cast=str)

    ALLOWED_ORIGINS: List[str] = ["*"]
    ALLOWED_METHODS: List[str] = ["*"]
    ALLOWED_HEADERS: List[str] = ["*"]

    LOGGING_LEVEL: int = logging.INFO
    LOGGERS: Tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")


    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        validate_assignment=True,
        case_sensitive=True,
    )


    @property
    def gset_backend_app_attributes(self) -> Dict[str, Any]:
        """
        algo backend template application necessary variable.
        """
        return {
            "title": self.TITLE,
            "version": self.VERSION,
            "debug": self.DEBUG,
            "description": self.DESCRIPTION,
            "docs_url": self.DOCS_URL,
            "openapi_url": self.OPENAPI_URL,
            "redoc_url": self.REDOC_URL,
            "openapi_prefix": self.OPENAPI_PREFIX,
            "api_prefix": self.API_PREFIX,
        }
