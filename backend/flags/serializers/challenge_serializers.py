"""
Daily challenge serializers.
"""

from rest_framework import serializers

from flags.models import DailyChallenge

from .country_serializers import CountryDetailSerializer


class DailyChallengeSerializer(serializers.ModelSerializer):
    """
    Daily challenge with nested country data.

    Pattern: Nesting serializers for related objects.
    We want full country info when user requests today's challenge.
    """

    # 'country' is a ForeignKey in model
    # By default, DRF would just show the ID
    # We override to nest the full country object
    country = CountryDetailSerializer(read_only=True)

    class Meta:
        model = DailyChallenge
        fields = [
            "id",
            "date",
            "country",  # Full nested object
            "difficulty_tier",
            "selection_algorithm_version",
            "created_at",
        ]
        read_only_fields = fields  # Challenges are read-only via API

    # Why nest CountryDetailSerializer?
    # - Frontend needs full country data to display info after guess
    # - Avoids second API call (frontend would need GET /countries/{code})
    # - Trade-off: Larger payload, but worth it for UX


class DailyChallengeListSerializer(serializers.ModelSerializer):
    """
    Minimal challenge data for history view.

    Pattern: Don't nest heavy serializers in list views.
    """

    country_name = serializers.CharField(source="country.name", read_only=True)
    country_flag = serializers.CharField(source="country.flag_emoji", read_only=True)
    country_code = serializers.CharField(source="country.code", read_only=True)

    class Meta:
        model = DailyChallenge
        fields = [
            "id",
            "date",
            "country_code",
            "country_name",
            "country_flag",
            "difficulty_tier",
        ]

    # Why not nest full CountryDetailSerializer?
    # - History might show 30 challenges
    # - Each challenge would include ~20 country fields
    # - Result: 600+ fields in response (huge payload)
    # - Instead: Just show name/flag (frontend can drill down if needed)
