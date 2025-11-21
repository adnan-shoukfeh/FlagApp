"""
Tests for daily challenge system.

Tests cover:
- DifficultyTierState model and country selection
- DailyChallenge model methods
- Daily challenge API endpoints
- Challenge history API endpoints
- Security (no answer leaks)
"""

from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from users.models import User
from flags.models import (
    Country,
    DailyChallenge,
    DifficultyTierState,
    TierShownCountry,
    Question,
    QuestionCategory,
    QuestionFormat,
    UserAnswer,
)


class DifficultyTierStateModelTests(TestCase):
    """Tests for DifficultyTierState model."""

    def setUp(self):
        """Create test countries."""
        self.countries = []
        for i in range(5):
            country = Country.objects.create(
                code=f"C{i:02d}",
                name=f"Country {i}",
                flag_emoji=f"🏴",
                flag_svg_url=f"http://example.com/{i}.svg",
                flag_png_url=f"http://example.com/{i}.png",
                flag_alt_text=f"Flag {i}",
                latitude=0.0,
                longitude=0.0,
                area_km2=1000.0,
                population=1000000,
                capital=f"Capital {i}",
                largest_city=f"City {i}",
            )
            self.countries.append(country)

    def test_difficulty_tier_state_creation(self):
        """Test creating a DifficultyTierState."""
        today = timezone.now().date()
        tier_state = DifficultyTierState.objects.create(
            tier='default',
            cycle_start_date=today,
        )

        self.assertEqual(tier_state.tier, 'default')
        self.assertEqual(tier_state.cycle_number, 1)
        self.assertIsNone(tier_state.user)
        self.assertEqual(tier_state.cycle_start_date, today)

    def test_difficulty_tier_state_select_next_country(self):
        """Test selecting next country."""
        today = timezone.now().date()
        tier_state = DifficultyTierState.objects.create(
            tier='default',
            cycle_start_date=today,
        )

        country = tier_state.select_next_country()

        # Verify a country was returned
        self.assertIsNotNone(country)
        self.assertIn(country, self.countries)

        # Verify TierShownCountry record created
        shown = TierShownCountry.objects.filter(
            tier_state=tier_state,
            country=country
        )
        self.assertTrue(shown.exists())

        # Verify last_selection_date updated
        tier_state.refresh_from_db()
        self.assertEqual(tier_state.last_selection_date, today)

    def test_difficulty_tier_state_no_duplicate_selection(self):
        """Test that countries aren't selected twice in same cycle."""
        today = timezone.now().date()
        tier_state = DifficultyTierState.objects.create(
            tier='default',
            cycle_start_date=today,
        )

        selected_countries = set()

        # Select all countries
        for i in range(len(self.countries)):
            country = tier_state.select_next_country()
            selected_countries.add(country.code)

        # Verify all countries were selected exactly once
        all_codes = {c.code for c in self.countries}
        self.assertEqual(selected_countries, all_codes)

    def test_difficulty_tier_state_cycle_reset(self):
        """Test cycle reset when all countries shown."""
        today = timezone.now().date()
        tier_state = DifficultyTierState.objects.create(
            tier='default',
            cycle_start_date=today,
        )

        # Select all countries (exhausts cycle)
        for i in range(len(self.countries)):
            tier_state.select_next_country()

        # Verify cycle_number is still 1 (hasn't cycled yet)
        tier_state.refresh_from_db()
        self.assertEqual(tier_state.cycle_number, 1)
        self.assertEqual(tier_state.shown_countries.count(), len(self.countries))

        # Select one more country (should trigger cycle reset)
        country = tier_state.select_next_country()

        # Verify cycle reset
        tier_state.refresh_from_db()
        self.assertEqual(tier_state.cycle_number, 2)
        self.assertEqual(tier_state.shown_countries.count(), 1)  # Only new selection
        self.assertIsNotNone(country)


class DailyChallengeModelTests(TestCase):
    """Tests for DailyChallenge model methods."""

    def setUp(self):
        """Create test country."""
        self.country = Country.objects.create(
            code="TST",
            name="Test Country",
            flag_emoji="🏴",
            flag_svg_url="http://example.com/test.svg",
            flag_png_url="http://example.com/test.png",
            flag_alt_text="Test flag",
            latitude=0.0,
            longitude=0.0,
            area_km2=1000.0,
            population=1000000,
            capital="Test Capital",
            largest_city="Test City",
        )

    def test_daily_challenge_get_or_create_today(self):
        """Test getting/creating today's challenge."""
        challenge, created = DailyChallenge.get_or_create_today()

        # Verify challenge created
        self.assertTrue(created)
        self.assertIsNotNone(challenge)
        self.assertEqual(challenge.date, timezone.now().date())
        self.assertIsNotNone(challenge.country)

        # Verify Question was created
        question = challenge.get_question()
        self.assertIsNotNone(question)
        self.assertEqual(question.category, QuestionCategory.FLAG)
        self.assertEqual(question.format, QuestionFormat.TEXT_INPUT)
        self.assertEqual(question.country, challenge.country)

    def test_daily_challenge_get_or_create_today_idempotent(self):
        """Test that calling get_or_create_today twice returns same challenge."""
        challenge1, created1 = DailyChallenge.get_or_create_today()
        challenge2, created2 = DailyChallenge.get_or_create_today()

        # First call creates, second returns existing
        self.assertTrue(created1)
        self.assertFalse(created2)
        self.assertEqual(challenge1.id, challenge2.id)
        self.assertEqual(challenge1.country, challenge2.country)

        # Verify only one challenge exists for today
        today = timezone.now().date()
        count = DailyChallenge.objects.filter(date=today).count()
        self.assertEqual(count, 1)


