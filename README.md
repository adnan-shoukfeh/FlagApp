# Globule

> A daily geography challenge app. Identify flags, learn countries, build streaks.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-5.0+-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/react-18+-61dafb.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/typescript-5.9-3178c6.svg)](https://www.typescriptlang.org/)

**Status: MVP — Backend complete, web frontend in progress**

---

## About

One flag per day, three attempts to name the country. Streaks, stats, and a Swiss motorway signage-inspired interface. Globule serves web, mobile, and widget clients from a single API.

## Tech Stack

| Layer | Stack |
|-------|-------|
| **Backend** | Django 5.0+ / DRF / PostgreSQL / JWT + Google OAuth / uv |
| **Frontend** | Vite + React 18 + TypeScript / Radix UI + Custom CSS / Zustand / Axios |
| **Design** | Swiss motorway signage aesthetic — Overpass font, dark green, white borders |
| **Data** | 195 countries from REST Countries API, flags via flagcdn.com CDN |

## Development

### Prerequisites

[Docker Desktop](https://www.docker.com/products/docker-desktop/), and nothing else — all services run in containers.

### First-time setup

```bash
# 1. Stop local PostgreSQL if running (avoids port 5432 conflict)
brew services stop postgresql@16

# 2. Configure environment files
cp backend/.env.example backend/.env    # fill in SECRET_KEY, GOOGLE_CLIENT_ID/SECRET
cp frontend/.env.example frontend/.env  # fill in VITE_GOOGLE_CLIENT_ID

# 3. Build images and start all services
make dev-build

# 4. Load country data (one-time)
make load-countries
```

Backend is at `http://localhost:8000`, frontend at `http://localhost:5173`.  
Migrations run automatically on every `make dev` startup.

### Daily workflow

```bash
make dev          # start all services (db + backend + frontend)
make down         # stop everything
make logs         # tail all container logs
make test         # run 76 backend tests
make check        # TypeScript + ESLint
```

### Database & Django

```bash
make migrate          # apply migrations
make makemigrations   # create new migrations
make shell            # Django shell
make dbshell          # psql inside the db container
```

### Production builds

```bash
# Build standalone images ready for GCP (or any container host)
make prod-build \
  VITE_API_BASE_URL=https://api.yourdomain.com \
  VITE_GOOGLE_CLIENT_ID=your-client-id
```

### Running without Docker

If you need to run services directly on the host:

```bash
# Backend
cd backend && uv sync && make dev

# Frontend (in a separate terminal)
cd frontend && yarn install && yarn dev
```

## Project Structure

```
Flag_Project/
├── backend/
│   ├── config/               # Django settings, urls
│   ├── users/                # User, UserStats, Google OAuth
│   ├── flags/                # Country, DailyChallenge, Question, UserAnswer
│   └── Makefile              # make dev, make test, make migrate, etc.
├── frontend/
│   └── src/
│       ├── styles/           # Design tokens + component CSS
│       ├── components/ui/    # SignPanel, Badge, FlagDisplay, Button, etc.
│       ├── screens/          # LoginScreen, DailyChallengeScreen, ResultsScreen
│       ├── stores/           # Zustand (authStore, challengeStore)
│       ├── api/              # Axios client with JWT interceptors
│       └── types/            # TypeScript interfaces from backend serializers
├── design-system/            # Design tokens, inspiration, extraction tools
├── docs/
│   └── Design_System_Pipeline.md  # Design token pipeline docs
├── scripts/                  # Utility scripts
├── CLAUDE.md                 # Development context
└── README.md
```

## API Endpoints

```
POST /api/v1/auth/google/          OAuth login
POST /api/v1/auth/token/refresh/   JWT refresh
GET  /api/v1/daily/                Today's challenge
POST /api/v1/daily/answer/         Submit answer
GET  /api/v1/daily/history/        Past challenges (paginated)
GET  /api/v1/countries/            List all countries
GET  /api/v1/countries/{id}/       Country detail
```

## Author

**Adnan Shoukfeh** — [@adnan-shoukfeh](https://github.com/adnan-shoukfeh)
