# AI Research Agent - System Architecture

## Architecture Overview

Building a scalable AI research platform using LangGraph for complex workflows, OpenRouter for cost-effective LLM access, and LangSmith for comprehensive observability.

### Core Design Principles
- **Cost Efficiency**: ~$6/month usage within $20 budget
- **Observability First**: Complete visibility into agent execution and costs
- **Multi-Agent Platform**: One UI for all current and future agents
- **Modular Design**: Easy to add new agent types beyond research
- **Simple UX**: Web interface for non-technical monitoring and control

---

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│  Web Dashboard  │  REST API  │  Real-time Updates              │
└─────────────────┴─────────────┴─────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  AGENT ORCHESTRATION                           │
├─────────────────────────────────────────────────────────────────┤
│  LangGraph       │  LangSmith      │  Research                 │
│  Workflow Engine │  Observability  │  Cache                    │
└─────────────────┴─────────────────┴───────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐
│   LLM LAYER     │ │ DATA LAYER   │ │ EXTERNAL APIs   │
├─────────────────┤ ├──────────────┤ ├─────────────────┤
│ OpenRouter      │ │ SQLite DB    │ │ Web Search      │
│ ├─Claude 3.5    │ │ File Storage │ │ News APIs       │
│ ├─GPT-4         │ │ Reports      │ │ Market Data     │
│ └─Perplexity    │ │ Cache        │ │ Company Info    │
└─────────────────┘ └──────────────┘ └─────────────────┘

WORKFLOW FLOW:
User → Dashboard → API → LangGraph → [Parallel Research] → Results → Storage → Dashboard
                                   ↓
                        [OpenRouter LLMs + External APIs]
                                   ↓
                        [LangSmith Observability Throughout]
```

---

## Component Architecture

### 1. LangGraph Workflow Engine

**Purpose**: Orchestrate complex multi-step research workflows with conditional logic

**Key Features**:
- **Parallel Processing**: Research multiple competitors simultaneously
- **Conditional Flows**: Skip sections based on data availability
- **Error Recovery**: Retry failed steps with different approaches
- **State Management**: Track progress across long-running research

**Workflow Structure**:
```python
# Main Research Workflow Nodes
nodes = [
    "initialize_research",
    "discover_competitors",
    "porters_analysis",            # competitive analysis (per component + overall)
    "macro_environment_pestel",    # separate macro research
    "product_market_swot",         # product-market positioning
    "growth_opportunities_ansoff", # market penetration + product development
    "customer_value_vpc",          # value proposition canvas
    "generate_reports",
    "finalize_output"
]

# Conditional Edges
edges = [
    ("initialize_research", "discover_competitors"),
    ("discover_competitors", "porters_analysis"),
    ("porters_analysis", "macro_environment_pestel"),
    ("macro_environment_pestel", "product_market_swot"),
    ("product_market_swot", "growth_opportunities_ansoff"),
    ("growth_opportunities_ansoff", "customer_value_vpc"),
    ("customer_value_vpc", "generate_reports"),
]
```

### 2. OpenRouter Integration

**Purpose**: Cost-effective access to multiple LLM providers

**Model Selection Strategy**:
- **Primary**: Claude 3.5 Sonnet (balance of quality/cost)
- **Fallback**: GPT-4o-mini (if Claude unavailable)
- **Specialized**: Perplexity for web search tasks

**Cost Management**:
```python
class CostTracker:
    def __init__(self):
        self.monthly_budget = 20.00
        self.current_usage = 0.00
        self.per_run_estimate = 1.50
    
    def can_execute_run(self) -> bool:
        return (self.current_usage + self.per_run_estimate) <= self.monthly_budget
    
    def track_usage(self, tokens_in: int, tokens_out: int, model: str):
        # Track costs per model, per framework, per run
        pass
```

### 3. LangSmith Observability

**Purpose**: Complete visibility into agent execution, debugging, and performance

**Monitoring Features**:
- **Real-time Tracing**: See each step of the research process
- **Cost Tracking**: Token usage and API costs per framework
- **Performance Metrics**: Response times, success rates
- **Error Analysis**: Failed API calls, parsing issues
- **Quality Scoring**: Research depth and accuracy metrics

**Integration Points**:
```python
from langsmith import traceable

