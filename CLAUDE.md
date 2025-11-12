# CLAUDE.md - Flag Learning App Development Guide

> **Purpose** — This file provides coding standards, guidelines, and workflow patterns for AI assistants (Claude Code, Cursor, etc.) working on this project. It ensures consistent code quality and keeps critical decisions in human hands.

---

## 0. Project Overview

Flag Learning App is a geography learning application with daily flag recognition challenges. Users get one flag per day to identify, with progress tracked across iOS app, website, and iOS widget.

**Tech Stack:**
- **Backend**: Python 3.11+, Django 5.0+, Django REST Framework, PostgreSQL
- **Frontend (Planned)**: React + MUI (web), React Native + React Native Paper (mobile)
- **State Management**: Zustand (shared between web/mobile)
- **Package Management**: uv (Python), npm (Node)
- **Authentication**: Custom OAuth + JWT (frontend token flow, NOT django-allauth)
- **Database**: PostgreSQL (dev & prod), timezone-aware (America/New_York)

**Current Status:** Phase 1 (MVP) - Day 3 Complete
- ✅ Models, migrations, database schema
- ✅ OAuth authentication (Google)
- ✅ JWT token generation & refresh
- ✅ Serializer architecture
- ✅ DRF setup with ViewSets
- ✅ 40 tests passing

**Golden Rule**: When unsure about implementation details or architectural decisions, ALWAYS consult the developer rather than making assumptions. Reference comprehensive documentation in `/docs/` for detailed design decisions.

---

## 1. Non-negotiable Golden Rules

| # | AI *may* do | AI *must NOT* do |
|---|-------------|------------------|
| G-0 | Ask developer for clarification when unsure about project-specific decisions or architecture. | ❌ Write code when uncertain about requirements, especially architectural changes. |
| G-1 | Generate code in `backend/` following Django patterns. Help write tests. | ❌ Edit existing tests to make them pass. Tests define behavior - code must conform. |
| G-2 | Add **`AIDEV-NOTE:` comments** near non-trivial code for context. Add **`AIDEV-TODO:`** for future tasks. | ❌ Delete or modify existing `AIDEV-` comments without developer instruction. |
| G-3 | Follow Ruff defaults (88 char lines, double quotes). Use Google-style docstrings. | ❌ Reformat code to different style or ignore linter configurations. |
| G-4 | **Keep code modular!** Files approaching ~500 lines should be refactored. Ask before changes >300 LOC or >3 files. | ❌ Create bloated files. Balance: Keep code readable, don't over-abstract. |
| G-5 | **Follow Django patterns**: Fat models (business logic), thin views (orchestration), thin serializers (validation/formatting). | ❌ Put business logic in views or serializers. |
| G-6 | **Check existing codebase** before implementing. Search for similar functionality, models, serializers. | ❌ Duplicate functionality or reinvent existing solutions. |
| G-7 | **Update `/docs/` after significant changes**: Backend_Technical_Design_Main.md, Backend_Development_Workflow.md, etc. | ❌ Leave documentation outdated after architectural or model changes. |
| G-8 | Use consistent libraries throughout. Follow project's choices (djangorestframework-simplejwt, google-auth, etc.). | ❌ Mix multiple libraries for same purpose or add dependencies without asking. |
| G-9 | Use **timezone-aware datetimes** via `django.utils.timezone.now()`. All timestamps in America/New_York. | ❌ Use naive datetimes or timezone.now().date() without considering timezone. |
| G-10 | **Write environment-aware code**: Support both dev and prod paths. Document environment-specific behavior with `AIDEV-NOTE:` comments. Update `/docs/` for critical env differences. | ❌ Hardcode dev-only or prod-only logic. Don't assume environment without checking `settings.DEBUG` or `settings.ENVIRONMENT`. |

---

## 2. Quick Command Reference

### Essential Django Commands (always use `uv run` prefix)
```bash
# Development server
uv run python manage.py runserver

# Database
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run python manage.py shell

# Testing
uv run python manage.py test                    # All tests
uv run python manage.py test users              # Specific app
uv run python manage.py test --parallel --keepdb  # Faster
uv run python manage.py test --verbosity=2      # Verbose

# Code Quality
uv run ruff check .                  # Lint
uv run ruff format .                 # Format
uv run python manage.py check        # Django system checks

# User Management
uv run python manage.py createsuperuser
```

