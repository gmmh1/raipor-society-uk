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
