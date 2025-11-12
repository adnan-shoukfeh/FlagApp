"""
Country serializers.

Two serializers: one for lists (minimal data), one for detail (full data).
This is a performance pattern - don't send massive objects in list views.
"""

from rest_framework import serializers

from flags.models import Country


class CountryListSerializer(serializers.ModelSerializer):
    """
    Minimal country data for list views (encyclopedia search results).

    Pattern: Light serializer for list endpoints.
    Only include what's needed to render a list item.
    """

    class Meta:
        model = Country
        fields = [
            "code",
            "name",
            "flag_emoji",
            "flag_svg_url",
            "population",  # Useful for sorting
            "capital",  # Useful for preview
        ]


class CountryDetailSerializer(serializers.ModelSerializer):
    """
    Complete country data for detail view.

    Pattern: Heavy serializer for detail endpoints.
    Include everything - user wants full info.
    """

    class Meta:
        model = Country
        fields = "__all__"  # All model fields
        # Alternative: Explicitly list fields (more maintainable)
        # fields = [
        #     "id", "code", "name", "flag_emoji",
        #     "flag_svg_url", "flag_png_url", ...
        # ]

    # Why use '__all__'?
    # - Country has 20+ fields, listing them all is tedious
    # - We control what frontend sees (it can ignore extra fields)
    # - If we add a field to model, serializer auto-includes it
    #
    # When NOT to use '__all__':
    # - Models with sensitive fields (passwords, tokens)
    # - Models where you want tight control over API contract


class CountrySearchSerializer(serializers.Serializer):
    """
    Input serializer for search queries.

    Pattern: Use plain Serializer (not ModelSerializer) for non-model data.
    This validates query parameters, doesn't map to a model.
    """

    query = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Search term (country name or flag emoji)",
    )
    limit = serializers.IntegerField(
        default=20, min_value=1, max_value=100, help_text="Number of results to return"
    )