### uv Package Management
```bash
uv add package-name           # Add dependency
uv add --dev package-name     # Add dev dependency
uv sync                       # Sync dependencies
uv pip list                   # List installed packages
```

### PostgreSQL (from project root or backend/)
```bash
psql -U flaglearning_user -d flaglearning_dev -h localhost
\dt                          # List tables
\d table_name               # Describe table
```

---

## 3. Coding Standards

### Python (Backend) - Follow Ruff Defaults

**Key Standards:**
- **Line length**: 88 characters (Ruff/Black default)
- **Quotes**: Double quotes for strings
- **Type hints**: Required for function signatures
- **Docstrings**: Google-style for public functions/classes
- **Imports**: `from __future__ import annotations` for forward references
- **Naming**: `snake_case` (functions/vars), `PascalCase` (classes), `SCREAMING_SNAKE` (constants)

**Anchor Comments:**
```python
# AIDEV-NOTE: This query is optimized for PostgreSQL JSON fields
# AIDEV-TODO: Add caching layer for daily challenge endpoint

# Regular comments don't need AIDEV- prefix
# Use these for explaining "what" the code does
```

**Error Handling Pattern:**
```python
from rest_framework.exceptions import ValidationError, NotFound

# Raise DRF exceptions, not Django's
def get_country_by_code(code: str) -> Country:
    """Get country by ISO code.
    
    Args:
        code: Three-letter ISO country code
        
    Returns:
        Country instance
        
    Raises:
        NotFound: If country doesn't exist
    """
    try:
        return Country.objects.get(code=code.upper())
    except Country.DoesNotExist:
        raise NotFound(f"Country with code '{code}' not found")
```

**Timezone-Aware Code:**
```python
from django.utils import timezone

# ✅ CORRECT - timezone aware
today = timezone.now().date()
challenge = DailyChallenge.objects.get(date=today)

# ❌ WRONG - naive datetime
from datetime import datetime
today = datetime.now().date()  # Don't use this!
```

### JavaScript/React (Frontend - Basic Standards)

**Key Standards:**
- **Framework**: React 18+ (web), React Native with Expo (mobile)
- **UI Libraries**: MUI (web), React Native Paper (mobile)
- **State**: Zustand (shared between platforms)
- **Style**: Functional components with hooks, 2-space indent
- **Naming**: camelCase (vars/functions), PascalCase (components)

**Note**: Detailed frontend standards will be added when frontend development begins.

---

## 4. Project Structure (Key Paths)

```
Flag_Project/
├── backend/
│   ├── config/              # Django project settings
│   │   ├── settings.py      # Main configuration
│   │   └── urls.py          # Root URL routing
│   ├── users/               # Users app
│   │   ├── models.py        # User, UserStats
│   │   ├── views.py         # GoogleLoginView
│   │   ├── serializers/     # User serializers
│   │   ├── tests/           # User tests
│   │   └── urls.py          # Auth endpoints
│   ├── flags/               # Flags app
│   │   ├── models.py        # Country, DailyChallenge, Question, UserAnswer
│   │   ├── views.py         # API ViewSets
│   │   ├── serializers/     # Country, Challenge, Question serializers
│   │   ├── tests/           # Flag tests
│   │   └── urls.py          # Flag endpoints
│   ├── manage.py
│   ├── pyproject.toml       # uv dependencies
│   └── .env                 # Environment variables (NOT in git!)
├── docs/                    # ⚠️ UPDATE AFTER SIGNIFICANT CHANGES
│   ├── Backend_Technical_Design_Main.md
│   ├── Backend_Development_Workflow.md
│   ├── Backend_PostgreSQL_Reference.md
│   └── North_Star_V1.md
├── frontend/                # (Future - React/React Native)
└── CLAUDE.md               # This file
```

---

## 5. Django Patterns (Critical)

### Fat Models, Thin Views, Thin Serializers

