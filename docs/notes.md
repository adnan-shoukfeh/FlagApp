# Project Notes


## Future Optimizations
### Database URL Parsing:
* Currently manual string splitting (works but ugly)
* Better approach for Phase 2: Install dj-database-url library
* For now, this works and helps you understand what each part does


## Best Practices
### Security Best Practice:
* Don't use your PostgreSQL superuser 
  * (probably postgres or your macOS username) for your app. 
* Create a dedicated role with limited permissions. 
  * If your app gets compromised, the attacker only has access to this one database, 
  * NOT your entire PostgreSQL server.

### Django Model Importing

**❌ DON'T DO THIS:**
```Python
from users.models import User
user = models.ForeignKey(User, ...)
```

**✅ DO THIS:**
```Python
from django.conf import settings
user = models.ForeignKey(settings.AUTH_USER_MODEL, ...)
# Why? Avoids circular imports and works with any custom User model
```

Save Postgres commands to doc
postgresql://flaglearning_user:dev_password_2024@localhost:5432/flaglearning_dev
Breaking down this URL:
* postgresql:// - Protocol
* flaglearning_user:dev_password_2024 - Username and password
* @localhost:5432 - Host and port (5432 is PostgreSQL's default)
* /flaglearning_dev - Database name

# ❌ DON'T DO THIS:
from users.models import User
user = models.ForeignKey(User, ...)

# ✅ DO THIS:
from django.conf import settings
user = models.ForeignKey(settings.AUTH_USER_MODEL, ...)
# Why? Avoids circular imports and works with any custom User model

# Generate migration files
uv run python manage.py makemigrations





FINAL REQ
Give me a summary of BE decisions and design so far. Going to use this as a full BE 
technical design doc and add things to it.
Can you add Postgres commands 
(for creating/dealing with prod and dev users and databases/tables)