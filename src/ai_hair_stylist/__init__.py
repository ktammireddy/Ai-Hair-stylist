"""Core utilities for building hair style recommendations."""

from .catalog import Hairstyle, HairstyleCatalog
from .preferences import ClientPreferences
from .recommendation import Recommendation, RecommendationEngine, recommend_hairstyles

__all__ = [
    "ClientPreferences",
    "Hairstyle",
    "HairstyleCatalog",
    "Recommendation",
    "RecommendationEngine",
    "recommend_hairstyles",
]
