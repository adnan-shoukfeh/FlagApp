# ---- base: production dependencies, cached independently of source ----
FROM python:3.12-slim AS base

WORKDIR /app

# Install uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install deps before copying source so this layer is cached on code-only changes
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# ---- dev: source is mounted via docker-compose volume ----
FROM base AS dev

EXPOSE 8000
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]

# ---- prod: copy source, harden with non-root user, run gunicorn ----
FROM base AS prod

COPY . .

RUN addgroup --system app && adduser --system --ingroup app app
USER app

EXPOSE 8000
CMD ["uv", "run", "gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
