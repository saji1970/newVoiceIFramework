.PHONY: dev install test lint format docker-up docker-down

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

db-upgrade:
	python -m server.storage.database upgrade