class DailyChallengeAPITests(APITestCase):
    """Tests for daily challenge API endpoints."""

    def setUp(self):
        """Create test user and countries."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create test countries
        for i in range(3):
            Country.objects.create(
                code=f"C{i:02d}",
                name=f"Country {i}",
                flag_emoji="🏴",
                flag_svg_url=f"http://example.com/{i}.svg",
                flag_png_url=f"http://example.com/{i}.png",
                flag_alt_text=f"Flag {i}",
                latitude=0.0,
                longitude=0.0,
                area_km2=1000.0,
                population=1000000,
                capital=f"Capital {i}",
                largest_city=f"City {i}",
            )

    def test_daily_challenge_endpoint_returns_challenge(self):
        """Test GET /api/v1/daily/ returns challenge."""
        response = self.client.get('/api/v1/daily/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertIn('date', response.data)
        self.assertIn('question', response.data)
        self.assertIn('country', response.data)
        self.assertIn('user_status', response.data)

    def test_daily_challenge_endpoint_requires_auth(self):
        """Test GET /api/v1/daily/ requires authentication."""
        self.client.logout()
        response = self.client.get('/api/v1/daily/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_daily_challenge_no_answer_leak(self):
        """Test that correct_answer is NOT in response."""
        response = self.client.get('/api/v1/daily/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify correct_answer NOT in question
        self.assertNotIn('correct_answer', response.data['question'])

        # Verify country name NOT in response (only flag data)
        self.assertNotIn('name', response.data['country'])
        self.assertIn('flag_emoji', response.data['country'])
        self.assertIn('flag_svg_url', response.data['country'])

    def test_daily_challenge_user_status_no_attempts(self):
        """Test user_status when user has no attempts."""
        response = self.client.get('/api/v1/daily/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_status = response.data['user_status']

        self.assertEqual(user_status['attempts_used'], 0)
        self.assertEqual(user_status['attempts_remaining'], 3)
        self.assertFalse(user_status['has_completed'])
        self.assertIsNone(user_status['is_correct'])
        self.assertIsNone(user_status['last_attempt_at'])

    def test_daily_challenge_history_returns_past_challenges(self):
        """Test GET /api/v1/daily/history/ returns past challenges."""
        # Create past challenges
        today = timezone.now().date()
        for i in range(3):
            date = today - timedelta(days=i+1)
            country = Country.objects.all()[i]
            challenge = DailyChallenge.objects.create(
                date=date,
                country=country,
            )
            challenge.create_question()

        response = self.client.get('/api/v1/daily/history/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreaterEqual(len(response.data['results']), 3)

    def test_daily_challenge_history_excludes_today(self):
        """Test that history excludes today's challenge."""
        # Create today's challenge
        DailyChallenge.get_or_create_today()

        # Create a past challenge
        yesterday = timezone.now().date() - timedelta(days=1)
        country = Country.objects.first()
        past_challenge = DailyChallenge.objects.create(
            date=yesterday,
            country=country,
        )
        past_challenge.create_question()

        response = self.client.get('/api/v1/daily/history/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify today's challenge NOT in results
        today = timezone.now().date()
        result_dates = [item['date'] for item in response.data['results']]
        self.assertNotIn(str(today), result_dates)

        # Verify yesterday's challenge IS in results
        self.assertIn(str(yesterday), result_dates)

    def test_daily_challenge_history_includes_user_answers(self):
        """Test that history includes user's answer data."""
        # Create past challenge
        yesterday = timezone.now().date() - timedelta(days=1)
        country = Country.objects.first()
        challenge = DailyChallenge.objects.create(
            date=yesterday,
            country=country,
        )
        question = challenge.create_question()

        # Create user answer
        UserAnswer.objects.create(
            user=self.user,
            question=question,
            answer_data={'text': 'Wrong Answer'},
            is_correct=False,
            attempt_number=1,
        )

        response = self.client.get('/api/v1/daily/history/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Find yesterday's challenge in results
        yesterday_item = None
        for item in response.data['results']:
            if item['date'] == str(yesterday):
                yesterday_item = item
                break

        self.assertIsNotNone(yesterday_item)
        self.assertIsNotNone(yesterday_item['user_answer'])
        self.assertEqual(yesterday_item['user_answer']['is_correct'], False)
        self.assertEqual(yesterday_item['user_answer']['attempts_used'], 1)
