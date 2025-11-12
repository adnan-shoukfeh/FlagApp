"""
Question and answer serializers.
"""

from rest_framework import serializers

from flags.models import Question, UserAnswer


class QuestionSerializer(serializers.ModelSerializer):
    """
    Question data (sent to frontend for user to answer).

    Important: DON'T include correct_answer in this serializer.
    That's sent separately after user submits.
    """

    country_code = serializers.CharField(source="country.code", read_only=True)
    country_name = serializers.CharField(source="country.name", read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "category",
            "format",
            "country_code",
            "country_name",
            "question_text",
            "metadata",
            # NOTE: 'correct_answer' is EXCLUDED
            # This is sent after user answers
        ]

    # Security pattern: Separate serializers for questions vs answers
    # Never send answers to frontend before user guesses!


class QuestionAnswerSerializer(serializers.Serializer):
    """
    Input serializer for user's answer submission.

    Pattern: Input validation for complex JSON structures.
    answer_data structure varies by question format.
    """

    answer_data = serializers.JSONField(
        help_text="User's answer. Structure depends on question format."
    )

    def validate_answer_data(self, value):
        """
        Validate answer_data has required structure.

        Pattern: Validation depends on context (question format).
        In a view, we'd do: serializer.context['question'] = question
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("answer_data must be an object")

        # We can't fully validate without knowing question format
        # (text_input needs 'text', multiple_choice needs 'selected_option', etc.)
        # That validation happens in Question.validate_answer() model method
        return value


class UserAnswerSerializer(serializers.ModelSerializer):
    """
    User's answer record (for history/stats).
    """

    question_text = serializers.CharField(
        source="question.question_text", read_only=True
    )
    country_name = serializers.CharField(source="question.country.name", read_only=True)
    country_flag = serializers.CharField(
        source="question.country.flag_emoji", read_only=True
    )

    class Meta:
        model = UserAnswer
        fields = [
            "id",
            "question_text",
            "country_name",
            "country_flag",
            "answer_data",
            "is_correct",
            "explanation",
            "attempt_number",
            "time_taken_seconds",
            "answered_at",
        ]
        read_only_fields = fields


class AnswerResultSerializer(serializers.Serializer):
    """
    Response after user submits an answer.

    Pattern: API response serializer (not model-backed).
    This defines what we send back after validating guess.
    """

    is_correct = serializers.BooleanField()
    explanation = serializers.CharField()
    attempts_remaining = serializers.IntegerField()
    correct_answer = serializers.JSONField(required=False)  # Only if wrong
    user_answer_id = serializers.IntegerField()

    # This serializer documents our API contract:
    # POST /api/daily/answer/ returns this structure
