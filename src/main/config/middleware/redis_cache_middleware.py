import datetime
import json
import hashlib
from typing import Callable, Dict, List, Optional, Set, Union, Any
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from loguru import logger
from src.main.core.util.redis_client import RedisClient
from src.main.config.manager import settings


class RedisCacheMiddleware(BaseHTTPMiddleware):
    """
    Redis缓存中间件，用于自动缓存API响应
    """
    
    def __init__(
        self, 
        app: ASGIApp,
        cache_prefix: str = "api_cache:",
        cache_time: int = 1800,  # 默认缓存30分钟
        exclude_paths: Optional[List[str]] = None,
        exclude_methods: Optional[List[str]] = None,
        include_paths: Optional[List[str]] = None
    ):
        super().__init__(app)
        self.cache_prefix = cache_prefix
        self.cache_time = cache_time
        self.exclude_paths = exclude_paths or []
        self.include_paths = include_paths or []
        # 默认只排除修改性质的HTTP方法，保留GET和POST
        self.exclude_methods = exclude_methods or ["PUT", "DELETE", "PATCH"]
        
        # 初始化Redis客户端
        self.redis_available = False
        try:
            self.redis_client = RedisClient()
            logger.info(f"🚀 Redis缓存中间件初始化成功，缓存HTTP方法: {[m for m in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'] if m not in self.exclude_methods]}")
            
            # 测试Redis连接
            test_key = f"{self.cache_prefix}test_connection"
            test_value = "connection_ok"
            if self.redis_client.set(test_key, test_value, ex=60):
                read_value = self.redis_client.get(test_key)
                if read_value == test_value:
                    logger.info(f"✅ Redis缓存读写测试成功")
                    self.redis_available = True
                else:
                    logger.warning(f"⚠️ Redis缓存读写测试失败，读取值不匹配: {read_value}")
            else:
                logger.warning(f"⚠️ Redis缓存写入测试失败")
                
        except Exception as e:
            logger.error(f"❌ Redis缓存中间件初始化失败: {str(e)}")
            logger.warning(f"⚠️ Redis不可用，缓存功能将被禁用，系统将正常运行")
            self.redis_client = None
            self.redis_available = False
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求和响应，实现缓存逻辑"""
        
        # 排除 OPTIONS 请求，不进行任何处理
        if request.method == "OPTIONS":
            return await call_next(request)

        # 打印请求信息以便调试
        logger.warning(f"🔍 处理请求: {request.method} {request.url.path}")
        
        # 如果指定了include_paths，则只缓存指定的路径 【优先级更高 include_paths】
        if self.include_paths and not any(request.url.path.startswith(p) for p in self.include_paths):
            logger.warning(f"⏭️ 跳过缓存，路径不在include_paths中: {request.method} {request.url.path}")
            return await call_next(request)
        
        # 检查是否应该跳过缓存 【优先级低 exclude_paths】
        if request.method in self.exclude_methods or any(request.url.path.startswith(p) for p in self.exclude_paths):
            logger.warning(f"⏭️ 跳过缓存: {request.method} {request.url.path}")
            return await call_next(request)
        
        # 检查请求头是否禁用缓存
        if request.headers.get("X-No-Cache", "").lower() == "true":
            logger.warning(f"⏭️ 跳过缓存，请求头指定 X-No-Cache=true")
            return await call_next(request)
        
        # 生成缓存键
        key_src = f"{request.url.path}|{request.method}|{str(request.query_params)}"
        
        # 对于POST请求，考虑请求体
        if (request.method == "POST" and 
            request.headers.get("Content-Type", "").startswith("application/json")):
            try:
                body_bytes = await request.body()
                try:
                    body = json.loads(body_bytes)
                    body_str = json.dumps(body, sort_keys=True)
                    key_src += f"|{body_str}"
                except json.JSONDecodeError:
                    body_str = hashlib.md5(body_bytes).hexdigest()
                    key_src += f"|{body_str}"
                
                logger.warning(f"📄 包含POST请求体在缓存键中: {request.url.path}")
            except Exception as e:
                logger.warning(f"⚠️ 无法读取POST请求体: {str(e)}")
        
        cache_key = self.cache_prefix + hashlib.md5(key_src.encode()).hexdigest()
        logger.warning(f"🔑 生成缓存键: {cache_key}, 原始key: {key_src}")
        
        # 尝试从缓存获取响应
        if self.redis_available and self.redis_client:
            try:
                cached_response = self.redis_client.get(cache_key)
                if cached_response:
                    logger.info(f"🎯 命中缓存: {request.method} {request.url.path}")
                    return JSONResponse(content=json.loads(cached_response))
            except Exception as e:
                logger.warning(f"⚠️ Redis读取失败，跳过缓存: {str(e)}")
        elif not self.redis_available:
            logger.warning(f"⏭️ Redis不可用，跳过缓存读取: {request.method} {request.url.path}")
        
        # 缓存未命中，执行原始请求
        logger.info(f"💾 缓存未命中，执行请求: {request.method} {request.url.path}")
        response = await call_next(request)
        
        # 详细记录响应信息
        response_type = type(response).__name__
        content_type = response.headers.get("Content-Type", "").lower()
        logger.warning(f"📊 响应信息: 类型={response_type}, 状态码={response.status_code}, 内容类型={content_type}")
        
        # 只缓存成功的JSON响应
        if response.status_code == 200 and content_type.startswith("application/json"):
            # 读取完整body
            body_bytes = None
            
            # 普通Response有body属性
            if hasattr(response, "body"):
                try:
                    body_bytes = response.body  # bytes
                except Exception as e:
                    logger.warning(f"⚠️ 无法读取response.body: {str(e)}")
                    body_bytes = None
            
            # 如果是StreamingResponse或body为空，用body_iterator
            if body_bytes is None and hasattr(response, "body_iterator"):
                try:
                    chunks = []
                    async for chunk in response.body_iterator:
                        chunks.append(chunk)
                    body_bytes = b"".join(chunks)
                    logger.warning("📦 从body_iterator读取了流式响应内容")
                except Exception as e:
                    logger.warning(f"⚠️ 无法读取response.body_iterator: {str(e)}")
                    body_bytes = None
            
            # 如果成功获取到内容
            if body_bytes:
                text = body_bytes.decode("utf-8", errors="ignore")
                try:
                    # 验证合法JSON
                    json.loads(text)
                    # 写入Redis
                    if self.redis_available and self.redis_client:
                        try:
                            result = self.redis_client.set(cache_key, text, ex=self.cache_time)
                            if result:
                                logger.info(f"✅ 已缓存响应，键: {cache_key}, 过期时间: {self.cache_time}秒，到{datetime.datetime.now() + datetime.timedelta(seconds=self.cache_time)}失效")
                            else:
                                logger.warning(f"⚠️ 响应缓存失败, Redis返回: {result}")
                        except Exception as e:
                            logger.warning(f"⚠️ Redis写入失败，跳过缓存: {str(e)}")
                    else:
                        logger.warning(f"⏭️ Redis不可用，跳过缓存写入: {request.method} {request.url.path}")
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ 响应不是有效的JSON，跳过缓存: {str(e)}")
                
                # 重建一个新的Response给客户端
                return Response(
                    content=body_bytes,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.headers.get("content-type")
                )
        else:
            logger.warning(f"⏭️ 不缓存响应: 状态码={response.status_code}, 内容类型={content_type}")
        
        return response


def add_redis_cache_middleware(
    app: FastAPI, 
    cache_time: int = 1800,
    exclude_paths: List[str] = None,
    exclude_methods: List[str] = None,
    include_paths: List[str] = None
) -> None:
    """
    添加Redis缓存中间件到FastAPI应用
    
    参数:
        app: FastAPI应用实例
        cache_time: 缓存时间(秒)，默认30分钟
        exclude_paths: 排除的路径列表，这些路径不会被缓存
        exclude_methods: 排除的HTTP方法列表，这些方法不会被缓存
        include_paths: 包含的路径列表，只有这些路径会被缓存（优先级高于exclude_paths）
    """
    # 默认基本排除路径，这些路径不需要添加API前缀
    no_prefix_paths = ["/docs", "/redoc", "/openapi.json", "/health", "/hidolphin-api.json", 
                  "/hidolphin-api-doc.html", "/hidolphin-api-redoc.html", "/login", 
                  "/download-openapi-json", "/download-openapi-endpoint-json"]
    
    # 需要添加API前缀的路径（API路径）
    api_paths = ["/v1/redis/clear_api_cache", "/v1/redis/delete_pattern"]
    
    # 如果传入了自定义排除路径，则使用它，否则使用默认路径
    exclude_paths = exclude_paths or no_prefix_paths
    
    # 默认只排除修改性质的HTTP方法
    exclude_methods = exclude_methods or ["PUT", "DELETE", "PATCH"]
    
    final_exclude_paths = []
    final_include_paths = []
    
    # 考虑API_PREFIX
    if hasattr(settings, 'API_PREFIX') and settings.API_PREFIX:
        api_prefix = settings.API_PREFIX.rstrip("/")
        
        # 添加不需要前缀的路径
        final_exclude_paths.extend(no_prefix_paths)
        
        # 添加需要前缀的API路径
        for path in api_paths:
            # 确保路径以/开头但不包含api_prefix
            if path.startswith("/"):
                path = path[1:]
            final_exclude_paths.append(f"{api_prefix}/{path}")
        
        # 处理传入的排除路径
        for path in exclude_paths:
            # 如果已经在final_exclude_paths中，跳过
            if path in final_exclude_paths:
                continue
                
            # 判断路径是否需要添加前缀
            if path in no_prefix_paths:
                # 不添加前缀
                if path not in final_exclude_paths:
                    final_exclude_paths.append(path)
            else:
                # 添加前缀（如果还没有）
                if not path.startswith(api_prefix):
                    if path.startswith("/"):
                        prefixed_path = f"{api_prefix}{path}"
                    else:
                        prefixed_path = f"{api_prefix}/{path}"
                    if prefixed_path not in final_exclude_paths:
                        final_exclude_paths.append(prefixed_path)
                else:
                    if path not in final_exclude_paths:
                        final_exclude_paths.append(path)
        
        # 处理传入的包含路径
        if include_paths:
            for path in include_paths:
                # 判断路径是否需要添加前缀
                if path in no_prefix_paths:
                    # 不添加前缀
                    if path not in final_include_paths:
                        final_include_paths.append(path)
                else:
                    # 添加前缀（如果还没有）
                    if not path.startswith(api_prefix):
                        if path.startswith("/"):
                            prefixed_path = f"{api_prefix}{path}"
                        else:
                            prefixed_path = f"{api_prefix}/{path}"
                        if prefixed_path not in final_include_paths:
                            final_include_paths.append(prefixed_path)
                    else:
                        if path not in final_include_paths:
                            final_include_paths.append(path)
    else:
        # 如果没有API前缀，直接使用所有路径
        final_exclude_paths = list(set(exclude_paths + no_prefix_paths))
        for path in api_paths:
            if path.startswith("/"):
                final_exclude_paths.append(path)
            else:
                final_exclude_paths.append(f"/{path}")
        
        # 处理包含路径
        if include_paths:
            final_include_paths = include_paths.copy()
        
    logger.info(f"📋 缓存排除路径: {final_exclude_paths}")
    logger.info(f"📋 缓存排除方法: {exclude_methods}")
    if final_include_paths:
        logger.info(f"📋 缓存包含路径: {final_include_paths}")
    
    app.add_middleware(
        RedisCacheMiddleware,
        cache_time=cache_time,
        exclude_paths=final_exclude_paths,
        exclude_methods=exclude_methods,
        include_paths=final_include_paths
    )
    logger.info(f"📦 Redis缓存中间件已添加到应用，缓存时间: {cache_time}秒")