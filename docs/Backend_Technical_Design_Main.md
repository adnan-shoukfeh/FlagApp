# Backend Technical Design Document

**Project:** Flag Learning App - Backend  
**Last Updated:** November 11, 2025 (OAuth & Authentication Complete)  
**Status:** Development - Phase 1 (MVP) - Day 3 Complete  
**Developer:** Adnan Shoukfeh

---

## Executive Summary

This document captures all backend architecture decisions, database design, and implementation patterns for the Flag Learning App. It serves as the authoritative reference for:
- Technology stack and rationale
- Database schema and relationships  
- Django configuration and patterns
- Authentication architecture
- Data models and business logic
- Serializer architecture and patterns
- Testing strategy
- API design

**Related Documentation:**
- **Backend_PostgreSQL_Reference.md** - PostgreSQL setup, commands, and operational queries
- **Backend_Development_Workflow.md** - Development workflow, design decisions, common commands

**Key Design Principles:**
- Django's "fat models, thin views" pattern
- Custom User model from day 1
- Frontend OAuth token flow (not django-allauth)
- Database-cached country data (eager loading)
- Timezone-aware with fixed ET timezone
- API versioning from day 1

**Current Status (Day 3 Complete):**
- ✅ Models, migrations, and database schema
- ✅ Serializer architecture implemented
- ✅ DRF setup with ViewSets and routing
- ✅ OAuth authentication system functional
- ✅ JWT token generation and refresh
- ✅ 40 tests passing (organized test suite)
- 🔄 Next: Daily challenge endpoint implementation

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Technology Stack](#2-technology-stack)
3. [Database Design](#3-database-design)
4. [Django Configuration](#4-django-configuration)
5. [Authentication System](#5-authentication-system)
6. [Data Models](#6-data-models)
7. [Serializer Architecture](#7-serializer-architecture)
8. [Business Logic Patterns](#8-business-logic-patterns)
9. [Testing Strategy](#9-testing-strategy)
10. [API Design](#10-api-design)
11. [Future Architecture](#11-future-architecture)

---

## 1. Architecture Overview

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   CLIENT LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  React Web   │  │ React Native │  │ iOS Widget   │   │
│  │    (MUI)     │  │   (Paper)    │  │ (WidgetKit)  │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│         │                  │                  │         │
│         └──────────────────┴──────────────────┘         │
│                   JWT Token Authentication              │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│              DJANGO REST FRAMEWORK API                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Views (Thin Orchestration)                      │   │
│  │  ↕                                               │   │
│  │  Serializers (Validation & Formatting)           │   │
│  │  ↕                                               │   │
│  │  Models (Business Logic)                         │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                  POSTGRESQL DATABASE                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ users_user   │  │ flags_       │  │  External    │   │
│  │ users_       │  │ country      │  │  Services    │   │
│  │ userstats    │  │ daily_       │  │  - REST      │   │
│  │              │  │ challenge    │  │  Countries   │   │
│  │              │  │ question     │  │  API         │   │
│  │              │  │ useranswer   │  │  (cached)    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Design Philosophy

**Django Patterns for MVP:**

| Layer | Responsibility | Pattern |
|-------|---------------|---------|
| **Views** | HTTP handling, orchestration | Thin - call model methods |
| **Serializers** | Validation & formatting | Thin - no business logic |
| **Models** | Business logic & domain rules | Fat - methods for behavior |
| **Services** | Complex multi-model logic | Not yet - Phase 2+ |

**Why This Works:**
- ✅ Django convention (familiar to developers)
- ✅ Rapid MVP development (less boilerplate)
- ✅ Testable (model methods isolated from HTTP)
- ✅ Easy to refactor to service layer later

---

## 2. Technology Stack

### Core Backend

| Component | Choice | Version | Rationale |
|-----------|--------|---------|-----------|
| **Language** | Python | 3.11+ | Modern features, type hints, managed via pyenv |
| **Framework** | Django | 5.0+ | Batteries included, ORM, admin, migrations |
| **API** | Django REST Framework | 3.14+ | Industry standard, powerful serializers |
| **Database** | PostgreSQL | 14+ | Production-ready, JSON support, ACID compliant |
| **Package Manager** | uv | Latest | 10-100x faster than pip, from Astral (ruff team) |

### Authentication & Security

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **JWT** | djangorestframework-simplejwt | Simple, well-maintained, DRF compatible |
| **OAuth** | google-auth | Official Google library, token verification |
| **Password Hashing** | PBKDF2 (Django default) | Secure, configurable iterations |

### Data & External Services

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Country Data** | REST Countries API | Free, comprehensive, 195 countries |
| **Images** | flagcdn.com & mainfacts.com | CDN URLs (MVP), reliable, zero cost |
| **Caching** | Database eager loading | Simple, 195 countries = tiny dataset |

### Dependencies

```toml
# pyproject.toml
[project]
dependencies = [
    "django>=5.0",
    "djangorestframework>=3.14",
    "djangorestframework-simplejwt>=5.3",
    "psycopg2-binary>=2.9",
    "python-dotenv>=1.0",
    "google-auth>=2.23",
]
```

---

## 3. Database Design

### Schema Overview

```
users APP:
┌─────────────────────────────────────┐
│ users_user                          │
│ ├─ id (PK)                          │
│ ├─ username                         │
│ ├─ email (unique, login)            │
│ ├─ password (hashed)                │
│ └─ [AbstractUser fields]            │
└─────────────────────────────────────┘
           │ 1:1
           ▼
┌─────────────────────────────────────┐
│ users_userstats                     │
│ ├─ id (PK)                          │
│ ├─ user_id (FK, OneToOne)           │
│ ├─ total_correct                    │
│ ├─ current_streak                   │
│ ├─ longest_streak                   │
│ ├─ last_guess_date                  │
│ ├─ incorrect_countries (JSON)       │
│ └─ category_stats (JSON) [Phase 3]  │
└─────────────────────────────────────┘

flags APP:
┌────────────────────────────────────────┐
│ flags_country                          │
│ ├─ id (PK)                             │
│ ├─ code (unique, indexed)              │
│ ├─ name (indexed)                      │
│ ├─ flag_emoji, flag_svg_url            │
│ ├─ flag_png_url, flag_alt_text         │
│ ├─ coat_of_arms_svg_url (nullable)     │
│ ├─ coat_of_arms_png_url (nullable)     │
│ ├─ population, capital, largest_city   │
│ ├─ languages, religions, currencies    │
│ ├─ lat/lng, area, economic data        │
│ ├─ difficulty_tier (nullable) [Phase 2]│
│ └─ raw_api_response (JSON)             │
└────────────────────────────────────────┘
           │
           │ FK
           ▼
┌────────────────────────────────────────┐
│ flags_dailychallenge                   │
│ ├─ id (PK)                             │
│ ├─ date (unique, indexed)              │
│ ├─ country_id (FK → country)           │
│ ├─ difficulty_tier [Phase 2]           │
│ └─ selection_algorithm_version         │
└────────────────────────────────────────┘
           │
           │ 1:Many
           ▼
┌────────────────────────────────────────┐
│ flags_question                         │
│ ├─ id (PK)                             │
│ ├─ category (indexed)                  │
│ ├─ format (indexed)                    │
│ ├─ country_id (FK → country)           │
│ ├─ question_text                       │
│ ├─ correct_answer (JSON)               │
│ ├─ metadata (JSON)                     │
│ └─ daily_challenge_id (FK, nullable)   │
└────────────────────────────────────────┘
           │
           │ 1:Many
           ▼
┌────────────────────────────────────────┐
│ flags_useranswer                       │
│ ├─ id (PK)                             │
│ ├─ user_id (FK → user)                 │
│ ├─ question_id (FK → question)         │
│ ├─ answer_data (JSON)                  │
│ ├─ is_correct                          │
│ ├─ explanation                         │
│ ├─ attempt_number (1-3)                │
│ ├─ time_taken_seconds (nullable)       │
│ └─ answered_at                         │
└────────────────────────────────────────┘
```

### Key Relationships

```
User (1) ↔↔ (1) UserStats
User (1) → (Many) UserAnswer
Question (1) → (Many) UserAnswer
Country (1) → (Many) Question
Country (1) → (Many) DailyChallenge
DailyChallenge (1) → (Many) Question
```

### Index Strategy

**Primary Indexes (Auto-created):**
- All `id` primary key fields
- All ForeignKey fields

**Custom Indexes:**

```python
# Country
indexes = [
    models.Index(fields=['code']),   # Encyclopedia search
    models.Index(fields=['name']),   # User search
    models.Index(fields=['difficulty_tier']),  # Phase 2
]

# DailyChallenge
indexes = [
    models.Index(fields=['date']),   # Daily lookup
]

# Question
indexes = [
    models.Index(fields=['category', 'format']),  # Quiz filtering
    models.Index(fields=['country']),
    models.Index(fields=['daily_challenge']),
]

# UserAnswer
indexes = [
    models.Index(fields=['user', 'question']),
    models.Index(fields=['user', 'is_correct']),  # Stats queries
]
```

---

## 4. Django Configuration

### Project Structure

```
backend/
├── config/                 # Django project settings
│   ├── __init__.py
│   ├── settings.py        # Main configuration
│   ├── urls.py            # Root URL routing
│   ├── asgi.py
│   └── wsgi.py
├── users/                 # Users app
│   ├── migrations/
│   ├── serializers/
│   │   └── user_serializers.py
│   ├── tests/
│   │   ├── test_auth.py
│   │   └── test_models.py
│   ├── models.py          # User, UserStats
│   ├── views.py           # GoogleLoginView
│   ├── urls.py            # Auth URLs
│   └── admin.py
├── flags/                 # Flags app
│   ├── migrations/
│   ├── serializers/
│   │   ├── country_serializers.py
│   │   ├── challenge_serializers.py
│   │   └── question_serializers.py
│   ├── tests/
│   │   ├── test_models.py
│   │   └── test_serializers.py
│   ├── models.py          # Country, Challenge, Question
│   ├── views.py           # API views
│   ├── urls.py            # Flag URLs
│   └── admin.py
├── manage.py
├── pyproject.toml         # uv dependencies
├── uv.lock
└── .env                   # Environment variables (NOT in git!)
```

### Environment Variables (.env)

```bash
# Database
DATABASE_URL=postgresql://flaglearning_user:dev_password_2024@localhost:5432/flaglearning_dev

# Django
DEBUG=True
SECRET_KEY=django-insecure-GENERATE-WITH-get_random_secret_key
ALLOWED_HOSTS=localhost,127.0.0.1

# OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com

# Timezone
TZ=America/New_York
```

**Generate SECRET_KEY:**
```bash
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Key Settings (config/settings.py)

```python
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# === SECURITY ===
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# === CUSTOM USER MODEL ===
# CRITICAL: Set before first migration!
AUTH_USER_MODEL = 'users.User'

# === APPS ===
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    # Our apps
    'users',
    'flags',
]

# === DATABASE ===
# MVP: Manual parsing (Phase 2: use dj-database-url)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_URL').split('/')[-1],
        'USER': os.getenv('DATABASE_URL').split('@')[0].split(':')[-2].split('//')[-1],
        'PASSWORD': os.getenv('DATABASE_URL').split('@')[0].split(':')[-1],
        'HOST': os.getenv('DATABASE_URL').split('@')[1].split(':')[0],
        'PORT': os.getenv('DATABASE_URL').split('@')[1].split(':')[1].split('/')[0],
    }
}

# === TIMEZONE ===
TIME_ZONE = 'America/New_York'  # Fixed timezone for all users
USE_TZ = True  # ALWAYS True! Enables timezone-aware datetimes

# === REST FRAMEWORK ===
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Secure by default
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# === JWT ===
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),     # Short-lived
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),   # Long-lived
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# === OAUTH ===
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
```

**Key Configuration Rationale:**

| Setting | Value | Why |
|---------|-------|-----|
| `AUTH_USER_MODEL` | `'users.User'` | Custom user from day 1 (can't change later) |
| `USE_TZ` | `True` | Prevents timezone bugs |
| `TIME_ZONE` | `'America/New_York'` | All users see same daily flag |
| `DEFAULT_PERMISSION_CLASSES` | `IsAuthenticated` | Secure by default |
| `ACCESS_TOKEN_LIFETIME` | 1 hour | Security (short-lived) |
| `REFRESH_TOKEN_LIFETIME` | 30 days | Convenience |
| `ROTATE_REFRESH_TOKENS` | `True` | Enhanced security - new refresh on each use |
| `BLACKLIST_AFTER_ROTATION` | `True` | Old refresh tokens become invalid |

---

## 5. Authentication System

**Status:** ✅ **IMPLEMENTED** (Day 3 Complete)

### Architecture: Frontend Token Flow

**Why NOT django-allauth:**
- ❌ Server-side redirects (bad SPA/mobile UX)
- ❌ Breaks React Router state
- ❌ Complex React Native integration

**Our Approach:**
- ✅ Frontend handles OAuth popup
- ✅ Backend verifies token & issues JWT
- ✅ Works identically web/mobile
- ✅ Better UX (no page redirects)

### Authentication Flow

```
1. User clicks "Login with Google"
   └─> Google JS SDK opens popup

2. User authenticates with Google
   └─> Google returns ID token to frontend

3. Frontend sends token to backend
   POST /api/v1/auth/google/
   {"id_token": "..."}

4. Backend:
   - Verifies token with Google
   - Creates/gets User in database
   - Generates JWT tokens
   - Returns tokens to frontend

5. Frontend:
   - Stores JWT in localStorage
   - Includes Bearer token in all requests
   - Refreshes when access token expires
```

### Implementation

**Backend View (users/views.py):**

```python
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]  # Public endpoint
    
    def post(self, request):
        token = request.data.get('id_token')
        
        try:
            # Verify with Google
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            
            # Create/get user
            user, created = User.objects.get_or_create(
                email=idinfo['email'],
                defaults={'username': idinfo['email'].split('@')[0]}
            )
            
            # Generate JWT
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': {'id': user.id, 'email': user.email}
            })
            
        except ValueError:
            return Response({'error': 'Invalid token'}, status=400)
```

**URL Routing (users/urls.py):**

```python
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import GoogleLoginView

urlpatterns = [
    path('auth/google/', GoogleLoginView.as_view(), name='google-login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
```

**Root URL Config (config/urls.py):**

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('users.urls')),   # Auth endpoints
    path('api/v1/', include('flags.urls')),   # App endpoints
]
```

### Available Endpoints

```
Authentication:
POST /api/v1/auth/google/             # OAuth login
POST /api/v1/auth/token/refresh/      # Refresh JWT token

Protected Resources:
GET  /api/v1/countries/               # List countries
GET  /api/v1/countries/{id}/          # Country detail
GET  /api/v1/test/                    # Test endpoint
```

### Frontend Usage (Future Implementation)

```javascript
// React
import { GoogleLogin } from '@react-oauth/google';

function LoginButton() {
  const handleSuccess = async (response) => {
    const { data } = await axios.post('/api/v1/auth/google/', {
      id_token: response.credential
    });
    
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    navigate('/daily');
  };
  
  return <GoogleLogin onSuccess={handleSuccess} />;
}
```

**Axios Interceptor (Auto-add JWT):**

```javascript
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto-refresh on 401
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true;
      const { data } = await axios.post('/api/v1/auth/token/refresh/', {
        refresh: localStorage.getItem('refresh_token')
      });
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      return axios(error.config);
    }
    return Promise.reject(error);
  }
);
```

### Security Features

**Token Rotation:**
- Every token refresh generates NEW refresh token
- Old refresh token is blacklisted
- Prevents token replay attacks

**Token Blacklist:**
- Tracks all issued refresh tokens
- Can revoke tokens (logout all devices)
- Automatic cleanup of expired tokens

**Short-Lived Access Tokens:**
- 1 hour expiration limits stolen token damage
- Frontend auto-refreshes transparently
- User never notices expiration

### Testing OAuth

**Generate Test Tokens:**
```bash
uv run python manage.py shell
```

```python
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken

user = User.objects.create_user(username='test', email='test@example.com')
refresh = RefreshToken.for_user(user)

print(f"Access: {refresh.access_token}")
print(f"Refresh: {refresh}")
```

**Test Protected Endpoint:**
```bash
curl http://127.0.0.1:8000/api/v1/test/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Test Token Refresh:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
```

---

## 6. Data Models

### User Model

```python
# users/models.py
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom user model. Email-based authentication.
    
    Inherits from AbstractUser:
    - username, email, password (hashed)
    - is_staff, is_active, is_superuser
    - date_joined, last_login
    - check_password(), set_password()
    """
    
    email = models.EmailField(unique=True, blank=False)
    USERNAME_FIELD = 'email'  # Login with email
    REQUIRED_FIELDS = ['username']  # For createsuperuser
    
    class Meta:
        db_table = 'users_user'
    
    def __str__(self):
        return self.email
```

**Why Custom User:**
- ✅ Django best practice (set before first migration)
- ✅ Can't switch later without complex migrations
- ✅ Flexible for future changes

### UserStats Model

```python
class UserStats(models.Model):
    """One-to-one with User. Performance tracking."""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stats'  # Access: user.stats.current_streak
    )
    
    # Daily challenge stats
    total_correct = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_guess_date = models.DateField(null=True, blank=True)
    incorrect_countries = models.JSONField(default=list)
    
    # Phase 3: Quiz stats
    category_stats = models.JSONField(default=dict)
    format_stats = models.JSONField(default=dict)
    
    def update_daily_streak(self, is_correct, guess_date):
        """Business logic: Update streak based on guess."""
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
    
    def add_incorrect_country(self, country_code):
        """Add to incorrect list if not present."""
        if country_code not in self.incorrect_countries:
            self.incorrect_countries.append(country_code)
            self.save()
```

### Country Model

```python
class Country(models.Model):
    """Country data from REST Countries API."""
    
    # Core
    code = models.CharField(max_length=3, unique=True, db_index=True)
    name = models.CharField(max_length=100, db_index=True)
    
    # Visual assets
    flag_emoji = models.CharField(max_length=10)
    flag_svg_url = models.URLField(max_length=500)
    flag_png_url = models.URLField(max_length=500)
    flag_alt_text = models.TextField(blank=True)
    coat_of_arms_svg_url = models.URLField(max_length=500, null=True, blank=True)
    coat_of_arms_png_url = models.URLField(max_length=500, null=True, blank=True)
    
    # Geographic
    latitude = models.FloatField()
    longitude = models.FloatField()
    area_km2 = models.FloatField()
    highest_point = models.CharField(max_length=100, null=True, blank=True)
    
    # Demographic
    population = models.BigIntegerField()
    capital = models.CharField(max_length=100)
    largest_city = models.CharField(max_length=100)
    
    # Cultural (JSON for flexibility)
    languages = models.JSONField(default=list)
    religions = models.JSONField(null=True, blank=True)
    currencies = models.JSONField(default=dict)
    
    # Economic
    gdp_nominal = models.BigIntegerField(null=True, blank=True)
    gdp_ppp_per_capita = models.IntegerField(null=True, blank=True)
    
    # Social indicators
    median_age = models.FloatField(null=True, blank=True)
    life_expectancy = models.FloatField(null=True, blank=True)
    school_expectancy = models.FloatField(null=True, blank=True)
    fertility_rate = models.FloatField(null=True, blank=True)
    arable_land_percent = models.FloatField(null=True, blank=True)
    
    # Phase 2
    difficulty_tier = models.CharField(max_length=10, null=True, blank=True)
    popularity_score = models.IntegerField(default=0)
    
    # API cache
    api_cache_date = models.DateTimeField(auto_now_add=True)
    raw_api_response = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'flags_country'
        verbose_name_plural = "Countries"
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name']),
            models.Index(fields=['difficulty_tier']),
        ]
```

**Image Strategy:**
- MVP: Store CDN URLs (zero cost, fast)
- Phase 2+: Download & self-host if needed

### Question System Models

```python
class QuestionCategory(models.TextChoices):
    """Extensible question categories."""
    FLAG = 'flag', 'Flag Recognition'
    CAPITAL = 'capital', 'Capital City'
    POPULATION = 'population', 'Population'
    # Add more: NO MIGRATION NEEDED!

class QuestionFormat(models.TextChoices):
    """Extensible answer formats."""
    TEXT_INPUT = 'text_input', 'Text Input'
    MULTIPLE_CHOICE = 'multiple_choice', 'Multiple Choice'
    TRUE_FALSE = 'true_false', 'True/False'
    # Add more: NO MIGRATION NEEDED!

class DailyChallenge(models.Model):
    """One challenge per day, same for all users."""
    
    date = models.DateField(unique=True, db_index=True)
    country = models.ForeignKey('Country', on_delete=models.PROTECT)
    difficulty_tier = models.CharField(max_length=10, null=True, blank=True)
    selection_algorithm_version = models.CharField(max_length=20, default='v1_random')
    
    @classmethod
    def get_or_create_today(cls):
        """Get today's challenge, creating if needed."""
        today = timezone.now().date()
        challenge, created = cls.objects.get_or_create(
            date=today,
            defaults={'country': cls._select_random_country()}
        )
        return challenge
    
    @classmethod
    def _select_random_country(cls):
        """MVP: Random without repeats."""
        shown_codes = cls.objects.values_list('country__code', flat=True)
        available = Country.objects.exclude(code__in=shown_codes)
        if not available.exists():
            available = Country.objects.all()
        return available.order_by('?').first()

class Question(models.Model):
    """Flexible question model."""
    
    category = models.CharField(max_length=30, choices=QuestionCategory.choices)
    format = models.CharField(max_length=30, choices=QuestionFormat.choices)
    country = models.ForeignKey('Country', on_delete=models.CASCADE)
    question_text = models.TextField()
    correct_answer = models.JSONField()  # Flexible structure
    metadata = models.JSONField(default=dict, blank=True)
    daily_challenge = models.ForeignKey('DailyChallenge', null=True, blank=True)
    
    def validate_answer(self, user_answer_data):
        """Validate user's answer. Returns (is_correct, explanation)."""
        if self.format == QuestionFormat.TEXT_INPUT:
            return self._validate_text_input(user_answer_data)
        elif self.format == QuestionFormat.MULTIPLE_CHOICE:
            return self._validate_multiple_choice(user_answer_data)
        # ... more formats
    
    def _validate_text_input(self, user_answer_data):
        user_text = user_answer_data.get('text', '').lower().strip()
        correct = self.correct_answer['answer'].lower()
        alternates = [alt.lower() for alt in self.correct_answer.get('alternates', [])]
        is_correct = user_text == correct or user_text in alternates
        return is_correct, f"Correct answer: {self.correct_answer['answer']}"

class UserAnswer(models.Model):
    """Records user's answer to question."""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    answer_data = models.JSONField()
    is_correct = models.BooleanField()
    explanation = models.TextField(blank=True)
    attempt_number = models.IntegerField(default=1)  # 1-3 for daily
    time_taken_seconds = models.IntegerField(null=True, blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)
```

---

## 7. Serializer Architecture

### Overview

Serializers are Django REST Framework's mechanism for converting complex data types (like Django models) to/from Python datatypes that can be easily rendered into JSON. They also handle input validation and deserialization.

**Our Philosophy:** Thin serializers - handle data transformation and validation only. Business logic lives in models.

### Serializer Organization

```
users/
├── serializers/
│   ├── __init__.py
│   └── user_serializers.py       # User, UserStats, UserCreate

flags/
├── serializers/
│   ├── __init__.py
│   ├── country_serializers.py    # Country (List/Detail/Search)
│   ├── challenge_serializers.py  # DailyChallenge
│   └── question_serializers.py   # Question, UserAnswer, Results
```

**Rationale:**
- Separate files by domain concept (not one giant serializers.py)
- Mirrors model organization
- Easy to locate and maintain
- Scales well as project grows

### Key Serializer Patterns

#### Pattern 1: List vs Detail Serializers

```python
# Lightweight for list endpoints
class CountryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['code', 'name', 'flag_emoji', 'population', 'capital']

# Complete data for detail endpoints  
class CountryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'
```

**Why:** List endpoints may return dozens of items. Including full country data (20+ fields) for each item creates massive payloads. Detail endpoints serve one item, so full data is appropriate.

#### Pattern 2: Input vs Output Serializers

```python
# Output: What we send to frontend
class UserSerializer(serializers.ModelSerializer):
    stats = UserStatsSerializer(read_only=True)  # Nested
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'stats']
        read_only_fields = ['id', 'date_joined']

# Input: What we accept from frontend
class UserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150, required=False)
    
    def validate_email(self, value):
        return value.lower()
```

**Why:**
- Output serializers show nested/computed data (user + stats)
- Input serializers validate incoming data structure
- Prevents coupling frontend submission format to model structure
- Different endpoints need different data shapes

#### Pattern 3: Security-Conscious Serialization

```python
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'id', 'category', 'format', 
            'question_text', 'metadata',
            # NOTE: 'correct_answer' is EXCLUDED
        ]

# Separate serializer for answer results
class AnswerResultSerializer(serializers.Serializer):
    is_correct = serializers.BooleanField()
    explanation = serializers.CharField()
    correct_answer = serializers.JSONField(required=False)  # Only if wrong
```

**Why:** Never send answers to frontend before user submits. Separate serializers enforce this at the serializer level, preventing accidental leaks.

#### Pattern 4: Nested Serializers

```python
class DailyChallengeSerializer(serializers.ModelSerializer):
    country = CountryDetailSerializer(read_only=True)  # Full nested object
    
    class Meta:
        model = DailyChallenge
        fields = ['id', 'date', 'country', 'difficulty_tier']
```

**Why:** 
- Frontend needs full country data with challenge
- Avoids second API call (better UX)
- Trade-off: Larger payload, but worth it for UX

**Alternative for lists:**
```python
class DailyChallengeListSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    country_flag = serializers.CharField(source='country.flag_emoji', read_only=True)
    
    # Don't nest full object in lists - just extract key fields
```

#### Pattern 5: Response Serializers (Non-Model)

```python
class AnswerResultSerializer(serializers.Serializer):
    """
    Defines structure of POST /api/daily/answer/ response.
    Not backed by a model - just an API contract.
    """
    is_correct = serializers.BooleanField()
    explanation = serializers.CharField()
    attempts_remaining = serializers.IntegerField()
    user_answer_id = serializers.IntegerField()
```

**Why:** Not every API response maps to a database model. Response serializers document your API contract and ensure consistent response structures.

### Serializer Types Explained

**`serializers.ModelSerializer`:**
- Auto-generates fields from model
- Use for: Standard CRUD, model → JSON
- Saves boilerplate

**`serializers.Serializer`:**
- Manually define all fields
- Use for: Input validation, non-model data, custom structures
- More control

**When to use each:**
- Model → JSON: `ModelSerializer`
- JSON → Model: `ModelSerializer` 
- Complex input validation: `Serializer`
- API response structures: `Serializer`

### Validation Patterns

```python
class QuestionAnswerSerializer(serializers.Serializer):
    answer_data = serializers.JSONField()
    
    # Field-level validation
    def validate_answer_data(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Must be an object")
        return value
    
    # Object-level validation (access multiple fields)
    def validate(self, data):
        # Can access self.context for additional info
        question = self.context.get('question')
        # Perform cross-field validation
        return data
```

**Validation Flow:**
1. Field-level: `validate_<field_name>()` methods
2. Object-level: `validate()` method
3. Model validators (if ModelSerializer)

### Implemented Serializers (Current Status)

**Users App:**
- `UserSerializer` - User with nested stats (output)
- `UserStatsSerializer` - User statistics (output)
- `UserCreateSerializer` - OAuth user creation (input)

**Flags App:**
- `CountryListSerializer` - Minimal country data for lists
- `CountryDetailSerializer` - Complete country data
- `CountrySearchSerializer` - Search query validation (input)
- `DailyChallengeSerializer` - Challenge with nested country (output)
- `DailyChallengeListSerializer` - Challenge history (output)
- `QuestionSerializer` - Question without answer (output)
- `QuestionAnswerSerializer` - Answer submission (input)
- `UserAnswerSerializer` - Answer history (output)
- `AnswerResultSerializer` - Answer validation result (output)

---

## 8. Business Logic Patterns

### Where Logic Lives

**Django Pattern: Fat Models, Thin Views**

```python
# ✅ GOOD: Logic in models
class UserStats(models.Model):
    def update_daily_streak(self, is_correct, guess_date):
        # All business logic here
        if is_correct:
            if self.last_guess_date == guess_date - timedelta(days=1):
                self.current_streak += 1
            else:
                self.current_streak = 1
        self.save()

# View just orchestrates
class SubmitGuessView(APIView):
    def post(self, request):
        is_correct = question.validate_answer(request.data)
        request.user.stats.update_daily_streak(is_correct, today)
        return Response({...})
```

```python
# ❌ BAD: Logic in views
class SubmitGuessView(APIView):
    def post(self, request):
        # DON'T put business logic here!
        stats = request.user.stats
        if is_correct:
            if stats.last_guess_date == today - timedelta(days=1):
                stats.current_streak += 1
            # ... 50 more lines ...
```

**Responsibilities:**

| Layer | Responsibility | Examples |
|-------|----------------|----------|
| **Models** | Business logic, domain rules | Streak calculation, answer validation |
| **Serializers** | Validation, formatting | Required fields, JSON structure |
| **Views** | HTTP handling, orchestration | Auth checks, call model methods |

### When to Extract to Services

**Not Now (MVP):** Models handle business logic  
**Future (Phase 2+):** Extract to services when:
- Models exceed ~500 lines
- Complex multi-model transactions
- Logic needed outside models (Celery tasks)
- Daily flag algorithm becomes complex

---

## 9. Testing Strategy

**Status:** ✅ **COMPREHENSIVE SUITE** (40 Tests Passing)

### Test Organization

```
users/tests/
├── __init__.py           # Module documentation
├── test_auth.py          # JWT & OAuth authentication tests (15 tests)
└── test_models.py        # User & UserStats model tests (13 tests)

flags/tests/
├── __init__.py           # Module documentation
├── test_models.py        # Country, DailyChallenge, Question tests (8 tests)
└── test_serializers.py   # Serializer tests (4 tests)
```

### Test Coverage by Component

| Component | Tests | Status |
|-----------|-------|--------|
| **JWT Token Generation** | 3 tests | ✅ Passing |
| **Google OAuth Login** | 6 tests | ✅ Passing |
| **Token Refresh** | 3 tests | ✅ Passing |
| **Protected Endpoints** | 3 tests | ✅ Passing |
| **User Model** | 5 tests | ✅ Passing |
| **UserStats Model** | 8 tests | ✅ Passing |
| **Country Model** | 3 tests | ✅ Passing |
| **DailyChallenge Model** | 3 tests | ✅ Passing |
| **Question Model** | 2 tests | ✅ Passing |
| **Serializers** | 4 tests | ✅ Passing |

### Running Tests

```bash
# All tests
uv run python manage.py test

# Specific module
uv run python manage.py test users.tests.test_auth

# Parallel (faster)
uv run python manage.py test --parallel

# With coverage
uv run coverage run --source='.' manage.py test
uv run coverage report
```

### Key Testing Patterns

**1. Mocking External Services:**
```python
@patch('users.views.id_token.verify_oauth2_token')
def test_valid_token_creates_new_user(self, mock_verify):
    mock_verify.return_value = self.mock_google_user
    # Test without calling Google API
```

**2. Test Fixtures:**
```python
def setUp(self):
    """Runs before EACH test method."""
    self.user = User.objects.create_user(...)
    # Fresh data for each test
```

**3. APIClient Usage:**
```python
self.client = APIClient()
self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
response = self.client.post(url, data)
```

### Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| Model methods | 100% | ~95% |
| Authentication | 90%+ | ~90% |
| API endpoints | 80%+ | ~75% |

---

## 10. API Design

### Versioned Endpoints

```
Authentication:
POST /api/v1/auth/google/              # OAuth login
POST /api/v1/auth/token/refresh/       # JWT refresh

Countries:
GET  /api/v1/countries/                # List all countries
GET  /api/v1/countries/{id}/           # Country detail

Development:
GET  /api/v1/test/                     # Test endpoint (require auth)

Future:
GET  /api/v1/daily/                    # Today's challenge
POST /api/v1/daily/answer/             # Submit guess
GET  /api/v1/stats/                    # User stats
```

**Implemented Endpoints (Current Status):**
- ✅ `POST /api/v1/auth/google/` - OAuth login (AllowAny)
- ✅ `POST /api/v1/auth/token/refresh/` - Token refresh (AllowAny)
- ✅ `GET /api/v1/countries/` - List countries (AllowAny)
- ✅ `GET /api/v1/countries/{id}/` - Country detail (AllowAny)
- ✅ `GET /api/v1/test/` - Test endpoint (IsAuthenticated)

**URL Configuration:**
- DRF Router automatically generates URLs for ViewSets
- `CountryViewSet` registered with router in `flags/urls.py`
- Auth endpoints in `users/urls.py`
- All endpoints under `/api/v1/` prefix for versioning

### Response Format

**Success:**
```json
{
    "date": "2025-11-11",
    "country": {
        "code": "FRA",
        "name": "France",
        "flag_svg_url": "https://..."
    },
    "user_status": {
        "has_answered_today": false,
        "current_streak": 5
    }
}
```

**Error:**
```json
{
    "error": "Invalid token",
    "detail": "Token verification failed"
}
```

### HTTP Status Codes

| Code | Use |
|------|-----|
| 200 | Success |
| 201 | Created |
| 400 | Bad request |
| 401 | Unauthorized |
| 404 | Not found |
| 500 | Server error |

---

## 11. Future Architecture

### Phase 2: Difficulty Tiers

```python
class DifficultyTierState(models.Model):
    tier = models.CharField(max_length=10)
    cycle_number = models.IntegerField(default=1)
    shown_countries = models.JSONField(default=list)
```

### Phase 3: Quiz Mode

```python
class QuizSession(models.Model):
    user = models.ForeignKey(User)
    question_count = models.IntegerField()
    selected_categories = models.JSONField()
    score = models.IntegerField(default=0)
```

### Infrastructure

**Caching (Redis):**
```python
from django.core.cache import cache
cache.set('daily_challenge', challenge, timeout=86400)
```

**Background Tasks (Celery):**
```python
@app.task
def refresh_country_data():
    # Weekly refresh from REST Countries API
    pass
```

---

## Quick Reference

### Essential Commands

```bash
# PostgreSQL
psql -U flaglearning_user -d flaglearning_dev -h localhost
\dt                    # List tables
\d table_name          # Describe table

# Django
uv run python manage.py migrate
uv run python manage.py test
uv run python manage.py runserver
uv run python manage.py shell

# uv
uv add package-name
uv run command
```

### Connection String

```bash
postgresql://flaglearning_user:dev_password_2024@localhost:5432/flaglearning_dev
```

---

## Troubleshooting

### OAuth Issues

**Problem:** "Invalid token" error

**Solutions:**
1. Verify `GOOGLE_CLIENT_ID` in `.env` matches Google Cloud Console
2. Check token hasn't expired (Google ID tokens expire quickly)
3. Verify frontend is sending `id_token`, not `access_token`
4. Test with fresh token from shell

**Problem:** User created but no JWT returned

**Solutions:**
1. Check `djangorestframework-simplejwt` is installed
2. Verify `SIMPLE_JWT` settings in `config/settings.py`
3. Run migrations: `uv run python manage.py migrate`

**Problem:** Token refresh fails with 401

**Solutions:**
1. Verify refresh token hasn't been blacklisted
2. Check `ROTATE_REFRESH_TOKENS` setting
3. Ensure using correct endpoint: `/api/v1/auth/token/refresh/`

### Testing Issues

**Problem:** Tests fail with authentication errors

**Solutions:**
1. Ensure test creates user in `setUp()`
2. Generate fresh tokens for each test
3. Use `@patch` for Google OAuth verification

**Problem:** Database errors in tests

**Solutions:**
1. Django test database is separate - no need to clean up
2. Each test gets fresh database via transactions
3. Check `setUp()` runs before each test

---

## Document Version

**Version:** 1.2  
**Date:** November 11, 2025  
**Status:** OAuth & Authentication Complete - Day 3

**Changelog:**

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Oct 30, 2025 | Initial version - models, migrations, database setup |
| 1.1 | Oct 31, 2025 | Added Serializer Architecture section, documented serializer implementation (serializers, DRF setup, URL routing, test endpoints), added note about temporary AllowAny permission setting |
| 1.2 | Nov 11, 2025 | **OAuth Implementation Complete**: Updated Authentication System section with full implementation details and "IMPLEMENTED" status; documented JWT configuration (token lifetimes, rotation, blacklisting); added GoogleLoginView implementation and URL routing structure; updated Testing Strategy with 40 passing tests and organized test suite; added Troubleshooting section for OAuth issues; updated Executive Summary with Day 3 completion status; documented all authentication endpoints and token flow |

---

**End of Document**
