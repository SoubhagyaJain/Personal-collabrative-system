# Personal Collaborative System Monorepo

Production-grade starter monorepo for a collaborative platform spanning web, API, ML workflows, and infrastructure.

## Tech Stack

- **Frontend:** Next.js 14, TypeScript, Tailwind CSS
- **Backend:** FastAPI, Pydantic, Uvicorn
- **Data:** PostgreSQL, Redis
- **Infra:** Docker Compose
- **DevEx:** Makefile, pre-commit, Ruff, Prettier

## Architecture at a Glance

- `apps/web`: Netflix-like UI foundation and app shell.
- `apps/api`: FastAPI service with modular routing, typed response models, and structured logging.
- `ml`: placeholders for training, feature, and inference pipelines.
- `infra`: compose manifests and deployment-oriented infrastructure assets.

See `docs/architecture.md` for the Mermaid diagram and boundaries.

## Repository Layout

```text
.
├── apps/
│   ├── api/
│   │   └── app/
│   │       ├── api/
│   │       ├── core/
│   │       └── models/
│   └── web/
├── docs/
├── infra/
├── ml/
├── docker-compose.yml
└── Makefile
```

## Local Development

### 1) Configure environment

```bash
cp .env.example .env
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
```

### 2) Run the full stack

```bash
docker compose up --build
```

### 3) Access services

- Web: http://localhost:3000
- API docs: http://localhost:8000/docs
- API health: http://localhost:8000/health

## Makefile Commands

```bash
make up       # docker compose up --build
make down     # stop and remove containers/volumes
make lint     # ruff + next lint
make test     # pytest + web test placeholder
make format   # ruff format + prettier
```

## Deployment

### Deploy `apps/web` to Vercel

1. Import repository in Vercel.
2. Set **Root Directory** to `apps/web`.
3. Build command: `npm run build`.
4. Set env var: `NEXT_PUBLIC_API_BASE_URL=https://<render-api-domain>`.
5. Deploy.

### Deploy `apps/api` to Render

1. Create a Render **Web Service** from this repo.
2. Set **Root Directory** to `apps/api`.
3. Runtime: **Docker**.
4. Exposed port: `8000`.
5. Health check path: `/health`.
6. Set env vars:
   - `APP_ENV=production`
   - `APP_LOG_LEVEL=INFO`

### Data services

Use managed Postgres + Redis (Render, Neon, Upstash, Railway, etc.) for production.

## Roadmap

- [ ] Auth + RBAC (JWT/OAuth)
- [ ] Collaborative workspace APIs (projects, tasks, comments)
- [ ] Background jobs + queue workers
- [ ] Observability stack (OpenTelemetry + tracing)
- [ ] CI pipeline with lint/test/build gates
- [ ] ML pipeline orchestration and feature store integration

## Quality Gates

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

This repo enforces:

- typed API payloads and responses,
- structured JSON logging,
- formatter/linter automation for Python + JS.
