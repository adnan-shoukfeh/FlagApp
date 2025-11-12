import logging

from django.conf import settings
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User

logger = logging.getLogger(__name__)


class GoogleLoginView(APIView):
    """
    Verify Google ID token and issue JWT tokens.

    Frontend Flow:
    1. User clicks "Login with Google"
    2. Google JS SDK opens popup, user authenticates
    3. Google returns ID token to frontend
    4. Frontend POSTs {id_token: "..."} to this endpoint
    5. This view verifies token with Google
    6. Creates/fetches User in database
    7. Returns JWT access + refresh tokens

    AllowAny so that unauthenticated users can access and become authenticated.
    - After this, all other endpoints require authentication
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Verify Google ID token and return JWT tokens.

        Request body:
        {
            "id_token": "eyJhbGc..."  # Google ID token from frontend
        }

        Response (success):
        {
            "access_token": "eyJhbGc...",   # Short-lived (1 hour)
            "refresh_token": "eyJhbGc...",  # Long-lived (30 days)
            "user": {
                "id": 1,
                "email": "user@example.com",
                "username": "user"
            }
        }

        Response (error):
        {
            "error": "Invalid token"
        }
        """
        id_token_str = request.data.get("id_token")

        if not id_token_str:
            return Response(
                {"error": "id_token is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Verify token with Google
            # This makes a request to Google's servers to validate:
            # 1. Token signature is valid
            # 2. Token hasn't expired
            # 3. Token was issued for OUR client ID
            # 4. Token hasn't been tampered with
            idinfo = id_token.verify_oauth2_token(
                id_token_str, requests.Request(), settings.GOOGLE_CLIENT_ID
            )

            # idinfo contains:
            # {
            #     'iss': 'https://accounts.google.com',
            #     'sub': '1234567890',  # Google user ID
            #     'email': 'user@example.com',
            #     'email_verified': True,
            #     'name': 'John Doe',
            #     'picture': 'https://...',
            #     'given_name': 'John',
            #     'family_name': 'Doe',
            #     'iat': 1234567890,  # Issued at
            #     'exp': 1234567890,  # Expires
            # }

            # Extract user info
            email = idinfo.get("email")
            if not email:
                return Response(
                    {"error": "Email not provided by Google"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create or get user
            # get_or_create returns (user, created) tuple
            # created=True if new user, False if existing
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    # Django requires username, so we derive it from email
                    "username": email.split("@")[0],
                    # Note: password is NOT set (OAuth users don't have passwords)
                },
            )

            if created:
                logger.info(f"New user created via Google OAuth: {email}")
                # In Phase 2, you might want to:
                # - Send welcome email
                # - Create UserStats automatically (if not using signals)
                # - Track signup source (Google vs future providers)

            # Generate JWT tokens
            # RefreshToken.for_user() creates both refresh and access tokens
            refresh = RefreshToken.for_user(user)

            # Return tokens and user info
            return Response(
                {
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            # Token verification failed
            # Common causes:
            # - Expired token
            # - Invalid signature
            # - Wrong client ID
            # - Token from different Google project
            logger.error(f"Google token verification failed: {str(e)}")
            return Response(
                {"error": "Invalid token", "detail": str(e)},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected error in GoogleLoginView: {str(e)}")
            return Response(
                {"error": "Authentication failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