**Models** — Business logic lives here:
```python
class UserStats(models.Model):
    # ... fields ...
    
    def update_daily_streak(self, is_correct: bool, guess_date: date) -> None:
        """Update streak based on guess. Business logic in model."""
        if is_correct:
            if self.last_guess_date == guess_date - timedelta(days=1):
                self.current_streak += 1
            else:
                self.current_streak = 1
            self.longest_streak = max(self.longest_streak, self.current_streak)
            self.total_correct += 1
        else:
            self.current_streak = 0
        self.last_guess_date = guess_date
        self.save()
```

**Views** — Orchestration only:
```python
class SubmitGuessView(APIView):
    def post(self, request):
        # AIDEV-NOTE: View orchestrates, model handles business logic
        is_correct = question.validate_answer(request.data)
        request.user.stats.update_daily_streak(is_correct, timezone.now().date())
        return Response({"is_correct": is_correct})
```

**Serializers** — Validation and formatting only:
```python
# ✅ CORRECT - Just validation
class QuestionAnswerSerializer(serializers.Serializer):
    answer_data = serializers.JSONField()
    
    def validate_answer_data(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Must be an object")
        return value

# ❌ WRONG - Business logic in serializer
class QuestionAnswerSerializer(serializers.Serializer):
    def create(self, validated_data):
        # Don't put 50 lines of business logic here!
        # Move to model methods instead
```

### Serializer Organization

Separate serializers by use case:
- **List vs Detail**: `CountryListSerializer` (minimal fields) vs `CountryDetailSerializer` (full data)
- **Input vs Output**: `UserSerializer` (output with stats) vs `UserCreateSerializer` (input validation)
- **Security**: Never include sensitive data (correct_answer, passwords) in serializers unless intended

### Custom User Model

**Already implemented** — `users.User` extends `AbstractUser`. Email-based login.

**Critical**: Can never change to custom user after first migration. Already done correctly in this project.

---

## 6. Authentication Architecture

**Current Implementation**: Frontend OAuth token flow (NOT django-allauth)

**Flow:**
1. Frontend handles Google OAuth popup
2. Frontend sends ID token to `/api/v1/auth/google/`
3. Backend verifies with Google, creates/gets User
4. Backend returns JWT (access + refresh tokens)
5. Frontend stores JWT, includes in Authorization header

**Why not django-allauth**: 
- Server-side redirects break SPA/React Native UX
- Our approach works identically for web and mobile
- Better control and understanding

**Key Files:**
- `users/views.py` - `GoogleLoginView`
- `config/settings.py` - `SIMPLE_JWT` configuration

---

## 7. Testing Standards

### Backend (pytest/Django TestCase)

**Coverage Targets:**
- Model methods: ~95-100%
- Authentication: ~90%
- API endpoints: ~80%

**Golden Rule**: Tests define expected behavior. Fix code to match tests, never edit tests to pass.

```python
class UserStatsModelTest(TestCase):
    """Test UserStats model methods."""
    
    def setUp(self):
        """Runs before EACH test method."""
        self.user = User.objects.create_user(
            username='test',
            email='test@example.com',
            password='test123'
        )
        self.stats = UserStats.objects.create(user=self.user)
    
    def test_update_daily_streak_first_correct(self):
        """Test streak starts at 1 on first correct guess."""
        today = date.today()
        self.stats.update_daily_streak(is_correct=True, guess_date=today)
        self.assertEqual(self.stats.current_streak, 1)
```

**Run tests:**
```bash
uv run python manage.py test                    # All tests
uv run python manage.py test --parallel --keepdb  # Faster
uv run python manage.py test users.tests.test_models  # Specific
```

---

## 8. Environment-Aware Development

### Critical Principle

**All code must work in both development and production environments.** When writing code that differs between environments, explicitly check the environment and document the decision.

### Environment Detection

```python
# config/settings.py
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')  # 'development' or 'production'

# In your code
from django.conf import settings

if settings.DEBUG:
    # Development behavior
else:
    # Production behavior

# Or for more explicit checks
if settings.ENVIRONMENT == 'production':
    # Production-specific code
```

### Common Environment-Dependent Patterns

**1. Timeouts and Rate Limits:**
```python
# AIDEV-NOTE: Use shorter timeout in dev for faster feedback, longer in prod for reliability
from django.conf import settings

timeout = 5 if settings.DEBUG else 30
rate_limit = 100 if settings.DEBUG else 10
```

