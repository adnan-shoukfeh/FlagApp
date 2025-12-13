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


class DailyChallengeAnswerAPITests(APITestCase):
    """Tests for daily challenge answer submission endpoint."""

    def setUp(self):
        """Create test user and countries."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create test country with a known name
        self.country = Country.objects.create(
            code="FRA",
            name="France",
            flag_emoji="🇫🇷",
            flag_svg_url="http://example.com/fra.svg",
            flag_png_url="http://example.com/fra.png",
            flag_alt_text="Flag of France",
            latitude=46.0,
            longitude=2.0,
            area_km2=640679.0,
            population=67000000,
            capital="Paris",
            largest_city="Paris",
        )

        # Create today's challenge with this country
        today = timezone.now().date()
        self.challenge = DailyChallenge.objects.create(
            date=today,
            country=self.country,
        )
        self.question = self.challenge.create_question()

    def test_answer_submission_correct(self):
        """Test submitting a correct answer."""
        response = self.client.post('/api/v1/daily/answer/', {
            'answer_data': {'text': 'France'}
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_correct'])
        self.assertEqual(response.data['attempts_remaining'], 2)
        self.assertIn('user_answer_id', response.data)
        # correct_answer revealed on correct answer
        self.assertIn('correct_answer', response.data)

    def test_answer_submission_incorrect(self):
        """Test submitting an incorrect answer."""
        response = self.client.post('/api/v1/daily/answer/', {
            'answer_data': {'text': 'Germany'}
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_correct'])
        self.assertEqual(response.data['attempts_remaining'], 2)
        # correct_answer NOT revealed (still have attempts)
        self.assertNotIn('correct_answer', response.data)

    def test_answer_submission_case_insensitive(self):
        """Test that answer validation is case-insensitive."""
        response = self.client.post('/api/v1/daily/answer/', {
            'answer_data': {'text': 'FRANCE'}
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_correct'])

    def test_answer_submission_with_time_taken(self):
        """Test submitting answer with time_taken_seconds."""
        response = self.client.post('/api/v1/daily/answer/', {
            'answer_data': {'text': 'France'},
            'time_taken_seconds': 15
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify time was recorded
        user_answer = UserAnswer.objects.get(id=response.data['user_answer_id'])
        self.assertEqual(user_answer.time_taken_seconds, 15)

    def test_answer_submission_requires_auth(self):
        """Test that answer submission requires authentication."""
        self.client.logout()
        response = self.client.post('/api/v1/daily/answer/', {
            'answer_data': {'text': 'France'}
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_answer_submission_invalid_data(self):
        """Test submitting invalid answer data."""
        # Missing answer_data
        response = self.client.post('/api/v1/daily/answer/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # answer_data is not an object
        response = self.client.post('/api/v1/daily/answer/', {
            'answer_data': 'France'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_answer_submission_max_attempts(self):
        """Test that only 3 attempts are allowed."""
        # Submit 3 wrong answers
        for i in range(3):
            response = self.client.post('/api/v1/daily/answer/', {
                'answer_data': {'text': f'Wrong{i}'}
            }, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 4th attempt should be rejected
        response = self.client.post('/api/v1/daily/answer/', {
            'answer_data': {'text': 'France'}
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('No attempts remaining', response.data['error'])

    def test_answer_submission_correct_answer_revealed_on_exhaustion(self):
        """Test that correct_answer is revealed when attempts are exhausted."""
        # Submit 2 wrong answers
        for i in range(2):
            self.client.post('/api/v1/daily/answer/', {
                'answer_data': {'text': f'Wrong{i}'}
            }, format='json')

        # 3rd (final) wrong answer
        response = self.client.post('/api/v1/daily/answer/', {
            'answer_data': {'text': 'Wrong3'}
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_correct'])
        self.assertEqual(response.data['attempts_remaining'], 0)
        # correct_answer SHOULD be revealed
        self.assertIn('correct_answer', response.data)
        self.assertEqual(response.data['correct_answer']['answer'], 'France')

    def test_answer_submission_prevents_duplicate_correct(self):
        """Test that user cannot submit after correct answer."""
        # Submit correct answer
        self.client.post('/api/v1/daily/answer/', {
            'answer_data': {'text': 'France'}
        }, format='json')

        # Try to submit again
        response = self.client.post('/api/v1/daily/answer/', {
            'answer_data': {'text': 'France'}
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('already answered', response.data['error'])

    def test_answer_submission_updates_streak_on_correct(self):
        """Test that streak is updated on correct answer."""
        from users.models import UserStats

        # Ensure stats exist
        stats, _ = UserStats.objects.get_or_create(user=self.user)
        initial_correct = stats.total_correct

        # Submit correct answer
        self.client.post('/api/v1/daily/answer/', {
            'answer_data': {'text': 'France'}
        }, format='json')

        # Verify stats updated
        stats.refresh_from_db()
        self.assertEqual(stats.current_streak, 1)  # First correct = streak of 1
        self.assertEqual(stats.total_correct, initial_correct + 1)

    def test_answer_submission_updates_streak_on_failure(self):
        """Test that streak is reset and country tracked on failure."""
        from users.models import UserStats

        # Set up a streak
        stats, _ = UserStats.objects.get_or_create(user=self.user)
        stats.current_streak = 5
        stats.save()

        # Exhaust all attempts with wrong answers
        for i in range(3):
            self.client.post('/api/v1/daily/answer/', {
                'answer_data': {'text': f'Wrong{i}'}
            }, format='json')

        # Verify stats updated
        stats.refresh_from_db()
        self.assertEqual(stats.current_streak, 0)  # Streak broken
        self.assertIn('FRA', stats.incorrect_countries)

    def test_answer_submission_streak_not_updated_on_intermediate_wrong(self):
        """Test that streak is NOT updated on wrong answer if attempts remain."""
        from users.models import UserStats

        # Set up a streak
        stats, _ = UserStats.objects.get_or_create(user=self.user)
        stats.current_streak = 5
        stats.save()

        # Submit one wrong answer (2 attempts remain)
        self.client.post('/api/v1/daily/answer/', {
            'answer_data': {'text': 'Wrong'}
        }, format='json')

        # Verify streak NOT changed yet
        stats.refresh_from_db()
        self.assertEqual(stats.current_streak, 5)  # Still 5

    def test_answer_submission_creates_user_answer(self):
        """Test that UserAnswer record is created."""
        response = self.client.post('/api/v1/daily/answer/', {
            'answer_data': {'text': 'France'}
        }, format='json')

        # Verify UserAnswer created
        user_answer = UserAnswer.objects.get(
            user=self.user,
            question=self.question
        )
        self.assertEqual(user_answer.answer_data, {'text': 'France'})
        self.assertTrue(user_answer.is_correct)
        self.assertEqual(user_answer.attempt_number, 1)

    def test_answer_submission_attempt_numbers(self):
        """Test that attempt_number increments correctly."""
        # Submit 3 wrong answers
        for i in range(3):
            self.client.post('/api/v1/daily/answer/', {
                'answer_data': {'text': f'Wrong{i}'}
            }, format='json')

        # Verify attempt numbers
        answers = UserAnswer.objects.filter(
            user=self.user,
            question=self.question
        ).order_by('attempt_number')

        self.assertEqual(answers.count(), 3)
        for i, answer in enumerate(answers, 1):
            self.assertEqual(answer.attempt_number, i)
