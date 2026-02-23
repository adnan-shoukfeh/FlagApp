# Globule — Roadmap

## Vision

Daily geography micro-learning (< 2 minutes/day). One flag, three attempts, streaks and stats. Cross-platform: web, iOS app, iOS widget.

## Current State — MVP

### Completed

- **Backend** — Django REST API, 7 endpoints, 76 tests, Google OAuth + JWT
- **Frontend scaffold** — Vite + React + TypeScript, design system, Login → Challenge → Results screens
- **Data** — 195 countries cached from REST Countries API, flag images via CDN
- **Design system** — Swiss motorway signage aesthetic implemented in CSS (see `~/.claude/skills/flag-design/SKILL.md`)

### Remaining for MVP Launch

- [ ] Visual polish and end-to-end testing
- [ ] Switch `DEFAULT_PERMISSION_CLASSES` to `IsAuthenticated` before production
- [ ] Add `http://localhost:5173` to Google Cloud Console authorized JS origins
- [ ] Production deployment (hosting TBD)

---

## Future Phases

### Phase 2: Enhanced Difficulty
- Three tiers (Easy/Medium/Hard) with day-of-week rotation
- Independent tier cycles — each tier shuffles separately
- `DifficultyTierState` model already exists in backend

### Phase 3: Quiz Mode
- Multiple question categories (capital, population, currency, language, area, etc.)
- Configurable quizzes: choose categories, count, difficulty, format
- `QuestionCategory` and `QuestionFormat` enums are extensible without migrations
- Uncomment `quiz_session` FK on Question model when ready

### Phase 4: Social & Gamification
- Achievement system, leaderboards, social sharing
- Streak milestones with badge-pop animations (design system ready)

### Phase 5: Mobile
- React Native app (shared Zustand stores + API layer)
- iOS WidgetKit widget (native Swift, flag emoji display)

---

## Deferred Decisions

| Decision | Trigger | Notes |
|----------|---------|-------|
| Service layer | Models > ~500 lines | Extract from fat models |
| Self-hosted images | CDN unreliable | ~2MB total, just download + update URLs |
| Rate limiting | Before production | django-ratelimit or DRF throttling |
| Caching | Phase 2 | Redis for daily challenges, leaderboards |
| Background tasks | Phase 3 | Celery for email, data refresh |
| API docs | Before production | drf-spectacular for OpenAPI |

---

## Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Backend | Django + DRF | Batteries-included, learning goal |
| Database | PostgreSQL | JSON support, production-ready |
| Auth | Custom OAuth (not django-allauth) | Frontend token flow for SPA + mobile |
| UI library | Radix UI + Custom CSS | Full visual control for motorway design |
| User model | Custom from day 1 | Django best practice (can't change later) |
| Business logic | Fat models | Django pattern, fast MVP |
| Timezone | Fixed America/New_York | Same daily flag globally |
| Images | CDN URLs (flagcdn.com) | Zero cost, SVG→PNG fallback |
| Package managers | uv (backend), yarn (frontend) | Fast, modern tooling |
