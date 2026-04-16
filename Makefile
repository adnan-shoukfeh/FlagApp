.PHONY: dev dev-build down restart logs \
        migrate makemigrations shell dbshell test load-countries \
        typecheck check \
        prod-build-backend prod-build-frontend prod-build

# Pass backend .env to compose for ${DATABASE_*} interpolation in the db service
COMPOSE = docker compose --env-file ./backend/.env

# ---------------------------------------------------------------------------
# Dev lifecycle
# NOTE: stop local PostgreSQL first if it's running on port 5432
#       brew services stop postgresql@16
# ---------------------------------------------------------------------------

dev:
	$(COMPOSE) up

dev-build:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) restart

logs:
	$(COMPOSE) logs -f

# ---------------------------------------------------------------------------
# Backend management (run against the live dev container)
# ---------------------------------------------------------------------------

migrate:
	$(COMPOSE) exec backend uv run python manage.py migrate

makemigrations:
	$(COMPOSE) exec backend uv run python manage.py makemigrations

shell:
	$(COMPOSE) exec backend uv run python manage.py shell

dbshell:
	$(COMPOSE) exec db sh -c 'psql -U $$POSTGRES_USER $$POSTGRES_DB'

test:
	$(COMPOSE) exec backend uv run python manage.py test

load-countries:
	$(COMPOSE) exec backend uv run python manage.py load_countries

# ---------------------------------------------------------------------------
# Frontend (run against the live dev container)
# ---------------------------------------------------------------------------

typecheck:
	$(COMPOSE) exec frontend yarn run typecheck

check:
	$(COMPOSE) exec frontend yarn run check

# ---------------------------------------------------------------------------
# Production builds (standalone images, deployable to GCP or any container host)
# Pass VITE_* vars at build time — they are baked into the JS bundle
# Example:
#   make prod-build VITE_API_BASE_URL=https://api.example.com VITE_GOOGLE_CLIENT_ID=xxx
# ---------------------------------------------------------------------------

prod-build-backend:
	docker build --target prod -t globule-backend ./backend

prod-build-frontend:
	docker build --target prod \
		--build-arg VITE_API_BASE_URL=$(VITE_API_BASE_URL) \
		--build-arg VITE_GOOGLE_CLIENT_ID=$(VITE_GOOGLE_CLIENT_ID) \
		-t globule-frontend ./frontend

prod-build: prod-build-backend prod-build-frontend
