import time
from loguru import logger
from fastapi import FastAPI
from starlette.requests import Request


def register_middleware(app: FastAPI):
    """
    请求响应拦截
    :param app: 应用
    :return:
    """

    @app.middleware("http")
    async def logger_request(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(round(process_time, 5))
        logger.info(f">>>访问记录:{request.method} url:{request.url}  耗时:{str(round(process_time, 5))}")
        return response
