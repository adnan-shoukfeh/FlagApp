"""
Daily challenge serializers for the daily flag challenge feature.

Serializer hierarchy:
- DailyChallengeCountrySerializer: Minimal country data (flag only, no name)
- DailyChallengeQuestionSerializer: Question without correct_answer
- UserChallengeStatusSerializer: User's progress on challenge
- DailyChallengeResponseSerializer: Complete response for GET /api/v1/daily/
- DailyChallengeHistoryItemSerializer: Individual items in history
"""

from rest_framework import serializers

from flags.models import DailyChallenge, Question, Country
from .country_serializers import CountryListSerializer


class DailyChallengeCountrySerializer(serializers.ModelSerializer):
    """
    Minimal country data for daily challenge.

    SECURITY: Only flag data - name is excluded as it's the answer!
    Pattern: Separate serializer for security-sensitive contexts.
    """

    class Meta:
        model = Country
        fields = [
            'flag_emoji',
            'flag_svg_url',
            'flag_png_url',
            'flag_alt_text',
        ]
        # IMPORTANT: 'name' is NOT included - it's the answer!


class DailyChallengeQuestionSerializer(serializers.ModelSerializer):
    """
    Question serializer for daily challenge.

    SECURITY: Explicitly excludes correct_answer field.
    Pattern: Security-conscious serialization.
    """

    class Meta:
        model = Question
        fields = [
            'id',
            'category',
            'format',
            'question_text',
            'metadata',
        ]
        # IMPORTANT: 'correct_answer' is EXCLUDED for security


class UserChallengeStatusSerializer(serializers.Serializer):
    """
    User's status for a specific challenge.

    Pattern: Non-model serializer for computed/aggregated data.
    """

    has_completed = serializers.BooleanField(
        help_text="True if user has correct answer OR exhausted attempts"
    )
    attempts_used = serializers.IntegerField(
        help_text="Number of attempts used (0-3)"
    )
    attempts_remaining = serializers.IntegerField(
        help_text="Attempts left (3 - attempts_used)"
    )
    is_correct = serializers.BooleanField(
        allow_null=True,
        help_text="True if correct, False if wrong and exhausted, None if in progress"
    )
    last_attempt_at = serializers.DateTimeField(
        allow_null=True,
        help_text="Timestamp of most recent attempt, None if no attempts"
    )


class DailyChallengeResponseSerializer(serializers.Serializer):
    """
    Complete response for GET /api/v1/daily/ endpoint.

    Pattern: Response serializer combining data from multiple sources.
    This is not backed by a model - it's an API contract.
    """

    id = serializers.IntegerField()
    date = serializers.DateField()
    question = DailyChallengeQuestionSerializer()
    country = DailyChallengeCountrySerializer()
    user_status = UserChallengeStatusSerializer()


class DailyChallengeHistoryItemSerializer(serializers.ModelSerializer):
    """
    Individual item in challenge history endpoint.

    Pattern: Nested serializers for list views with user-specific data.
    For past challenges, we CAN show the country name (answer is already known).
    """

    country = CountryListSerializer(read_only=True)
    user_answer = serializers.SerializerMethodField()

    class Meta:
        model = DailyChallenge
        fields = [
            'id',
            'date',
            'country',
            'user_answer',
        ]

    def get_user_answer(self, obj):
        """
        Get user's answer data for this challenge.

        Returns:
            dict or None: Answer data if user participated, None otherwise
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None

        # Get the question for this challenge
        question = obj.get_question()
        if not question:
            return None

        # Get user's answers for this question
        from flags.models import UserAnswer
        answers = UserAnswer.objects.filter(
            user=request.user,
            question=question
        ).order_by('-answered_at')

        if not answers.exists():
            return None

        # Aggregate answer data
        is_correct = any(answer.is_correct for answer in answers)
        attempts_used = answers.count()
        last_answer = answers.first()

        return {
            'is_correct': is_correct,
            'attempts_used': attempts_used,
            'answered_at': last_answer.answered_at,
        }
