.PHONY: dev test check migrate makemigrations shell dbshell lint

# Development server
dev:
	uv run python manage.py runserver

# Run all tests
test:
	uv run python manage.py test

# Django system check
check:
	uv run python manage.py check

# Apply migrations
migrate:
	uv run python manage.py migrate

# Create migrations
makemigrations:
	uv run python manage.py makemigrations

# Django shell
shell:
	uv run python manage.py shell

# Database shell
dbshell:
	uv run python manage.py dbshell

# Install/sync dependencies
install:
	uv sync
