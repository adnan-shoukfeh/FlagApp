# Globule — Backend

Django + Django REST Framework backend for Globule.

## Quick Start

```bash
# From this directory (backend/)

cp .env.example .env          # Fill in DATABASE_URL, SECRET_KEY, GOOGLE_CLIENT_ID/SECRET
uv sync                       # Install dependencies
make migrate                  # Apply migrations
uv run python manage.py load_countries  # Load 195 countries
make dev                      # Start server at :8000
```

## Key Commands

```bash
make dev              # runserver
make test             # run all tests (76)
make check            # Django system check
make migrate          # apply migrations
make makemigrations   # create migrations
```

## Project Structure

```
backend/
├── config/              # Django settings, URL routing
├── users/               # User model (email-based), UserStats, Google OAuth
├── flags/               # Country, DailyChallenge, Question, UserAnswer models
├── Makefile
├── pyproject.toml       # Dependencies (uv)
└── .env                 # Environment variables (gitignored)
```

## Environment Setup

Copy `.env.example` to `.env` and fill in:

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for local dev |
| `ALLOWED_HOSTS` | Comma-separated hostnames |
| `GOOGLE_CLIENT_ID` | From Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | From Google Cloud Console |

## Testing

```bash
make test                                              # All 76 tests
uv run python manage.py test --parallel --keepdb      # Fast (keep DB)
uv run python manage.py test users                    # Specific app
uv run python manage.py test --verbosity=2            # Verbose
```

## API Endpoints

```
POST /api/v1/auth/google/          # OAuth login (AllowAny)
POST /api/v1/auth/token/refresh/   # JWT refresh (AllowAny)
GET  /api/v1/daily/                # Today's challenge (IsAuthenticated)
POST /api/v1/daily/answer/         # Submit answer (IsAuthenticated)
GET  /api/v1/daily/history/        # Past challenges (IsAuthenticated)
GET  /api/v1/countries/            # List countries (AllowAny)
GET  /api/v1/countries/{id}/       # Country detail (AllowAny)
```

## Architecture Patterns

- **Fat models, thin views, thin serializers** — business logic lives in models
- **List vs Detail serializers** — minimal for lists, full for detail
- **Security** — `correct_answer` never exposed before challenge completion
- **ViewSets** for CRUD (Country), **APIView** for custom logic (OAuth, answer submission)
