# Development Context

**Project:** Globule — daily geography/flag challenge app
**Status:** MVP — Backend complete, frontend scaffolded (Login → Challenge → Results)

## Tech Stack

### Backend
- Python 3.11+ / Django 5.0+ / DRF / PostgreSQL / JWT auth / uv
- Custom User model (email-based login)
- Fat models, thin views, thin serializers

### Frontend (Web)
- Vite + React 18 + TypeScript / Radix UI (headless) + Custom CSS / Zustand / Axios
- Design system: Swiss motorway signage aesthetic (see `~/.claude/skills/flag-design/SKILL.md`)
- Overpass font, dark green palette, white borders, red/green badges
- yarn package manager

## Project Structure

```
backend/                        frontend/src/
├── config/       (settings)    ├── styles/        (design tokens, CSS)
├── users/        (User, OAuth) ├── components/ui/ (SignPanel, Badge, etc.)
├── flags/        (Challenge)   ├── screens/       (Login, Challenge, Results)
├── Makefile                    ├── stores/        (Zustand: auth, challenge)
└── .env                        ├── api/           (Axios client + endpoints)
                                ├── types/         (TS interfaces from serializers)
                                └── animations/    (framer-motion variants)
```

## Key Commands

```bash
# Backend (from backend/)
make dev              # runserver
make test             # run all tests
make check            # Django system check
make migrate          # apply migrations
make makemigrations   # create migrations

# Frontend (from frontend/)
yarn dev              # Vite dev server (port 5173, proxies /api to :8000)
yarn build            # tsc + vite build
yarn run check        # typecheck + lint
yarn run typecheck    # tsc --noEmit only
```

## Architecture Patterns

### Backend
- **Business logic in models** — views orchestrate, serializers validate/format only
- **Serializers by domain** — `user_serializers.py`, `country_serializers.py`, etc.
- **List vs Detail serializers** — minimal for lists, full for detail
- **Security** — never expose `correct_answer` before challenge completion
- **ViewSets** for CRUD (Country), **APIView** for custom logic (OAuth, answer submission)

### Frontend
- **CSS custom properties only** — never hardcode colors, use `var(--color-*)`
- **Component styles in separate CSS files** — `src/styles/` imported via `global.css`
- **Zustand stores** — `authStore` (login/logout/hydrate), `challengeStore` (load/submit)
- **Axios interceptors** — auto-attach JWT, transparent token refresh with mutex

## Key Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Auth | Frontend OAuth → backend JWT | SPA + mobile compatible |
| UI library | Radix UI + Custom CSS | Full visual control for motorway design system |
| Timezone | Fixed America/New_York | Same daily flag globally |
| Images | CDN URLs (flagcdn.com) | Zero cost, SVG→PNG fallback |
| Question system | Extensible enums + JSON `correct_answer` | New categories without migrations |
| Service layer | Not yet | Extract when models exceed ~500 lines |
| Default permissions | AllowAny (dev) | Individual views have correct permissions; switch to IsAuthenticated for production |
| CORS | django-cors-headers | `CORS_ALLOW_ALL_ORIGINS=True` in dev |

## API Endpoints

```
POST /api/v1/auth/google/         # OAuth login (AllowAny)
POST /api/v1/auth/token/refresh/  # JWT refresh (AllowAny)
GET  /api/v1/daily/               # Today's challenge (IsAuthenticated)
POST /api/v1/daily/answer/        # Submit answer (IsAuthenticated)
GET  /api/v1/daily/history/       # Past challenges (IsAuthenticated)
GET  /api/v1/countries/           # List countries (AllowAny)
GET  /api/v1/countries/{id}/      # Country detail (AllowAny)
```

## Before Committing

1. `make test` — 76 backend tests pass
2. `make check` — no Django errors
3. `yarn run check` — no TS errors, no lint errors
4. Migrations created if models changed
5. Commits follow `.gitmessage` format

## What NOT to Do

- Don't put business logic in views or serializers
- Don't expose answers in question serializers before submission
- Don't use django-allauth (we use custom OAuth)
- Don't hardcode colors in components (use CSS custom properties)
- Don't use any font other than Overpass
- Don't use light backgrounds — the app is night-drive green

## Documentation

- `CLAUDE.md` — this file (development context)
- `docs/ROADMAP.md` — project vision, future phases, deferred decisions
- `docs/design/road_sign.png` — visual reference for the design system
- Design system spec: `~/.claude/skills/flag-design/SKILL.md`
