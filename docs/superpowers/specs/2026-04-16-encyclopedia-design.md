# Encyclopedia Feature Design

**Date:** 2026-04-16  
**Status:** Approved

## Context

Globule stores rich country data (45 fields) but surfaces only a small slice during the daily challenge. The encyclopedia gives users a way to browse and learn about any country at any time — deepening the geography-learning mission beyond the daily game loop.

---

## What We're Building

Two new screens behind a persistent top nav bar:

1. **Encyclopedia index** (`/encyclopedia`) — searchable list of all countries
2. **Country detail** (`/encyclopedia/:code`) — full country profile

---

## Navigation

A persistent **top nav bar** is added to `AppLayout`, replacing the current layout that just renders `<Outlet />`. Two tabs:

| Tab | Route | Active on |
|-----|-------|-----------|
| 🚩 Daily Challenge | `/daily` or `/results` | `/daily`, `/results` |
| 🌍 Encyclopedia | `/encyclopedia` | `/encyclopedia`, `/encyclopedia/:code` |

The active tab gets a white bottom-border underline and a slightly lighter green background (`--color-surface-2`). Both tabs are protected routes (require auth).

---

## Encyclopedia Index (`/encyclopedia`)

### Data loading
- On mount, fetch **all countries** from the existing `GET /api/v1/countries/` endpoint — returns `code, name, flag_emoji, flag_svg_url, population, capital` for each country (~195 records).
- Store the full list in component local state (no Zustand store needed — no cross-screen sharing).
- Filter client-side on the stored list as the user types. No additional backend calls.

### Layout
- **Search panel** — sign-panel styled input (`SignPanel` + custom input), placeholder "Search countries…"
- **Country list** — each row contains:
  - Flag thumbnail (36×24px container, 2px padding, `max-width/max-height: 100%`, `width/height: auto`)
  - Country name (bold)
  - Capital + formatted population (dimmed, right-aligned)
  - Chevron `›`
- Rows separated by `--color-border-dim` dividers
- Clicking a row navigates to `/encyclopedia/:code`

### Search behaviour
- Filters by country name (case-insensitive substring match)
- Instant — no debounce needed at this scale

---

## Country Detail (`/encyclopedia/:code`)

### Data loading
- `GET /api/v1/countries/{code}/` — the existing `CountryDetailSerializer` already exposes all needed fields. The `CountryViewSet` needs `lookup_field = 'code'` added so the URL uses the ISO alpha-3 code (e.g. `FRA`) instead of the database pk.

### Layout (top to bottom)

**Back link** — `‹ All countries`, navigates to `/encyclopedia`

**Flag display** — fixed-height container (180px tall, full width), `background: var(--color-surface-1)`, 12px padding on all four sides. Image uses `max-width: 100%; max-height: 100%; width: auto; height: auto;` — never stretches, always centered, works for any aspect ratio including Nepal's pennon shape.

**Country header** — large name (`1.8rem`, `font-weight: 800`) + ISO code subtitle below (`FRA`), centered. No region — there is no region field on the model.

**Sign panels** (each a `SignPanel`-styled bordered box):

| Panel | Fields | Display |
|-------|--------|---------|
| Geography | capital, largest_city, area_km2, highest_point | DistanceRow per field |
| People | population, median_age, life_expectancy, fertility_rate | DistanceRow per field |
| Economy | gdp_ppp_per_capita, currencies | DistanceRow per field; currency shown as `Euro (€)` |
| Languages | languages (JSON array) | One plain list-row per language, dash bullet, divider between rows |
| Religions | religions (JSON array) | One plain list-row per religion, dash bullet, divider between rows |

Fields that are `null` in the database are omitted from the panel (no empty rows). If an entire panel has no data, the panel is omitted.

---

## Backend Changes

### `CountryViewSet` (`backend/flags/views.py`)
Add `lookup_field = 'code'` so `GET /api/v1/countries/{code}/` works with ISO codes.

### `CountryDetailSerializer` (`backend/flags/serializers/country_serializers.py`)
No changes — already exposes all fields via `fields = "__all__"`.

### URL conf (`backend/flags/urls.py`)
No changes — the router already generates `{lookup}/` from the ViewSet.

---

## Frontend Changes

### New files
| File | Purpose |
|------|---------|
| `src/screens/EncyclopediaScreen.tsx` | Index page — country list + search |
| `src/screens/CountryDetailScreen.tsx` | Detail page — full country profile |
| `src/api/encyclopedia.ts` | `fetchCountries()` and `fetchCountryDetail(code)` |
| `src/types/encyclopedia.ts` | `CountryListItem`, `CountryDetail` TS interfaces |
| `src/components/ui/NavBar.tsx` | Top nav bar component |
| `src/styles/nav-bar.css` | Nav bar styles |
| `src/styles/encyclopedia.css` | Shared styles for index + detail screens |

### Modified files
| File | Change |
|------|--------|
| `src/App.tsx` | Add `/encyclopedia` and `/encyclopedia/:code` routes |
| `src/App.tsx` | Wrap layout in `NavBar` (replaces bare `<Outlet />` in AppLayout or adds nav above it) |
| `src/styles/global.css` | Import `nav-bar.css`, `encyclopedia.css` |

### Flag display
The existing `FlagDisplay` component enforces a `3:2` aspect ratio (padding-top trick). For the encyclopedia we need ratio-agnostic behaviour. Two options:
- **Preferred:** add a `contained` prop to `FlagDisplay` that switches to the fixed-height container + padding approach.
- The challenge/results screens continue using the existing 3:2 mode unchanged.

---

## Verification

1. `make test` — all 76 backend tests pass
2. `make check` — no Django system check errors  
3. Navigate to `/encyclopedia` — list loads, all ~195 countries visible
4. Type in search box — list filters instantly, no network requests
5. Click a country — navigates to `/encyclopedia/:code`, all panels render
6. Test France (wide flag), Switzerland (square), Nepal (pennon) — all display correctly inside the flag zone with equal padding on all sides, no stretching
7. Test a country with null fields (e.g. a country missing `highest_point`) — row is omitted, no blank entries
8. `yarn run check` — no TS errors, no lint errors
9. Top nav active state correct on all routes
