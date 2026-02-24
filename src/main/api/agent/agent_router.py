"""
Agent Router - Agent 框架核心 API 路由

提供完整的 Agent 对话和会话管理 API：
- POST /chat/completions          对话接口 (流式/非流式)
- GET  /sessions                  获取会话列表
- POST /sessions                  创建新会话
- GET  /sessions/{session_id}     获取会话详情
- PUT  /sessions/{session_id}     更新会话
- DELETE /sessions/{session_id}   删除会话
- PATCH /sessions/{session_id}/rename  重命名会话
- POST /sessions/{session_id}/stop     停止响应
- DELETE /sessions/{session_id}/messages/{message_id}  删除消息
- GET  /agent/info                获取 Agent 信息
- GET  /agent/models              获取可用模型列表
- GET  /health                    健康检查

所有接口均为通用框架接口，不包含具体业务逻辑。
"""

import time
from typing import List, Optional

from fastapi import APIRouter, Depends, Body, Query, status, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse

from src.main.schema.chat import (
    ChatRequest,
    ChatSessionResponse,
    ChatSessionListResponse,
    ChatHistoryDetailResponse,
    ChatMessageResponse,
    ChatCompletionResponse,
    SessionCreateRequest,
    SessionRenameRequest,
    SessionUpdateRequest,
    MessageFeedbackRequest,
)
from src.main.schema.agent import (
    AgentInfoResponse,
    AgentModelsResponse,
    HealthCheckResponse,
)
from src.main.repository.chat_repository import ChatRepository
from src.main.service.agent.default_agent_service import DefaultAgentService
from src.main.service.agent.base_agent_service import BaseAgentService
from src.main.core.orm.depend.base import get_async_repository, get_async_service
from src.main.core.schema.base import ResponseVo

# ============================================================
# 路由定义
# ============================================================

router = APIRouter(prefix="/agent/v1", tags=["Agent"])

# 应用启动时间 (用于 health check)
_start_time = time.time()


# ============================================================
# 对话接口
# ============================================================

@router.post(
    path="/chat/completions",
    summary="对话接口 (支持流式/非流式)",
    description="兼容 OpenAI Chat Completions API 格式。stream=true 时返回 SSE 流式响应。",
    status_code=status.HTTP_200_OK,
)
async def chat_completions(
    request: ChatRequest = Body(
        ...,
        examples=[
            {
                "summary": "基础对话",
                "value": {
                    "messages": [{"role": "user", "content": "你好"}],
                    "stream": True,
                },
            },
            {
                "summary": "带会话ID的多轮对话",
                "value": {
                    "messages": [{"role": "user", "content": "继续上面的话题"}],
                    "session_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                    "user_id": "user_001",
                    "stream": True,
                },
            },
        ],
    ),
    agent_service: DefaultAgentService = Depends(
        get_async_service(ser_type=DefaultAgentService, repo_type=ChatRepository)
    ),
):
    """
    核心对话接口

    - `stream=true`:  返回 SSE 流式响应 (text/event-stream)
    - `stream=false`: 返回一次性 JSON 响应 (兼容 OpenAI 格式)
    - 不传 `session_id` 时自动创建新会话
    - 首条用户消息自动生成会话标题
    """
    if request.stream:
        return StreamingResponse(
            agent_service.stream_chat(request),
            media_type="text/event-stream",
        )
    else:
        result = await agent_service.non_stream_chat(request)
        return result


# ============================================================
# 会话管理接口
# ============================================================

@router.get(
    path="/sessions",
    response_model=ChatSessionListResponse,
    summary="获取会话列表",
)
async def get_sessions(
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    user_id: Optional[str] = Query(None, description="按用户ID筛选"),
    chat_repo: ChatRepository = Depends(get_async_repository(ChatRepository)),
):
    """获取对话会话列表，支持分页和按用户筛选。"""
    sessions = await chat_repo.get_all_sessions(limit=limit, offset=offset, user_id=user_id)
    total = await chat_repo.count_sessions(user_id=user_id)
    return ChatSessionListResponse(total=total, items=sessions)


@router.post(
    path="/sessions",
    response_model=ChatSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建新会话",
)
async def create_session(
    request: SessionCreateRequest = Body(...),
    chat_repo: ChatRepository = Depends(get_async_repository(ChatRepository)),
):
    """手动创建一个新的空会话。"""
    session = await chat_repo.create_session(
        user_id=request.user_id,
        title=request.title,
        model=request.model,
        system_prompt=request.system_prompt,
        metadata=request.metadata,
    )
    await chat_repo.async_session.commit()
    await chat_repo.async_session.refresh(session)
    return session


@router.get(
    path="/sessions/{session_id}",
    response_model=ChatHistoryDetailResponse,
    summary="获取会话详情及消息记录",
)
async def get_session_detail(
    session_id: str,
    chat_repo: ChatRepository = Depends(get_async_repository(ChatRepository)),
):
    """根据会话 ID 获取会话详情和所有历史消息。"""
    session = await chat_repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = await chat_repo.get_messages(session_id)
    total = await chat_repo.count_messages(session_id)

    return ChatHistoryDetailResponse(
        session=session,
        messages=messages,
        total_messages=total,
    )


