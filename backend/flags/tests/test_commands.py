"""
Tests for flags management commands.

Tests cover:
- Data transformation logic
- API integration (mocked)
- Error handling
- Idempotency
"""

from io import StringIO
from unittest.mock import Mock, patch

import requests
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from flags.management.commands.load_countries import Command
from flags.models import Country


class LoadCountriesCommandTest(TestCase):
    """Tests for load_countries management command"""

    def setUp(self):
        """Set up test fixtures"""
        self.command = Command()
        self.maxDiff = None

    def test_transform_country_complete_data(self):
        """Test _transform_country with complete country data"""
        # Sample complete data from REST Countries API
        api_data = {
            "cca3": "USA",
            "name": {"common": "United States"},
            "flag": "🇺🇸",
            "flags": {
                "svg": "https://flagcdn.com/us.svg",
                "png": "https://flagcdn.com/us.png",
                "alt": "The flag of the United States",
            },
            "coatOfArms": {
                "svg": "https://mainfacts.com/media/images/coats_of_arms/us.svg",
                "png": "https://mainfacts.com/media/images/coats_of_arms/us.png",
            },
            "population": 340110988,
            "capital": ["Washington, D.C."],
            "latlng": [38.0, -97.0],
            "area": 9525067.0,
            "languages": {"eng": "English"},
            "currencies": {"USD": {"name": "United States dollar", "symbol": "$"}},
        }

        # Transform data
        result = self.command._transform_country(api_data)

        # Verify all fields mapped correctly
        self.assertEqual(result["name"], "United States")
        self.assertEqual(result["flag_emoji"], "🇺🇸")
        self.assertEqual(result["flag_svg_url"], "https://flagcdn.com/us.svg")
        self.assertEqual(result["flag_png_url"], "https://flagcdn.com/us.png")
        self.assertEqual(result["flag_alt_text"], "The flag of the United States")
        self.assertEqual(
            result["coat_of_arms_svg_url"],
            "https://mainfacts.com/media/images/coats_of_arms/us.svg",
        )
        self.assertEqual(
            result["coat_of_arms_png_url"],
            "https://mainfacts.com/media/images/coats_of_arms/us.png",
        )
        self.assertEqual(result["population"], 340110988)
        self.assertEqual(result["capital"], "Washington, D.C.")
        self.assertEqual(result["largest_city"], "Washington, D.C.")
        self.assertEqual(result["latitude"], 38.0)
        self.assertEqual(result["longitude"], -97.0)
        self.assertEqual(result["area_km2"], 9525067.0)
        self.assertEqual(result["languages"], {"eng": "English"})
        self.assertEqual(result["currencies"], {"USD": {"name": "United States dollar", "symbol": "$"}})
        self.assertIsNotNone(result["api_cache_date"])
        self.assertEqual(result["raw_api_response"], api_data)

    def test_transform_country_missing_optional_fields(self):
        """Test _transform_country with missing optional fields"""
        # Minimal data with missing optional fields
        api_data = {
            "cca3": "XXX",
            "name": {"common": "Test Country"},
            "population": 1000000,
            "capital": ["Test Capital"],
            "latlng": [0.0, 0.0],
            "area": 1000.0,
            # Missing: flag (should default to 🏳)
            # Missing: flags.alt (should default to "")
            # Missing: coatOfArms (should default to None)
            "flags": {
                "svg": "https://example.com/flag.svg",
                "png": "https://example.com/flag.png",
            },
            "languages": {"eng": "English"},
            "currencies": {},
        }

        result = self.command._transform_country(api_data)

        # Verify defaults applied
        self.assertEqual(result["flag_emoji"], "🏳")
        self.assertEqual(result["flag_alt_text"], "")
        self.assertIsNone(result["coat_of_arms_svg_url"])
        self.assertIsNone(result["coat_of_arms_png_url"])
        self.assertEqual(result["currencies"], {})

    def test_transform_country_missing_capital(self):
        """Test _transform_country with missing capital field"""
        api_data = {
            "cca3": "ATA",
            "name": {"common": "Antarctica"},
            "flag": "🇦🇶",
            "flags": {
                "svg": "https://flagcdn.com/aq.svg",
                "png": "https://flagcdn.com/aq.png",
            },
            "population": 0,
            "capital": [],  # Antarctica has no capital
            "latlng": [-75.0, 0.0],
            "area": 14000000.0,
            "languages": {},
            "currencies": {},
        }

        result = self.command._transform_country(api_data)

        # Verify fallback to "N/A"
        self.assertEqual(result["capital"], "N/A")
        self.assertEqual(result["largest_city"], "N/A")

    @patch("flags.management.commands.load_countries.requests.get")
    def test_load_countries_creates_records(self, mock_get):
        """Test load_countries command creates database records"""
        # Mock API responses for both calls
        mock_call1_data = [
            {
                "cca3": "FRA",
                "name": {"common": "France"},
                "flag": "🇫🇷",
                "flags": {
                    "svg": "https://flagcdn.com/fr.svg",
                    "png": "https://flagcdn.com/fr.png",
                },
                "coatOfArms": {},
                "population": 67795000,
                "capital": ["Paris"],
                "latlng": [46.0, 2.0],
                "area": 543908.0,
                "languages": {"fra": "French"},
            },
            {
                "cca3": "DEU",
                "name": {"common": "Germany"},
                "flag": "🇩🇪",
                "flags": {
                    "svg": "https://flagcdn.com/de.svg",
                    "png": "https://flagcdn.com/de.png",
                },
                "coatOfArms": {},
                "population": 83190556,
                "capital": ["Berlin"],
                "latlng": [51.0, 9.0],
                "area": 357114.0,
                "languages": {"deu": "German"},
            },
        ]

        mock_call2_data = [
            {"cca3": "FRA", "currencies": {"EUR": {"name": "Euro", "symbol": "€"}}},
            {"cca3": "DEU", "currencies": {"EUR": {"name": "Euro", "symbol": "€"}}},
        ]

        # Configure mock to return different data for each call
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = mock_call1_data

        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = mock_call2_data

        mock_get.side_effect = [mock_response1, mock_response2]

        # Run command
        out = StringIO()
        call_command("load_countries", stdout=out)

        # Verify records created
        self.assertEqual(Country.objects.count(), 2)

        france = Country.objects.get(code="FRA")
        self.assertEqual(france.name, "France")
        self.assertEqual(france.flag_emoji, "🇫🇷")
        self.assertEqual(france.population, 67795000)
        self.assertEqual(france.capital, "Paris")

        germany = Country.objects.get(code="DEU")
        self.assertEqual(germany.name, "Germany")
        self.assertEqual(germany.flag_emoji, "🇩🇪")

        # Verify output shows "Created"
        output = out.getvalue()
        self.assertIn("Created: 🇫🇷 France", output)
        self.assertIn("Created: 🇩🇪 Germany", output)

    @patch("flags.management.commands.load_countries.requests.get")
    def test_load_countries_idempotent(self, mock_get):
        """Test load_countries is idempotent - no duplicates on second run"""
        # Mock API data
        mock_call1_data = [
            {
                "cca3": "JPN",
                "name": {"common": "Japan"},
                "flag": "🇯🇵",
                "flags": {
                    "svg": "https://flagcdn.com/jp.svg",
                    "png": "https://flagcdn.com/jp.png",
                },
                "coatOfArms": {},
                "population": 125580000,
                "capital": ["Tokyo"],
                "latlng": [36.0, 138.0],
                "area": 377930.0,
                "languages": {"jpn": "Japanese"},
            }
        ]

        mock_call2_data = [
            {"cca3": "JPN", "currencies": {"JPY": {"name": "Japanese yen", "symbol": "¥"}}}
        ]

        # Configure mock for first run
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = mock_call1_data

        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = mock_call2_data

        mock_get.side_effect = [mock_response1, mock_response2]

        # First run
        out1 = StringIO()
        call_command("load_countries", stdout=out1)

        # Verify first run created record
        self.assertEqual(Country.objects.count(), 1)
        output1 = out1.getvalue()
        self.assertIn("Created: 🇯🇵 Japan", output1)

        # Configure mock for second run (reset side_effect)
        mock_response3 = Mock()
        mock_response3.status_code = 200
        mock_response3.json.return_value = mock_call1_data

        mock_response4 = Mock()
        mock_response4.status_code = 200
        mock_response4.json.return_value = mock_call2_data

        mock_get.side_effect = [mock_response3, mock_response4]

        # Second run
        out2 = StringIO()
        call_command("load_countries", stdout=out2)

        # Verify still only 1 record (no duplicates)
        self.assertEqual(Country.objects.count(), 1)

        # Verify second run shows "Updated" not "Created"
        output2 = out2.getvalue()
        self.assertIn("Updated: 🇯🇵 Japan", output2)
        self.assertNotIn("Created: 🇯🇵 Japan", output2)

    @patch("flags.management.commands.load_countries.requests.get")
    def test_load_countries_handles_api_error(self, mock_get):
        """Test load_countries handles API errors gracefully"""
        # Mock requests to raise exception
        mock_get.side_effect = requests.exceptions.RequestException("API connection failed")

        # Run command
        out = StringIO()
        call_command("load_countries", stdout=out)

        # Verify no records created
        self.assertEqual(Country.objects.count(), 0)

        # Verify error message in output
        output = out.getvalue()
        self.assertIn("Failed to fetch data from API", output)
        self.assertIn("API connection failed", output)
