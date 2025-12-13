"""
API views for flags app.
"""

from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from flags.models import Country, DailyChallenge, UserAnswer
from flags.serializers import (
    CountryDetailSerializer,
    CountryListSerializer,
    DailyChallengeHistoryItemSerializer,
    DailyChallengeResponseSerializer,
    QuestionAnswerSerializer,
)

# Daily challenge allows 3 attempts before locking out
MAX_DAILY_ATTEMPTS = 3


# Simple function-based view for testing
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])  # Require auth for test endpoint
def test_api(request):
    """
    Test endpoint to verify DRF is working.

    GET /api/v1/test/
    """
    return Response(
        {
            "message": "API is working!",
            "drf_installed": True,
            "user": str(request.user),
            "id": str(request.user.id),
            "email": request.user.email,
            "authenticated": request.user.is_authenticated,
        }
    )


# ViewSet for countries (we'll expand this on Day 5-7)
class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API for countries.

    Pattern: ViewSets for standard CRUD operations.
    ReadOnlyModelViewSet provides: list() and retrieve()
    (No create/update/delete)
    """

    queryset = Country.objects.all()
    permission_classes = [permissions.AllowAny]  # Public for MVP

    def get_serializer_class(self):
        """
        Use different serializers for list vs detail.

        Pattern: Conditional serializer selection.
        DRF calls this method to decide which serializer to use.
        """
        if self.action == "list":
            return CountryListSerializer
        return CountryDetailSerializer


class DailyChallengeView(APIView):
    """
    Get today's daily challenge.

    GET /api/v1/daily/

    Pattern: APIView for custom logic (not standard CRUD).
    Thin view - orchestrates model methods and builds response.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Get today's challenge with user's attempt status.

        Returns:
            Response: DailyChallengeResponseSerializer data
        """
        # Get or create today's challenge (business logic in model)
        challenge, created = DailyChallenge.get_or_create_today()

        # Get the challenge's question
        question = challenge.get_question()

        # If question doesn't exist (edge case), create it
        if not question:
            question = challenge.create_question()

        # Get user's answers for this question
        user_answers = UserAnswer.objects.filter(
            user=request.user,
            question=question
        ).order_by('-answered_at')

        # Build user_status dict
        attempts_used = user_answers.count()
        has_correct = any(answer.is_correct for answer in user_answers)
        has_completed = has_correct or attempts_used >= MAX_DAILY_ATTEMPTS

        # Determine is_correct state:
        # - True: user got it right
        # - False: all attempts exhausted without correct answer
        # - None: challenge still in progress
        if has_correct:
            is_correct = True
        elif attempts_used >= MAX_DAILY_ATTEMPTS:
            is_correct = False
        else:
            is_correct = None

        user_status = {
            'has_completed': has_completed,
            'attempts_used': attempts_used,
            'attempts_remaining': max(0, MAX_DAILY_ATTEMPTS - attempts_used),
            'is_correct': is_correct,
            'last_attempt_at': user_answers.first().answered_at if user_answers.exists() else None,
        }

        # Build response data
        response_data = {
            'id': challenge.id,
            'date': challenge.date,
            'question': question,
            'country': challenge.country,
            'user_status': user_status,
        }

        # Serialize and return
        serializer = DailyChallengeResponseSerializer(response_data)
        return Response(serializer.data)


class DailyChallengeHistoryView(generics.ListAPIView):
    """
    Get user's daily challenge history.

    GET /api/v1/daily/history/

    Pattern: ListAPIView for paginated lists.
    Uses pagination settings from DRF config (PAGE_SIZE=20).
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DailyChallengeHistoryItemSerializer

    def get_queryset(self):
        """
        Get all past challenges (excluding today).

        Returns:
            QuerySet: DailyChallenge objects ordered by -date
        """
        today = timezone.now().date()
        return DailyChallenge.objects.filter(
            date__lt=today
        ).order_by('-date')

    def get_serializer_context(self):
        """
        Pass request to serializer for user-specific data.

        Pattern: Context passing for user-specific serialization.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class DailyChallengeAnswerView(APIView):
    """
    Submit an answer for today's daily challenge.

    POST /api/v1/daily/answer/

    Pattern: APIView for custom logic (not standard CRUD).
    Thin view - orchestrates model methods and builds response.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Submit an answer to today's daily challenge.

        Request body:
            {
                "answer_data": {"text": "France"},
                "time_taken_seconds": 15  // optional
            }

        Returns:
            Response: AnswerResultSerializer data

        Error responses:
            400: No attempts remaining, already completed, or invalid data
            404: No challenge exists for today
        """
        # Validate input
        serializer = QuestionAnswerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Get today's challenge
        try:
            challenge, _ = DailyChallenge.get_or_create_today()
        except Exception:
            return Response(
                {'error': 'Could not retrieve today\'s challenge.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get the question
        question = challenge.get_question()
        if not question:
            question = challenge.create_question()

        # Get user's existing answers for this question
        existing_answers = UserAnswer.objects.filter(
            user=request.user,
            question=question
        ).order_by('-answered_at')

        attempts_used = existing_answers.count()
        has_correct = any(answer.is_correct for answer in existing_answers)

        # Check if user already answered correctly
        if has_correct:
            return Response(
                {'error': 'You have already answered this challenge correctly.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user has attempts remaining
        if attempts_used >= MAX_DAILY_ATTEMPTS:
            return Response(
                {'error': 'No attempts remaining for today\'s challenge.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate the answer (business logic in model)
        answer_data = serializer.validated_data['answer_data']
        time_taken = serializer.validated_data.get('time_taken_seconds')
        is_correct, explanation = question.validate_answer(answer_data)

        # Create UserAnswer record
        attempt_number = attempts_used + 1
        user_answer = UserAnswer.objects.create(
            user=request.user,
            question=question,
            answer_data=answer_data,
            is_correct=is_correct,
            explanation=explanation,
            attempt_number=attempt_number,
            time_taken_seconds=time_taken,
        )

        # Update user stats based on outcome
        if is_correct:
            self._update_stats_on_correct(request.user)
        elif attempt_number >= MAX_DAILY_ATTEMPTS:
            self._update_stats_on_failure(request.user, challenge.country.code)

        # Calculate attempts remaining after this submission
        attempts_remaining = max(0, MAX_DAILY_ATTEMPTS - attempt_number)

        # Determine if challenge is completed (correct or no attempts left)
        is_completed = is_correct or attempts_remaining == 0

        # Build response
        response_data = {
            'is_correct': is_correct,
            'explanation': explanation,
            'attempts_remaining': attempts_remaining,
            'user_answer_id': user_answer.id,
        }

        # Only reveal correct_answer when challenge is completed
        if is_completed:
            response_data['correct_answer'] = question.correct_answer

        return Response(response_data, status=status.HTTP_200_OK)

    def _update_stats_on_correct(self, user):
        """Update user stats when answer is correct."""
        from users.models import UserStats
        stats, _ = UserStats.objects.get_or_create(user=user)
        stats.update_daily_streak(is_correct=True, guess_date=timezone.now().date())

    def _update_stats_on_failure(self, user, country_code):
        """Update user stats when all attempts exhausted without correct answer."""
        from users.models import UserStats
        stats, _ = UserStats.objects.get_or_create(user=user)
        stats.update_daily_streak(is_correct=False, guess_date=timezone.now().date())
        stats.add_incorrect_country(country_code)