@router.put(
    path="/sessions/{session_id}",
    response_model=ChatSessionResponse,
    summary="更新会话信息",
)
async def update_session(
    session_id: str,
    request: SessionUpdateRequest = Body(...),
    chat_repo: ChatRepository = Depends(get_async_repository(ChatRepository)),
):
    """更新会话标题、系统提示词或元数据。"""
    update_kwargs = {}
    if request.title is not None:
        update_kwargs["title"] = request.title
    if request.system_prompt is not None:
        update_kwargs["system_prompt"] = request.system_prompt
    if request.metadata is not None:
        update_kwargs["metadata_"] = request.metadata

    session = await chat_repo.update_session(session_id, **update_kwargs)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await chat_repo.async_session.commit()
    await chat_repo.async_session.refresh(session)
    return session


@router.delete(
    path="/sessions/{session_id}",
    summary="删除会话",
    status_code=status.HTTP_200_OK,
)
async def delete_session(
    session_id: str,
    hard: bool = Query(False, description="是否硬删除(不可恢复)"),
    chat_repo: ChatRepository = Depends(get_async_repository(ChatRepository)),
):
    """
    删除指定会话。

    - `hard=false` (默认): 软删除，可恢复
    - `hard=true`: 硬删除，同步级联删除所有消息
    """
    if hard:
        success = await chat_repo.hard_delete_session(session_id)
    else:
        success = await chat_repo.soft_delete_session(session_id)

    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    await chat_repo.async_session.commit()
    return ResponseVo(code=200, success=True, data="Session deleted")


@router.patch(
    path="/sessions/{session_id}/rename",
    response_model=ChatSessionResponse,
    summary="重命名会话",
)
async def rename_session(
    session_id: str,
    request: SessionRenameRequest = Body(...),
    chat_repo: ChatRepository = Depends(get_async_repository(ChatRepository)),
):
    """重命名指定会话。"""
    session = await chat_repo.rename_session(session_id, request.title)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await chat_repo.async_session.commit()
    await chat_repo.async_session.refresh(session)
    return session


# ============================================================
# 停止响应
# ============================================================

@router.post(
    path="/sessions/{session_id}/stop",
    summary="停止响应",
    status_code=status.HTTP_200_OK,
)
async def stop_generation(
    session_id: str,
    agent_service: DefaultAgentService = Depends(
        get_async_service(ser_type=DefaultAgentService, repo_type=ChatRepository)
    ),
):
    """停止指定会话正在进行的流式响应。"""
    stopped = agent_service.stop_stream(session_id)
    if not stopped:
        raise HTTPException(status_code=404, detail="No active stream found for this session")
    return ResponseVo(code=200, success=True, data="Stream stopped")


# ============================================================
# 消息管理
# ============================================================

@router.delete(
    path="/sessions/{session_id}/messages/{message_id}",
    summary="删除消息",
    status_code=status.HTTP_200_OK,
)
async def delete_message(
    session_id: str,
    message_id: str,
    chat_repo: ChatRepository = Depends(get_async_repository(ChatRepository)),
):
    """删除指定消息 (软删除)。"""
    # 校验会话存在
    session = await chat_repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    success = await chat_repo.soft_delete_message(message_id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")

    await chat_repo.async_session.commit()
    return ResponseVo(code=200, success=True, data="Message deleted")


# ============================================================
# Agent 信息
# ============================================================

@router.get(
    path="/agent/info",
    response_model=AgentInfoResponse,
    summary="获取 Agent 基本信息",
)
async def get_agent_info(
    agent_service: DefaultAgentService = Depends(
        get_async_service(ser_type=DefaultAgentService, repo_type=ChatRepository)
    ),
):
    """获取当前 Agent 的基本信息、能力列表和支持的模型。"""
    return agent_service.get_agent_info()


@router.get(
    path="/agent/models",
    response_model=AgentModelsResponse,
    summary="获取可用模型列表",
)
async def get_models(
    agent_service: DefaultAgentService = Depends(
        get_async_service(ser_type=DefaultAgentService, repo_type=ChatRepository)
    ),
):
    """获取当前 Agent 支持的模型列表。"""
    models = agent_service.get_available_models()
    return AgentModelsResponse(data=models)


# ============================================================
# 健康检查
# ============================================================

@router.get(
    path="/health",
    response_model=HealthCheckResponse,
    summary="健康检查",
    tags=["System"],
)
async def health_check():
    """服务健康检查，返回运行状态和启动时长。"""
    from src.main.config.manager import settings

    return HealthCheckResponse(
        status="ok",
        version=settings.VERSION,
        uptime=round(time.time() - _start_time, 2),
    )
