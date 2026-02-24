"""
Agent-FastAPI 应用入口

通用 Agent 开发框架，基于 FastAPI 构建。
"""

import fastapi
import fastapi_cdn_host
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse, HTMLResponse
from fastapi import Request

from src.main.api.endpoints import router as api_endpoint_router
from src.main.config.handler.life_circle_handler import (
    execute_backend_server_event_handler, terminate_backend_server_event_handler,
    execute_another_db_connection_event_handler, terminate_another_db_connection_event_handler
)
from src.main.config.manager import settings
from src.main.config.handler.global_exception_handler import register_exception
from src.main.config.handler.api_access_handler import register_middleware


def initialize_backend_application() -> fastapi.FastAPI:
    """初始化 Agent 后端应用"""

    app = fastapi.FastAPI(**settings.gset_backend_app_attributes)  # type: ignore

    # 注册异常处理器和中间件
    register_exception(app)
    register_middleware(app)

    # Redis 缓存中间件 (按需启用)
    # from src.main.config.middleware.redis_cache_middleware import add_redis_cache_middleware
    # add_redis_cache_middleware(
    #     app=app,
    #     cache_time=1800,
    #     include_paths=["/api/v1/some-cacheable-path"],
    #     exclude_methods=["PUT", "DELETE", "PATCH"],
    # )

    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
    )

    # 数据库生命周期事件
    app.add_event_handler("startup", execute_backend_server_event_handler(backend_app=app))
    app.add_event_handler("shutdown", terminate_backend_server_event_handler(backend_app=app))

    # # 如果有其他数据库连接，按需启用
    # app.add_event_handler("startup", execute_another_db_connection_event_handler(backend_app=app))
    # app.add_event_handler("shutdown", terminate_another_db_connection_event_handler(backend_app=app))

    # 注册 API 路由
    app.include_router(router=api_endpoint_router, prefix=settings.API_PREFIX)

    # ---- Docs 鉴权页面 (可选) ----
    import login_html
    LOGIN_HTML = login_html.LOGIN_HTML

    @app.get("/login", tags=["Auth FOR DOCS"])
    async def login_page():
        return HTMLResponse(content=LOGIN_HTML)

    @app.post("/login", tags=["Auth FOR DOCS"])
    async def login(request: Request):
        form_data = await request.form()
        username = form_data.get("username")
        password = form_data.get("password")
        USERNAME = settings.DOCS_AUTH_USERNAME
        PASSWORD = settings.DOCS_AUTH_PASSWORD

        if username == USERNAME and password == PASSWORD:
            response = RedirectResponse(url=settings.DOCS_URL, status_code=303)
            response.set_cookie(key="auth", value="approved", httponly=True)
            return response
        else:
            error_html = LOGIN_HTML.replace(
                '<form action="/login" method="post" id="loginForm">',
                '<div class="error-message">❌ 用户名或密码错误，请重试</div><form action="/login" method="post" id="loginForm">'
            )
            return HTMLResponse(content=error_html)

    @app.get("/", tags=["Auth FOR DOCS"])
    async def root():
        return RedirectResponse(url="/login")

    # Swagger UI 增强
    original_swagger_ui = app.routes[-1].endpoint

    async def custom_swagger_ui_html(*args, **kwargs):
        response = await original_swagger_ui(*args, **kwargs)
        if isinstance(response, HTMLResponse):
            html_content = response.body.decode('utf-8')
            return HTMLResponse(content=html_content)
        return response

    for route in app.routes:
        if route.path == settings.DOCS_URL:
            route.endpoint = custom_swagger_ui_html
            break

    fastapi_cdn_host.patch_docs(app)

    return app


backend_app: fastapi.FastAPI = initialize_backend_application()

if __name__ == "__main__":
    uvicorn.run(
        app="main:backend_app",
        host=settings.BACKEND_SERVER_HOST,
        port=settings.BACKEND_SERVER_PORT,
        reload=settings.DEBUG,
        workers=settings.BACKEND_SERVER_WORKERS,
        log_level=settings.LOGGING_LEVEL,
        lifespan="on",
    )
