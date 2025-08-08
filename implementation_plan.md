# AI Research Agent – Implementation Plan

## References
- Implementation logic, sources, and workflows: `Implementation-Idea-Document.md`
- Architecture, components, and data design: `System-Architecture.md`

## Objective
Implement a cost-efficient, observable research agent for Crane with a simple multi-agent-ready platform (backend + web dashboard). Prioritize Porter’s competitive analysis, PESTEL macro research, SWOT synthesis, Ansoff growth, and Value Proposition Canvas.

## Assumptions & Prerequisites
- Positioning document for Crane components is provided before execution (see `Implementation-Idea-Document.md` → 1.1)
- API keys available: OpenRouter, LangSmith
- Weekly budget target: ≤ $6; hard cap: $20/month; per-run soft cap: ~$1.50

## Target File/Folder Structure
```text
ai-research-platform/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── research_agent.py
│   │   └── registry.py
│   ├── workflows/
│   │   ├── __init__.py
│   │   ├── research_workflow.py
│   │   └── framework_analysis.py
│   ├── research/
│   │   ├── deep_research.py
│   │   ├── queries.py
│   │   └── sources.py           # trusted sources, weighting
│   ├── observability/
│   │   ├── __init__.py
│   │   ├── tracker.py           # cost tracker
│   │   └── dashboard_stream.py
│   ├── data/
│   │   ├── watchlist.json       # journals/newsletters/influencers
│   │   └── migrations/          # optional future
│   ├── db/
│   │   ├── models.py
│   │   └── schema.sql
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI
│   │   └── routes/
│   │       ├── research.py
│   │       ├── runs.py
│   │       └── costs.py
│   └── frontend/
│       ├── package.json
│       ├── vite.config.ts
│       ├── src/
│       │   ├── main.tsx
│       │   ├── App.tsx
│       │   └── components/
│       │       ├── AgentOverview.tsx
│       │       ├── RunHistory.tsx
│       │       ├── CostBreakdown.tsx
│       │       └── ResultViewer.tsx
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── .env.example
└── README.md
```

## Phased Plan

### Phase 0 – Bootstrap (Day 0–1)
- Create repo structure above; add `.env.example` with `OPENROUTER_API_KEY`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, `DATABASE_URL`.
- Pin Python deps in `requirements.txt` per `Implementation-Idea-Document.md`.
- Initialize FastAPI skeleton (`src/api/main.py`) with `/health` endpoint.
- Add SQLite schema from `System-Architecture.md` (research_runs, framework_results, cost_tracking, competitors).
- Acceptance: App runs locally; health endpoint OK; DB file created.

### Phase 1 – Core Backend & Costs (Day 2–3)
- Implement `OpenRouterClient` with token-cost logging.
- Implement `observability/tracker.py` CostTracker with soft/hard caps; monthly + per-run caps.
- Integrate LangSmith basic tracing in API layer.
- Acceptance: Any model call logs tokens/costs; budget guardrails enforced; traces visible in LangSmith.

### Phase 2 – Competitive Analysis (Porter’s) (Day 4–6)
- Implement `research/queries.py` with 3 deep queries using component description input; enforce citations per policy.
- Implement `research/deep_research.py` to call Perplexity/Google-like research via OpenRouter; validate structured JSON.
- Implement `research/sources.py` trusted sources catalog + weighting; store in `data/watchlist.json` (seed from Implementation doc).
- Build synthesis: `synthesize_competitor_analysis` → select top 2–3 direct/partial per component.
- Implement `workflows/research_workflow.py` steps for `discover_competitors` and `porters_analysis` (per-component + overall).
- Acceptance: For a mock component input, returns structured competitor sets with citations; Porter’s outputs include scores and factors.

### Phase 3 – Macro Environment (PESTEL) (Day 7–8)
- Implement parallel PESTEL queries with structured outputs and citations; US-focused with global overview.
- Generate macro insights, opportunities, threats; persist results.
- Acceptance: PESTEL results present for all 6 factors with impact scores and citations.

### Phase 4 – SWOT (Product-Market) (Day 9–10)
- Wire strengths (from positioning doc + competitive gaps), weaknesses (gaps), opportunities (from PESTEL), threats (Porter’s + PESTEL).
- Produce structured SWOT JSON + recommendations generator stub.
- Acceptance: SWOT returns all four elements with source links and rationale.

### Phase 5 – Ansoff (Growth) (Day 11–12)
- Implement market penetration and product development strategies; rank/prioritize opportunities.
- Acceptance: Returns opportunities with success factors, risks, and basic roadmap fields.

### Phase 6 – Value Proposition Canvas (Day 13–14)
- Persona loops for GCs, subcontractors, PMs, suppliers; customer jobs-pains-gains; feature-value mapping.
- Identify value gaps; map to opportunities.
- Acceptance: VPC JSON per persona + overall gaps.

### Phase 7 – Observability & Storage (Day 15–16)
- Full LangSmith tracing on all phases; custom metrics per phase.
- Persist run-level records, framework results, and per-call costs.
- Acceptance: A complete run shows all traces/metrics; DB has entries for run, frameworks, and costs.

### Phase 8 – Frontend MVP (Day 17–19)
- React + Vite + Tailwind skeleton in `src/frontend`.
- Pages/components:
  - AgentOverview: running/idle state, start/stop, progress %, ETA.
  - RunHistory: table of runs with status, duration, cost.
  - CostBreakdown: chart by framework/agent; month-to-date.
  - ResultViewer: markdown render of latest reports; download MD.
- Realtime: WebSocket stream for status, cost, and progress.
- Acceptance: Dashboard shows live run status, cost updates, and can view latest results.

### Phase 9 – Packaging & Deployment (Day 20)
- Dockerfile and docker-compose validated locally.
- Deployment: choose Railway or Render; configure env vars.
- Acceptance: Service accessible over the internet; dashboard functional; LangSmith traces appear for cloud runs.

## APIs (initial)
- POST `/research/run` start a run; payload: components[], positioning_doc_ref
- GET `/research/runs` list runs; filters
- GET `/research/run/{id}` run detail (status, outputs, costs)
- WS `/ws/stream` realtime status/cost updates

## Testing & QA
- Unit: JSON schema validation for research outputs; cost calculation; budget guardrails.
- Integration: end-to-end run with mock component + stubbed responses.
- Manual QA: visual check of dashboard, citations rendered, costs tally to DB.

## Risks & Mitigations
- Research API variability → strict schema validation + retries
- Cost overrun → hard caps + early abort with partial results
- Source reliability → enforce trusted-source weighting + citations per claim

## Deliverables Checklist
- Backend: API, workflows, research calls, observability, SQLite
- Frontend: 4 core views + WebSocket streaming + report viewer
- Docs: `.env.example`, README (setup/run), watchlist seed
- Runbook: start/stop commands, budget configuration

```text
Next action: Execute Phase 0 – Bootstrap (create folders, env, DB schema, health endpoint).
```