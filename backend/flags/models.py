from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Country(models.Model):
    """
    Represents a country with comprehensive geographic and demographic data.

    Data source: REST Countries API (https://restcountries.com)
    Caching strategy: Eager loading via management command, refresh weekly

    Design decisions:
    - Explicit fields for common queries (fast lookups)
    - raw_api_response stores full JSON (flexibility without migrations)
    - difficulty_tier nullable (MVP doesn't use, Phase 2 activation)
    """

    # === Core Identification ===
    code = models.CharField(
        max_length=3,
        unique=True,
        db_index=True,  # Fast lookups by code
        help_text="ISO 3166-1 alpha-3 code (USA, FRA, JPN)",
    )
    name = models.CharField(
        max_length=100,
        db_index=True,  # Fast lookups for encyclopedia search
        help_text="Official country name",
    )

    # === Visual Assets (URLs from REST Countries API) ===
    flag_svg_url = models.URLField(
        max_length=500, help_text="SVG flag image URL from flagcdn.com"
    )
    flag_png_url = models.URLField(
        max_length=500, help_text="PNG flag image URL (fallback for older browsers)"
    )
    flag_alt_text = models.TextField(
        blank=True, help_text="Descriptive text for flag (accessibility)"
    )

    coat_of_arms_svg_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        help_text="SVG coat of arms URL (not all countries have one)",
    )
    coat_of_arms_png_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        help_text="PNG coat of arms URL (fallback)",
    )

    flag_emoji = models.CharField(max_length=10, help_text="Unicode flag emoji (🇺🇸)")

    # === Geographic Data ===
    # Why separate lat/lng instead of PointField?
    # PointField requires PostGIS extension. For simple display, floats suffice.
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text="Latitude coordinate",
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text="Longitude coordinate",
    )
    area_km2 = models.FloatField(
        validators=[MinValueValidator(0)], help_text="Total area in square kilometers"
    )
    highest_point = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Highest elevation point (Mt. Everest, etc.)",
    )

    # === Demographic Data ===
    population = models.BigIntegerField(
        validators=[MinValueValidator(0)], help_text="Current population estimate"
    )
    capital = models.CharField(max_length=100, help_text="Capital city name")
    largest_city = models.CharField(
        max_length=100, help_text="Most populous city (may differ from capital)"
    )

    # === Cultural Data ===
    # Why JSONField? Arrays of strings. Could use separate Language model
    # with M2M, but that's overkill for display-only data.
    languages = models.JSONField(
        default=list, help_text='List of languages: ["English", "Spanish"]'
    )
    religions = models.JSONField(
        null=True, blank=True, help_text="List of major religions"
    )
    currencies = models.JSONField(
        default=dict,
        help_text='Currency info: {"USD": {"name": "US Dollar", "symbol": "$"}}',
    )

    # === Economic Data ===
    gdp_nominal = models.BigIntegerField(
        null=True, blank=True, help_text="GDP in current USD"
    )
    gdp_ppp_per_capita = models.IntegerField(
        null=True, blank=True, help_text="GDP per capita adjusted for purchasing power"
    )

    # === Social Indicators ===
    median_age = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        help_text="Median age of population",
    )
    life_expectancy = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        help_text="Average life expectancy in years",
    )
    school_expectancy = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Expected years of schooling",
    )
    fertility_rate = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Average births per woman",
    )
    arable_land_percent = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage of land suitable for crops",
    )

    # === Future Features (Phase 2) ===
    difficulty_tier = models.CharField(
        max_length=10,
        choices=[
            ("easy", "Easy"),
            ("medium", "Medium"),
            ("hard", "Hard"),
        ],
        null=True,
        blank=True,
        db_index=True,  # For filtering by difficulty later
        help_text="Recognition difficulty (MVP: unused, Phase 2: active)",
    )
    popularity_score = models.IntegerField(
        default=0, help_text="Algorithm input for tier assignment (search volume, etc.)"
    )

    # === API Caching ===
    api_cache_date = models.DateTimeField(
        auto_now_add=True,  # Set when first loaded from API
        help_text="When we last fetched from REST Countries API",
    )
    raw_api_response = models.JSONField(
        null=True,
        blank=True,
        help_text="Full JSON from REST Countries API for future flexibility",
    )

    # === Timestamps ===
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # === Meta Data ===
    class Meta:
        db_table = "flags_country"
        verbose_name_plural = "Countries"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["name"]),
            models.Index(fields=["difficulty_tier"]),
        ]

    # === Methods ===
    def __str__(self):
        return f"{self.flag_emoji} {self.name}"


