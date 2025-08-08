# AI Research Platform

A multi-agent platform for strategic business research with comprehensive observability, designed to perform deep competitive analysis using established business frameworks.

## Features

- **Multi-Agent System**: Extensible platform supporting multiple AI agents
- **Strategic Research**: Porter's Five Forces, PESTEL, SWOT, Ansoff Matrix, Value Proposition Canvas
- **Full Observability**: Real-time cost tracking, activity monitoring, and performance analytics
- **Trusted Sources**: Curated academic and industry sources with credibility weighting
- **Cost Control**: Built-in budget management and spending alerts

## Quick Start

### Prerequisites

- Python 3.11+
- OpenRouter API key (for LLM access)
- LangSmith API key (for observability)
- Perplexity API key (for research, optional)

### Installation

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd ai-research-platform
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Initialize database**:
   ```bash
   sqlite3 ai_research_platform.db < src/db/schema.sql
   ```

4. **Run the application**:
   ```bash
   python src/api/main.py
   ```

### Using Docker

```bash
# Build and run
docker-compose up --build

# API will be available at http://localhost:8000
# Health check: http://localhost:8000/health
```

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check with system status
- `GET /api/status` - Detailed system status
- `GET /api/agents` - List available agents (coming in Phase 1)
- `GET /api/runs` - Research run history (coming in Phase 1)
- `GET /api/costs` - Cost analytics (coming in Phase 1)

## Development

### Project Structure

```
ai-research-platform/
├── src/
│   ├── api/           # FastAPI application
│   ├── db/            # Database schema and operations
│   ├── agents/        # Agent implementations (Phase 1+)
│   ├── research/      # Research logic (Phase 1+)
│   └── config.py      # Configuration management
├── requirements.txt   # Python dependencies
├── Dockerfile        # Container configuration
├── docker-compose.yml # Multi-service setup
└── .env.example      # Environment template
```

### Environment Variables

Key configuration options in `.env`:

```bash
# API Keys
OPENROUTER_API_KEY=your_key_here
LANGCHAIN_API_KEY=your_key_here
PERPLEXITY_API_KEY=your_key_here

# Cost Control
API_BUDGET_SOFT_CAP=50.0
API_BUDGET_HARD_CAP=100.0

# Models
DEFAULT_RESEARCH_MODEL=anthropic/claude-3.5-sonnet
FALLBACK_MODEL=openai/gpt-4o-mini
```

## Research Frameworks

The platform implements five strategic analysis frameworks:

1. **Porter's Five Forces**: Competitive environment analysis
2. **PESTEL Analysis**: Macro environment factors
3. **SWOT Analysis**: Strategic positioning
4. **Ansoff Matrix**: Growth opportunities
5. **Value Proposition Canvas**: Customer value mapping

## Observability

- **Real-time Tracing**: LangSmith integration for workflow visibility
- **Cost Tracking**: Per-operation cost monitoring with budget controls
- **Activity Logging**: Detailed step-by-step execution logs
- **Performance Metrics**: Execution time and success rate analytics

## Next Steps

This is Phase 0 (Bootstrap). Coming next:

- **Phase 1**: Core backend with cost tracking and LangSmith integration
- **Phase 2**: Strategic research agent implementation
- **Phase 3**: Frontend dashboard for observability
- **Phase 4**: Multi-agent platform expansion

## License

[Your License Here]