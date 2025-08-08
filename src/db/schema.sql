-- AI Research Platform Database Schema
-- SQLite schema for multi-agent platform with observability

-- Agent Registry Table
CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    type TEXT NOT NULL, -- 'researcher', 'analyst', etc.
    version TEXT DEFAULT '1.0.0',
    config JSON, -- Agent-specific configuration
    status TEXT DEFAULT 'active', -- 'active', 'inactive', 'maintenance'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Research Runs Table
CREATE TABLE IF NOT EXISTS research_runs (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed', 'cancelled'
    input_data JSON, -- Research parameters and input
    output_data JSON, -- Final research results
    metadata JSON, -- Additional run metadata
    started_at DATETIME,
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents (id)
);

-- Cost Tracking Table
CREATE TABLE IF NOT EXISTS cost_tracking (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    provider TEXT NOT NULL, -- 'openrouter', 'langsmith', etc.
    model TEXT, -- Model used (e.g., 'claude-3.5-sonnet')
    operation_type TEXT NOT NULL, -- 'llm_call', 'research_api', 'trace', etc.
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    cost_usd DECIMAL(10, 6) DEFAULT 0.0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata JSON, -- Additional cost metadata
    FOREIGN KEY (run_id) REFERENCES research_runs (id)
);

-- Activity Log Table (for observability)
CREATE TABLE IF NOT EXISTS activity_log (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    step_name TEXT NOT NULL, -- LangGraph node name
    step_type TEXT, -- 'node', 'edge', 'tool_call', etc.
    status TEXT NOT NULL, -- 'started', 'completed', 'failed'
    input_data JSON,
    output_data JSON,
    error_message TEXT,
    duration_ms INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    FOREIGN KEY (run_id) REFERENCES research_runs (id)
);

-- LangSmith Traces Table (for integration)
CREATE TABLE IF NOT EXISTS langsmith_traces (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    trace_id TEXT NOT NULL, -- LangSmith trace ID
    trace_url TEXT, -- LangSmith dashboard URL
    session_id TEXT,
    status TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES research_runs (id)
);

-- Research Components Table (for Porter's analysis)
CREATE TABLE IF NOT EXISTS research_components (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    component_name TEXT NOT NULL, -- 'material_manager', 'ai_agent', etc.
    component_description TEXT,
    analysis_data JSON, -- Component-specific analysis results
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES research_runs (id)
);

-- Competitors Table (discovered during research)
CREATE TABLE IF NOT EXISTS competitors (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    component_id TEXT, -- Optional: component-specific competitor
    name TEXT NOT NULL,
    type TEXT, -- 'direct', 'partial'
    description TEXT,
    market_presence TEXT, -- 'high', 'medium', 'low'
    funding_info TEXT,
    feature_similarity_score DECIMAL(3, 2), -- 0.0 to 1.0
    analysis_data JSON, -- Detailed competitor analysis
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES research_runs (id),
    FOREIGN KEY (component_id) REFERENCES research_components (id)
);

-- Research Sources Table (for citation tracking)
CREATE TABLE IF NOT EXISTS research_sources (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    source_type TEXT NOT NULL, -- 'academic', 'industry_report', 'news', 'linkedin', etc.
    source_name TEXT NOT NULL,
    source_url TEXT,
    credibility_score DECIMAL(3, 2), -- 0.0 to 1.0 based on source weighting
    content_snippet TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    FOREIGN KEY (run_id) REFERENCES research_runs (id)
);

-- Framework Analysis Results (Porter's, PESTEL, SWOT, etc.)
CREATE TABLE IF NOT EXISTS framework_analysis (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    framework_type TEXT NOT NULL, -- 'porters', 'pestel', 'swot', 'ansoff', 'vpc'
    component_id TEXT, -- Optional: for component-specific analysis
    analysis_data JSON NOT NULL, -- Structured framework results
    confidence_score DECIMAL(3, 2), -- 0.0 to 1.0
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES research_runs (id),
    FOREIGN KEY (component_id) REFERENCES research_components (id)
);

-- User Settings/Preferences
CREATE TABLE IF NOT EXISTS user_settings (
    id TEXT PRIMARY KEY DEFAULT 'default',
    api_budget_soft_cap DECIMAL(10, 2) DEFAULT 50.0, -- USD
    api_budget_hard_cap DECIMAL(10, 2) DEFAULT 100.0, -- USD
    preferred_models JSON, -- Model preferences for different tasks
    notification_preferences JSON,
    dashboard_settings JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_research_runs_agent_id ON research_runs (agent_id);
CREATE INDEX IF NOT EXISTS idx_research_runs_status ON research_runs (status);
CREATE INDEX IF NOT EXISTS idx_research_runs_created_at ON research_runs (created_at);

CREATE INDEX IF NOT EXISTS idx_cost_tracking_run_id ON cost_tracking (run_id);
CREATE INDEX IF NOT EXISTS idx_cost_tracking_timestamp ON cost_tracking (timestamp);
CREATE INDEX IF NOT EXISTS idx_cost_tracking_provider ON cost_tracking (provider);

CREATE INDEX IF NOT EXISTS idx_activity_log_run_id ON activity_log (run_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_timestamp ON activity_log (timestamp);
CREATE INDEX IF NOT EXISTS idx_activity_log_step_name ON activity_log (step_name);

CREATE INDEX IF NOT EXISTS idx_competitors_run_id ON competitors (run_id);
CREATE INDEX IF NOT EXISTS idx_competitors_type ON competitors (type);

CREATE INDEX IF NOT EXISTS idx_research_sources_run_id ON research_sources (run_id);
CREATE INDEX IF NOT EXISTS idx_research_sources_type ON research_sources (source_type);

CREATE INDEX IF NOT EXISTS idx_framework_analysis_run_id ON framework_analysis (run_id);
CREATE INDEX IF NOT EXISTS idx_framework_analysis_type ON framework_analysis (framework_type);

-- Insert default researcher agent
INSERT OR IGNORE INTO agents (id, name, description, type, config) VALUES (
    'researcher-agent-v1',
    'Strategic Business Researcher',
    'Multi-framework business analysis agent using Porter''s Five Forces, PESTEL, SWOT, Ansoff Matrix, and Value Proposition Canvas',
    'researcher',
    json('{"frameworks": ["porters", "pestel", "swot", "ansoff", "vpc"], "max_components": 10, "research_depth": "deep"}')
);

-- Insert default user settings
INSERT OR IGNORE INTO user_settings (id, api_budget_soft_cap, api_budget_hard_cap) VALUES (
    'default',
    50.0,
    100.0
);