@traceable(name="competitor_analysis")
def analyze_competitor(competitor_name: str, component: str) -> dict:
    # Automatic tracing of LLM calls, costs, and outputs
    pass

@traceable(name="framework_analysis")  
def run_porters_analysis(competitor_data: list) -> dict:
    # Track framework-specific performance
    pass
```

### 4. Data Architecture

**Database Schema** (SQLite for simplicity):

```sql
-- Research Runs
CREATE TABLE research_runs (
    id INTEGER PRIMARY KEY,
    run_date TIMESTAMP,
    status TEXT, -- 'running', 'completed', 'failed'
    total_cost REAL,
    duration_seconds INTEGER,
    frameworks_completed TEXT, -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Competitors Watchlist
CREATE TABLE competitors (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    category TEXT, -- 'direct', 'partial'
    component TEXT, -- 'material_manager', 'submittal_viewer', etc.
    url TEXT,
    last_analyzed TIMESTAMP,
    analysis_data TEXT, -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Framework Results
CREATE TABLE framework_results (
    id INTEGER PRIMARY KEY,
    run_id INTEGER REFERENCES research_runs(id),
    framework_type TEXT, -- 'porters', 'pestel', 'swot', 'ansoff'
    component TEXT,
    results TEXT, -- JSON
    confidence_score REAL,
    tokens_used INTEGER,
    cost REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cost Tracking
CREATE TABLE cost_tracking (
    id INTEGER PRIMARY KEY,
    run_id INTEGER REFERENCES research_runs(id),
    model_name TEXT,
    tokens_input INTEGER,
    tokens_output INTEGER,
    cost REAL,
    api_call_type TEXT, -- 'competitor_research', 'framework_analysis', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Detailed Workflow Design

### Research Agent Workflow

```
┌─────────────────┐
│ Start Research  │
│ Run             │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐     ┌─────────────────┐
│ Initialize &    │────▶│ Check Budget &  │
│ Validate        │     │ Limits          │
└─────────────────┘     └─────┬───────────┘
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
      ┌─────────────────┐         ┌─────────────────┐
      │ Budget OK:      │         │ Budget Exceeded:│
      │ Discover        │         │ Abort with     │
      │ Competitors     │         │ Warning         │
      └─────┬───────────┘         └─────────────────┘
            │
            ▼
      ┌─────────────────┐
      │ Filter &        │
      │ Prioritize      │
      │ (Top 2-3/comp)  │
      └─────┬───────────┘
            │
            ▼
      ┌─────────────────┐
      │ PARALLEL        │
      │ ANALYSIS        │
      └─────┬───────────┘
            │
    ┌───────┼───────┬───────┬───────┐
    ▼       ▼       ▼       ▼       ▼
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│Comp │ │Comp │ │Comp │ │     │ │     │
│  1  │ │  2  │ │  3  │ │ ... │ │ ... │
└──┬──┘ └──┬──┘ └──┬──┘ └─────┘ └─────┘
   │      │      │
   └──────┼──────┘
          │
          ▼
    ┌─────────────────┐
    │ FRAMEWORK       │
    │ ANALYSIS        │
    │ (Weighted)      │
    └─────┬───────────┘
          │
    ┌─────┼─────┬─────┬─────┐
    ▼     ▼     ▼     ▼     ▼
┌─────┐┌─────┐┌─────┐┌─────┐
│Port-││PEST-││SWOT ││Ans- │
│er's ││EL   ││35% ││off  │
│35% ││25%  ││25% ││15%  │
└──┬──┘└──┬──┘└──┬──┘└──┬──┘
   │     │     │     │
   └─────┼─────┼─────┘
         │     │
         ▼     ▼
     
    ┌─────────────────┐
    │ Generate        │
    │ Markdown        │
    │ Reports         │
    └─────┬───────────┘
          │
          ▼
    ┌─────────────────┐
    │ Store Results   │
    │ & Notify        │
    │ Completion      │
    └─────────────────┘

ERROR HANDLING:
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ API Failure     │────▶│ Retry with      │────▶│ Partial Results │
│ Detection       │     │ Fallback Model  │     │ if Needed       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Component Analysis Flow

Each Crane component gets analyzed separately:

1. **Material Manager**
   - Competitors: Top 2-3 (identified via research)
   - Focus: Feature comparison, pricing models, integration capabilities

2. **Submittal Viewer**  
   - Competitors: Submittal tracking/document management tools
   - Focus: Workflow efficiency, approval processes, collaboration features

3. **Project Schedule**
   - Competitors: Construction scheduling tools
   - Focus: CPM capabilities, real-time updates, mobile access

4. **Delivery Portal**
   - Competitors: Logistics/supplier portals
   - Focus: Real-time tracking, QR code functionality, driver experience

5. **Multi-Agent System**
   - Competitors: AI-powered construction tools, automated workflows
   - Focus: AI capabilities, automation level, learning algorithms

---

## Technology Stack Details

### Backend Infrastructure
```python
# Core Dependencies
langchain = "^0.1.0"
langgraph = "^0.0.40" 
langsmith = "^0.1.0"
openrouter = "^1.0.0"  # Custom client
fastapi = "^0.104.0"
sqlite3 = "built-in"
pydantic = "^2.0.0"
asyncio = "built-in"
```

### Frontend Dashboard
```javascript
// Simple React Dashboard
- React 18 + TypeScript
- Tailwind CSS for styling  
- Chart.js for cost/performance visualization
- WebSocket for real-time updates
- Simple table views for research results
```

### Deployment Options
1. **Local Development**: Python virtual environment + SQLite
2. **Cloud Deployment**: Railway/Render for simple hosting
3. **Container**: Docker for consistent environments

---

## Observability Dashboard Design

### Main Dashboard Views

1. **Agent Status Panel**
   ```
   [🟢 Research Agent - Running]
   Current Task: Analyzing Material Manager competitors
   Progress: 3/5 components completed
   Estimated Time Remaining: 12 minutes
   Current Cost: $0.85 / $1.50 budgeted
   ```

2. **Research Run History**
   ```
   | Date       | Status    | Cost  | Duration | Frameworks |
   |------------|-----------|-------|----------|------------|
   | 2024-01-15 | Completed | $1.42 | 18m 30s  | All 4      |
   | 2024-01-08 | Completed | $1.38 | 16m 45s  | All 4      |
   | 2024-01-01 | Failed    | $0.23 | 3m 12s   | Partial    |
   ```

3. **Cost Tracking**
   ```
   Monthly Usage: $5.67 / $20.00 (28%)
   Average per Run: $1.42
   Runs Remaining: ~10
   
   [Chart showing cost breakdown by framework]
   Porter's: 35% | PESTEL: 25% | SWOT: 25% | Ansoff: 15%
   ```

4. **Research Results Viewer**
   - Expandable sections for each framework
   - Markdown rendering of reports
   - Download options (MD, PDF)
   - Search/filter through historical results

---

## Development Phases

### Phase 1: Core Architecture (Week 1-2)
- [x] LangGraph workflow setup
- [x] OpenRouter integration
- [x] Basic database schema
- [x] Simple CLI for testing

### Phase 2: Research Logic (Week 3-4)
- [ ] Competitor discovery algorithms
- [ ] Framework analysis implementations
- [ ] Error handling and retries
- [ ] Cost tracking integration

### Phase 3: Observability (Week 5-6)
- [ ] LangSmith integration
- [ ] Web dashboard development
- [ ] Real-time status updates
- [ ] Report generation and storage

### Phase 4: Polish & Scale (Week 7-8)
- [ ] Performance optimization
- [ ] UI/UX improvements
- [ ] Documentation and testing
- [ ] Deployment setup

---

## Success Metrics

- **Cost Efficiency**: Stay under $6/month average usage
- **Reliability**: >90% successful research runs
- **Performance**: Complete full research in <20 minutes
- **Quality**: Consistent framework analysis across runs
- **Usability**: Non-technical dashboard interaction

---

## Multi-Agent Platform Design

### Adding New Agents to the Platform

The architecture is designed as a **unified multi-agent platform**. Here's how you can easily add new agents:

#### 1. Agent Registry System
```python
# agents/registry.py
from enum import Enum
from typing import Dict, Type
from .base_agent import BaseAgent

class AgentType(Enum):
    RESEARCH = "research"
    CONTENT_WRITER = "content_writer"
    DATA_ANALYST = "data_analyst"
    SOCIAL_MEDIA = "social_media"
    EMAIL_AUTOMATION = "email_automation"
    # Add new agent types here

class AgentRegistry:
    _agents: Dict[AgentType, Type[BaseAgent]] = {}
    
    @classmethod
    def register(cls, agent_type: AgentType):
        def decorator(agent_class):
            cls._agents[agent_type] = agent_class
            return agent_class
        return decorator
    
    @classmethod
    def get_agent(cls, agent_type: AgentType) -> Type[BaseAgent]:
        return cls._agents.get(agent_type)
    
    @classmethod
    def list_agents(cls) -> Dict[AgentType, Type[BaseAgent]]:
        return cls._agents.copy()
```

#### 2. Base Agent Interface
```python
# agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel

class AgentConfig(BaseModel):
    name: str
    description: str
    cost_per_run_estimate: float
    average_duration_minutes: int
    required_inputs: Dict[str, str]
    output_format: str

class AgentStatus(BaseModel):
    agent_id: str
    agent_type: str
    status: str  # 'idle', 'running', 'completed', 'failed'
    progress: Optional[Dict[str, Any]]
    current_step: Optional[str]
    estimated_completion: Optional[str]

class BaseAgent(ABC):
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        
    @property
    @abstractmethod
    def config(self) -> AgentConfig:
        """Return agent configuration and metadata"""
        pass
    
    @abstractmethod
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution method for the agent"""
        pass
    
    @abstractmethod
    async def get_status(self) -> AgentStatus:
        """Get current execution status"""
        pass
    
    async def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate required inputs before execution"""
        required = self.config.required_inputs.keys()
        return all(key in inputs for key in required)
```

#### 3. Example: New Content Writer Agent
```python
# agents/content_writer.py
from .base_agent import BaseAgent, AgentConfig, AgentStatus
from .registry import AgentRegistry, AgentType

@AgentRegistry.register(AgentType.CONTENT_WRITER)
class ContentWriterAgent(BaseAgent):
    @property
    def config(self) -> AgentConfig:
        return AgentConfig(
            name="Content Writer",
            description="Creates blog posts, marketing copy, and documentation",
            cost_per_run_estimate=2.50,
            average_duration_minutes=15,
            required_inputs={
                "topic": "Content topic or theme",
                "tone": "Writing tone (professional, casual, technical)",
                "length": "Target word count",
                "audience": "Target audience description"
            },
            output_format="markdown"
        )
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # LangGraph workflow for content creation
        # - Research topic
        # - Generate outline
        # - Write content
        # - Review and edit
        pass
```

### Unified Dashboard Interface

#### Multi-Agent Dashboard Views

**1. Agent Overview Panel**
```
┌─────────────────────────────────────────────────────────────┐
│                    AI AGENT PLATFORM                       │
├─────────────────────────────────────────────────────────────┤
│ Active Agents: 3/5    │ Monthly Budget: $15.67/$20.00      │
│ Running: 1           │ Est. Remaining: $4.33              │
└─────────────────────────────────────────────────────────────┘

Agent Status:
┌─────────────┬──────────────┬────────────┬─────────────┐
│ Agent       │ Status       │ Progress   │ Est. Time   │
├─────────────┼──────────────┼────────────┼─────────────┤
│ 🔍 Research │ Running      │ 60% (3/5)  │ 8 min       │
│ ✍️  Content │ Idle         │ -          │ -           │
│ 📊 Analytics│ Idle         │ -          │ -           │
│ 📱 Social   │ Scheduled    │ -          │ 2 hrs       │
│ 📧 Email    │ Idle         │ -          │ -           │
└─────────────┴──────────────┴────────────┴─────────────┘
```

**2. Agent Library & Creation**
```
┌─────────────────────────────────────────────────────────────┐
│                    AVAILABLE AGENTS                        │
├─────────────────────────────────────────────────────────────┤
│ [+] Add New Agent                                          │
└─────────────────────────────────────────────────────────────┘

┌──────────────┬─────────────────┬──────────────┬────────────┐
│ 🔍 Research  │ Business Intel  │ ~$1.50/run  │ [Configure]│
│              │ & Competitive   │ 20 min avg   │ [Run Now] │
│              │ Analysis        │              │           │
├──────────────┼─────────────────┼──────────────┼────────────┤
│ ✍️  Content  │ Blog Posts &    │ ~$2.50/run  │ [Configure]│
│              │ Marketing Copy  │ 15 min avg   │ [Run Now] │
├──────────────┼─────────────────┼──────────────┼────────────┤
│ 📊 Analytics │ Data Analysis   │ ~$1.00/run  │ [Configure]│
│              │ & Reporting     │ 10 min avg   │ [Run Now] │
└──────────────┴─────────────────┴──────────────┴────────────┘
```

**3. Universal Cost Tracking**
```
Cost Breakdown (This Month):
┌─────────────┬────────────┬─────────────┬──────────────┐
│ Agent       │ Runs       │ Total Cost  │ Avg/Run     │
├─────────────┼────────────┼─────────────┼──────────────┤
│ Research    │ 4          │ $6.20       │ $1.55        │
│ Content     │ 6          │ $14.50      │ $2.42        │
│ Analytics   │ 12         │ $11.80      │ $0.98        │
│ Social      │ 8          │ $8.40       │ $1.05        │
├─────────────┼────────────┼─────────────┼──────────────┤
│ TOTAL       │ 30         │ $40.90      │ $1.36        │
└─────────────┴────────────┴─────────────┴──────────────┘
```

### Database Schema for Multi-Agent Support

```sql
-- Extended schema for multiple agents
CREATE TABLE agents (
    id INTEGER PRIMARY KEY,
    agent_type TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    config JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent_runs (
    id INTEGER PRIMARY KEY,
    agent_id INTEGER REFERENCES agents(id),
    agent_type TEXT NOT NULL,
    status TEXT, -- 'queued', 'running', 'completed', 'failed'
    inputs JSON,
    outputs JSON,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    total_cost REAL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent_steps (
    id INTEGER PRIMARY KEY,
    run_id INTEGER REFERENCES agent_runs(id),
    step_name TEXT,
    step_order INTEGER,
    status TEXT,
    inputs JSON,
    outputs JSON,
    cost REAL,
    duration_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent-specific tables (e.g., for research agent)
CREATE TABLE research_competitors (
    id INTEGER PRIMARY KEY,
    run_id INTEGER REFERENCES agent_runs(id),
    company_name TEXT,
    component TEXT,
    analysis_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Future Agent Ideas & Integration

**Easy to Add Agent Types:**

1. **📝 Content Writer Agent**
   - Blog posts, marketing copy, documentation
   - Input: topic, tone, length, audience
   - Output: Polished content in multiple formats

2. **📊 Data Analytics Agent**  
   - Analyze CSV files, generate insights
   - Input: data files, analysis questions
   - Output: Charts, summaries, recommendations

3. **📱 Social Media Agent**
   - Create posts for multiple platforms
   - Input: content theme, brand voice, platforms
   - Output: Platform-specific posts with hashtags

4. **📧 Email Marketing Agent**
   - Newsletter creation, drip campaigns
   - Input: audience, goals, content calendar
   - Output: Email sequences with A/B test variants

5. **🎨 Design Agent**
   - Generate design briefs, mood boards
   - Input: project requirements, brand guidelines
   - Output: Design concepts and specifications

### Benefits of Unified Platform

✅ **Shared Infrastructure**: One LangSmith account, one database, one UI
✅ **Cost Efficiency**: Shared budget monitoring across all agents  
✅ **Consistent UX**: Same interface patterns for all agent types
✅ **Cross-Agent Insights**: Compare performance across different agents
✅ **Workflow Chaining**: Future ability to chain agents together
✅ **Centralized Observability**: All agent traces in one LangSmith project

**The research agent is just the first citizen of your AI agent platform!**

---

*This architecture provides the foundation for a scalable, observable, and cost-effective multi-agent AI platform.*