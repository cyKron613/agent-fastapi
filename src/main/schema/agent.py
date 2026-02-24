"""
Agent Schema - Agent 基本信息和配置相关模型
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class AgentCapability(BaseModel):
    """Agent 能力描述"""
    name: str = Field(..., description="能力名称")
    description: str = Field("", description="能力描述")
    enabled: bool = Field(True, description="是否启用")


class AgentModelInfo(BaseModel):
    """模型信息"""
    id: str = Field(..., description="模型ID")
    name: str = Field(..., description="模型名称")
    description: str = Field("", description="模型描述")
    max_tokens: Optional[int] = Field(None, description="最大token数")
    is_default: bool = Field(False, description="是否为默认模型")


class AgentInfoResponse(BaseModel):
    """
    Agent 基本信息响应

    开发者应在配置或 AgentService 中定义这些信息。
    """
    name: str = Field("Agent", description="Agent 名称")
    description: str = Field("", description="Agent 描述")
    version: str = Field("1.0.0", description="Agent 版本号")
    author: str = Field("", description="开发者/组织")
    capabilities: List[AgentCapability] = Field(default_factory=list, description="Agent 能力列表")
    models: List[AgentModelInfo] = Field(default_factory=list, description="支持的模型列表")
    default_model: Optional[str] = Field(None, description="默认模型ID")
    system_prompt: Optional[str] = Field(None, description="默认系统提示词(可选是否暴露)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="自定义元数据")


class AgentModelsResponse(BaseModel):
    """可用模型列表响应"""
    object: str = "list"
    data: List[AgentModelInfo] = Field(default_factory=list)


class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: str = Field("ok", description="服务状态")
    version: str = Field("", description="版本号")
    uptime: Optional[float] = Field(None, description="运行时长(秒)")
    timestamp: datetime = Field(default_factory=datetime.now)
    checks: Optional[Dict[str, Any]] = Field(None, description="各组件健康状态")