**2. Logging Levels:**
```python
# AIDEV-NOTE: Verbose logging in dev, minimal in prod
import logging

logger = logging.getLogger(__name__)
if settings.DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.WARNING)
```

**3. External API Behavior:**
```python
# AIDEV-NOTE: Use mock/sandbox APIs in dev, real APIs in prod
from django.conf import settings

if settings.DEBUG:
    google_client_id = settings.GOOGLE_CLIENT_ID_DEV
    verify_tokens = False  # Skip verification in dev tests
else:
    google_client_id = settings.GOOGLE_CLIENT_ID
    verify_tokens = True
```

**4. Database Queries:**
```python
# AIDEV-NOTE: Enable query logging in dev for debugging
from django.conf import settings
from django.db import connection

if settings.DEBUG:
    # Log slow queries in development
    connection.force_debug_cursor = True
```

**5. Email/Notifications:**
```python
# AIDEV-NOTE: Console backend in dev, real email in prod
# config/settings.py
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
```

### Documentation Requirements

When implementing environment-specific behavior, you MUST:

1. **Add `AIDEV-NOTE:` comment** explaining why behavior differs
2. **Document in `/docs/Backend_Technical_Design_Main.md`** if it's architectural
3. **Update `.env.example`** if new environment variables are needed
4. **Write tests for BOTH environments** if behavior differs significantly

**Example Documentation in Technical Design:**
```markdown
### Environment-Specific Configuration

**OAuth Token Verification:**
- **Development**: Tokens are verified against Google but with relaxed timeout (5s)
- **Production**: Strict verification with 30s timeout and retry logic
- **Rationale**: Dev environment prioritizes fast feedback for debugging
```

### Environment Variables

**Required in `.env`:**
```bash
# Environment control
DEBUG=True                    # Django debug mode
ENVIRONMENT=development       # 'development' or 'production'

# Database (different credentials per environment)
DATABASE_URL=postgresql://...

# OAuth (different client IDs per environment)
GOOGLE_CLIENT_ID=...         # Production ID
GOOGLE_CLIENT_ID_DEV=...     # Development ID (optional)
```

### Testing Environment-Specific Code

```python
from django.test import TestCase, override_settings

class EnvironmentAwareTest(TestCase):
    
    @override_settings(DEBUG=True)
    def test_dev_behavior(self):
        """Test development-specific behavior"""
        result = get_timeout()
        self.assertEqual(result, 5)
    
    @override_settings(DEBUG=False)
    def test_prod_behavior(self):
        """Test production-specific behavior"""
        result = get_timeout()
        self.assertEqual(result, 30)
```

### Common Pitfalls

❌ **Don't hardcode environment assumptions:**
```python
# BAD - assumes always development
timeout = 5
```

✅ **Do check environment explicitly:**
```python
# GOOD - environment-aware
from django.conf import settings
timeout = 5 if settings.DEBUG else 30
```

❌ **Don't skip documentation:**
```python
# BAD - no explanation why behavior differs
if settings.DEBUG:
    return quick_result()
else:
    return thorough_result()
```

✅ **Do document the reasoning:**
```python
# GOOD - documented decision
# AIDEV-NOTE: Dev uses cached result for speed, prod always fresh for accuracy
if settings.DEBUG:
    return get_cached_result()
else:
    return fetch_fresh_result()
```

---

## 9. API Design

### Versioning
All endpoints under `/api/v1/` prefix for future-proofing.

### Current Endpoints
```
Authentication:
POST /api/v1/auth/google/              # OAuth login (AllowAny)
POST /api/v1/auth/token/refresh/       # JWT refresh (AllowAny)

Countries:
GET  /api/v1/countries/                # List countries
GET  /api/v1/countries/{id}/           # Country detail

Future (Day 4+):
GET  /api/v1/daily/                    # Today's challenge
POST /api/v1/daily/answer/             # Submit guess
GET  /api/v1/stats/                    # User stats
```

### Response Format
```json
{
  "data": { ... },
  "meta": { "page": 1, "total": 195 },
  "errors": null
}
```

