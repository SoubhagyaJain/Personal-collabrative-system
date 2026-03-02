COMPOSE ?= docker compose -f infra/docker-compose.yml

.PHONY: up down build lint test format migrate seed

up:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down -v

build:
	$(COMPOSE) build

lint:
	$(COMPOSE) run --rm api ruff check /app
	$(COMPOSE) run --rm web npm run lint

test:
	$(COMPOSE) run --rm api pytest -q
	$(COMPOSE) run --rm web npm run test

format:
	$(COMPOSE) run --rm api ruff format /app
	$(COMPOSE) run --rm web npm run format

migrate:
	$(COMPOSE) run --rm api alembic upgrade head

seed:
	$(COMPOSE) run --rm api python -m app.scripts.seed_db