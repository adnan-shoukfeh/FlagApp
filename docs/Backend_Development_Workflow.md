# Backend Development Workflow

**Project:** Flag Learning App - Backend  
**Last Updated:** October 31, 2025  
**Purpose:** Development workflow, design decisions, and common commands  
**Developer:** Adnan Shoukfeh

---

## Overview

This document captures the development workflow, key design decisions, and common commands for day-to-day backend development. Use this as your daily reference for development tasks.

**Related Documentation:**
- **Backend_Technical_Design.md** - Architecture, models, and patterns
- **Backend_PostgreSQL_Reference.md** - Database operations and queries

---

## Quick Command Reference

### Most Common Daily Commands

```bash
# Start development server
uv run python manage.py runserver

# Run all tests
uv run python manage.py test

# Create migrations after model changes
uv run python manage.py makemigrations

# Apply migrations
uv run python manage.py migrate

# Open Django shell
uv run python manage.py shell

# Create superuser (for admin access)
uv run python manage.py createsuperuser
```

---

## Table of Contents

1. [Design Decisions Log](#1-design-decisions-log)
2. [Daily Development Workflow](#2-daily-development-workflow)
3. [Django Commands](#3-django-commands)
4. [Testing Workflow](#4-testing-workflow)
5. [Git Workflow](#5-git-workflow)
6. [Common Development Tasks](#6-common-development-tasks)
7. [Troubleshooting](#7-troubleshooting)
8. [Code Quality Checklist](#8-code-quality-checklist)

---

## 1. Design Decisions Log

### Locked Decisions

These decisions are foundational and unlikely to change.

| Decision | Choice | Rationale | Date |
|----------|--------|-----------|------|
| **Backend Framework** | Django + DRF | Learning goal, rapid dev, batteries-included | Oct 30 |
| **Database** | PostgreSQL | Production-ready, JSON support, ACID | Oct 30 |
| **Package Manager** | uv | 10-100x faster than pip, modern tooling | Oct 30 |
| **Authentication** | Frontend token flow | Better UX, works for SPA + mobile | Oct 30 |
| **User Model** | Custom from day 1 | Django best practice (can't change later) | Oct 30 |
| **Business Logic** | Model methods (fat models) | Django pattern, fast MVP | Oct 30 |
| **Image Storage** | CDN URLs (flagcdn.com) | Zero cost, fast, reliable | Oct 30 |
| **Timezone** | America/New_York (fixed) | Same daily flag for all users globally | Oct 30 |
| **API Versioning** | /api/v1/ prefix | Future-proof, industry standard | Oct 30 |
| **Serializer Pattern** | Thin serializers | Data transformation only, logic in models | Oct 31 |

### Deferred Decisions

These will be decided when needed.

| Decision | Timeline | Notes |
|----------|----------|-------|
| **Service Layer** | Phase 2 | Extract when models exceed ~500 lines |
| **Image Self-Hosting** | Phase 2+ | Only if CDN becomes unreliable |
| **Rate Limiting** | Before Production | Use django-ratelimit or DRF throttling |
| **Caching** | Phase 2 | Redis for hot data (daily challenges, leaderboards) |
| **Background Tasks** | Phase 3 | Celery for email, data refresh, etc. |
| **Full-Text Search** | Phase 3 | PostgreSQL full-text or Elasticsearch |
| **API Documentation** | Before Production | drf-spectacular for OpenAPI/Swagger |

### Decision-Making Process

When making new architectural decisions:

1. **Document the decision** - Add to this log with rationale
2. **Consider reversibility** - How hard is it to undo?
3. **Favor Django conventions** - "Convention over configuration"
4. **Optimize for learning** - Choose options that teach Django/DRF patterns
5. **Keep it simple** - Defer complexity until proven necessary

---

## 2. Daily Development Workflow

### Standard Development Cycle

```bash
# ===== START OF DAY =====

# 1. Navigate to project
cd /Users/adnanshoukfeh/Documents/code_projects/Flag_Project/backend

# 2. Sync dependencies (if pyproject.toml changed)
uv sync

# 3. Apply any new migrations
uv run python manage.py migrate

# 4. Run tests to ensure everything works
uv run python manage.py test

# 5. Start development server
uv run python manage.py runserver
# Server runs at http://127.0.0.1:8000/

# ===== DURING DEVELOPMENT =====

# When you modify models:
uv run python manage.py makemigrations
uv run python manage.py migrate

# Test your changes:
uv run python manage.py test

# Check for issues:
uv run python manage.py check

# ===== END OF DAY =====

# Commit your work
git add .
git commit -m "feat: Descriptive commit message"
git push
```

### Before Committing Checklist

- [ ] Tests pass: `uv run python manage.py test`
- [ ] No Django errors: `uv run python manage.py check`
- [ ] Migrations created if models changed
- [ ] Code follows project patterns (fat models, thin views)
- [ ] No sensitive data (passwords, tokens) in code
- [ ] Commit message follows convention (see Git Workflow)

---

## 3. Django Commands

### Core Django Commands

```bash
# ===== SERVER =====

# Start development server
uv run python manage.py runserver

# Start on different port
uv run python manage.py runserver 8080

# Allow external connections (for testing on phone)
uv run python manage.py runserver 0.0.0.0:8000

# ===== DATABASE =====

# Create migrations
uv run python manage.py makemigrations

# Apply migrations
uv run python manage.py migrate

# Show migration status
uv run python manage.py showmigrations

# Show SQL for a migration (without running it)
uv run python manage.py sqlmigrate users 0001

# Rollback migration
uv run python manage.py migrate users 0001

# ===== APPS =====

# Create new app
uv run python manage.py startapp appname

# ===== USERS =====

# Create superuser for admin panel
uv run python manage.py createsuperuser

# Change user password
uv run python manage.py changepassword username

# ===== TESTING =====

# Run all tests
uv run python manage.py test

# Run specific app tests
uv run python manage.py test users

# Run specific test class
uv run python manage.py test users.tests.UserStatsModelTest

# Run specific test method
uv run python manage.py test users.tests.UserStatsModelTest.test_update_daily_streak

# Run tests in parallel (faster)
uv run python manage.py test --parallel

# Keep test database (faster repeated runs)
uv run python manage.py test --keepdb

# Verbose output
uv run python manage.py test --verbosity=2

# ===== SHELL =====

# Django shell (has access to all models)
uv run python manage.py shell

# Shell with IPython (if installed)
uv run python manage.py shell -i ipython

# ===== UTILITIES =====

# Check for problems
uv run python manage.py check

# Collect static files (for production)
uv run python manage.py collectstatic

# Clear database (use with caution!)
uv run python manage.py flush

# Load data from fixture
uv run python manage.py loaddata fixture.json

# Dump data to fixture
uv run python manage.py dumpdata users > users_fixture.json
```

### uv Package Management

```bash
# ===== INSTALLING PACKAGES =====

# Add package
uv add package-name

# Add specific version
uv add "django>=5.0,<6.0"

# Add dev dependency
uv add --dev pytest

# ===== MANAGING ENVIRONMENT =====

# Sync dependencies (after pulling changes)
uv sync

# Update all packages
uv sync --upgrade

# Remove package
uv remove package-name

# ===== INFORMATION =====

# List installed packages
uv pip list

# Show package info
uv pip show package-name

# ===== RUNNING COMMANDS =====

# Run any Python command
uv run python script.py

# Run Django command (alternative to manage.py)
uv run django-admin help
```

---

## 4. Testing Workflow

### Writing Tests

**Location:** `app_name/tests.py` or `app_name/tests/test_*.py`

**Pattern:**

```python
from django.test import TestCase
from users.models import User, UserStats

class UserStatsModelTest(TestCase):
    """Test UserStats model methods."""
    
    def setUp(self):
        """Run before each test method."""
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
    
    def tearDown(self):
        """Run after each test method (optional)."""
        pass
```

### Running Tests Effectively

```bash
# ===== BASIC TESTING =====

# Run all tests
uv run python manage.py test

# Run with coverage (if django-coverage installed)
uv run coverage run --source='.' manage.py test
uv run coverage report

# ===== SELECTIVE TESTING =====

# Test one app
uv run python manage.py test users

# Test one file
uv run python manage.py test users.tests.test_models

# Test one class
uv run python manage.py test users.tests.test_models.UserStatsModelTest

# Test one method
uv run python manage.py test users.tests.test_models.UserStatsModelTest.test_update_daily_streak

# ===== FASTER TESTING =====

# Run in parallel (use all CPU cores)
uv run python manage.py test --parallel

# Keep test database between runs
uv run python manage.py test --keepdb

# Both (fastest repeated testing)
uv run python manage.py test --parallel --keepdb

# ===== DEBUGGING TESTS =====

# Verbose output
uv run python manage.py test --verbosity=2

# Stop on first failure
uv run python manage.py test --failfast

# Run only failed tests from last run
uv run python manage.py test --failed
```

### Test Organization

```
app_name/
├── tests/
│   ├── __init__.py
│   ├── test_models.py      # Model tests
│   ├── test_serializers.py # Serializer tests
│   ├── test_views.py       # View/API tests
│   └── test_utils.py       # Utility function tests
```

### What to Test

**Always Test:**
- ✅ Model methods (business logic)
- ✅ Custom validation logic
- ✅ Database constraints
- ✅ Serializer validation
- ✅ API endpoints (input/output)

**Don't Test (Django already does):**
- ❌ Django ORM operations
- ❌ Built-in Django views
- ❌ Third-party package functionality

---

## 5. Git Workflow

### Commit Message Convention

```bash
# Format: <type>: <description>

# Types:
feat:     # New feature
fix:      # Bug fix
refactor: # Code restructuring (no behavior change)
test:     # Add/modify tests
docs:     # Documentation only
style:    # Formatting, missing semicolons, etc.
chore:    # Maintenance (dependencies, configs)

# Examples:
git commit -m "feat: Add user statistics tracking"
git commit -m "fix: Correct streak calculation for consecutive days"
git commit -m "refactor: Extract serializers to separate files"
git commit -m "test: Add tests for daily challenge selection"
git commit -m "docs: Update API endpoint documentation"
```

### Daily Git Workflow

```bash
# ===== STARTING WORK =====

# Pull latest changes
git pull origin main

# Create feature branch (optional, for bigger features)
git checkout -b feature/user-stats

# ===== DURING WORK =====

# Check what changed
git status

# See detailed changes
git diff

# Stage specific files
git add users/models.py users/serializers.py

# Or stage everything
git add .

# Commit with message
git commit -m "feat: Add user statistics model"

# ===== END OF WORK =====

# Push to remote
git push origin main

# Or push feature branch
git push origin feature/user-stats

# ===== USEFUL COMMANDS =====

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo changes to file
git checkout -- filename.py

# View commit history
git log --oneline

# Stash changes temporarily
git stash
git stash pop
```

---

## 6. Common Development Tasks

### Adding a New Model

```bash
# 1. Define model in app/models.py
# 2. Create migration
uv run python manage.py makemigrations

# 3. Review migration (optional but recommended)
uv run python manage.py sqlmigrate appname 0001

# 4. Apply migration
uv run python manage.py migrate

# 5. Register in admin (optional, for testing)
# Edit app/admin.py

# 6. Test in shell
uv run python manage.py shell
>>> from app.models import ModelName
>>> ModelName.objects.create(...)
```

### Adding a New API Endpoint

```bash
# 1. Create serializer in app/serializers/
# 2. Create view in app/views.py
# 3. Add URL pattern in app/urls.py or config/urls.py
# 4. Test endpoint
#    - Open http://127.0.0.1:8000/api/v1/endpoint/
#    - Or use curl/Postman

# 5. Write tests in app/tests/test_views.py
# 6. Run tests
uv run python manage.py test app.tests.test_views
```

### Loading Country Data (Future)

```bash
# When REST Countries data loading is implemented:

# Create management command
# backend/flags/management/commands/load_countries.py

# Run command
uv run python manage.py load_countries

# Verify
uv run python manage.py shell
>>> from flags.models import Country
>>> Country.objects.count()  # Should be 195
```

### Debugging in Django Shell

```python
# Start shell
# uv run python manage.py shell

# Import models
from users.models import User, UserStats
from flags.models import Country, DailyChallenge

# Get all users
User.objects.all()

# Get specific user
user = User.objects.get(email='test@example.com')

# Access related objects
user.stats
user.stats.current_streak

# Create test data
user = User.objects.create_user(
    username='testuser',
    email='test@example.com',
    password='test123'
)

# Test model methods
user.stats.update_daily_streak(True, date.today())
print(user.stats.current_streak)

# Raw SQL queries (for debugging)
from django.db import connection
connection.queries  # Shows all queries run

# Exit shell
exit()
```

---

## 7. Troubleshooting

### Common Issues & Solutions

#### Issue: Migrations not applying

```bash
# Problem: "No migrations to apply" but model changed

# Solution 1: Force detection
uv run python manage.py makemigrations --empty appname

# Solution 2: Check migration status
uv run python manage.py showmigrations

# Solution 3: Fake migration if schema already correct
uv run python manage.py migrate --fake appname migration_name
```

#### Issue: Test database errors

```bash
# Problem: "permission denied to create database"

# Solution: Grant CREATEDB to user (see PostgreSQL reference)
# Or run tests with existing database
uv run python manage.py test --keepdb
```

#### Issue: Import errors

```bash
# Problem: "ModuleNotFoundError: No module named 'app'"

# Solution 1: Check INSTALLED_APPS in settings.py
# Solution 2: Sync dependencies
uv sync

# Solution 3: Restart shell/server
```

#### Issue: Server won't start

```bash
# Problem: "Address already in use"

# Solution: Kill existing Django process
# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Or use different port:
uv run python manage.py runserver 8080
```

#### Issue: Static files not loading

```bash
# Problem: CSS/JS not loading in development

# Solution 1: Check STATIC_URL in settings.py
# Solution 2: Collect static files
uv run python manage.py collectstatic

# Solution 3: Run with --insecure (development only)
uv run python manage.py runserver --insecure
```

### Django Debug Toolbar (Optional)

For detailed debugging, consider installing django-debug-toolbar:

```bash
uv add django-debug-toolbar

# Add to INSTALLED_APPS and MIDDLEWARE in settings.py
# Shows SQL queries, template rendering, signals, etc.
```

---

## 8. Code Quality Checklist

### Before Committing Code

**Functionality:**
- [ ] Code works as expected
- [ ] Tests pass: `uv run python manage.py test`
- [ ] No Django errors: `uv run python manage.py check`
- [ ] Migrations created and applied

**Code Quality:**
- [ ] Follows "fat models, thin views" pattern
- [ ] Serializers contain no business logic
- [ ] Docstrings for complex methods
- [ ] No commented-out code (delete it, Git remembers)
- [ ] No print statements (use logging instead)

**Security:**
- [ ] No sensitive data (passwords, API keys) in code
- [ ] User input validated in serializers
- [ ] Proper permissions set on views
- [ ] No SQL injection risks (use ORM, not raw SQL)

**Django Conventions:**
- [ ] Model methods for business logic
- [ ] Serializers for data transformation
- [ ] Views for orchestration only
- [ ] Follow Django naming conventions

### Code Review Questions

Ask yourself:
1. **Could this be simpler?** - Favor readability over cleverness
2. **Is this testable?** - If hard to test, probably too complex
3. **Does this follow Django patterns?** - When in doubt, check Django docs
4. **Would I understand this in 6 months?** - Add comments for "why", not "what"

---

## Project File Structure Reference

```
Flag_Project/backend/
├── config/                   # Django project settings
│   ├── settings.py          # Main configuration
│   ├── urls.py              # Root URL routing
│   └── wsgi.py
│
├── users/                    # Users app
│   ├── migrations/
│   ├── serializers/
│   │   └── user_serializers.py
│   ├── tests/
│   │   └── test_models.py
│   ├── models.py            # User, UserStats
│   ├── views.py             # Auth views
│   └── admin.py
│
├── flags/                    # Flags app
│   ├── migrations/
│   ├── serializers/
│   │   ├── country_serializers.py
│   │   ├── challenge_serializers.py
│   │   └── question_serializers.py
│   ├── tests/
│   │   ├── test_models.py
│   │   ├── test_serializers.py
│   │   └── test_views.py
│   ├── models.py            # Country, Challenge, Question
│   ├── views.py             # API views
│   └── admin.py
│
├── manage.py                # Django management script
├── pyproject.toml           # Dependencies (uv)
├── uv.lock                  # Locked dependencies
└── .env                     # Environment variables (NOT in Git!)
```

---

## Environment Variables Reference

```bash
# .env file (create in backend/ directory)

# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://flaglearning_user:dev_password_2024@localhost:5432/flaglearning_dev

# OAuth (to be configured)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# Timezone
TZ=America/New_York
```

---

## Document Version

**Version:** 1.0  
**Date:** October 31, 2025  
**Extracted from:** Backend Technical Design v1.1

**Changelog:**
- **v1.0 (Oct 31, 2025):** Initial standalone workflow document. Extracted Design Decisions Log and Development Workflow from Backend Technical Design, significantly expanded common commands, added testing workflow, Git workflow, troubleshooting, and code quality checklist.

---

**End of Document**
