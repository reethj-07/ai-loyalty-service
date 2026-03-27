# Architecture

```mermaid
flowchart LR
  FE[React Dashboard] --> API[FastAPI]
  API --> LG[LangGraph Agent Pipeline]
  LG --> T1[Tool: Segmentation]
  LG --> T2[Tool: Behavioral Alerts]
  LG --> T3[Tool: RAG Retrieval]
  LG --> T4[Tool: ROI Estimator]

  API --> DB[(Supabase PostgreSQL)]
  DB --> PV[(pgvector)]

  API --> CE[Celery Worker]
  CE --> R[(Redis)]
  CE --> API

  API --> WS[WebSocket/SSE]
  WS --> FE

  API --> OTEL[OpenTelemetry SDK]
  CE --> OTEL
  OTEL --> J[Jaeger]

  API --> PM[/metrics]
  PM --> PR[Prometheus]
  PR --> GF[Grafana]

  GH[GitHub Actions] --> CI[Lint/Test/Build]
  CI --> IMG[Docker image validation]
```

## Notes
- Frontend receives proposal/alert/transaction updates via WebSocket channels.
- AI reasoning steps stream via SSE endpoint during graph execution.
- pgvector is used for similarity retrieval over historical campaign outcomes.
- Celery schedules recurring segmentation and detection tasks via beat.
