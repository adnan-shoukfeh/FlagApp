from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.

    What we inherit from AbstractUser:
    - username, first_name, last_name
    - email, password (hashed automatically)
    - is_staff, is_active, is_superuser
    - date_joined, last_login
    - All authentication methods (check_password, set_password, etc.)
    """

    # === Core Identification ===
    # Override email to make it required and unique
    # AbstractUser has email, but it's not unique by default
    email = models.EmailField(
        unique=True, blank=False, help_text="Email address for OAuth login"
    )

    # Use email for login, not username
    # But AbstractUser requires username, so we'll auto-generate it
    USERNAME_FIELD = "email"  # This makes email the login identifier
    REQUIRED_FIELDS = ["username"]  # Required for createsuperuser command

    # === Meta Data ===
    class Meta:
        db_table = "users_user"  # Explicit table name
        verbose_name = "User"
        verbose_name_plural = "Users"

    # === Methods ===
    def __str__(self):
        return self.email


class UserStats(models.Model):
    """
    Tracks user performance statistics for daily challenges and quizzes.

    Relationship: OneToOne with User (each user has exactly one stats object)

    Design decisions:
    - JSONFields for flexible stats (category_stats, format_stats)
    - Avoids migrations when adding new quiz categories in Phase 3
    - Model methods encapsulate business logic (Django convention)

    Why separate from User model?
    - Separation of concerns (auth vs statistics)
    - User model stays lean (fewer joins in auth queries)
    - Can delete stats without affecting user account
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # References our custom User model
        on_delete=models.CASCADE,  # If user deleted, delete their stats
        related_name="stats",  # Access via user.stats
        help_text="The user these statistics belong to",
    )

    # === Daily Challenge Stats ===
    total_correct = models.IntegerField(
        default=0, help_text="Total number of correct daily challenge guesses"
    )
    current_streak = models.IntegerField(
        default=0, help_text="Consecutive days with correct guess"
    )
    longest_streak = models.IntegerField(
        default=0, help_text="Best streak ever achieved"
    )
    last_guess_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of most recent guess (for streak calculation)",
    )

    # List of country codes guessed incorrectly
    # Why list not ForeignKey? Simple tracking, no need for full relationship
    incorrect_countries = models.JSONField(
        default=list, help_text='List of country codes: ["USA", "FRA", "JPN"]'
    )

    # === Quiz Mode Stats (Phase 3) ===
    # Structure: {
    #   "flag": {
    #     "correct": 50,
    #     "total": 100,
    #     "accuracy": 0.50,
    #     "by_format": {
    #       "text_input": {"correct": 30, "total": 50, "accuracy": 0.60},
    #       "multiple_choice": {"correct": 20, "total": 50, "accuracy": 0.40}
    #     }
    #   },
    #   "capital": {...},
    # }
    category_stats = models.JSONField(
        default=dict, help_text="Performance breakdown by question category"
    )

    # Structure: {
    #   "text_input": {"correct": 80, "total": 150, "accuracy": 0.53},
    #   "multiple_choice": {"correct": 95, "total": 120, "accuracy": 0.79}
    # }
    format_stats = models.JSONField(
        default=dict, help_text="Performance breakdown by answer format"
    )

    # Flexible field for future metrics without migrations
    extra_stats = models.JSONField(
        default=dict, help_text="Extensibility field for future statistics"
    )

    # === Timestamps ===
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # === Meta Data ===
    class Meta:
        db_table = "users_userstats"
        verbose_name = "User Stats"
        verbose_name_plural = "User Stats"

    # === Methods ===
    def __str__(self):
        return f"{self.user.email} - {self.total_correct} correct"

    def update_daily_streak(self, is_correct, guess_date):
        """
        Update streak based on today's guess result.

        Streak rules:
        - Correct guess + yesterday was guessed = increment streak
        - Correct guess + gap in days = reset to 1
        - Incorrect guess = reset to 0

        Args:
            is_correct (bool): Whether the guess was correct
            guess_date (date): The date of this guess

        Example usage:
            user.stats.update_daily_streak(is_correct=True, guess_date=today)
        """
        if is_correct:
            # Check if this continues a streak
            if self.last_guess_date == guess_date - timedelta(days=1):
                self.current_streak += 1
            else:
                # First guess or gap in streak
                self.current_streak = 1

            # Update longest streak if current is new record
            self.longest_streak = max(self.longest_streak, self.current_streak)

            # Increment total correct
            self.total_correct += 1
        else:
            # Incorrect guess breaks streak
            self.current_streak = 0

        # Always update last guess date
        self.last_guess_date = guess_date
        self.save()

    def add_incorrect_country(self, country_code):
        """
        Add a country to the incorrect list if not already present.

        Args:
            country_code (str): ISO country code (e.g., "USA")
        """
        if country_code not in self.incorrect_countries:
            self.incorrect_countries.append(country_code)
            self.save()

    # Phase 3 methods (documented now, implemented later)
    def update_category_stat(self, category, format_type, is_correct):
        """
        Update per-category and per-format statistics.
        Implementation deferred to Phase 3.
        """
        # TODO: Phase 3 implementation
        pass

    def get_weakest_categories(self, limit=5):
        """
        Returns categories where user performs worst.
        Implementation deferred to Phase 3.
        """
        # TODO: Phase 3 implementation
        return []

    def get_strongest_formats(self, limit=3):
        """
        Returns question formats user is best at.
        Implementation deferred to Phase 3.
        """
        # TODO: Phase 3 implementation
        return []
