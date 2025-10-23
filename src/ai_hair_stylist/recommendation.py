"""Scoring logic for hairstyle recommendations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping

from .catalog import Hairstyle, HairstyleCatalog
from .preferences import ClientPreferences

DEFAULT_WEIGHTS: Dict[str, float] = {
    "face_shape": 3.0,
    "hair_length": 2.5,
    "hair_texture": 3.0,
    "gender": 1.0,
    "occasion": 1.5,
    "maintenance": 1.5,
    "keyword": 0.8,
    "avoid": -4.0,
}

_MAINTENANCE_LEVELS: Dict[str, int] = {"low": 0, "medium": 1, "high": 2}


@dataclass(frozen=True, slots=True)
class Recommendation:
    """A scored hairstyle suggestion."""

    hairstyle: Hairstyle
    score: float
    reasons: tuple[str, ...]


class RecommendationEngine:
    """Rank hairstyles according to client preferences."""

    def __init__(
        self,
        catalog: HairstyleCatalog,
        *,
        weights: Dict[str, float] | None = None,
        minimum_score: float = 0.0,
    ) -> None:
        self.catalog = catalog
        self.weights = DEFAULT_WEIGHTS | (weights or {})
        self.minimum_score = minimum_score

    def _score(self, hairstyle: Hairstyle, preferences: ClientPreferences) -> Recommendation:
        score = 0.0
        reasons: List[str] = []

        if preferences.face_shape:
            if preferences.face_shape in hairstyle.face_shapes:
                score += self.weights["face_shape"]
                reasons.append(f"suits {preferences.face_shape} face shapes")
        if preferences.hair_length:
            if preferences.hair_length in hairstyle.hair_lengths:
                score += self.weights["hair_length"]
                reasons.append(f"matches {preferences.hair_length} length goal")
        if preferences.hair_texture:
            if preferences.hair_texture in hairstyle.hair_textures:
                score += self.weights["hair_texture"]
                reasons.append(f"works with {preferences.hair_texture} texture")
        if preferences.gender:
            if preferences.gender in hairstyle.genders:
                score += self.weights["gender"]
                reasons.append(f"popular with {preferences.gender} clients")
        if preferences.occasion:
            if preferences.occasion in hairstyle.occasions:
                score += self.weights["occasion"]
                reasons.append(f"appropriate for {preferences.occasion} occasions")
        if preferences.maintenance:
            desired = _MAINTENANCE_LEVELS.get(preferences.maintenance)
            current = _MAINTENANCE_LEVELS.get(hairstyle.maintenance)
            if desired is not None and current is not None:
                difference = abs(desired - current)
                if difference == 0:
                    score += self.weights["maintenance"]
                    reasons.append(f"meets {preferences.maintenance} maintenance goal")
                elif difference == 1:
                    score += self.weights["maintenance"] * 0.5
                    reasons.append(
                        "slightly different maintenance but still manageable"
                    )
        if preferences.keywords:
            overlap = preferences.keywords & hairstyle.tags
            if overlap:
                increment = self.weights["keyword"] * len(overlap)
                score += increment
                reasons.append(
                    "matches requested features: " + ", ".join(sorted(overlap))
                )
        if preferences.avoid:
            conflict = preferences.avoid & hairstyle.tags
            if conflict:
                penalty = self.weights["avoid"] * len(conflict)
                score += penalty
                reasons.append(
                    "conflicts with avoid list: " + ", ".join(sorted(conflict))
                )

        return Recommendation(hairstyle=hairstyle, score=score, reasons=tuple(reasons))

    def rank(self, preferences: ClientPreferences) -> List[Recommendation]:
        """Return recommendations sorted by score."""

        results = [self._score(style, preferences) for style in self.catalog]
        filtered = [
            result
            for result in results
            if result.score >= self.minimum_score and not self._has_conflict(result)
        ]
        return sorted(
            filtered,
            key=lambda rec: (rec.score, rec.hairstyle.name.lower()),
            reverse=True,
        )

    def recommend(self, preferences: ClientPreferences, limit: int = 3) -> List[Recommendation]:
        ranked = self.rank(preferences)
        return ranked[:limit] if limit > 0 else ranked

    @staticmethod
    def _has_conflict(recommendation: Recommendation) -> bool:
        return any(reason.startswith("conflicts with") for reason in recommendation.reasons)


def recommend_hairstyles(
    preferences: ClientPreferences | Mapping[str, object],
    *,
    catalog: HairstyleCatalog | None = None,
    limit: int = 3,
    weights: Dict[str, float] | None = None,
) -> List[Recommendation]:
    """Convenience wrapper around :class:`RecommendationEngine`."""

    if not isinstance(preferences, ClientPreferences):
        preferences = ClientPreferences.from_dict(preferences)
    if catalog is None:
        catalog = HairstyleCatalog.default()
    engine = RecommendationEngine(catalog, weights=weights)
    return engine.recommend(preferences, limit=limit)
