.PHONY: up down build migrate test shell logs

# Startup/Shutdown
up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

# Development
logs:
	docker compose logs -f backend

# Migrations (requires alembic setup)
migrate-init:
	docker compose exec backend alembic init alembic

migrate-generate:
	docker compose exec backend alembic revision --autogenerate -m "$(name)"

migrate-run:
	docker compose exec backend alembic upgrade head

# Testing
test:
	docker compose exec backend pytest

# cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -exec rm -f {} +
