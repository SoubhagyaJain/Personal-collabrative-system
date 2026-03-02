# Architecture Overview

The monorepo follows a modular architecture with clear boundaries between frontend, backend, ML, and infrastructure concerns.

```mermaid
flowchart LR
    User((User)) --> Web[apps/web\nNext.js + Tailwind]
    Web --> API[apps/api\nFastAPI]
    API --> Postgres[(PostgreSQL)]
    API --> Redis[(Redis)]
    API --> ML[ml/pipelines\nML Workflows]

    subgraph Infrastructure
      Postgres
      Redis
      API
      Web
    end
```

## Components

- **apps/web**: UI foundation inspired by streaming-service layouts.
- **apps/api**: FastAPI service with health checks, typed response models, and structured logging.
- **ml**: Placeholders for training, feature, and inference pipelines.
- **infra**: Container orchestration via Docker Compose.
