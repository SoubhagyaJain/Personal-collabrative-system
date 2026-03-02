# Personal Collaborative System Monorepo

Production-grade starter monorepo for a collaborative platform spanning web, API, ML workflows, and infrastructure.

## Tech Stack

- **Frontend:** Next.js 14, TypeScript, Tailwind CSS
- **Backend:** FastAPI, SQLAlchemy 2.0 async, Alembic, Redis
- **Data:** PostgreSQL, Redis
- **Infra:** Docker Compose
- **DevEx:** Makefile, pre-commit, Ruff, Prettier

## Architecture at a Glance

- `apps/web`: Netflix-like UI foundation and app shell.
- `apps/api`: versioned FastAPI API (`/api/v1`) with modular endpoints, async DB, migrations, and caching.
- `ml`: placeholders for training, feature, and inference pipelines.
- `infra`: compose manifests and deployment-oriented infrastructure assets.

See `docs/architecture.md` for the Mermaid diagram and boundaries.

## Local Development

### 1) Configure environment

```bash
cp .env.example .env
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
```

### 2) Run the full stack

```bash
docker compose -f infra/docker-compose.yml up --build
```

> Note: `infra/docker-compose.yml` is the source of truth. Root `docker-compose.yml` is a thin wrapper for convenience.

### 3) Access services

- Web: http://localhost:3000
- API docs: http://localhost:8000/docs
- API health (liveness): http://localhost:8000/api/v1/health
- API ready (readiness): http://localhost:8000/api/v1/ready

## Backend commands

```bash
make migrate   # alembic upgrade head
make seed      # load demo user/items
make test      # API + web tests
```

## API examples

### Home feed

```bash
curl "http://localhost:8000/api/v1/home?user_id=<demo_user_uuid>"
```

### Log an event

```bash
curl -X POST "http://localhost:8000/api/v1/events" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "<demo_user_uuid>",
    "item_id": "<item_uuid>",
    "event_type": "play",
    "row_id": "trending",
    "rank_position": 1,
    "session_id": "sess-1",
    "variant_id": "A",
    "watch_time_sec": 120
  }'
```


## Web + API end-to-end flow (PR-003)

After stack boot, seed catalog data:

```bash
make migrate
make seed
```

Then open `http://localhost:3000`.

- Home page fetches `GET /api/v1/home?user_id=...`.
- Clicking a title opens `/title/{id}` and fetches `GET /api/v1/item/{id}`.
- Web logs events via `POST /api/v1/events` for impressions, clicks, and plays.

### Demo identity strategy

- `user_id`: stored in browser `localStorage` as `recsysflix_user_id` (created with `crypto.randomUUID()` if missing).
- `session_id`: stored per-tab in `sessionStorage` as `recsysflix_session_id`.
- Impression dedupe key: `(session_id, row_id, item_id)` stored in `sessionStorage` as `recsysflix_impressions`.


## ML training + CF artifacts (PR-004)

Train MovieLens 1M collaborative filtering artifacts:

```bash
python ml/pipelines/training/download_movielens.py
python ml/pipelines/training/preprocess_movielens.py
python ml/pipelines/training/train_als.py
python ml/pipelines/inference/build_item_neighbors.py
```

Artifacts are generated under `ml/artifacts/v1`.

Point API to artifacts with:

```bash
export APP_ARTIFACT_PATH=ml/artifacts/v1
```

(or set `APP_ARTIFACT_PATH` in `apps/api/.env`).

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
5. Health check path: `/api/v1/health`.
6. Set env vars:
   - `APP_DATABASE_URL=<managed_postgres_asyncpg_url>`
   - `APP_REDIS_URL=<managed_redis_url>`
   - `APP_MODEL_VERSION=prod`

## Roadmap

- [ ] Auth + RBAC (JWT/OAuth)
- [ ] Collaborative workspace APIs (projects, tasks, comments)
- [ ] Background jobs + queue workers
- [ ] Observability stack (OpenTelemetry + tracing)
- [ ] CI pipeline with lint/test/build gates
- [ ] ML pipeline orchestration and feature store integration
