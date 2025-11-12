"""
User and UserStats serializers.

Philosophy: These are OUTPUT serializers (how we send data to frontend).
Input validation for authentication happens in views (OAuth flow).
"""

from rest_framework import serializers

from users.models import User, UserStats


class UserStatsSerializer(serializers.ModelSerializer):
    """
    Serialize user statistics.

    All fields from model, no business logic.
    The model methods (update_daily_streak, etc.) handle logic.
    """

    class Meta:
        model = UserStats
        fields = [
            "id",
            "total_correct",
            "current_streak",
            "longest_streak",
            "last_guess_date",
            "incorrect_countries",
            "category_stats",
            "format_stats",
        ]
        # All fields read-only from API perspective
        # Updates happen through model methods, not direct API writes
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    """
    Serialize User model with nested stats.

    Pattern: Nested serializers for related objects.
    The 'stats' field is a OneToOne relationship, so we inline it.
    """

    # Include the related UserStats object
    # 'source' tells DRF where to find this data (the related_name from model)
    stats = UserStatsSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "date_joined",
            "stats",  # Nested stats object
        ]
        read_only_fields = ["id", "date_joined"]

    # Do not include password
    # - Password is write-only during user creation
    # - Never send password hashes to frontend (security)
    # - Password changes handled by separate endpoint


class UserCreateSerializer(serializers.Serializer):
    """
    Input serializer for OAuth user creation.

    Pattern: Separate input/output serializers.
    This validates data from Google OAuth, doesn't map to model directly.
    """

    email = serializers.EmailField()
    username = serializers.CharField(max_length=150, required=False)
    # OAuth providers give us these
    # We validate them, then create User in view

    def validate_email(self, value):
        """
        Custom validation: Ensure email doesn't exist.

        Pattern: Field-level validation with validate_<fieldname> method.
        Runs during serializer.is_valid()
        """
        # Check if user already exists
        # If they do, that's OK for OAuth (just login)
        # But we validate the email format
        if not value:
            raise serializers.ValidationError("Email is required")
        return value.lower()  # Normalize email