---

## 10. Documentation Updates

**Update `/docs/` after these changes:**

1. **Backend_Technical_Design_Main.md** — When:
   - Adding/modifying models
   - Changing authentication
   - Updating serializer architecture
   - Adding new API endpoints

2. **Backend_Development_Workflow.md** — When:
   - Adding new development commands
   - Changing deployment process
   - Updating design decisions
   - Adding troubleshooting steps

3. **Backend_PostgreSQL_Reference.md** — When:
   - Changing database schema
   - Adding complex queries
   - Updating backup procedures

**Note**: Documentation is in Markdown. Keep consistent with existing formatting.

---

## 11. Common Pitfalls

### Django-Specific
- ❌ Using naive datetimes — Always use `timezone.now()`
- ❌ Forgetting migrations after model changes — Run `makemigrations` + `migrate`
- ❌ Putting business logic in views/serializers — Keep in models
- ❌ Not running tests before committing — Tests must pass
- ❌ Editing `settings.py` without checking `.env` — Use environment variables

### Environment-Specific
- ❌ Hardcoding dev/prod behavior — Always check `settings.DEBUG` or `settings.ENVIRONMENT`
- ❌ Not documenting environment differences — Add `AIDEV-NOTE:` and update `/docs/`
- ❌ Same timeout/rate limits for dev and prod — Use environment-aware values
- ❌ Testing only in one environment — Test both dev and prod code paths
- ❌ Forgetting to update `.env.example` — Document new environment variables

### Project-Specific
- ❌ Adding django-allauth — We use custom OAuth frontend flow
- ❌ Making `AUTH_USER_MODEL` changes — Already set to `users.User`, can't change
- ❌ Hardcoding timezone — Always `America/New_York` via settings
- ❌ Creating duplicate serializers — Check `serializers/` directories first
- ❌ Not using `uv run` — All Python commands need this prefix

### Code Quality
- ❌ Files >500 lines — Refactor into smaller modules
- ❌ Duplicating functionality — Search codebase first
- ❌ Mixing libraries — Stick to project's chosen stack
- ❌ Removing `AIDEV-` comments — Only developer can remove these
- ❌ Over-abstracting — Keep code readable, not clever

---

## 12. Git Commit Standards

### Conventional Commits Format

Use structured commit messages for clear history and potential automation (changelog generation, semantic versioning).

**Format:**
```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat:` - New feature (e.g., "feat: Add daily challenge endpoint")
- `fix:` - Bug fix (e.g., "fix: Correct streak calculation for consecutive days")
- `refactor:` - Code restructuring without behavior change (e.g., "refactor: Extract serializers to separate files")
- `test:` - Add or modify tests (e.g., "test: Add tests for OAuth token refresh")
- `docs:` - Documentation only (e.g., "docs: Update API endpoint documentation")
- `style:` - Formatting, linting (e.g., "style: Run ruff format on flags app")
- `chore:` - Maintenance tasks (e.g., "chore: Update dependencies in pyproject.toml")
- `perf:` - Performance improvements (e.g., "perf: Add database index to Country.code")

**Examples:**
```bash
# Simple feature
feat: Add user statistics tracking

# Bug fix with context
fix: Correct timezone handling in daily challenge
- Was using naive datetime instead of timezone.now()
- Added AIDEV-NOTE comment explaining timezone decision

# Refactoring
refactor: Split country serializers by use case
- Created CountryListSerializer (minimal fields)
- Created CountryDetailSerializer (full data)
- Improves API response performance

# Documentation update
docs: Add environment-aware development section to CLAUDE.md
```

**Guidelines:**
- **Imperative mood**: "Add feature" not "Added feature" or "Adds feature"
- **Lowercase**: Type and description both lowercase
- **No period**: Don't end description with period
- **50 chars max** for description (first line)
- **72 chars max** for body lines
- **Reference issues** if applicable: "fix: Correct JWT refresh (#42)"

**What AI assistants should do:**
- Suggest commit messages following this format
- Include relevant context in body for non-trivial changes
- Reference documentation updates in commit message

**Git template:** See `.gitmessage` in project root for template

---

## 13. Environment Variables

**Location**: `backend/.env` (NOT in git, see `.env.example`)

