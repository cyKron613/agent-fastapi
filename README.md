# Agent-FastAPI

> **通用 Agent 开发框架** — 基于 FastAPI 构建的 AI Agent 后端脚手架，开箱即用，专为快速构建对话式 AI Agent 应用而设计。

## 目录

- [项目简介](#项目简介)
- [核心特性](#核心特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [API 接口一览](#api-接口一览)
- [开发指南](#开发指南)
  - [创建自定义 Agent](#创建自定义-agent)
  - [框架扩展点](#框架扩展点)
  - [切换 Agent 实现](#切换-agent-实现)
- [数据库设计](#数据库设计)
- [配置说明](#配置说明)
- [部署指南](#部署指南)
- [架构设计](#架构设计)

---

## 项目简介

Agent-FastAPI 是一个 **通用的 Agent 开发框架**，提供了构建对话式 AI Agent 所需的全部基础设施：

- **会话管理** — 创建、查询、重命名、删除会话
- **对话接口** — 兼容 OpenAI Chat Completions API 格式 (流式/非流式)
- **消息持久化** — 自动保存对话历史到 PostgreSQL
- **停止响应** — 支持中断正在进行的流式生成
- **Agent 信息** — 标准化的 Agent 元信息和能力声明
- **可扩展架构** — 通过继承 `BaseAgentService` 快速实现自定义 Agent

**开发者无需关心对话管理、Session 持久化、流式传输等基础设施，只需专注于实现自己的 Agent 逻辑。**

---

## 核心特性

| 特性 | 说明 |
|------|------|
| 🤖 **OpenAI 兼容** | Chat Completions API 格式，前端可直接对接 |
| 🌊 **流式/非流式** | 同时支持 SSE 流式和一次性 JSON 响应 |
| 📝 **自动会话管理** | 自动创建会话、生成标题、持久化消息 |
| 🔌 **插件式架构** | 继承 `BaseAgentService` 实现自定义 Agent |
| ⏹️ **停止响应** | 支持中断流式生成 |
| 🗑️ **软删除** | 会话和消息支持软删除，数据可恢复 |
| 🎯 **生命周期钩子** | `on_before_chat` / `on_after_chat` 扩展点 |
| 🛡️ **异常处理** | 全局异常处理、参数校验、业务异常 |
| 📊 **数据库监控** | 连接池监控、自动重试机制 |
| 🔄 **Redis 支持** | 内置 Redis 缓存客户端和中间件(可选) |

---

## 技术栈

| 组件 | 技术 |
|------|------|
| Web 框架 | FastAPI |
| ORM | SQLAlchemy 2.0 (AsyncIO) |
| 数据库 | PostgreSQL + asyncpg |
| 缓存 | Redis (可选) |
| HTTP 客户端 | httpx |
| 配置管理 | pydantic-settings + python-decouple |
| 日志 | loguru |

---

## 项目结构

```
agent-fastapi/
├── main.py                          # 应用入口
├── requirements.txt                 # Python 依赖
├── create_chat_tables.sql           # 数据库建表脚本
├── .env                             # 环境变量配置 (需自行创建)
├── system_prompt.txt                # 系统提示词模板 (可选)
│
├── src/
│   └── main/
│       ├── api/                     # 🔵 API 路由层
│       │   ├── endpoints.py         # 路由注册入口
│       │   └── agent/
│       │       └── agent_router.py  # ⭐ Agent 核心路由 (所有 API 定义)
│       │
│       ├── service/                 # 🟢 服务层 (业务逻辑)
│       │   └── agent/
│       │       ├── base_agent_service.py     # ⭐ Agent 服务基类 (抽象)
│       │       ├── default_agent_service.py  # ⭐ 默认 Agent 实现
│       │       └── example_custom_agent.py   # 📖 自定义 Agent 示例
│       │
│       ├── schema/                  # 🟡 数据模型 (Pydantic)
│       │   ├── chat.py              # 对话相关请求/响应模型
│       │   └── agent.py             # Agent 信息模型
│       │
│       ├── models/                  # 🔴 ORM 模型
│       │   └── chat.py              # 会话 & 消息表定义
│       │
│       ├── repository/              # 🟣 数据访问层
│       │   └── chat_repository.py   # 会话/消息 CRUD
│       │
│       ├── config/                  # ⚙️ 配置
│       │   ├── manager.py           # 配置工厂
│       │   ├── settings/            # 环境配置 (dev/prod)
│       │   ├── handler/             # 异常/中间件/生命周期处理器
│       │   └── middleware/          # Redis 缓存中间件
│       │
│       └── core/                    # 🧱 核心基础设施
│           ├── orm/                 # ORM 基类 (DB/Session/Repository/Service)
│           ├── schema/              # 通用响应模型
│           └── util/                # 工具类 (Redis/异常/格式化)
│
├── deploy/                          # 部署配置
│   ├── docker/                      # Docker 配置
│   └── k8s/                         # Kubernetes 配置
```

---

## 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd agent-fastapi
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件：

```env
# ===== 服务器配置 =====
ENVIRONMENT=DEV
BACKEND_SERVER_HOST=0.0.0.0
BACKEND_SERVER_PORT=8000
BACKEND_SERVER_WORKERS=1
API_PREFIX=/api/v1
DOCS_URL=/api-doc.html
OPENAPI_URL=/api.json
REDOC_URL=/api-redoc.html
DOCS_AUTH_USERNAME=admin
DOCS_AUTH_PASSWORD=admin123

# ===== 数据库配置 (主库) =====
POSTGRES_CONNECT=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=agent_db
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=postgres

# ===== 数据库配置 (副库，可与主库相同) =====
POSTGRES_CONNECT_ANOTHER=postgresql
POSTGRES_HOST_ANOTHER=localhost
POSTGRES_PORT_ANOTHER=5432
POSTGRES_DB_ANOTHER=agent_db
POSTGRES_USERNAME_ANOTHER=postgres
POSTGRES_PASSWORD_ANOTHER=postgres

# ===== 数据库连接池 =====
DB_MAX_POOL_CON=10
DB_POOL_SIZE=5
DB_POOL_OVERFLOW=10
DB_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_POOL_TIMEOUT=30
DB_POOL_RESET_ON_RETURN=rollback
DB_RETRY_ATTEMPTS=3
DB_RETRY_DELAY=1
DB_RETRY_BACKOFF=2
IS_DB_ECHO_LOG=false
IS_DB_FORCE_ROLLBACK=false
IS_DB_EXPIRE_ON_COMMIT=false

# ===== Redis 配置 =====
PROD_REDIS_HOST=localhost
PROD_REDIS_PORT=6379
PROD_REDIS_PASSWORD=
PROD_REDIS_DB=0
PROD_REDIS_CLUSTER=false
PROD_REDIS_NODES=
TEST_REDIS_HOST=localhost
TEST_REDIS_PORT=6379
TEST_REDIS_PASSWORD=
TEST_REDIS_DB=0

# ===== LLM 配置 =====
LLM_API_KEY=sk-your-api-key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4o
```

### 4. 初始化数据库

```bash
psql -U postgres -d agent_db -f create_chat_tables.sql
```

### 5. 启动服务

```bash
python main.py
```

服务启动后访问：
- API 文档: `http://localhost:8000/api-doc.html`
- ReDoc: `http://localhost:8000/api-redoc.html`

---

## API 接口一览

所有接口前缀: `/api/v1/agent/v1`

### 对话接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/chat/completions` | 对话接口 (流式/非流式) |

### 会话管理

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/sessions` | 获取会话列表 (支持分页) |
| `POST` | `/sessions` | 创建新会话 |
| `GET` | `/sessions/{session_id}` | 获取会话详情及消息记录 |
| `PUT` | `/sessions/{session_id}` | 更新会话信息 |
| `DELETE` | `/sessions/{session_id}` | 删除会话 (软删除/硬删除) |
| `PATCH` | `/sessions/{session_id}/rename` | 重命名会话 |

### 流控制

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/sessions/{session_id}/stop` | 停止流式响应 |

### 消息管理

| 方法 | 路径 | 说明 |
|------|------|------|
| `DELETE` | `/sessions/{session_id}/messages/{message_id}` | 删除消息 |

### Agent 信息

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/agent/info` | 获取 Agent 基本信息 |
| `GET` | `/agent/models` | 获取可用模型列表 |

### 系统

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/health` | 健康检查 |

---

### 接口详细说明

#### POST `/chat/completions` — 对话

**请求体:**
```json
{
  "messages": [
    {"role": "user", "content": "你好"}
  ],
  "user_id": "user_001",
  "session_id": null,
  "stream": true,
  "model": "gpt-4o",
  "temperature": 0.7,
  "max_tokens": 2048,
  "metadata": {}
}
```

- `session_id` 为空时自动创建新会话
- `stream=true` 返回 SSE 流式响应
- `stream=false` 返回标准 JSON 响应 (OpenAI 格式)

**流式响应格式 (SSE):**
```
data: {"type": "session_info", "session_id": "xxxx-xxxx"}

data: {"choices": [{"delta": {"content": "你"}}]}

data: {"choices": [{"delta": {"content": "好"}}]}

data: [DONE]
```

#### GET `/sessions` — 获取会话列表

**参数:**
| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `limit` | int | 20 | 每页数量 (1-100) |
| `offset` | int | 0 | 偏移量 |
| `user_id` | string | null | 按用户筛选 |

**响应:**
```json
{
  "total": 42,
  "items": [
    {
      "id": "uuid",
      "title": "关于天气的对话",
      "user_id": "user_001",
      "model": "gpt-4o",
      "created_at": "2026-02-24T10:00:00",
      "updated_at": "2026-02-24T10:05:00"
    }
  ]
}
```

#### DELETE `/sessions/{session_id}` — 删除会话

**参数:**
| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `hard` | bool | false | 是否硬删除 (不可恢复) |

#### POST `/sessions/{session_id}/stop` — 停止响应

停止指定会话正在进行的流式输出。前端点击"停止生成"按钮时调用。

---

## 开发指南

### 创建自定义 Agent

**核心步骤: 继承 `BaseAgentService`，实现 `process_chat()` 方法。**

```python
# src/main/service/agent/my_agent_service.py

from typing import AsyncGenerator, List, Dict, Optional
from src.main.service.agent.base_agent_service import BaseAgentService
from src.main.schema.chat import ChatRequest
from src.main.schema.agent import AgentInfoResponse


class MyAgentService(BaseAgentService):
    """我的自定义 Agent"""

    def get_agent_info(self) -> AgentInfoResponse:
        return AgentInfoResponse(
            name="My Agent",
            description="我的自定义 AI Agent",
            version="1.0.0",
        )

    def get_system_prompt(self, request=None) -> Optional[str]:
        return "你是一个专业的助手。"

    async def process_chat(
        self,
        messages: List[Dict[str, str]],
        request: ChatRequest,
        session_id: str,
    ) -> AsyncGenerator[str, None]:
        """
        在这里实现你的 Agent 核心逻辑:
        - RAG 检索增强
        - Function Calling
        - 多模型路由
        - 业务数据注入
        - ...
        """
        # 示例: 调用 LLM
        import httpx, json
        from src.main.config.manager import settings

        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                f"{settings.LLM_BASE_URL}/chat/completions",
                json={"model": settings.LLM_MODEL_NAME, "messages": messages, "stream": True},
                headers={"Authorization": f"Bearer {settings.LLM_API_KEY}"},
            ) as response:
                async for line in response.aiter_lines():
                    if self.is_stream_cancelled(session_id):
                        break
                    if line.strip():
                        yield f"{line}\n\n"
```

### 框架扩展点

`BaseAgentService` 提供以下可覆盖的方法:

| 方法 | 必须实现 | 说明 |
|------|---------|------|
| `process_chat()` | ✅ | **核心对话处理逻辑** — 接收上下文消息，流式返回 SSE 格式响应 |
| `get_agent_info()` | ❌ | 返回 Agent 元信息 (名称、能力、版本等) |
| `get_system_prompt()` | ❌ | 返回系统提示词 (支持根据 request 动态生成) |
| `get_available_models()` | ❌ | 返回可用模型列表 |
| `on_before_chat()` | ❌ | **对话前钩子** — 预处理、校验、审计日志 |
| `on_after_chat()` | ❌ | **对话后钩子** — 统计、评估、异步任务 |

**框架自动处理的事项 (开发者无需关心):**
- ✅ 会话创建/恢复
- ✅ 历史消息上下文构建
- ✅ 用户消息持久化
- ✅ 助手回复持久化
- ✅ 会话标题自动生成
- ✅ 流式传输管理
- ✅ 停止响应支持
- ✅ 异常捕获和错误响应

### 切换 Agent 实现

在 `agent_router.py` 中，将 `DefaultAgentService` 替换为你的实现:

```python
# src/main/api/agent/agent_router.py

# 替换前:
from src.main.service.agent.default_agent_service import DefaultAgentService

# 替换后:
from src.main.service.agent.my_agent_service import MyAgentService as DefaultAgentService
```

或者更精细地控制:

```python
# 只替换 chat_completions 端点中的依赖
@router.post("/chat/completions")
async def chat_completions(
    request: ChatRequest = Body(...),
    agent_service: MyAgentService = Depends(
        get_async_service(ser_type=MyAgentService, repo_type=ChatRepository)
    ),
):
    ...
```

---

## 数据库设计

### agent_chat_sessions (会话表)

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | UUID | 主键 |
| `user_id` | VARCHAR(64) | 用户ID |
| `title` | VARCHAR(255) | 会话标题 (自动生成) |
| `model` | VARCHAR(100) | 使用的模型名称 |
| `system_prompt` | TEXT | 会话级系统提示词 |
| `metadata` | JSONB | 自定义元数据 |
| `is_deleted` | BOOLEAN | 软删除标记 |
| `created_at` | TIMESTAMP | 创建时间 |
| `updated_at` | TIMESTAMP | 更新时间 |

### agent_chat_messages (消息表)

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | UUID | 主键 |
| `session_id` | UUID | 所属会话ID (外键, CASCADE) |
| `user_id` | VARCHAR(64) | 用户ID |
| `role` | VARCHAR(20) | 角色: system / user / assistant / tool |
| `content` | TEXT | 消息内容 |
| `token_count` | VARCHAR(20) | Token 消耗量 |
| `metadata` | JSONB | 自定义元数据 |
| `is_deleted` | BOOLEAN | 软删除标记 |
| `created_at` | TIMESTAMP | 创建时间 |

---

## 配置说明

所有配置通过 `.env` 文件或环境变量注入。

### 核心配置项

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `ENVIRONMENT` | 运行环境 | `DEV` / `PROD` |
| `BACKEND_SERVER_HOST` | 服务地址 | `0.0.0.0` |
| `BACKEND_SERVER_PORT` | 服务端口 | `8000` |
| `API_PREFIX` | API 路径前缀 | `/api/v1` |

### LLM 配置

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `LLM_API_KEY` | API 密钥 | `sk-xxxx` |
| `LLM_BASE_URL` | API 地址 (兼容 OpenAI 格式) | `https://api.openai.com/v1` |
| `LLM_MODEL_NAME` | 默认模型 | `gpt-4o` |

> **支持任何兼容 OpenAI API 格式的 LLM 服务**，如: OpenAI、Azure OpenAI、通义千问、DeepSeek、Ollama 等。

### 数据库配置

| 变量名 | 说明 |
|--------|------|
| `POSTGRES_HOST` | 数据库地址 |
| `POSTGRES_PORT` | 数据库端口 |
| `POSTGRES_DB` | 数据库名 |
| `POSTGRES_USERNAME` | 用户名 |
| `POSTGRES_PASSWORD` | 密码 |
| `DB_POOL_SIZE` | 连接池大小 |

---

## 部署指南

### Docker 部署

```bash
# 构建镜像
docker build -f deploy/docker/Dockerfile -t agent-fastapi .

# 运行容器
docker run -d \
  --name agent-fastapi \
  -p 8000:8000 \
  --env-file .env \
  agent-fastapi
```

### Docker Compose

```bash
cd deploy/docker
docker-compose up -d
```

### Kubernetes

```bash
# 测试环境
kubectl apply -f deploy/k8s/test/

# 生产环境
kubectl apply -f deploy/k8s/prod/
```

---

## 架构设计

```
┌──────────────────────────────────────────────────────────────┐
│                        Client (前端/SDK)                      │
│              POST /chat/completions  (SSE Stream)             │
└─────────────────────────┬────────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────────┐
│                     API Router Layer                          │
│                   (agent_router.py)                           │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐  │
│  │ /chat/       │ │ /sessions    │ │ /agent/info          │  │
│  │ completions  │ │ CRUD         │ │ /agent/models        │  │
│  └──────┬───────┘ └──────┬───────┘ │ /health              │  │
│         │                │         └──────────┬───────────┘  │
└─────────┼────────────────┼────────────────────┼──────────────┘
          │                │                    │
┌─────────▼────────────────▼────────────────────▼──────────────┐
│                     Service Layer                             │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              BaseAgentService (抽象基类)                  │  │
│  │  ┌───────────────────────────────────────────────────┐  │  │
│  │  │  stream_chat()      ← 框架核心流程 (自动管理)      │  │  │
│  │  │  non_stream_chat()  ← 非流式封装                   │  │  │
│  │  │  stop_stream()      ← 停止响应                     │  │  │
│  │  └───────────────────────────────────────────────────┘  │  │
│  │  ┌───────────────────────────────────────────────────┐  │  │
│  │  │  process_chat()     ← ⭐ 开发者实现 (核心逻辑)     │  │  │
│  │  │  get_system_prompt() ← 开发者可选覆盖              │  │  │
│  │  │  on_before_chat()   ← 前置钩子                     │  │  │
│  │  │  on_after_chat()    ← 后置钩子                     │  │  │
│  │  └───────────────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                           ↓                                   │
│  ┌──────────────────────────────────┐                         │
│  │  DefaultAgentService (默认实现)    │  ← 直接代理 LLM        │
│  │  ExampleCustomAgent  (示例)       │  ← 参考实现             │
│  │  YourAgentService    (你的实现)    │  ← 开发者自定义         │
│  └──────────────────────────────────┘                         │
└──────────────────────────┬───────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│                   Repository Layer                            │
│                 (chat_repository.py)                          │
│           Session CRUD  |  Message CRUD                       │
└──────────────────────────┬───────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│                   Database (PostgreSQL)                        │
│              agent_chat_sessions  |  agent_chat_messages          │
└──────────────────────────────────────────────────────────────┘
```

**核心设计原则:**

1. **关注点分离** — API 路由 / 服务逻辑 / 数据访问 / 模型定义 各层职责清晰
2. **开放-封闭原则** — 框架处理基础设施，开发者通过继承扩展业务逻辑
3. **兼容性** — OpenAI Chat Completions API 格式，前端/SDK 可无缝对接
4. **渐进式** — 可从 DefaultAgentService 开始，逐步添加 RAG、Tool Use 等能力

---

## License

MIT
