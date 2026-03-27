# AI Loyalty Service
> Agentic AI platform for real-time customer loyalty management

[![CI](https://github.com/reethj-07/ai-loyalty-service/actions/workflows/ci.yml/badge.svg)](https://github.com/reethj-07/ai-loyalty-service/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/reethj-07/ai-loyalty-service/branch/main/graph/badge.svg)](https://codecov.io/gh/reethj-07/ai-loyalty-service)
![Python 3.11](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)

🎥 Demo video: https://www.loom.com/share/replace-with-your-demo-link

## What makes this interesting (2-minute pitch)
- Multi-node LangGraph agent that reasons, retrieves context, estimates ROI, and routes to human approval
- RFM + KMeans dynamic segmentation (ML-backed, not static SQL segment labels)
- pgvector semantic search grounding proposals in historical campaign outcomes
- Full observability with structured logs, OTEL traces, Prometheus metrics, Grafana dashboards
- Real-time frontend using WebSocket events and SSE streaming of AI reasoning steps

## Architecture
See the full architecture and flow diagram in [ARCHITECTURE.md](ARCHITECTURE.md).

## Quick start (under 5 minutes)
### 1) Clone and install
```bash
git clone https://github.com/reethj-07/ai-loyalty-service.git
cd ai-loyalty-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Configure environment
```bash
copy .env.example .env
```
Set at minimum:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_KEY`
- `REDIS_URL=redis://localhost:6379/0`
- `LLM_PROVIDER=groq`
- `GROQ_API_KEY=...` (free tier)

### 3) Run migrations
```bash
alembic upgrade head
```

### 4) Start local stack
```bash
make docker-up
```

### 5) Seed compelling demo data
```bash
make demo
```

### 6) Start backend + frontend
```bash
make dev
```

Backend docs: `http://localhost:8000/docs`  
Frontend: `http://localhost:8080`

## Core features
- LangGraph agent pipeline with context gathering, reasoning, proposal generation, ROI estimation, confidence gate
- Human-in-the-loop review queue for campaign approvals
- RFM scoring and KMeans clustering with segment explanations
- Celery + Redis task queue for detection, segmentation, and AI tasks
- WebSocket channels for proposals, alerts, transactions, KPI updates
- SSE streaming endpoint for step-by-step agent reasoning

## Observability stack
- Structlog for structured logging
- OpenTelemetry traces exported to Jaeger
- Prometheus metrics endpoint at `/metrics`
- Grafana dashboard at `monitoring/grafana/dashboards/loyalty_dashboard.json`

## API highlights
- `POST /api/v1/ai/pipeline/{member_id}`
- `GET /api/v1/ai/stream/{member_id}`
- `GET /api/v1/ai/metrics`
- `GET /api/v1/segments/stats`
- `GET /api/v1/members/{member_id}/rfm`
- `POST /api/v1/ml/retrain`
- `POST /api/v1/events/transaction`
- `GET /metrics`

## Testing and CI
```bash
make test
```
CI runs backend lint/typecheck/tests, frontend lint/build, and Docker build verification via GitHub Actions.

## Free tools used (zero-cost stack)
| Tool | Purpose | Free tier |
|------|---------|-----------|
| Groq | LLM inference | ~14,400 requests/day |
| Supabase | PostgreSQL + pgvector | Free plan |
| Redis | Cache + Celery broker | Local/self-hosted free |
| sentence-transformers | Local embeddings | Open source |
| scikit-learn | RFM + KMeans | Open source |
| Jaeger | Tracing | Self-hosted free |
| Prometheus + Grafana | Metrics | Self-hosted free |
| GitHub Actions | CI/CD | Free minutes on public repos |

No paid OpenAI APIs are required. Anthropic remains optional, while Groq is the default evaluator-friendly provider.