**Required Variables:**
```bash
# Environment Control
DEBUG=True                              # Django debug mode (False in production)
ENVIRONMENT=development                 # 'development' or 'production'

# Database (different credentials per environment)
DATABASE_URL=postgresql://flaglearning_user:password@localhost:5432/flaglearning_dev

# Django
SECRET_KEY=<generate-with-django-secret-key-generator>
ALLOWED_HOSTS=localhost,127.0.0.1      # Add production domains in prod

# OAuth (use different client IDs per environment)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com

# Timezone
TZ=America/New_York
```

**Environment-Specific Best Practices:**

1. **Never commit `.env`** — Use `.env.example` as template
2. **Different credentials per environment** — Dev DB ≠ Prod DB
3. **Separate OAuth apps** — Use Google's test/dev projects for development
4. **Document all variables in `.env.example`** — Include comments explaining purpose
5. **Use environment detection** — Code should check `DEBUG` or `ENVIRONMENT` setting

**Generate SECRET_KEY:**
```bash
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 14. Key Files Reference

**Configuration:**
- `backend/config/settings.py` — Django settings, DRF config, JWT config
- `backend/config/urls.py` — Root URL routing
- `backend/.env` — Environment variables (gitignored)

**Core Models:**
- `backend/users/models.py` — User, UserStats
- `backend/flags/models.py` — Country, DailyChallenge, Question, UserAnswer

**Authentication:**
- `backend/users/views.py` — GoogleLoginView, JWT token handling
- `backend/users/urls.py` — Auth endpoints

**API:**
- `backend/flags/views.py` — CountryViewSet, DailyChallengeViewSet (future)
- `backend/flags/urls.py` — Flag endpoints
- `backend/flags/serializers/` — All serializers organized by domain

**Documentation:**
- `/docs/Backend_Technical_Design_Main.md` — Comprehensive architecture
- `/docs/Backend_Development_Workflow.md` — Development process
- `/docs/North_Star_V1.md` — Product vision and phases

---

## 15. AI Assistant Workflow

1. **Check guidance**: Read CLAUDE.md (this file) and relevant `/docs/` files
2. **Search codebase**: Before implementing, check if functionality exists
3. **Clarify**: Ask questions if requirements are unclear
4. **Plan**: Outline approach using Django patterns and project conventions
5. **Consider environments**: Will code behave differently in dev vs prod? Plan for both paths
6. **Execute**: For trivial changes, proceed. For complex tasks (>300 LOC, architectural), present plan first
7. **Track**: Use internal checklist for multi-step tasks
8. **Test**: Ensure tests pass before marking complete
9. **Document**: Add comments (especially `AIDEV-NOTE:` for env-specific code), update `/docs/` if needed
10. **Review**: Request developer review for significant changes
11. **Session boundaries**: Suggest fresh session if context is unclear or stale

---

## 16. Database Schema Quick Reference

**Current Tables:**
- `users_user` — Custom user model (email login)
- `users_userstats` — User statistics (1:1 with user)
- `flags_country` — Country data from REST Countries API
- `flags_dailychallenge` — Daily flag selection
- `flags_question` — Flexible question model (categories + formats)
- `flags_useranswer` — User answer history

**Key Relationships:**
```
User (1) ↔ (1) UserStats
User (1) → (Many) UserAnswer
Question (1) → (Many) UserAnswer
Country (1) → (Many) Question
Country (1) → (Many) DailyChallenge
DailyChallenge (1) → (Many) Question
```

See `docs/Backend_Technical_Design_Main.md` for detailed schema.

---

## Notes for AI Assistants

- **This project is for learning Django**: Developer is experienced backend engineer learning Django patterns
- **Explain Django idioms**: Don't skip Django-specific concepts, but skip basic programming
- **Reference comprehensive docs**: `/docs/` has detailed architecture decisions
- **Modular code**: Balance modularity with readability
- **Test-driven**: Tests define behavior, code must conform
- **Document as you go**: Update `/docs/` for significant changes

---

**Version**: 1.0  
**Last Updated**: November 11, 2025  
**Project Status**: Phase 1 MVP - Day 3 Complete (OAuth & Authentication)
