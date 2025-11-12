"""
API views for flags app.
"""

from rest_framework import permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from flags.models import Country
from flags.serializers import CountryDetailSerializer, CountryListSerializer


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
