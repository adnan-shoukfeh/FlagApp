# Backend PostgreSQL Reference

**Project:** Flag Learning App - Backend  
**Last Updated:** October 31, 2025  
**Purpose:** PostgreSQL setup, operations, and command reference  
**Developer:** Adnan Shoukfeh

---

## Overview

This document provides comprehensive PostgreSQL reference material for the Flag Learning App backend. Use this for database setup, daily operations, troubleshooting, and maintenance tasks.

**Related Documentation:**
- **Backend_Technical_Design.md** - Architecture, models, and design decisions
- **Backend_Development_Workflow.md** - Development process and common commands

---

## Quick Reference Card

### Essential Commands

```bash
# Connect to database
psql -U flaglearning_user -d flaglearning_dev -h localhost

# Common psql commands (run inside psql)
\dt                    # List all tables
\d table_name          # Describe table structure
\di                    # List indexes
\l                     # List all databases
\du                    # List all users/roles
\q                     # Quit psql
```

### Connection String
```
postgresql://flaglearning_user:dev_password_2024@localhost:5432/flaglearning_dev
```

### Quick Tasks

| Task | Command |
|------|---------|
| Create backup | `pg_dump -U flaglearning_user flaglearning_dev > backup.sql` |
| Restore backup | `psql -U flaglearning_user flaglearning_dev < backup.sql` |
| Count records | `SELECT COUNT(*) FROM table_name;` |
| Check DB size | `SELECT pg_size_pretty(pg_database_size('flaglearning_dev'));` |
| Drop test DBs | See [Clean Up Test Databases](#clean-up-test-databases) |

---

## Table of Contents

1. [Initial Setup](#1-initial-setup)
2. [Database Inspection](#2-database-inspection)
3. [Backup & Restore](#3-backup--restore)
4. [Database Reset](#4-database-reset-development-only)
5. [Production Setup](#5-production-setup)
6. [Monitoring & Maintenance](#6-monitoring--maintenance)
7. [Common Queries](#7-common-queries)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Initial Setup

### Create Development Database

**Step 1: Connect as PostgreSQL superuser**

```bash
psql postgres
```

**Step 2: Create application user and database**

```sql
-- Create dedicated application user
-- Principle of least privilege: separate user per application
CREATE USER flaglearning_user WITH PASSWORD 'dev_password_2024';

-- Grant CREATEDB for Django tests
-- Django creates temporary test databases (test_flaglearning_dev)
ALTER USER flaglearning_user CREATEDB;

-- Create development database
CREATE DATABASE flaglearning_dev OWNER flaglearning_user;

-- Grant all privileges (redundant but explicit)
GRANT ALL PRIVILEGES ON DATABASE flaglearning_dev TO flaglearning_user;

-- Verify setup
\du flaglearning_user  -- Should show: Login, Create DB
\l flaglearning_dev    -- Should show: flaglearning_user as owner

-- Exit
\q
```

**Step 3: Test connection**

```bash
# Connect as application user
psql -U flaglearning_user -d flaglearning_dev -h localhost
# Password: dev_password_2024

# Success: You'll see flaglearning_dev=> prompt
\q
```

**What We Created:**
- **User:** `flaglearning_user` with CREATEDB privilege
- **Database:** `flaglearning_dev` owned by flaglearning_user
- **Purpose:** Isolated development environment with test database support

---

## 2. Database Inspection

### Table Management

```sql
-- Connect to database
psql -U flaglearning_user -d flaglearning_dev -h localhost

-- List all tables
\dt

-- Describe table structure (shows columns, types, constraints)
\d users_user
\d flags_country

-- View all indexes on a table
\di flags_country

-- View Foreign Key constraints
\d flags_question

-- View table sizes
\dt+

-- View database size
SELECT pg_size_pretty(pg_database_size('flaglearning_dev'));
```

### User & Role Management

```sql
-- List all databases
\l

-- List all users/roles
\du

-- View active connections
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query_start
FROM pg_stat_activity
WHERE datname = 'flaglearning_dev';
```

### Migration Status

```sql
-- Check migration history
SELECT app, name, applied 
FROM django_migrations 
ORDER BY applied DESC 
LIMIT 10;
```

---

## 3. Backup & Restore

### Backup Operations

```bash
# ===== FULL DATABASE BACKUP =====

# Standard backup
pg_dump -U flaglearning_user -h localhost flaglearning_dev > backup_$(date +%Y%m%d).sql

# Compressed backup (recommended)
pg_dump -U flaglearning_user -h localhost flaglearning_dev | gzip > backup_$(date +%Y%m%d).sql.gz

# ===== SPECIFIC TABLE BACKUP =====

# Backup single table (useful for country data)
pg_dump -U flaglearning_user -h localhost -t flags_country flaglearning_dev > countries_backup.sql

# ===== SCHEMA vs DATA =====

# Schema only (no data) - useful for creating test environments
pg_dump -U flaglearning_user -h localhost --schema-only flaglearning_dev > schema_backup.sql

# Data only (no schema) - useful for data migration
pg_dump -U flaglearning_user -h localhost --data-only flaglearning_dev > data_backup.sql
```

### Restore Operations

```bash
# ===== RESTORE FROM BACKUP =====

# Restore standard backup
psql -U flaglearning_user -h localhost flaglearning_dev < backup_20251030.sql

# Restore compressed backup
gunzip -c backup_20251030.sql.gz | psql -U flaglearning_user -h localhost flaglearning_dev

# ===== RESTORE SPECIFIC TABLE =====

# Restore single table
psql -U flaglearning_user -h localhost flaglearning_dev < countries_backup.sql
```

**Best Practices:**
- ✅ Use compressed backups for daily automation
- ✅ Include date in filename
- ✅ Test restore process periodically
- ✅ Store backups outside the database server
- ✅ Keep schema-only backup for quick environment setup

---

## 4. Database Reset (Development Only!)

### ⚠️ WARNING: Destroys All Data

```bash
psql postgres
```

```sql
-- Terminate all connections first
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'flaglearning_dev'
  AND pid <> pg_backend_pid();

-- Drop and recreate database
DROP DATABASE IF EXISTS flaglearning_dev;
CREATE DATABASE flaglearning_dev OWNER flaglearning_user;
\q
```

```bash
# Rerun Django migrations
cd backend
uv run python manage.py migrate
```

**When to Use:**
- Starting fresh during development
- After major model changes
- Testing migration scripts from scratch

**Never use in production!**

---

## 5. Production Setup

### Create Production Database

```sql
-- Create production user with STRONG password
-- Generate with: openssl rand -base64 32
CREATE USER flaglearning_prod WITH PASSWORD 'STRONG_PASSWORD_32_CHARS_MIN';

-- NO CREATEDB in production
-- (Tests don't run in production)

-- Create production database
CREATE DATABASE flaglearning_prod OWNER flaglearning_prod;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE flaglearning_prod TO flaglearning_prod;

-- Enable SSL (edit postgresql.conf)
-- ssl = on
-- ssl_cert_file = '/path/to/server.crt'
-- ssl_key_file = '/path/to/server.key'

-- Restrict connections to SSL (edit pg_hba.conf)
-- hostssl all flaglearning_prod 0.0.0.0/0 md5
```

### Production Connection String

```bash
# With SSL required
postgresql://flaglearning_prod:STRONG_PASSWORD@db.host.com:5432/flaglearning_prod?sslmode=require
```

### Production Checklist

- ✅ Strong password (32+ characters, random)
- ✅ SSL/TLS required for connections
- ✅ NO CREATEDB privilege
- ✅ Automated backups configured
- ✅ Connection pooling (pgBouncer)
- ✅ Firewall rules
- ✅ Monitoring (pg_stat_statements)

---

## 6. Monitoring & Maintenance

### Performance Monitoring

```sql
-- View table bloat and sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- View slow queries (requires pg_stat_statements extension)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

SELECT 
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Maintenance Operations

```sql
-- Manual VACUUM (usually automatic)
VACUUM ANALYZE flags_country;

-- Reindex table (if performance degrades)
REINDEX TABLE flags_country;

-- Update table statistics
ANALYZE flags_country;
```

### Clean Up Test Databases

Django creates temporary test databases (prefixed with `test_`). These can accumulate during development.

```sql
-- List orphaned test databases
SELECT datname FROM pg_database WHERE datname LIKE 'test_%';

-- Drop specific test database
DROP DATABASE IF EXISTS test_flaglearning_dev;

-- Drop all test databases (careful!)
DO $$ 
DECLARE 
    db_name TEXT;
BEGIN
    FOR db_name IN 
        SELECT datname FROM pg_database WHERE datname LIKE 'test_%'
    LOOP
        EXECUTE 'DROP DATABASE IF EXISTS ' || quote_ident(db_name);
    END LOOP;
END $$;
```

---

## 7. Common Queries

### Application Data Queries

```sql
-- Connect to database
psql -U flaglearning_user -d flaglearning_dev -h localhost

-- ===== COUNTRY DATA =====

-- Count countries (should be 195 after loading)
SELECT COUNT(*) FROM flags_country;

-- View all countries (sample)
SELECT code, name, flag_emoji 
FROM flags_country 
ORDER BY name 
LIMIT 10;

-- ===== DAILY CHALLENGE =====

-- Check today's challenge
SELECT 
    dc.date, 
    c.name, 
    c.flag_emoji,
    dc.selection_algorithm_version
FROM flags_dailychallenge dc
JOIN flags_country c ON dc.country_id = c.id
WHERE dc.date = CURRENT_DATE;

-- ===== USER STATISTICS =====

-- View user stats (all users)
SELECT 
    u.email, 
    us.total_correct, 
    us.current_streak, 
    us.longest_streak
FROM users_user u
JOIN users_userstats us ON u.id = us.user_id
ORDER BY us.total_correct DESC;

-- Find users with active streaks
SELECT 
    u.email,
    us.current_streak,
    us.last_guess_date
FROM users_user u
JOIN users_userstats us ON u.id = us.user_id
WHERE us.current_streak > 0
ORDER BY us.current_streak DESC;

-- ===== ANALYTICS QUERIES =====

-- Most guessed countries
SELECT 
    c.name,
    c.flag_emoji,
    COUNT(ua.id) as guess_count
FROM flags_country c
JOIN flags_question q ON q.country_id = c.id
JOIN flags_useranswer ua ON ua.question_id = q.id
GROUP BY c.id, c.name, c.flag_emoji
ORDER BY guess_count DESC
LIMIT 10;

-- User answer accuracy
SELECT 
    u.email,
    COUNT(ua.id) as total_answers,
    SUM(CASE WHEN ua.is_correct THEN 1 ELSE 0 END) as correct,
    ROUND(100.0 * SUM(CASE WHEN ua.is_correct THEN 1 ELSE 0 END) / COUNT(ua.id), 2) as accuracy_pct
FROM users_user u
JOIN flags_useranswer ua ON ua.user_id = u.id
GROUP BY u.id, u.email
HAVING COUNT(ua.id) > 0
ORDER BY accuracy_pct DESC;
```

---

## 8. Troubleshooting

### Connection Issues

**Problem:** Can't connect to database

```bash
# Check if PostgreSQL is running
pg_isready

# Check PostgreSQL status (macOS)
brew services list | grep postgresql

# Start PostgreSQL (macOS)
brew services start postgresql

# Check if database exists
psql -U flaglearning_user -l
```

**Problem:** Password authentication failed

```bash
# Reset user password
psql postgres
ALTER USER flaglearning_user WITH PASSWORD 'new_password';
\q

# Update your .env file with new password
```

### Performance Issues

**Problem:** Queries are slow

```sql
-- Check for missing indexes
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    most_common_vals
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY schemaname, tablename;

-- Check for table bloat
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Run VACUUM ANALYZE
VACUUM ANALYZE;
```

### Space Issues

**Problem:** Database taking too much space

```sql
-- Find largest tables
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

-- Clean up test databases (see above)
-- Drop old backups
-- Run VACUUM FULL (locks table)
VACUUM FULL flags_useranswer;
```

### Migration Issues

**Problem:** Django migrations failing

```bash
# Check current migration status
uv run python manage.py showmigrations

# Check database migration table
psql -U flaglearning_user -d flaglearning_dev -c "SELECT * FROM django_migrations ORDER BY applied DESC LIMIT 5;"

# Fake a migration (only if you know what you're doing)
uv run python manage.py migrate --fake appname migration_name

# Reset migrations (nuclear option)
# See "Database Reset" section above
```

---

## Connection String Reference

### Development
```bash
# Standard format
postgresql://flaglearning_user:dev_password_2024@localhost:5432/flaglearning_dev

# For .env file
DATABASE_URL=postgresql://flaglearning_user:dev_password_2024@localhost:5432/flaglearning_dev
```

### Production
```bash
# With SSL required
postgresql://flaglearning_prod:STRONG_PASSWORD@db.host.com:5432/flaglearning_prod?sslmode=require

# Breakdown:
# postgresql://     - Protocol
# user:password     - Credentials
# @host:port       - Server (5432 = PostgreSQL default)
# /database        - Database name
# ?sslmode=require - Connection options (production)
```

---

## Quick Task Index

### By Frequency

**Daily Tasks:**
- [Connect to database](#2-database-inspection)
- [View tables](#table-management)
- [Run common queries](#7-common-queries)

**Weekly Tasks:**
- [Create backup](#backup-operations)
- [Check database size](#database-inspection)
- [Clean test databases](#clean-up-test-databases)

**As Needed:**
- [Restore from backup](#restore-operations)
- [Reset development database](#4-database-reset-development-only)
- [Monitor performance](#performance-monitoring)
- [Troubleshoot issues](#8-troubleshooting)

**One-Time Setup:**
- [Initial database setup](#1-initial-setup)
- [Production setup](#5-production-setup)

---

## Document Version

**Version:** 1.0  
**Date:** October 31, 2025  
**Extracted from:** Backend Technical Design v1.1

**Changelog:**
- **v1.0 (Oct 31, 2025):** Initial standalone PostgreSQL reference document. Extracted from Backend Technical Design, reorganized for quick reference, added troubleshooting section.

---

**End of Document**
