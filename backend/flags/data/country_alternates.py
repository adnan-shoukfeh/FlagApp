"""
Manual country name alternates that supplement REST Countries API altSpellings.

These are merged with API-provided alternates when generating questions.
Add entries here for common user inputs that the API doesn't include.

Format:
    "COUNTRY_CODE": ["alternate1", "alternate2", ...]

The country code is ISO 3166-1 alpha-3 (e.g., "USA", "GBR", "FRA").
Alternates are case-insensitive during matching.
"""

# Manual overrides for country name alternates
# Add entries here as needed - these supplement API altSpellings
MANUAL_ALTERNATES = {
    # Example entries (uncomment and modify as needed):
    # "USA": ["America", "The States"],
    # "GBR": ["England", "Britain", "Great Britain"],
    # "KOR": ["Korea", "South Korea"],
    # "PRK": ["North Korea"],
    # "CHN": ["China"],
    # "RUS": ["Russia"],
}


def get_alternates_for_country(country_code: str, api_alternates: list | None = None) -> list:
    """
    Get all alternate names for a country, merging API and manual sources.

    Args:
        country_code: ISO 3166-1 alpha-3 code (e.g., "USA")
        api_alternates: List of alternates from REST Countries API

    Returns:
        List of unique alternate names (excludes duplicates, case-insensitive)
    """
    alternates = set()

    # Add API alternates
    if api_alternates:
        for alt in api_alternates:
            alternates.add(alt.lower())

    # Add manual overrides
    manual = MANUAL_ALTERNATES.get(country_code, [])
    for alt in manual:
        alternates.add(alt.lower())

    # Return as sorted list (excluding empty strings)
    return sorted([alt for alt in alternates if alt])
