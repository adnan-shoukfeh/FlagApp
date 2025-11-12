"""
URL configuration.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),
    # API v1 endpoints
    # All app URLs are automatically prefixed with /api/v1/
    path("api/v1/", include("users.urls")),  # /api/v1/auth/google/, etc.
    path("api/v1/", include("flags.urls")),  # /api/v1/countries/, etc.
    # FUTURE: API versioning
    # path('api/v2/', include('users.v2_urls')),
]
