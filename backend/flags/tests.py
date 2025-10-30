from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from flags.models import (
    Country,
    DailyChallenge,
    Question,
    QuestionCategory,
    QuestionFormat,
    UserAnswer,
)

User = get_user_model()


class CountryModelTest(TestCase):
    """Tests for Country model"""

    def setUp(self):
        self.country = Country.objects.create(
            code="USA",
            name="United States",
            flag_emoji="🇺🇸",
            flag_svg_url="https://flagcdn.com/us.svg",
            flag_png_url="https://flagcdn.com/w320/us.png",
            flag_alt_text="The flag of the United States of America is composed of...",
            coat_of_arms_svg_url="https://mainfacts.com/media/images/coats_of_arms/us.svg",
            coat_of_arms_png_url="https://mainfacts.com/media/images/coats_of_arms/us.png",
            population=331000000,
            capital="Washington, D.C.",
            largest_city="New York City",
            languages=["English"],
            area_km2=9833520,
            currencies={"USD": {"name": "US Dollar", "symbol": "$"}},
            latitude=37.0902,
            longitude=-95.7129,
        )

    def test_country_creation(self):
        """Test country is created with all required fields"""
        self.assertEqual(self.country.code, "USA")
        self.assertEqual(self.country.name, "United States")
        self.assertEqual(self.country.population, 331000000)

    def test_country_string_representation(self):
        """Test __str__ includes flag emoji and name"""
        self.assertEqual(str(self.country), "🇺🇸 United States")

    def test_code_is_unique(self):
        """Test that country codes must be unique"""
        with self.assertRaises(Exception):
            Country.objects.create(
                code="USA",  # Duplicate!
                name="Another USA",
                flag_emoji="🇺🇸",
                flag_svg_url="https://flagcdn.com/us.svg",
                flag_png_url="https://flagcdn.com/w320/us.png",
                flag_alt_text="The flag of the United States of America is composed of...",
                coat_of_arms_svg_url="https://mainfacts.com/media/images/coats_of_arms/us.svg",
                coat_of_arms_png_url="https://mainfacts.com/media/images/coats_of_arms/us.png",
                population=1,
                capital="X",
                largest_city="Y",
                languages=[],
                area_km2=1,
                currencies={},
                latitude=0,
                longitude=0,
            )


class DailyChallengeModelTest(TestCase):
    """Tests for DailyChallenge model and selection algorithm"""

    def setUp(self):
        # Create test countries
        self.usa = Country.objects.create(
            code="USA",
            name="United States",
            flag_emoji="🇺🇸",
            flag_svg_url="https://flagcdn.com/us.svg",
            flag_png_url="https://flagcdn.com/w320/us.png",
            flag_alt_text="The flag of the United States of America is composed of...",
            coat_of_arms_svg_url="https://mainfacts.com/media/images/coats_of_arms/us.svg",
            coat_of_arms_png_url="https://mainfacts.com/media/images/coats_of_arms/us.png",
            population=331000000,
            capital="Washington",
            largest_city="NYC",
            languages=[],
            area_km2=1,
            currencies={},
            latitude=0,
            longitude=0,
        )
        self.france = Country.objects.create(
            code="FRA",
            name="France",
            flag_emoji="🇫🇷",
            flag_svg_url="https://flagcdn.com/fr.svg",
            flag_png_url="https://flagcdn.com/w320/fr.png",
            flag_alt_text="The flag of France is composed of three equal vertical bands...",
            coat_of_arms_svg_url="https://mainfacts.com/media/images/coats_of_arms/fr.svg",
            coat_of_arms_png_url="https://mainfacts.com/media/images/coats_of_arms/fr.png",
            population=67000000,
            capital="Paris",
            largest_city="Paris",
            languages=[],
            area_km2=1,
            currencies={},
            latitude=0,
            longitude=0,
        )

    def test_get_or_create_today_creates_new(self):
        """Test that get_or_create_today creates challenge if doesn't exist"""
        challenge = DailyChallenge.get_or_create_today()

        self.assertIsNotNone(challenge)
        self.assertEqual(challenge.date, date.today())
        self.assertIn(challenge.country, [self.usa, self.france])

    def test_get_or_create_today_returns_existing(self):
        """Test that get_or_create_today doesn't create duplicate"""
        challenge1 = DailyChallenge.get_or_create_today()
        challenge2 = DailyChallenge.get_or_create_today()

        # Should be the same object
        self.assertEqual(challenge1.id, challenge2.id)
        self.assertEqual(challenge1.country, challenge2.country)

    def test_selection_algorithm_no_repeats(self):
        """Test that algorithm doesn't repeat until all countries shown"""
        # Show USA today
        DailyChallenge.objects.create(date=date.today(), country=self.usa)

        # Tomorrow should be France (only remaining country)
        tomorrow_country = DailyChallenge._select_random_country()
        self.assertEqual(tomorrow_country, self.france)

    def test_selection_algorithm_resets(self):
        """Test that algorithm resets after all countries shown"""
        # Show both countries
        DailyChallenge.objects.create(date=date(2024, 1, 1), country=self.usa)
        DailyChallenge.objects.create(date=date(2024, 1, 2), country=self.france)

        # Next selection should reset and choose from all countries
        next_country = DailyChallenge._select_random_country()
        self.assertIn(next_country, [self.usa, self.france])


