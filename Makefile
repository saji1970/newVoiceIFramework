.PHONY: dev install test lint format docker-up docker-down db-init

install:
	pip install -e ".[dev,voice,all-providers]"

dev:
	uvicorn server.main:app --reload --host 0.0.0.0 --port 8000

dashboard:
	cd dashboard && npm run dev

test:
	pytest -v

lint:
	ruff check server/ tests/

format:
	ruff format server/ tests/

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

# Initialize / migrate DB schema (SQLAlchemy create_all)
db-init:
	python -c "import asyncio; from server.storage.database import init_db; asyncio.run(init_db())"
