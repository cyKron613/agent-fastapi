"""
BaseAgentService - Agent 服务基类

定义了 Agent 服务的核心接口。开发者需要继承此类并实现具体的业务逻辑。
框架提供了 DefaultAgentService 作为最小可用实现。
"""

import abc
import asyncio
import json
import uuid
from datetime import datetime
from typing import AsyncGenerator, Optional, Dict, Any, List, Set

from loguru import logger

from src.main.core.orm.service.base import BaseService
from src.main.repository.chat_repository import ChatRepository
from src.main.schema.chat import (
    ChatRequest,
    Message,
    ChatCompletionResponse,
    ChatCompletionChoice,
    ChatCompletionUsage,
)
from src.main.schema.agent import AgentInfoResponse, AgentModelInfo, AgentCapability


class BaseAgentService(BaseService[ChatRepository], abc.ABC):
    """
    Agent 服务抽象基类

    开发者通过继承此类实现自定义 Agent：
    1. 必须实现 `process_chat()` - 核心对话处理逻辑
    2. 可选覆盖 `get_agent_info()` - 返回 Agent 信息
    3. 可选覆盖 `get_system_prompt()` - 动态系统提示词
    4. 可选覆盖 `on_before_chat()` / `on_after_chat()` - 生命周期钩子
    """

    # ---- 活跃流追踪 (用于"停止响应") ----
    _active_streams: Dict[str, asyncio.Event] = {}

    def __init__(self, repo: ChatRepository):
        super().__init__(repo=repo)
        self.chat_repo = repo

    @staticmethod
    def _make_jsonable(value: Any) -> Any:
        """将 Pydantic 模型或嵌套结构转换成可 JSON 序列化的对象。"""
        if hasattr(value, "model_dump"):
            return value.model_dump(exclude_none=True)
        if isinstance(value, list):
            return [BaseAgentService._make_jsonable(item) for item in value]
        if isinstance(value, dict):
            return {key: BaseAgentService._make_jsonable(item) for key, item in value.items()}
        return value

    @classmethod
    def _stringify_message_content(cls, content: Any) -> str:
        """将消息内容转换成数据库可保存的字符串。"""
        if isinstance(content, str):
            return content
        return json.dumps(cls._make_jsonable(content), ensure_ascii=False)

    @classmethod
    def _restore_message_content(cls, content: str) -> Any:
        """尽量还原历史消息中的多模态 JSON 内容。"""
        try:
            parsed = json.loads(content)
            if isinstance(parsed, (list, dict)):
                return parsed
        except (TypeError, json.JSONDecodeError):
            pass
        return content

    @classmethod
    def _message_content_title(cls, content: Any) -> str:
        """从文本或多模态内容中提取可用于会话标题的文本。"""
        if isinstance(content, str):
            return content.strip()
        for item in cls._make_jsonable(content) or []:
            if isinstance(item, dict) and item.get("type") == "text" and item.get("text"):
                return str(item["text"]).strip()
        return cls._stringify_message_content(content)

    @classmethod
    def _extract_content_image_urls(cls, content: Any) -> List[str]:
        """从多模态消息内容中提取 image_url。"""
        image_urls: List[str] = []
        seen = set()
        for item in cls._make_jsonable(content) if isinstance(content, list) else []:
            if not isinstance(item, dict) or item.get("type") != "image_url":
                continue
            image_url = item.get("image_url") or {}
            url = image_url.get("url") if isinstance(image_url, dict) else None
            if url and url not in seen:
                image_urls.append(url)
                seen.add(url)
        return image_urls

    @classmethod
    def _collect_request_image_urls(cls, request: ChatRequest) -> List[str]:
        """汇总顶层 images 和 messages 内的图片 URL。"""
        image_urls: List[str] = []
        seen = set()
        for url in request.images or []:
            if url and url not in seen:
                image_urls.append(url)
                seen.add(url)
        for message in request.messages or []:
            for url in cls._extract_content_image_urls(message.content):
                if url and url not in seen:
                    image_urls.append(url)
                    seen.add(url)
        return image_urls

    @classmethod
    def _content_with_images(cls, content: Any, image_urls: List[str]) -> Any:
        """确保保存到历史中的用户消息包含关联图片，便于后续上下文和历史回显。"""
        if not image_urls:
            return content

        jsonable_content = cls._make_jsonable(content)
        if isinstance(jsonable_content, list):
            content_parts = list(jsonable_content)
        else:
            text = str(jsonable_content).strip() if jsonable_content is not None else ""
            content_parts = [{"type": "text", "text": text}] if text else []

        existing_images = set(cls._extract_content_image_urls(content_parts))
        for url in image_urls:
            if url and url not in existing_images:
                content_parts.append({"type": "image_url", "image_url": {"url": url}})
                existing_images.add(url)
        return content_parts

    @staticmethod
    def _message_metadata(request: ChatRequest, image_urls: List[str]) -> Optional[Dict[str, Any]]:
        """构造消息元数据，用于会话历史回显图片等信息。"""
        metadata: Dict[str, Any] = dict(request.metadata or {})
        if image_urls:
            metadata["images"] = image_urls
        if request.chat_type:
            metadata["chat_type"] = request.chat_type
        return metadata or None

    @classmethod
    def _build_synthetic_messages(cls, request: ChatRequest) -> List[Message]:
        """从 query/images 快捷字段构造一条用户消息。"""
        content_parts: List[Dict[str, Any]] = []
        if getattr(request, "query", None):
            content_parts.append({"type": "text", "text": request.query})
        for image_url in getattr(request, "images", None) or []:
            if image_url:
                content_parts.append({"type": "image_url", "image_url": {"url": image_url}})
        if not content_parts:
            return []
        return [Message(role="user", content=content_parts)]

    # ==============================================================
    # 抽象方法 - 开发者必须实现
    # ==============================================================

    @abc.abstractmethod
    async def process_chat(
        self,
        messages: List[Dict[str, Any]],
        request: ChatRequest,
        session_id: str,
    ) -> AsyncGenerator[str, None]:
        """
        核心对话处理逻辑 (流式)

        Args:
            messages: 完整的上下文消息列表 [{"role": "...", "content": "..."}]
            request: 原始请求对象
            session_id: 当前会话ID

        Yields:
            SSE 格式的字符串，如 "data: {...}\\n\\n"

        开发者应在此方法中：
        1. 构造 LLM prompt (可调用外部 API、RAG、工具等)
        2. 调用 LLM 并流式返回结果
        3. 可通过 `self.is_stream_cancelled(session_id)` 检查是否被取消
        """
        yield ""  # pragma: no cover

    # ==============================================================
    # 可选覆盖方法
    # ==============================================================

    def get_agent_info(self) -> AgentInfoResponse:
        """
        返回 Agent 基本信息。开发者可覆盖此方法。
        """
        return AgentInfoResponse(
            name="Agent",
            description="A base agent powered by hi-dolphin-ocr-service",
            version="1.0.0",
        )

    def get_system_prompt(self, request: Optional[ChatRequest] = None) -> Optional[str]:
        """
        获取系统提示词。开发者可覆盖此方法实现动态 prompt。
        返回 None 表示不添加系统提示词。
        """
        return None

    def get_available_models(self) -> List[AgentModelInfo]:
        """返回可用模型列表。开发者可覆盖。"""
        return []

    async def on_before_chat(self, request: ChatRequest, session_id: str) -> ChatRequest:
        """
        对话前钩子。可用于：请求预处理、参数校验、审计日志等。
        返回处理后的 request。
        """
        return request

    async def on_after_chat(self, session_id: str, assistant_content: str, request: ChatRequest) -> None:
        """
        对话后钩子。可用于：统计、评估、异步任务触发等。
        """
        pass

    # ==============================================================
    # 框架核心流程 (一般不需要覆盖)
    # ==============================================================

    async def stream_chat(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """
        完整的流式对话流程：
        1. 会话管理 (创建/恢复)
        2. 历史上下文构建
        3. 用户消息持久化
        4. 调用开发者实现的 process_chat()
        5. 助手回复持久化
        """
        session_id = request.session_id
        user_id = request.user_id.strip() if request.user_id else None
        request.user_id = user_id
        messages = request.messages or []
        if not messages:
            messages = self._build_synthetic_messages(request)
            if messages:
                request.messages = messages

        # --- 1. 会话管理 ---
        # 只有同时上传 session_id 和 user_id 时才恢复历史，避免跨用户串会话。
        if session_id and user_id:
            session = await self.chat_repo.get_session(session_id, user_id=user_id)
            if not session:
                # session_id 不存在，自动创建
                session = await self.chat_repo.create_session(
                    user_id=user_id,
                    model=request.model,
                )
                await self.chat_repo.async_session.commit()
                await self.chat_repo.async_session.refresh(session)
        else:
            session = await self.chat_repo.create_session(
                user_id=user_id,
                model=request.model,
            )
            await self.chat_repo.async_session.commit()
            await self.chat_repo.async_session.refresh(session)

        current_session_id = str(session.id)
        request.session_id = current_session_id

        # 注册活跃流
        cancel_event = asyncio.Event()
        self._active_streams[current_session_id] = cancel_event

        try:
            # --- 2. 构建上下文 ---
            db_messages = await self.chat_repo.get_messages(current_session_id)
            history_msgs = [
                {"role": msg.role, "content": self._restore_message_content(msg.content)}
                for msg in db_messages
            ]

            # --- 3. 保存用户消息 ---
            if messages:
                last_msg = messages[-1]
                image_urls = self._collect_request_image_urls(request) if last_msg.role == "user" else []
                persisted_content = self._content_with_images(last_msg.content, image_urls)
                message_metadata = self._message_metadata(request, image_urls) if last_msg.role == "user" else None
                await self.chat_repo.add_message(
                    current_session_id,
                    last_msg.role,
                    self._stringify_message_content(persisted_content),
                    user_id,
                    metadata=message_metadata,
                )

                # 自动生成标题
                if not session.title and last_msg.role == "user":
                    title_source = self._message_content_title(persisted_content)
                    title = title_source[:50] + ("..." if len(title_source) > 50 else "")
                    session.title = title
                    self.chat_repo.async_session.add(session)

                await self.chat_repo.async_session.commit()

                request_msgs = []
                context_messages = [last_msg] if history_msgs else messages
                for msg in context_messages:
                    content_for_context = persisted_content if msg is last_msg else msg.content
                    request_msgs.append({"role": msg.role, "content": self._make_jsonable(content_for_context)})
                full_context = history_msgs + request_msgs
            else:
                if not history_msgs:
                    yield f"data: {json.dumps({'error': 'No messages provided'})}\n\n"
                    return
                full_context = history_msgs

            # 添加系统提示词
            system_prompt = self.get_system_prompt(request)
            if system_prompt:
                full_context = [{"role": "system", "content": system_prompt}] + full_context

            # 发送 session_id
            yield f"data: {json.dumps({'type': 'session_info', 'session_id': current_session_id}, ensure_ascii=False)}\n\n"

            # --- 4. 前置钩子 ---
            request = await self.on_before_chat(request, current_session_id)

            # --- 5. 调用开发者的处理逻辑 ---
            full_assistant_content = ""
            async for chunk in self.process_chat(full_context, request, current_session_id):
                if cancel_event.is_set():
                    logger.info(f"Stream cancelled for session: {current_session_id}")
                    yield f"data: {json.dumps({'type': 'stream_cancelled'})}\n\n"
                    break

                yield chunk

                # 尝试提取文本用于持久化
                if chunk.startswith("data: "):
                    data_str = chunk[6:].strip()
                    if data_str and data_str != "[DONE]":
                        try:
                            parsed = json.loads(data_str)
                            if "choices" in parsed:
                                delta = parsed["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                full_assistant_content += content
                        except (json.JSONDecodeError, KeyError, IndexError):
                            pass

            # --- 6. 保存助手回复 ---
            if full_assistant_content:
                await self.chat_repo.add_message(
                    current_session_id, "assistant", full_assistant_content, user_id
                )
                await self.chat_repo.async_session.commit()

            # --- 7. 后置钩子 ---
            await self.on_after_chat(current_session_id, full_assistant_content, request)

        except Exception as e:
            logger.error(f"stream_chat error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            self._active_streams.pop(current_session_id, None)
            yield "data: [DONE]\n\n"

    async def non_stream_chat(self, request: ChatRequest) -> ChatCompletionResponse:
        """
        非流式对话 - 收集完整响应后一次性返回
        """
        full_content = ""
        session_id_out = None

        async for chunk in self.stream_chat(request):
            if chunk.startswith("data: "):
                data_str = chunk[6:].strip()
                if data_str == "[DONE]":
                    continue
                try:
                    parsed = json.loads(data_str)
                    if parsed.get("type") == "session_info":
                        session_id_out = parsed.get("session_id")
                    elif "choices" in parsed:
                        delta = parsed["choices"][0].get("delta", {})
                        full_content += delta.get("content", "")
                except (json.JSONDecodeError, KeyError, IndexError):
                    pass

        return ChatCompletionResponse(
            model=request.model or "",
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=Message(role="assistant", content=full_content),
                    finish_reason="stop",
                )
            ],
            session_id=session_id_out,
        )

    # ==============================================================
    # 停止响应
    # ==============================================================

    def stop_stream(self, session_id: str) -> bool:
        """停止指定会话的流式响应"""
        event = self._active_streams.get(session_id)
        if event:
            event.set()
            return True
        return False

    def is_stream_cancelled(self, session_id: str) -> bool:
        """检查流是否已被取消"""
        event = self._active_streams.get(session_id)
        return event.is_set() if event else False
