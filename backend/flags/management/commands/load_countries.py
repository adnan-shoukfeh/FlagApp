"""
Django management command to load country data from REST Countries API.

Usage:
    python manage.py load_countries

Design:
- Fetches from https://restcountries.com/v3.1/all
- Uses update_or_create for idempotency (safe to run multiple times)
- Handles missing fields gracefully with defaults
- Stores full API response for future flexibility
"""

import requests
from django.core.management.base import BaseCommand
from django.utils import timezone

from flags.models import Country


class Command(BaseCommand):
    help = "Load country data from REST Countries API into the database"

    # API endpoint base URL
    API_BASE_URL = "https://restcountries.com/v3.1/all"

    # API has a 10-field limit, so we split into multiple calls
    # Call 1: Core data (10 fields max)
    API_FIELDS_CALL1 = "cca3,name,flag,flags,coatOfArms,population,capital,latlng,area,languages"
    # Call 2: Currencies and alternate spellings
    API_FIELDS_CALL2 = "cca3,currencies,altSpellings"

    def handle(self, *args, **options):
        """Main command execution"""
        self.stdout.write("=" * 70)
        self.stdout.write(
            self.style.HTTP_INFO("Loading countries from REST Countries API...")
        )
        self.stdout.write(f"API Base URL: {self.API_BASE_URL}")
        self.stdout.write(
            "NOTE: API limits to 10 fields per request - making 2 API calls"
        )
        self.stdout.write("=" * 70)

        # Fetch data from API (2 calls required due to field limit)
        try:
            countries_data = self._fetch_all_data()
            self.stdout.write(
                self.style.SUCCESS(f"\nFetched {len(countries_data)} countries from API")
            )
        except requests.exceptions.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f"\nFailed to fetch data from API: {e}")
            )
            return

        # Process each country
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for idx, country_data in enumerate(countries_data, 1):
            # Progress indicator
            if idx % 10 == 0:
                self.stdout.write(f"Processing country {idx}/{len(countries_data)}...")

            # Transform and save country
            result = self._process_country(country_data)

            if result == "created":
                created_count += 1
            elif result == "updated":
                updated_count += 1
            elif result == "skipped":
                skipped_count += 1

        # Print summary
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("LOAD COMPLETE"))
        self.stdout.write("=" * 70)
        self.stdout.write(f"Total countries processed: {len(countries_data)}")
        self.stdout.write(self.style.SUCCESS(f"  ✓ Created: {created_count}"))
        self.stdout.write(self.style.WARNING(f"  ↻ Updated: {updated_count}"))
        if skipped_count > 0:
            self.stdout.write(self.style.ERROR(f"  ✗ Skipped: {skipped_count}"))
        self.stdout.write("=" * 70)

    def _fetch_all_data(self):
        """
        Fetch all country data from REST Countries API.

        Makes 2 API calls due to 10-field limit and merges results.

        Returns:
            list: Complete country data with all fields
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; FlagLearningApp/1.0)",
            "Accept": "application/json",
        }

        # Call 1: Core data (10 fields)
        self.stdout.write("\nFetching core data (call 1/2)...")
        url1 = f"{self.API_BASE_URL}?fields={self.API_FIELDS_CALL1}"
        response1 = requests.get(url1, headers=headers, timeout=30)
        response1.raise_for_status()
        data_call1 = response1.json()
        self.stdout.write(
            self.style.SUCCESS(f"  ✓ Call 1 complete: {len(data_call1)} countries")
        )

        # Call 2: Currencies
        self.stdout.write("\nFetching currencies (call 2/2)...")
        url2 = f"{self.API_BASE_URL}?fields={self.API_FIELDS_CALL2}"
        response2 = requests.get(url2, headers=headers, timeout=30)
        response2.raise_for_status()
        data_call2 = response2.json()
        self.stdout.write(
            self.style.SUCCESS(f"  ✓ Call 2 complete: {len(data_call2)} countries")
        )

        # Merge data by cca3 code
        self.stdout.write("\nMerging data from both API calls...")
        call2_by_code = {
            country["cca3"]: {
                "currencies": country.get("currencies", {}),
                "altSpellings": country.get("altSpellings", []),
            }
            for country in data_call2
        }

        # Add currencies and altSpellings to main data
        for country in data_call1:
            code = country.get("cca3")
            if code in call2_by_code:
                country["currencies"] = call2_by_code[code]["currencies"]
                country["altSpellings"] = call2_by_code[code]["altSpellings"]
            else:
                country["currencies"] = {}
                country["altSpellings"] = []

        self.stdout.write(self.style.SUCCESS(f"  ✓ Data merged successfully"))
        return data_call1

    def _process_country(self, data):
        """
        Process a single country from API data.

        Args:
            data (dict): Country data from REST Countries API

        Returns:
            str: "created", "updated", or "skipped"
        """
        try:
            # Extract and validate required fields
            code = data.get("cca3")
            name = data.get("name", {}).get("common")

            if not code or not name:
                self.stdout.write(
                    self.style.ERROR(
                        f"  ✗ Skipping country: Missing code or name - {data.get('name', {})}"
                    )
                )
                return "skipped"

            # Transform data
            transformed_data = self._transform_country(data)

            # Update or create country
            country, created = Country.objects.update_or_create(
                code=code, defaults=transformed_data
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ Created: {country.flag_emoji} {country.name}")
                )
                return "created"
            else:
                self.stdout.write(
                    self.style.WARNING(f"  ↻ Updated: {country.flag_emoji} {country.name}")
                )
                return "updated"

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"  ✗ Error processing {data.get('name', {}).get('common', 'Unknown')}: {str(e)}"
                )
            )
            return "skipped"

    def _transform_country(self, data):
        """
        Transform REST Countries API data to Country model format.

        Field mapping documented in CLAUDE.md and technical design docs.

        TODO: Add additional API calls to source remaining fields:
            - largest_city: Currently uses capital as placeholder
            - gdp_nominal, gdp_ppp_per_capita: Requires World Bank API or similar
            - median_age, life_expectancy, fertility_rate: Requires demographic API
            - school_expectancy: Requires education API
            - religions: Requires cultural/demographic API
            - arable_land_percent: Requires agricultural API
            - highest_point: Requires geographic/elevation API
            - difficulty_tier: Algorithm to be implemented in Phase 2

        Args:
            data (dict): Raw country data from API

        Returns:
            dict: Transformed data ready for Country model
        """
        # Helper to safely get nested values
        def safe_get(dictionary, *keys, default=None):
            """Safely navigate nested dictionaries"""
            for key in keys:
                if isinstance(dictionary, dict):
                    dictionary = dictionary.get(key, default)
                else:
                    return default
            return dictionary

        # Extract capital (array in API, string in model)
        capitals = data.get("capital", [])
        capital = capitals[0] if capitals else "N/A"

        # Extract languages (dict in API, dict in model)
        languages_dict = data.get("languages", {})
        # Keep as dict for model's JSONField
        languages = languages_dict if languages_dict else {}

        # Extract currencies (dict in API, dict in model)
        currencies = data.get("currencies", {})

        # Extract flag URLs
        flags = data.get("flags", {})
        flag_svg_url = flags.get("svg", "")
        flag_png_url = flags.get("png", "")
        flag_alt_text = flags.get("alt", "")

        # Extract coat of arms
        coat_of_arms = data.get("coatOfArms", {})
        coat_of_arms_svg_url = coat_of_arms.get("svg")
        coat_of_arms_png_url = coat_of_arms.get("png")

        # Extract coordinates
        latlng = data.get("latlng", [0.0, 0.0])
        latitude = latlng[0] if len(latlng) > 0 else 0.0
        longitude = latlng[1] if len(latlng) > 1 else 0.0

        # Build transformed data dictionary
        transformed = {
            # Core identification
            "name": data.get("name", {}).get("common", "Unknown"),
            # Visual assets
            "flag_emoji": data.get("flag", "🏳"),
            "flag_svg_url": flag_svg_url,
            "flag_png_url": flag_png_url,
            "flag_alt_text": flag_alt_text,
            "coat_of_arms_svg_url": coat_of_arms_svg_url,
            "coat_of_arms_png_url": coat_of_arms_png_url,
            # Geographic data
            "latitude": latitude,
            "longitude": longitude,
            "area_km2": data.get("area", 0.0),
            # Demographic data
            "population": data.get("population", 0),
            "capital": capital,
            "largest_city": capital,  # Placeholder: API doesn't provide largest_city
            # Cultural data
            "languages": languages,
            "currencies": currencies,
            # API caching
            "api_cache_date": timezone.now(),
            "raw_api_response": data,
        }

        return transformed