class QuestionCategory(models.TextChoices):
    """
    Question categories - what aspect of country we're testing.

    Adding new categories (Phase 3):
    1. Add here: BORDER_COUNTRIES = 'border_countries', 'Bordering Countries'
    2. Add generator in question_generators.py
    3. That's it! No migration needed (CharField handles any string)
    """

    # === Question Type Enums ===
    # TextChoices: Modern Django pattern for enum-like choices
    FLAG = "flag", "Flag Recognition"
    CAPITAL = "capital", "Capital City"
    POPULATION = "population", "Population"
    CURRENCY = "currency", "Currency"
    LANGUAGE = "language", "Language(s)"
    AREA = "area", "Area Size"
    LARGEST_CITY = "largest_city", "Largest City"
    CONTINENT = "continent", "Continent/Region"
    HIGHEST_POINT = "highest_point", "Highest Point"
    GDP = "gdp", "GDP"
    LIFE_EXPECTANCY = "life_expectancy", "Life Expectancy"


class QuestionFormat(models.TextChoices):
    """
    Question formats - how user answers.

    Adding new formats (Phase 3):
    1. Add here: MAP_LOCATION = 'map_location', 'Locate on Map'
    2. Add validation logic in Question.validate_answer()
    3. Update frontend to render this format
    """

    TEXT_INPUT = "text_input", "Text Input"
    MULTIPLE_CHOICE = "multiple_choice", "Multiple Choice"
    TRUE_FALSE = "true_false", "True/False"


class DailyChallenge(models.Model):
    """
    Represents each day's flag challenge.

    Singleton per date - only one challenge exists for each calendar day.
    All users worldwide see the same country on the same date.

    Design decisions:
    - Date is unique (enforced by database)
    - Selection algorithm versioned (can A/B test algorithms later)
    - Difficulty tier nullable (MVP doesn't use)
    """

    # === Core Identification ===
    date = models.DateField(
        unique=True,
        db_index=True,
        help_text="Date of this challenge (timezone: America/New_York)",
    )
    country = models.ForeignKey(
        "Country",  # String reference (forward declaration)
        on_delete=models.PROTECT,  # Never delete country if used in challenge
        related_name="daily_challenges",
        help_text="The country for this day's challenge",
    )

    # === Future Features (Phase 2) ===
    difficulty_tier = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Difficulty tier if using rotation algorithm",
    )

    # Algorithm versioning for A/B testing
    selection_algorithm_version = models.CharField(
        max_length=20,
        default="v1_random",
        help_text="Which algorithm selected this country",
    )

    # === Timestamps ===
    created_at = models.DateTimeField(auto_now_add=True)

    # === Meta Data ===
    class Meta:
        db_table = "flags_dailychallenge"
        ordering = ["-date"]  # Newest first
        indexes = [
            models.Index(fields=["date"]),
        ]

    # === Methods ===
    def __str__(self):
        return f"{self.date} - {self.country.flag_emoji} {self.country.name}"

    @classmethod
    def get_or_create_today(cls):
        """
        Get today's challenge, creating if it doesn't exist.
        Uses DifficultyTierState for country selection.

        TODO: Convert to scheduled Celery task in production to avoid
        race conditions and ensure challenge exists before first request.

        Returns:
            tuple: (DailyChallenge instance, bool created)

        Example:
            challenge, created = DailyChallenge.get_or_create_today()
            print(challenge.country.name)
        """
        from django.utils import timezone

        today = timezone.now().date()

        # Try to get existing challenge
        try:
            return cls.objects.get(date=today), False
        except cls.DoesNotExist:
            pass

        # Get or create the default tier state
        tier_state, _ = DifficultyTierState.objects.get_or_create(
            tier='default',
            user=None,
            defaults={
                'cycle_start_date': today,
            }
        )

        # Select country using tier state
        country = tier_state.select_next_country()

        # Create challenge
        challenge = cls.objects.create(
            date=today,
            country=country,
            selection_algorithm_version='v1_tier_random'
        )

        # Create associated question
        challenge.create_question()

        return challenge, True

    def create_question(self):
        """
        Create the Question for this daily challenge.
        MVP: Always creates a flag recognition text input question.

        Returns:
            Question: The created question instance
        """
        question = Question.objects.create(
            daily_challenge=self,
            category=QuestionCategory.FLAG,
            format=QuestionFormat.TEXT_INPUT,
            country=self.country,
            question_text="Which country does this flag belong to?",
            correct_answer={
                'answer': self.country.name,
                'alternates': []  # TODO: Add common alternates (e.g., "USA" for "United States")
            }
        )
        return question

    def get_question(self):
        """
        Get the question for this challenge.

        Returns:
            Question: The associated question, or None if not found
        """
        return self.questions.first()


