- # Development Context

  **Project:** Flag Learning App - Django REST API Backend
   **Status:** Phase 1 (MVP) - OAuth & Auth implemented **Purpose** This file provides coding standards, guidelines, and workflow patterns for AI assistants (and humans) working on this project. It ensures consistent code quality and keeps critical decisions in human hands.

  ## Essential Context

  ### Project Goal

  Geography learning app with daily flag challenges. Backend serves web (React), mobile (React Native), and iOS widget clients via RESTful API.

  ### Tech Stack

  - Python 3.11+
  - Django 5.0+ / DRF / PostgreSQL / JWT auth / uv package manager
  - Custom User model (email-based login)
  - Frontend OAuth token flow (NOT django-allauth)
  - React + MUI (web) / React Native + React Native Paper (mobile) / npm / Zustand

  ### Architecture Pattern

  **Fat Models, Thin Views:** Business logic in models, views orchestrate, serializers validate/format only.

  ## Project Structure
  
  ```
  backend/
  ├── config/          # Django settings, urls
  ├── users/           # User, UserStats, OAuth
  │   ├── serializers/
  │   ├── tests/
  │   └── views.py
  ├── flags/           # Country, DailyChallenge, Question
  │   ├── serializers/
  │   ├── tests/
  │   └── views.py
  ├── manage.py
  ├── pyproject.toml   # uv dependencies
  └── .env            # DATABASE_URL, SECRET_KEY, GOOGLE_CLIENT_ID
  ```

  ## Reference Documentation
  
  Detailed information in project docs:

  - **Backend_Technical_Design_Main.md** - Complete architecture, all models, serializers, auth flow
  - **Backend_Development_Workflow.md** - Daily commands, Git workflow, troubleshooting
  - **Backend_PostgreSQL_Reference.md** - Database operations, queries, maintenance
  - **North_Star_V1.md** - Complete project vision and requirements

  ## Core Patterns

  ### Serializer Organization

  Separate files by domain: `user_serializers.py`, `country_serializers.py`, etc.

  **Patterns:**

  - List vs Detail: Minimal fields for lists, full data for details
  - Input vs Output: Separate serializers for API requests vs responses
  - Security: Never expose `correct_answer` in question serializers
  - ModelSerializer for models, Serializer for input validation and custom responses

  ### Model Methods (Business Logic)

  ```python
  class UserStats(models.Model):
      def update_daily_streak(self, is_correct, guess_date):
          # All business logic here, not in views
  ```

  ### ViewSets vs APIViews

  - ViewSets: Standard CRUD (Country, DailyChallenge)
  - APIView: Custom logic (OAuth, answer submission)

  ## Key Decisions

  ### Authentication

  Frontend handles OAuth popup, sends Google ID token to backend. Backend verifies with Google, creates/gets user, returns JWT. Access tokens: 1hr, refresh tokens: 30 days with rotation.

  **Endpoints:**

  - `POST /api/v1/auth/google/` - OAuth login (AllowAny)
  - `POST /api/v1/auth/token/refresh/` - Token refresh (AllowAny)

  ### Database Design

  - User (1:1) UserStats
  - Country (1:Many) DailyChallenge
  - DailyChallenge (1:Many) Question
  - Question (1:Many) UserAnswer
  - JSON fields for flexibility: `category_stats`, `raw_api_response`, `correct_answer`

  ### Image Storage

  MVP uses CDN URLs (flagcdn.com, mainfacts.com). Can migrate to self-hosted in Phase 2+ by updating URL fields.

  ### Timezone

  Fixed `America/New_York` for all users. Same daily flag globally, resets midnight ET.

  ### Question System

  Extensible via enums: Add categories/formats to `QuestionCategory`/`QuestionFormat` choices without migrations. Flexible `correct_answer` JSON field supports any format.

  ## Development Workflow

  ### Daily Commands

  ```bash
  # Development
  uv run python manage.py runserver
  uv run python manage.py test
  uv run python manage.py makemigrations
  uv run python manage.py migrate
  
  # Database
  psql -U flaglearning_user -d flaglearning_dev -h localhost
  # Connection: postgresql://flaglearning_user:dev_password_2024@localhost:5432/flaglearning_dev
  ```

  ### Before Committing

  1. Tests pass: `uv run python manage.py test`
  2. No Django errors: `uv run python manage.py check`
  3. Migrations created if models changed
  4. Code follows fat models pattern
  5. Changes are reflected in documentation
  6. Commits follow the format found in `.gitmessage`

  ### Testing Strategy

  40 tests organized by component. Mock external services (Google OAuth). Fresh database per test via fixtures.

  ### Documentation Updates

  Update docs when changes affect them:

  - Example changes:
    - Models/serializers changed
    - New patterns/decisions
    - Database schema changed
    - Feature milestones reached
  - Include doc updates in same commit as code changes when possible
  - Always inform me of the full update to documents before making them

  ## Common Tasks

  ### Add Model Field

  1. Edit model, run `makemigrations`, `migrate`
  2. Update serializer if field should appear in API
  3. Add tests for new behavior

  ### Add API Endpoint

  1. Create serializer in `app/serializers/`
  2. Create view in `app/views.py`
  3. Add URL in `app/urls.py` or register ViewSet
  4. Write tests in `app/tests/test_views.py`

  ### Add Question Category

  1. Add to `QuestionCategory` enum (no migration needed)
  2. Create generator function
  3. Update `Question.validate_answer()` method

  ## Important Notes

  ### What NOT to Do

  - Don't put business logic in views or serializers
  - Don't modify custom User model after migrations
  - Don't expose answers in question serializers before submission
  - Don't use django-allauth (we use custom OAuth)

  ### Django Conventions

  - Custom User model set via `AUTH_USER_MODEL = 'users.User'` (must be set before first migration)
  - `USE_TZ = True` always (enables timezone awareness)
  - Migrations track schema changes automatically
  - Test database is separate, auto-cleaned after tests

  ### Service Layer Decision

  Starting without service layer for MVP. Extract to services in Phase 2 when:

  - Models exceed ~500 lines
  - Complex multi-model transactions needed
  - Logic needed outside models (Celery tasks)

  ## Environment Setup

  ```bash
  # .env file structure
  DATABASE_URL=postgresql://user:password@localhost:5432/dbname
  SECRET_KEY=django-insecure-GENERATE-THIS
  GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
  DEBUG=True
  ALLOWED_HOSTS=localhost,127.0.0.1
  TZ=America/New_York
  ```

  ## Working with Claude Code

  When implementing features:

  1. Review relevant sections in reference docs first
  2. Follow established patterns (fat models, thin serializers)
  3. Write tests alongside features
  4. Use `uv run` prefix for all Python commands
  5. Check existing serializers/views for patterns to follow