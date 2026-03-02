COMPOSE ?= docker compose

.PHONY: up down build lint test format

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
