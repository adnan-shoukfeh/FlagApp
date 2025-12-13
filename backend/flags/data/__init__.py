"""
Data files for flags app.

Contains supplementary data that enhances REST Countries API data.
"""

from .country_alternates import MANUAL_ALTERNATES, get_alternates_for_country

__all__ = ["MANUAL_ALTERNATES", "get_alternates_for_country"]
