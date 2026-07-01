SHELL := /bin/bash

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	docker compose exec backend python manage.py migrate

superuser:
	docker compose exec backend python manage.py createsuperuser

test:
	docker compose exec backend pytest -q

lint:
	docker compose exec backend ruff check .

dev:
	docker compose up --build

web-install:
	cd web && npm install --no-audit --no-fund

web-dev:
	cd web && npm run dev

web-build:
	cd web && npm run build
