"""
URLs for flags app.
All country, challenge, and flag-related endpoints.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CountryViewSet, test_api

# Router for ViewSet-based endpoints
# This automatically creates:
# - GET    /countries/          -> list
# - POST   /countries/          -> create (if allowed)
# - GET    /countries/{id}/     -> retrieve
# - PUT    /countries/{id}/     -> update (if allowed)
# - DELETE /countries/{id}/     -> destroy (if allowed)
router = DefaultRouter()
router.register(r"countries", CountryViewSet, basename="country")

urlpatterns = [
    # Test endpoint (temporary, for development)
    path("test/", test_api, name="test-api"),
    # Include all router URLs
    # This adds /countries/ and /countries/{id}/
    path("", include(router.urls)),
    # FUTURE: Add these when you implement them
    # path('daily/', DailyChallengeView.as_view(), name='daily-challenge'),
    # path('daily/answer/', DailyChallengeAnswerView.as_view(), name='daily-answer'),
]