class DifficultyTierState(models.Model):
    """
    Tracks cycle state for a difficulty tier.

    MVP: Single 'default' tier with user=NULL for global daily challenge.
    Phase 2: Multiple tiers ('easy', 'medium', 'hard') for difficulty rotation.
    Phase 3: User-specific tiers (user FK set) for quiz mode.

    Design:
    - Tracks which countries shown this cycle
    - Resets when all countries shown
    - Efficient database-level tracking via TierShownCountry
    """

    # === Core Identification ===
    tier = models.CharField(
        max_length=20,
        db_index=True,
        help_text="Tier name: 'default', 'easy', 'medium', 'hard', or custom",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='tier_states',
        help_text="NULL for global daily challenge, FK for user-specific quiz cycles",
    )

    # === Cycle Tracking ===
    cycle_number = models.PositiveIntegerField(
        default=1,
        help_text="Current cycle number (increments when all countries shown)",
    )

    cycle_start_date = models.DateField(
        help_text="When current cycle began",
    )

    last_selection_date = models.DateField(
        null=True,
        blank=True,
        help_text="Most recent country selection date",
    )

    # === Timestamps ===
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # === Meta Data ===
    class Meta:
        db_table = 'flags_difficultytierstate'
        unique_together = ['tier', 'user']
        ordering = ['tier', 'user']

    # === Methods ===
    def __str__(self):
        if self.user:
            return f"{self.user.email} - {self.tier} (cycle {self.cycle_number})"
        return f"Global - {self.tier} (cycle {self.cycle_number})"

    def select_next_country(self):
        """
        Select next country for this tier, handling cycle reset.
        All operations are database-level for efficiency.

        Returns:
            Country: The selected country instance

        Future extensions:
            - Regional filtering: Add region field, filter tier_countries by Country.region
            - User custom tiers: Query UserCountryTier when self.user is set
        """
        from django.utils import timezone

        # Get countries eligible for this tier
        if self.user is None:
            # Global tier (daily challenge)
            if self.tier == 'default':
                tier_countries = Country.objects.all()
            else:
                tier_countries = Country.objects.filter(difficulty_tier=self.tier)
        else:
            # TODO: User-specific tier (Phase 3 quiz mode)
            # Will query UserCountryTier model when implemented
            tier_countries = Country.objects.all()

        # Exclude already shown this cycle (efficient DB subquery)
        shown_country_ids = self.shown_countries.values_list('country_id', flat=True)
        available = tier_countries.exclude(id__in=shown_country_ids)

        # Reset cycle if all shown
        if not available.exists():
            self.shown_countries.all().delete()  # Single DELETE query
            self.cycle_number += 1
            self.cycle_start_date = timezone.now().date()
            self.save()
            available = tier_countries

        # Random selection
        country = available.order_by('?').first()

        # Record as shown
        TierShownCountry.objects.create(tier_state=self, country=country)

        # Update state
        self.last_selection_date = timezone.now().date()
        self.save()

        return country


class TierShownCountry(models.Model):
    """
    Tracks which countries have been shown in a tier's current cycle.

    Records are deleted when cycle resets (all countries shown).
    Efficient lookup via tier_state FK and unique constraint.
    """

    # === Core Identification ===
    tier_state = models.ForeignKey(
        'DifficultyTierState',
        on_delete=models.CASCADE,
        related_name='shown_countries',
        help_text="Which tier state this belongs to",
    )

    country = models.ForeignKey(
        'Country',
        on_delete=models.CASCADE,
        help_text="Country that was shown",
    )

    # === Timestamps ===
    shown_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this country was selected",
    )

    # === Meta Data ===
    class Meta:
        db_table = 'flags_tiershowncountry'
        unique_together = ['tier_state', 'country']
        ordering = ['-shown_at']

    # === Methods ===
    def __str__(self):
        return f"{self.tier_state.tier} - {self.country.name}"


