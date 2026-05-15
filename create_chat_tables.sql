-- ============================================================
-- Agent-FastAPI 数据库初始化脚本
-- 创建会话和消息表，支持 Agent 对话管理
-- 适用数据库: PostgreSQL
-- ============================================================

CREATE SCHEMA IF NOT EXISTS sdc_test;

-- 会话表
CREATE TABLE IF NOT EXISTS sdc_test.agent_chat_sessions_test (
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

COMMENT ON TABLE sdc_test.agent_chat_sessions_test IS 'Agent 对话会话表';
COMMENT ON COLUMN sdc_test.agent_chat_sessions_test.id IS '主键ID (UUID)';
COMMENT ON COLUMN sdc_test.agent_chat_sessions_test.user_id IS '用户ID';
COMMENT ON COLUMN sdc_test.agent_chat_sessions_test.title IS '会话标题';
COMMENT ON COLUMN sdc_test.agent_chat_sessions_test.model IS '使用的模型名称';
COMMENT ON COLUMN sdc_test.agent_chat_sessions_test.system_prompt IS '会话级系统提示词';
COMMENT ON COLUMN sdc_test.agent_chat_sessions_test.metadata IS '会话元数据 (JSON)';
COMMENT ON COLUMN sdc_test.agent_chat_sessions_test.is_deleted IS '软删除标记';
COMMENT ON COLUMN sdc_test.agent_chat_sessions_test.created_at IS '创建时间';
COMMENT ON COLUMN sdc_test.agent_chat_sessions_test.updated_at IS '更新时间';

-- 消息表
CREATE TABLE IF NOT EXISTS sdc_test.agent_chat_messages_test (
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
        REFERENCES sdc_test.agent_chat_sessions_test(id) ON DELETE CASCADE
);

COMMENT ON TABLE sdc_test.agent_chat_messages_test IS 'Agent 对话消息表';
COMMENT ON COLUMN sdc_test.agent_chat_messages_test.id IS '主键ID (UUID)';
COMMENT ON COLUMN sdc_test.agent_chat_messages_test.session_id IS '所属会话ID';
COMMENT ON COLUMN sdc_test.agent_chat_messages_test.user_id IS '消息所属用户ID';
COMMENT ON COLUMN sdc_test.agent_chat_messages_test.role IS '角色: system / user / assistant / tool';
COMMENT ON COLUMN sdc_test.agent_chat_messages_test.content IS '消息内容';
COMMENT ON COLUMN sdc_test.agent_chat_messages_test.token_count IS 'Token 消耗数量';
COMMENT ON COLUMN sdc_test.agent_chat_messages_test.metadata IS '消息元数据 (JSON)';
COMMENT ON COLUMN sdc_test.agent_chat_messages_test.is_deleted IS '软删除标记';
COMMENT ON COLUMN sdc_test.agent_chat_messages_test.created_at IS '创建时间';

-- 索引
CREATE INDEX IF NOT EXISTS idx_agent_chat_sessions_test_user_id ON sdc_test.agent_chat_sessions_test(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_chat_sessions_test_is_deleted ON sdc_test.agent_chat_sessions_test(is_deleted);
CREATE INDEX IF NOT EXISTS idx_agent_chat_sessions_test_updated_at ON sdc_test.agent_chat_sessions_test(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_chat_messages_test_session_id ON sdc_test.agent_chat_messages_test(session_id);
CREATE INDEX IF NOT EXISTS idx_agent_chat_messages_test_user_id ON sdc_test.agent_chat_messages_test(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_chat_messages_test_is_deleted ON sdc_test.agent_chat_messages_test(is_deleted);
CREATE INDEX IF NOT EXISTS idx_agent_chat_messages_test_created_at ON sdc_test.agent_chat_messages_test(created_at);
