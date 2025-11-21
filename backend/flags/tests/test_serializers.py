"""
Test serializers work correctly.
"""

from django.test import TestCase
from django.utils import timezone
from users.models import User, UserStats
from users.serializers import UserSerializer

from flags.models import Country, DailyChallenge, Question
from flags.serializers import (
    CountryDetailSerializer,
    QuestionSerializer,
)


class CountrySerializerTest(TestCase):
    """Test country serialization."""

    def setUp(self):
        """Create test country."""
        self.country = Country.objects.create(
            code="TST",
            name="Test Country",
            flag_emoji="🏳️",
            flag_svg_url="https://example.com/flag.svg",
            flag_png_url="https://example.com/flag.png",
            flag_alt_text="Test flag",
            population=1000000,
            capital="Test City",
            largest_city="Test City",
            languages=["English"],
            area_km2=100000,
            currencies={"USD": "US Dollar"},
            latitude=0.0,
            longitude=0.0,
        )

    def test_country_serialization(self):
        """Test serializer includes all expected fields."""
        serializer = CountryDetailSerializer(self.country)
        data = serializer.data

        # Check key fields present
        self.assertEqual(data["code"], "TST")
        self.assertEqual(data["name"], "Test Country")
        self.assertEqual(data["flag_emoji"], "🏳️")
        self.assertIn("population", data)
        self.assertIn("capital", data)


class UserSerializerTest(TestCase):
    """Test user serialization with nested stats."""

    def setUp(self):
        """Create test user with stats."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="test123"
        )
        # UserStats created automatically by signal (if you added that)
        # Or create manually:
        UserStats.objects.create(user=self.user)

    def test_user_with_stats(self):
        """Test user serializer includes nested stats."""
        serializer = UserSerializer(self.user)
        data = serializer.data

        # Check user fields
        self.assertEqual(data["email"], "test@example.com")
        self.assertEqual(data["username"], "testuser")

        # Check nested stats
        self.assertIn("stats", data)
        self.assertEqual(data["stats"]["total_correct"], 0)
        self.assertEqual(data["stats"]["current_streak"], 0)


class QuestionSerializerTest(TestCase):
    """Test question serializer excludes answer."""

    def setUp(self):
        """Create test question."""
        country = Country.objects.create(
            code="TST",
            name="Test",
            flag_emoji="🏳️",
            flag_svg_url="https://example.com/flag.svg",
            flag_png_url="https://example.com/flag.png",
            flag_alt_text="Test",
            population=1000000,
            capital="Test",
            largest_city="Test",
            languages=["English"],
            area_km2=100000,
            currencies={"USD": "US Dollar"},
            latitude=0.0,
            longitude=0.0,
        )

        self.question = Question.objects.create(
            category="flag",
            format="text_input",
            country=country,
            question_text="What country is this?",
            correct_answer={"answer": "Test", "alternates": []},
        )

    def test_question_excludes_answer(self):
        """Test serializer does NOT include correct_answer."""
        serializer = QuestionSerializer(self.question)
        data = serializer.data

        # Should have question data
        self.assertIn("question_text", data)
        self.assertEqual(data["question_text"], "What country is this?")

        # Should NOT have answer
        self.assertNotIn("correct_answer", data)

        # Should have country info
        self.assertEqual(data["country_code"], "TST")
        self.assertEqual(data["country_name"], "Test")
