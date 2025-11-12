# Flag Learning App - Backend

Django + Django REST Framework backend for the Flag Learning App.

## 📚 Development Guidelines

**Before coding, read the project guidelines:**
- **[`../CLAUDE.md`](../CLAUDE.md)** - Coding standards, Django patterns, AI assistant guidelines
- **[`../docs/Backend_Technical_Design_Main.md`](../docs/Backend_Technical_Design_Main.md)** - Complete architecture
- **[`../docs/Backend_Development_Workflow.md`](../docs/Backend_Development_Workflow.md)** - Daily workflow

## 🚀 Quick Start

```bash
# From this directory (backend/)

# Run development server
uv run python manage.py runserver

# Run tests
uv run python manage.py test

# Create migrations
uv run python manage.py makemigrations
uv run python manage.py migrate

# Django shell
uv run python manage.py shell
```

## 📁 Project Structure

```
backend/
├── config/              # Django settings
├── users/               # User & authentication
├── flags/               # Flags, challenges, questions
├── manage.py
├── pyproject.toml       # Dependencies (uv)
└── .env                 # Environment variables (gitignored)
```

## ⚙️ Environment Setup

1. Copy `.env.example` to `.env`
2. Update DATABASE_URL and GOOGLE_CLIENT_ID
3. Run migrations: `uv run python manage.py migrate`
4. Create superuser: `uv run python manage.py createsuperuser`

## 🧪 Testing

```bash
# All tests
uv run python manage.py test

# Fast (parallel + keep DB)
uv run python manage.py test --parallel --keepdb

# Specific app
uv run python manage.py test users
uv run python manage.py test flags

# Verbose
uv run python manage.py test --verbosity=2
```

## 📊 Current Status

**Phase 1 (MVP) - Day 3 Complete:**
- ✅ Models, migrations, database schema
- ✅ OAuth authentication (Google)
- ✅ JWT token generation & refresh
- ✅ Serializer architecture
- ✅ DRF setup with ViewSets
- ✅ 40 tests passing

**Next Steps:**
- Day 4: Daily challenge endpoint
- Day 5: User stats endpoint
- Day 6: Testing & refinement

## 🔗 Key Documentation

All comprehensive documentation lives in `/docs/`:
- [Technical Design](../docs/Backend_Technical_Design_Main.md)
- [Development Workflow](../docs/Backend_Development_Workflow.md)
- [PostgreSQL Reference](../docs/Backend_PostgreSQL_Reference.md)
- [North Star Vision](../docs/North_Star_V1.md)

## 🤖 For AI Assistants

If you're an AI coding assistant (Claude Code, Cursor, etc.):
1. **Read [`../CLAUDE.md`](../CLAUDE.md) first** - Contains all coding standards and guidelines
2. Follow Django patterns: Fat models, thin views, thin serializers
3. Use `uv run` prefix for all Python commands
4. Update `/docs/` after significant changes
5. Add `AIDEV-NOTE:` comments for environment-specific code
6. Use conventional commit format: `<type>: <description>` (see CLAUDE.md section 12)