class Question(models.Model):
    """
    Flexible question model supporting multiple categories and formats.

    Key design: JSONField for correct_answer allows any answer structure.
    New question types need NO database migrations.

    Examples:
    - Flag text input: correct_answer = {"answer": "France", "alternates": [...]}
    - Multiple choice: correct_answer = {"correct": "Paris", "options": [...]}
    - True/false: correct_answer = {"answer": true}
    """

    # === Core Identification ===
    category = models.CharField(
        max_length=30,
        choices=QuestionCategory.choices,
        db_index=True,
        help_text="What aspect of the country we're asking about",
    )

    format = models.CharField(
        max_length=30,
        choices=QuestionFormat.choices,
        db_index=True,
        help_text="How the user should answer",
    )

    country = models.ForeignKey(
        "Country",
        on_delete=models.CASCADE,
        related_name="questions",
        help_text="Which country this question is about",
    )

    question_text = models.TextField(help_text="The actual question shown to user")

    # Flexible answer structure (varies by format)
    correct_answer = models.JSONField(
        help_text="Structure depends on format - see Question docstring"
    )

    # Optional metadata for complex questions
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Optional: hints, explanations, difficulty overrides",
    )

    # Links to either daily challenge OR quiz session (not both)
    daily_challenge = models.ForeignKey(
        "DailyChallenge",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="questions",
        help_text="If this is a daily challenge question",
    )

    # === Future Features (Phase 3) ===
    """
    quiz_session = models.ForeignKey(
        "flags.QuizSession",  # Will create this model in Phase 3
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="questions",
        help_text="If this is part of a quiz",
    )
    """

    # === Timestamps ===
    created_at = models.DateTimeField(auto_now_add=True)

    # === Meta Data ===
    class Meta:
        db_table = "flags_question"
        indexes = [
            models.Index(fields=["category", "format"]),
            models.Index(fields=["country"]),
            models.Index(fields=["daily_challenge"]),
        ]

    # === Methods ===
    def __str__(self):
        return f"{self.get_category_display()} - {self.get_format_display()} - {self.country.name}"

    def validate_answer(self, user_answer_data):
        """
        Validate user's answer against correct answer.

        Args:
            user_answer_data (dict): User's answer (structure varies by format)

        Returns:
            tuple: (is_correct: bool, explanation: str)

        Example usage:
            is_correct, explanation = question.validate_answer({
                'text': 'france'
            })
        """
        if self.format == QuestionFormat.TEXT_INPUT:
            return self._validate_text_input(user_answer_data)
        elif self.format == QuestionFormat.MULTIPLE_CHOICE:
            return self._validate_multiple_choice(user_answer_data)
        elif self.format == QuestionFormat.TRUE_FALSE:
            return self._validate_true_false(user_answer_data)
        else:
            return False, "Unknown question format"

    def _validate_text_input(self, user_answer_data):
        """Validate text input answer (case-insensitive, accepts alternates)"""
        user_text = user_answer_data.get("text", "").lower().strip()
        correct = self.correct_answer["answer"].lower()
        alternates = [alt.lower() for alt in self.correct_answer.get("alternates", [])]

        is_correct = user_text == correct or user_text in alternates
        explanation = f"Correct answer: {self.correct_answer['answer']}"

        return is_correct, explanation

    def _validate_multiple_choice(self, user_answer_data):
        """Validate multiple choice answer"""
        user_choice = user_answer_data.get("selected_option")
        is_correct = user_choice == self.correct_answer["correct"]
        explanation = f"Correct answer: {self.correct_answer['correct']}"

        return is_correct, explanation

    def _validate_true_false(self, user_answer_data):
        """Validate true/false answer"""
        user_bool = user_answer_data.get("answer")
        is_correct = user_bool == self.correct_answer["answer"]
        explanation = f"The statement is {self.correct_answer['answer']}"

        return is_correct, explanation


class UserAnswer(models.Model):
    """
    Records a user's answer to a question.

    Why separate from Question?
    - Multiple users answer same question
    - Track attempts (daily challenge allows 3)
    - Performance metrics (time taken)
    """

    # === Core Identification ===
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="answers",
        help_text="User who submitted this answer",
    )

    question = models.ForeignKey(
        "Question",
        on_delete=models.CASCADE,
        related_name="user_answers",
        help_text="Which question this answers",
    )

    # Flexible answer structure (matches question format)
    answer_data = models.JSONField(
        help_text="User's answer - structure matches question format"
    )

    is_correct = models.BooleanField(help_text="Whether the answer was correct")

    explanation = models.TextField(
        blank=True, help_text="Why the answer was correct/incorrect"
    )

    # For daily challenge's 3-attempt limit
    attempt_number = models.IntegerField(
        default=1, help_text="Attempt number (1, 2, or 3 for daily challenges)"
    )

    # Performance tracking
    time_taken_seconds = models.IntegerField(
        null=True, blank=True, help_text="How long user took to answer (optional)"
    )

    # === Timestamps ===
    answered_at = models.DateTimeField(auto_now_add=True)

    # === Meta Data ===
    class Meta:
        db_table = "flags_useranswer"
        ordering = ["-answered_at"]
        indexes = [
            models.Index(fields=["user", "question"]),
            models.Index(fields=["user", "is_correct"]),
            models.Index(fields=["question"]),
        ]

    # === Methods ===
    def __str__(self):
        status = "✓" if self.is_correct else "✗"
        return f"{status} {self.user.email} - {self.question}"
