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

## Quick Start

### Prerequisites

- Python 3.11+, PostgreSQL 14+, [uv](https://github.com/astral-sh/uv), Node.js 18+, yarn

### Backend

```bash
cd backend
cp .env.example .env          # Configure DATABASE_URL, SECRET_KEY, GOOGLE_CLIENT_ID
uv sync                       # Install dependencies
make migrate                  # Apply migrations
uv run python manage.py load_countries  # Load 195 countries
make dev                      # Start server at :8000
```

### Frontend

```bash
cd frontend
cp .env.example .env          # Set VITE_GOOGLE_CLIENT_ID
yarn install
yarn dev                      # Start at :5173 (proxies /api to :8000)
```

### Verify

```bash
make test                     # 76 backend tests
yarn run check                # TypeScript + ESLint
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
├── docs/
│   ├── ROADMAP.md            # Vision, phases, key decisions
│   └── design/road_sign.png  # Visual design reference
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
