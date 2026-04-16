# Globule — Frontend

Vite + React 18 + TypeScript frontend for Globule.

## Quick Start

```bash
# From this directory (frontend/)

cp .env.example .env          # Set VITE_GOOGLE_CLIENT_ID
yarn install
yarn dev                      # Start at :5173 (proxies /api to :8000)
```

## Key Commands

```bash
yarn dev              # Vite dev server (port 5173, proxies /api to :8000)
yarn build            # tsc + vite build
yarn run check        # typecheck + lint
yarn run typecheck    # tsc --noEmit only
```

## Project Structure

```
src/
├── styles/           # Design tokens (CSS custom properties) + component CSS
├── components/ui/    # SignPanel, Badge, FlagDisplay, Button, Wordmark, etc.
├── screens/          # LoginScreen, DailyChallengeScreen, ResultsScreen
├── stores/           # Zustand: authStore, challengeStore
├── api/              # Axios client (JWT interceptors + refresh mutex), endpoints
├── types/            # TypeScript interfaces mirroring backend serializers
└── animations/       # Framer Motion variants
```

## Environment Variables

| Variable | Description |
|---|---|
| `VITE_API_BASE_URL` | API base path — defaults to `/api/v1` (Vite proxy in dev) |
| `VITE_GOOGLE_CLIENT_ID` | Google OAuth client ID |

## Design System

Swiss motorway signage aesthetic — Overpass font, dark green palette, white borders.
All colors via CSS custom properties (`var(--color-*)`). Never hardcode colors.
See `~/.claude/skills/flag-design/SKILL.md` for the full design spec.

## Architecture

- **Zustand stores** — `authStore` (login/logout/hydrate), `challengeStore` (load/submit)
- **Axios interceptors** — auto-attach JWT, transparent token refresh with mutex to prevent race conditions
- **Radix UI** (headless) + custom CSS — full visual control for motorway design system
