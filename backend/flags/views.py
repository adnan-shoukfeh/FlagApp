"""
API views for flags app.
"""

from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from flags.models import Country, DailyChallenge, UserAnswer
from flags.serializers import (
    CountryDetailSerializer,
    CountryListSerializer,
    DailyChallengeResponseSerializer,
    DailyChallengeHistoryItemSerializer,
)


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
        has_completed = has_correct or attempts_used >= 3

        # is_correct logic:
        # - True if any answer is correct
        # - False if all wrong and attempts exhausted
        # - None if still have attempts remaining
        if has_correct:
            is_correct = True
        elif attempts_used >= 3:
            is_correct = False
        else:
            is_correct = None

        user_status = {
            'has_completed': has_completed,
            'attempts_used': attempts_used,
            'attempts_remaining': max(0, 3 - attempts_used),
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
