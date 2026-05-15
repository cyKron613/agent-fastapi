"""
示例: 自定义 Agent 实现

本文件展示如何基于 BaseAgentService 创建自定义 Agent。
开发者可以参考此文件，创建自己的 Agent 实现。

使用方式:
1. 继承 BaseAgentService 或 DefaultAgentService
2. 实现/覆盖 process_chat() 方法
3. 在 agent_router.py 中将 DefaultAgentService 替换为你的实现
"""

import json
from typing import AsyncGenerator, List, Dict, Optional

import httpx
from loguru import logger

from src.main.config.manager import settings
from src.main.repository.chat_repository import ChatRepository
from src.main.schema.chat import ChatRequest
from src.main.schema.agent import AgentInfoResponse, AgentModelInfo, AgentCapability
from src.main.service.agent.default_agent_service import DefaultAgentService


class ExampleCustomAgent(DefaultAgentService):
    """
    示例自定义 Agent

    演示如何：
    - 自定义 Agent 信息
    - 注入自定义系统提示词
    - 在对话前后添加自定义逻辑
    - 覆盖核心对话处理流程
    """

    def get_agent_info(self) -> AgentInfoResponse:
        return AgentInfoResponse(
            name="My Custom Agent",
            description="一个示例自定义 Agent，演示框架扩展方式",
            version="1.0.0",
            author="Your Name",
            capabilities=[
                AgentCapability(name="chat", description="多轮对话", enabled=True),
                AgentCapability(name="streaming", description="流式输出", enabled=True),
                AgentCapability(name="rag", description="RAG 检索增强", enabled=True),
                AgentCapability(name="function_calling", description="函数调用", enabled=False),
            ],
            models=self.get_available_models(),
            default_model=self.llm_model,
            metadata={"custom_field": "custom_value"},
        )

    def get_system_prompt(self, request: Optional[ChatRequest] = None) -> Optional[str]:
        """
        自定义系统提示词

        可以根据 request 中的参数动态生成不同的系统提示词。
        例如，根据 metadata 中的场景选择不同的 prompt 模板。
        """
        return (
            "你是一个专业的 AI 助手。请用简洁、准确的语言回答用户问题。\n"
            "如果不确定答案，请明确告知用户。"
        )

    async def on_before_chat(self, request: ChatRequest, session_id: str) -> ChatRequest:
        """
        对话前钩子示例

        可用于：
        - 请求参数校验和修正
        - 审计日志记录
        - 用量检查和限流
        - RAG 检索预处理
        """
        logger.info(f"[ExampleAgent] Before chat - session: {session_id}")
        # 示例: 强制设置温度
        # request.temperature = 0.5
        return request

    async def on_after_chat(self, session_id: str, assistant_content: str, request: ChatRequest) -> None:
        """
        对话后钩子示例

        可用于：
        - Token 用量统计
        - 对话质量评估
        - 触发异步任务(如知识库更新)
        - 告警监控
        """
        logger.info(
            f"[ExampleAgent] After chat - session: {session_id}, "
            f"response length: {len(assistant_content)} chars"
        )

    # 如果需要完全自定义对话流程，覆盖 process_chat:
    #
    # async def process_chat(
    #     self,
    #     messages: List[Dict[str, Any]],
    #     request: ChatRequest,
    #     session_id: str,
    # ) -> AsyncGenerator[str, None]:
    #     """
    #     完全自定义的对话处理逻辑
    #
    #     示例场景:
    #     1. RAG: 先检索相关文档，注入 context 到 prompt
    #     2. Multi-Agent: 根据意图路由到不同的子 Agent
    #     3. Tool Use: 解析 LLM 的 tool_call 并执行
    #     """
    #     # 1. RAG 检索
    #     user_query = messages[-1]["content"]
    #     # relevant_docs = await self.rag_service.search(user_query)
    #     # context = "\n".join([doc.content for doc in relevant_docs])
    #
    #     # 2. 构造增强 prompt
    #     # enhanced_messages = [
    #     #     {"role": "system", "content": f"参考资料:\n{context}"},
    #     #     *messages
    #     # ]
    #
    #     # 3. 调用 LLM (可复用父类逻辑)
    #     async for chunk in super().process_chat(messages, request, session_id):
    #         yield chunk
