# Agents

See `CLAUDE.md` for full project context, architecture patterns, and coding guidelines.

## Cursor Cloud specific instructions

### Services overview

| Service | Port | Start command | Working directory |
|---------|------|---------------|-------------------|
| PostgreSQL | 5432 | `sudo pg_ctlcluster 16 main start` | N/A |
| Backend (Django) | 8000 | `make dev` | `backend/` |
| Frontend (Vite) | 5173 | `yarn dev` | `frontend/` |

### Startup sequence

1. **PostgreSQL** must be running before the backend. Start with `sudo pg_ctlcluster 16 main start`. The database `globule` and user `globule` (password `globule`) are pre-configured.
2. **Backend**: `cd backend && make dev` — runs on port 8000.
3. **Frontend**: `cd frontend && yarn dev` — runs on port 5173, proxies `/api` to `http://127.0.0.1:8000`.

### Key caveats

- **No SQLite fallback**: The backend hard-requires PostgreSQL. There is no SQLite fallback in settings.
- **`.env` files are gitignored**: Both `backend/.env` and `frontend/.env` must exist. Copy from `.env.example` if missing. The backend `.env` requires at minimum `DATABASE_URL`, `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS`.
- **Google OAuth placeholders**: `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` can be set to `placeholder` for local dev. The app's default permissions are `AllowAny` in dev mode, so authenticated endpoints can be tested without real OAuth.
- **Country data**: After a fresh database, run `uv run python manage.py load_countries` from `backend/` to populate the 250 countries (fetched from REST Countries API; requires internet).
- **uv must be on PATH**: The `uv` binary installs to `~/.local/bin`. Ensure `PATH` includes it (the update script handles this via `source`).

### Commands reference

See `CLAUDE.md` "Key Commands" section for the full list. Quick reference:
- **Backend tests**: `make test` (from `backend/`)
- **Backend lint/check**: `make check` (from `backend/`)
- **Frontend typecheck + lint**: `yarn run check` (from `frontend/`)
- **Frontend typecheck only**: `yarn run typecheck` (from `frontend/`)