class QuestionModelTest(TestCase):
    """Tests for Question model and answer validation"""

    def setUp(self):
        self.country = Country.objects.create(
            code="USA",
            name="United States",
            flag_emoji="🇺🇸",
            flag_svg_url="https://flagcdn.com/us.svg",
            flag_png_url="https://flagcdn.com/w320/us.png",
            flag_alt_text="The flag of the United States of America is composed of...",
            coat_of_arms_svg_url="https://mainfacts.com/media/images/coats_of_arms/us.svg",
            coat_of_arms_png_url="https://mainfacts.com/media/images/coats_of_arms/us.png",
            population=331000000,
            capital="Washington",
            largest_city="NYC",
            languages=[],
            area_km2=1,
            currencies={},
            latitude=0,
            longitude=0,
        )

    def test_text_input_validation_correct(self):
        """Test text input validation accepts correct answer"""
        question = Question.objects.create(
            category=QuestionCategory.FLAG,
            format=QuestionFormat.TEXT_INPUT,
            country=self.country,
            question_text="Which country?",
            correct_answer={
                "answer": "United States",
                "alternates": ["USA", "United States of America"],
            },
        )

        # Test exact match (case insensitive)
        is_correct, explanation = question.validate_answer({"text": "united states"})
        self.assertTrue(is_correct)

        # Test alternate
        is_correct, explanation = question.validate_answer({"text": "USA"})
        self.assertTrue(is_correct)

    def test_text_input_validation_incorrect(self):
        """Test text input validation rejects incorrect answer"""
        question = Question.objects.create(
            category=QuestionCategory.FLAG,
            format=QuestionFormat.TEXT_INPUT,
            country=self.country,
            question_text="Which country?",
            correct_answer={"answer": "United States", "alternates": []},
        )

        is_correct, explanation = question.validate_answer({"text": "France"})
        self.assertFalse(is_correct)

    def test_multiple_choice_validation(self):
        """Test multiple choice validation"""
        question = Question.objects.create(
            category=QuestionCategory.CAPITAL,
            format=QuestionFormat.MULTIPLE_CHOICE,
            country=self.country,
            question_text="What is the capital?",
            correct_answer={
                "correct": "Washington",
                "options": ["Washington", "New York", "Boston", "Chicago"],
            },
        )

        # Correct
        is_correct, explanation = question.validate_answer(
            {"selected_option": "Washington"}
        )
        self.assertTrue(is_correct)

        # Incorrect
        is_correct, explanation = question.validate_answer(
            {"selected_option": "New York"}
        )
        self.assertFalse(is_correct)


class UserAnswerModelTest(TestCase):
    """Tests for UserAnswer model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="test", email="test@example.com", password="pass"
        )
        self.country = Country.objects.create(
            code="USA",
            name="United States",
            flag_emoji="🇺🇸",
            flag_svg_url="https://flagcdn.com/us.svg",
            flag_png_url="https://flagcdn.com/w320/us.png",
            flag_alt_text="The flag of the United States of America is composed of...",
            coat_of_arms_svg_url="https://mainfacts.com/media/images/coats_of_arms/us.svg",
            coat_of_arms_png_url="https://mainfacts.com/media/images/coats_of_arms/us.png",
            population=1,
            capital="X",
            largest_city="Y",
            languages=[],
            area_km2=1,
            currencies={},
            latitude=0,
            longitude=0,
        )
        self.question = Question.objects.create(
            category=QuestionCategory.FLAG,
            format=QuestionFormat.TEXT_INPUT,
            country=self.country,
            question_text="Which country?",
            correct_answer={"answer": "United States", "alternates": []},
        )

    def test_user_answer_creation(self):
        """Test creating a user answer"""
        answer = UserAnswer.objects.create(
            user=self.user,
            question=self.question,
            answer_data={"text": "United States"},
            is_correct=True,
            explanation="Correct!",
            attempt_number=1,
        )

        self.assertEqual(answer.user, self.user)
        self.assertEqual(answer.question, self.question)
        self.assertTrue(answer.is_correct)
        self.assertEqual(answer.attempt_number, 1)


class CountryImageFieldsTest(TestCase):
    """Test flag and coat of arms image fields"""

    def test_country_with_all_images(self):
        """Test country creation with all image URLs"""
        country = Country.objects.create(
            code="FRA",
            name="France",
            flag_emoji="🇫🇷",
            flag_svg_url="https://flagcdn.com/fr.svg",
            flag_png_url="https://flagcdn.com/w320/fr.png",
            flag_alt_text="The flag of France is composed of three equal vertical bands...",
            coat_of_arms_svg_url="https://mainfacts.com/media/images/coats_of_arms/fr.svg",
            coat_of_arms_png_url="https://mainfacts.com/media/images/coats_of_arms/fr.png",
            population=67000000,
            capital="Paris",
            largest_city="Paris",
            languages=["French"],
            area_km2=551695,
            currencies={"EUR": {"name": "Euro", "symbol": "€"}},
            latitude=46.2276,
            longitude=2.2137,
        )

        self.assertEqual(country.flag_svg_url, "https://flagcdn.com/fr.svg")
        self.assertIsNotNone(country.coat_of_arms_svg_url)

    def test_country_without_coat_of_arms(self):
        """Test that coat of arms is optional"""
        country = Country.objects.create(
            code="ATA",
            name="Antarctica",
            flag_emoji="🇦🇶",
            flag_svg_url="https://flagcdn.com/aq.svg",
            flag_png_url="https://flagcdn.com/w320/aq.png",
            flag_alt_text="Antarctica flag",
            # No coat of arms!
            population=1000,
            capital="N/A",
            largest_city="N/A",
            languages=[],
            area_km2=14000000,
            currencies={},
            latitude=-75.250973,
            longitude=-0.071389,
        )

        self.assertIsNone(country.coat_of_arms_svg_url)
        self.assertIsNone(country.coat_of_arms_png_url)
