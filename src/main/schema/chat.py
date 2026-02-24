"""
Agent Chat Schema - 对话相关的请求/响应模型

兼容 OpenAI Chat Completions API 格式，同时扩展 Agent 会话管理能力。
开发者可在此基础上扩展自定义字段。
"""

from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


# ============================================================
# 枚举定义
# ============================================================

class MessageRole(str, Enum):
    """消息角色枚举"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


# ============================================================
# 基础消息模型
# ============================================================

class Message(BaseModel):
    """单条消息"""
    role: str = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")
    name: Optional[str] = Field(None, description="发送者名称(可选)")


# ============================================================
# Chat Completions 请求/响应 (兼容 OpenAI 格式)
# ============================================================

class ChatRequest(BaseModel):
    """
    对话请求 - 兼容 OpenAI Chat Completions API

    开发者在实现具体 Agent 时，可通过 metadata 字段传递业务自定义参数。
    """
    messages: Optional[List[Message]] = Field(None, description="对话消息列表")
    user_id: Optional[str] = Field(None, description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID(不传则自动创建)")
    stream: bool = Field(True, description="是否流式返回")
    model: Optional[str] = Field(None, description="使用的模型名称(不传则使用默认)")
    temperature: Optional[float] = Field(0.7, ge=0, le=2, description="温度参数")
    top_p: Optional[float] = Field(1.0, ge=0, le=1, description="Top-P 采样")
    n: Optional[int] = Field(1, ge=1, description="生成数量")
    stop: Optional[List[str]] = Field(None, description="停止序列")
    max_tokens: Optional[int] = Field(None, description="最大token数")
    presence_penalty: Optional[float] = Field(0.0, ge=-2, le=2, description="存在惩罚")
    frequency_penalty: Optional[float] = Field(0.0, ge=-2, le=2, description="频率惩罚")
    tools: Optional[List[Dict[str, Any]]] = Field(None, description="可用工具列表(Function Calling)")
    tool_choice: Optional[Any] = Field(None, description="工具选择策略")
    metadata: Optional[Dict[str, Any]] = Field(None, description="业务自定义元数据")

    @model_validator(mode='before')
    @classmethod
    def unwrap_envelope(cls, data: Any) -> Any:
        """支持 Swagger/OpenAPI 示例格式 (含 summary 和 value)"""
        if isinstance(data, dict) and "value" in data and isinstance(data["value"], dict):
            # 将 value 中的内容展平到外层，防止 Swagger 复制示例时带上的外层结构导致校验失败
            payload = data["value"].copy()
            for k, v in data.items():
                if k not in ("summary", "value") and v is not None:
                    payload[k] = v
            return payload
        return data


class ChatCompletionChoice(BaseModel):
    """Chat Completion 选项"""
    index: int = 0
    message: Message
    finish_reason: Optional[str] = "stop"


class ChatCompletionUsage(BaseModel):
    """Token 使用量"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletionResponse(BaseModel):
    """
    非流式对话响应 - 兼容 OpenAI 格式
    """
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:12]}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    model: str = ""
    choices: List[ChatCompletionChoice] = []
    usage: ChatCompletionUsage = ChatCompletionUsage()
    session_id: Optional[str] = Field(None, description="会话ID")


# ============================================================
# Session 会话管理相关
# ============================================================

class SessionCreateRequest(BaseModel):
    """创建会话请求"""
    user_id: Optional[str] = Field(None, description="用户ID")
    title: Optional[str] = Field(None, description="会话标题")
    model: Optional[str] = Field(None, description="指定模型")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    metadata: Optional[Dict[str, Any]] = Field(None, description="会话元数据")


class SessionRenameRequest(BaseModel):
    """会话重命名请求"""
    title: str = Field(..., min_length=1, max_length=255, description="新标题")


class SessionUpdateRequest(BaseModel):
    """会话更新请求(通用)"""
    title: Optional[str] = Field(None, max_length=255, description="新标题")
    system_prompt: Optional[str] = Field(None, description="新系统提示词")
    metadata: Optional[Dict[str, Any]] = Field(None, description="更新元数据")


class ChatMessageResponse(BaseModel):
    """消息响应"""
    id: uuid.UUID
    role: str
    content: str
    user_id: Optional[str] = None
    token_count: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata_")
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class ChatSessionResponse(BaseModel):
    """会话响应"""
    id: uuid.UUID
    title: Optional[str] = None
    user_id: Optional[str] = None
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata_")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class ChatSessionListResponse(BaseModel):
    """会话列表响应"""
    total: int = Field(0, description="总数")
    items: List[ChatSessionResponse] = Field(default_factory=list, description="会话列表")


class ChatHistoryDetailResponse(BaseModel):
    """会话详细记录响应"""
    session: ChatSessionResponse
    messages: List[ChatMessageResponse]
    total_messages: int = 0


class MessageFeedbackRequest(BaseModel):
    """消息反馈请求"""
    rating: Optional[str] = Field(None, description="评分: thumbs_up / thumbs_down")
    comment: Optional[str] = Field(None, max_length=1000, description="反馈内容")
