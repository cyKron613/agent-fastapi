"""
API 路由注册入口

所有 API 路由在此统一注册。
开发者新增路由模块后，在此处 include_router 即可。
"""

import fastapi

from src.main.api.agent.agent_router import router as agent_router
# from src.main.api.redis_cache.redis_router import router as redis_router

router = fastapi.APIRouter()

# Agent 核心路由 (对话、会话管理、Agent信息)
router.include_router(router=agent_router)

# Redis 缓存管理路由 (按需启用)
# router.include_router(router=redis_router)


