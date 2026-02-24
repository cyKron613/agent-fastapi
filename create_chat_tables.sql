-- ============================================================
-- Agent-FastAPI 数据库初始化脚本
-- 创建会话和消息表，支持 Agent 对话管理
-- 适用数据库: PostgreSQL
-- ============================================================

CREATE SCHEMA IF NOT EXISTS sdc_test;

-- 会话表
CREATE TABLE IF NOT EXISTS sdc_test.agent_chat_sessions (
    id UUID PRIMARY KEY,
    user_id VARCHAR(64),
    title VARCHAR(255),
    model VARCHAR(100),
    system_prompt TEXT,
    metadata JSONB,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE sdc_test.agent_chat_sessions IS 'Agent 对话会话表';
COMMENT ON COLUMN sdc_test.agent_chat_sessions.id IS '主键ID (UUID)';
COMMENT ON COLUMN sdc_test.agent_chat_sessions.user_id IS '用户ID';
COMMENT ON COLUMN sdc_test.agent_chat_sessions.title IS '会话标题';
COMMENT ON COLUMN sdc_test.agent_chat_sessions.model IS '使用的模型名称';
COMMENT ON COLUMN sdc_test.agent_chat_sessions.system_prompt IS '会话级系统提示词';
COMMENT ON COLUMN sdc_test.agent_chat_sessions.metadata IS '会话元数据 (JSON)';
COMMENT ON COLUMN sdc_test.agent_chat_sessions.is_deleted IS '软删除标记';
COMMENT ON COLUMN sdc_test.agent_chat_sessions.created_at IS '创建时间';
COMMENT ON COLUMN sdc_test.agent_chat_sessions.updated_at IS '更新时间';

-- 消息表
CREATE TABLE IF NOT EXISTS sdc_test.agent_chat_messages (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL,
    user_id VARCHAR(64),
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    token_count VARCHAR(20),
    metadata JSONB,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_agent_chat_session FOREIGN KEY (session_id) 
        REFERENCES sdc_test.agent_chat_sessions(id) ON DELETE CASCADE
);

COMMENT ON TABLE sdc_test.agent_chat_messages IS 'Agent 对话消息表';
COMMENT ON COLUMN sdc_test.agent_chat_messages.id IS '主键ID (UUID)';
COMMENT ON COLUMN sdc_test.agent_chat_messages.session_id IS '所属会话ID';
COMMENT ON COLUMN sdc_test.agent_chat_messages.user_id IS '消息所属用户ID';
COMMENT ON COLUMN sdc_test.agent_chat_messages.role IS '角色: system / user / assistant / tool';
COMMENT ON COLUMN sdc_test.agent_chat_messages.content IS '消息内容';
COMMENT ON COLUMN sdc_test.agent_chat_messages.token_count IS 'Token 消耗数量';
COMMENT ON COLUMN sdc_test.agent_chat_messages.metadata IS '消息元数据 (JSON)';
COMMENT ON COLUMN sdc_test.agent_chat_messages.is_deleted IS '软删除标记';
COMMENT ON COLUMN sdc_test.agent_chat_messages.created_at IS '创建时间';

-- 索引
CREATE INDEX IF NOT EXISTS idx_agent_chat_sessions_user_id ON sdc_test.agent_chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_chat_sessions_is_deleted ON sdc_test.agent_chat_sessions(is_deleted);
CREATE INDEX IF NOT EXISTS idx_agent_chat_sessions_updated_at ON sdc_test.agent_chat_sessions(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_chat_messages_session_id ON sdc_test.agent_chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_agent_chat_messages_user_id ON sdc_test.agent_chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_chat_messages_is_deleted ON sdc_test.agent_chat_messages(is_deleted);
CREATE INDEX IF NOT EXISTS idx_agent_chat_messages_created_at ON sdc_test.agent_chat_messages(created_at);
