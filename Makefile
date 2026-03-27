.PHONY: dev test lint format docker-up celery-worker celery-beat flower demo

dev:
	docker compose up -d postgres redis jaeger prometheus grafana
	uvicorn app.main:app --reload --port 8000 &
	cd frontend && npm run dev

test:
	pytest tests/ -v --cov=app --cov-report=term-missing

lint:
	ruff check app/ tests/ && mypy app/

format:
	ruff format app/ tests/

docker-up:
	docker compose up --build

celery-worker:
	celery -A app.celery_app worker --loglevel=info

celery-beat:
	celery -A app.celery_app beat --loglevel=info

flower:
	celery -A app.celery_app flower --port=5555

demo:
	python seed_database.py
