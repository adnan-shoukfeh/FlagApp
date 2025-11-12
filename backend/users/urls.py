"""
URLs for users app.
All authentication, user management, and stats endpoints.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import GoogleLoginView

urlpatterns = [
    # OAuth endpoints
    path("auth/google/", GoogleLoginView.as_view(), name="google-login"),
    # JWT token management
    # simplejwt provides TokenRefreshView for us
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    # FUTURE: Add these when you implement them
    # path('auth/logout/', LogoutView.as_view(), name='logout'),
    # path('profile/', UserProfileView.as_view(), name='user-profile'),
    # path('stats/', UserStatsView.as_view(), name='user-stats'),
]
