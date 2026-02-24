"""
DefaultAgentService - 默认 Agent 实现

提供一个最小可用的 Agent 实现，直接代理 LLM 请求。
开发者可以：
1. 直接使用此实现进行简单对话
2. 继承并覆盖 process_chat() 等方法实现自定义逻辑
"""

import json
from typing import AsyncGenerator, List, Dict, Any, Optional

import httpx
from loguru import logger

from src.main.config.manager import settings
from src.main.repository.chat_repository import ChatRepository
from src.main.schema.chat import ChatRequest
from src.main.schema.agent import AgentInfoResponse, AgentModelInfo, AgentCapability
from src.main.service.agent.base_agent_service import BaseAgentService


class DefaultAgentService(BaseAgentService):
    """
    默认 Agent 服务实现

    直接代理 OpenAI 兼容的 LLM API，不包含任何业务逻辑。
    开发者可继承此类并覆盖相应方法来添加：
    - 自定义系统提示词
    - RAG 检索增强
    - Function Calling / Tool Use
    - 业务数据注入
    - 自定义前后处理逻辑
    """

    def __init__(self, repo: ChatRepository):
        super().__init__(repo=repo)
        self.llm_url = settings.LLM_BASE_URL
        self.llm_key = settings.LLM_API_KEY
        self.llm_model = settings.LLM_MODEL_NAME

    def get_agent_info(self) -> AgentInfoResponse:
        """返回 Agent 基本信息"""
        return AgentInfoResponse(
            name="Default Agent",
            description="基于 Agent-FastAPI 框架的默认 Agent 实现，直接代理 LLM 对话",
            version=settings.VERSION,
            author="Agent-FastAPI",
            capabilities=[
                AgentCapability(name="chat", description="多轮对话", enabled=True),
                AgentCapability(name="streaming", description="流式输出", enabled=True),
                AgentCapability(name="session_management", description="会话管理", enabled=True),
            ],
            models=self.get_available_models(),
            default_model=self.llm_model,
        )

    def get_available_models(self) -> List[AgentModelInfo]:
        """返回可用模型列表"""
        return [
            AgentModelInfo(
                id=self.llm_model,
                name=self.llm_model,
                description=f"Default LLM model: {self.llm_model}",
                is_default=True,
            )
        ]

    def get_system_prompt(self, request: Optional[ChatRequest] = None) -> Optional[str]:
        """
        获取系统提示词

        开发者可覆盖此方法返回自定义系统提示词。
        返回 None 表示不注入系统提示词。
        """
        return None

    async def process_chat(
        self,
        messages: List[Dict[str, str]],
        request: ChatRequest,
        session_id: str,
    ) -> AsyncGenerator[str, None]:
        """
        核心对话处理：直接代理 LLM 流式请求

        开发者可覆盖此方法实现：
        - 自定义 prompt 工程
        - RAG 增强
        - Tool/Function Calling
        - 多模型路由
        - 业务数据注入
        """
        model = request.model or self.llm_model
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "temperature": request.temperature or 0.7,
            "top_p": request.top_p or 1.0,
        }

        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens
        if request.stop:
            payload["stop"] = request.stop
        if request.tools:
            payload["tools"] = request.tools
        if request.tool_choice:
            payload["tool_choice"] = request.tool_choice

        logger.info(f"[DefaultAgent] Calling LLM: {self.llm_url} model={model} session={session_id}")

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.llm_url}/chat/completions",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.llm_key}"},
                ) as response:
                    if response.status_code != 200:
                        error_body = await response.aread()
                        logger.error(f"LLM API Error {response.status_code}: {error_body}")
                        yield f"data: {json.dumps({'error': f'LLM API Error {response.status_code}'})}\n\n"
                        return

                    async for line in response.aiter_lines():
                        if self.is_stream_cancelled(session_id):
                            break
                        if line.strip():
                            yield f"{line}\n\n"

            except httpx.TimeoutException:
                logger.error(f"LLM request timeout for session {session_id}")
                yield f"data: {json.dumps({'error': 'LLM request timeout'})}\n\n"
            except Exception as e:
                logger.error(f"LLM request error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
