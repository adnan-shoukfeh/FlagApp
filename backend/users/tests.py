from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase

from users.models import UserStats

User = get_user_model()  # Gets our custom User model


class UserModelTest(TestCase):
    """
    Tests for the custom User model.

    Django's TestCase:
    - Creates a test database
    - Wraps each test in a transaction (rollback after test)
    - Provides assertion helpers
    """

    def setUp(self):
        """
        Run before each test method.

        Why setUp?
        - Avoid repeating user creation in every test
        - Each test gets a fresh user (transaction rollback)
        """
        self.user = User.objects.create_user(
            username="test_user", email="test@example.com", password="testpass123"
        )

    def test_user_creation(self):
        """Test that user is created with correct fields"""
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)

    def test_user_string_representation(self):
        """Test __str__ returns email"""
        self.assertEqual(str(self.user), "test@example.com")

    def test_email_is_unique(self):
        """Test that duplicate emails are not allowed"""
        with self.assertRaises(Exception):
            User.objects.create_user(
                username="test_user2",
                email="test@example.com",  # Duplicate!
                password="testpass123",
            )


class UserStatsModelTest(TestCase):
    """Tests for UserStats model and business logic"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user", email="test@example.com", password="testpass123"
        )
        # UserStats should be auto-created via signal (we'll add this later)
        # For now, create manually:
        self.stats = UserStats.objects.create(user=self.user)

    def test_stats_creation(self):
        """Test that user stats are created with correct defaults"""
        self.assertEqual(self.stats.total_correct, 0)
        self.assertEqual(self.stats.current_streak, 0)
        self.assertEqual(self.stats.longest_streak, 0)
        self.assertIsNone(self.stats.last_guess_date)
        self.assertEqual(self.stats.incorrect_countries, [])

    def test_update_daily_streak_first_correct(self):
        """Test streak starts at 1 on first correct guess"""
        today = date.today()
        self.stats.update_daily_streak(is_correct=True, guess_date=today)

        self.assertEqual(self.stats.current_streak, 1)
        self.assertEqual(self.stats.longest_streak, 1)
        self.assertEqual(self.stats.total_correct, 1)
        self.assertEqual(self.stats.last_guess_date, today)

    def test_update_daily_streak_consecutive_days(self):
        """Test streak increments on consecutive correct days"""
        today = date.today()
        yesterday = today - timedelta(days=1)

        # First day
        self.stats.update_daily_streak(is_correct=True, guess_date=yesterday)
        self.assertEqual(self.stats.current_streak, 1)

        # Second day (consecutive)
        self.stats.update_daily_streak(is_correct=True, guess_date=today)
        self.assertEqual(self.stats.current_streak, 2)
        self.assertEqual(self.stats.longest_streak, 2)

    def test_update_daily_streak_breaks_on_incorrect(self):
        """Test that incorrect guess resets streak to 0"""
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Build a streak
        self.stats.update_daily_streak(is_correct=True, guess_date=yesterday)
        self.assertEqual(self.stats.current_streak, 1)

        # Break it
        self.stats.update_daily_streak(is_correct=False, guess_date=today)
        self.assertEqual(self.stats.current_streak, 0)
        self.assertEqual(self.stats.longest_streak, 1)  # Longest preserved
        self.assertEqual(self.stats.total_correct, 1)  # Doesn't increment

    def test_update_daily_streak_gap_resets(self):
        """Test that missing a day resets streak to 1"""
        today = date.today()
        three_days_ago = today - timedelta(days=3)

        # Guess 3 days ago
        self.stats.update_daily_streak(is_correct=True, guess_date=three_days_ago)
        self.assertEqual(self.stats.current_streak, 1)

        # Guess today (gap of 2 days)
        self.stats.update_daily_streak(is_correct=True, guess_date=today)
        self.assertEqual(self.stats.current_streak, 1)  # Resets
        self.assertEqual(self.stats.total_correct, 2)  # Still counts

    def test_add_incorrect_country(self):
        """Test adding countries to incorrect list"""
        self.stats.add_incorrect_country("USA")
        self.assertIn("USA", self.stats.incorrect_countries)

        # Adding same country twice doesn't duplicate
        self.stats.add_incorrect_country("USA")
        self.assertEqual(self.stats.incorrect_countries.count("USA"), 1)
