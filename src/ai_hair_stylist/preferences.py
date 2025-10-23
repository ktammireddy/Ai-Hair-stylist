"""Client preference modelling for hairstyle recommendations."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping, MutableMapping


def _normalise_value(value: str | None) -> str | None:
    if value is None:
        return None
    value = str(value).strip().lower()
    return value or None


def _normalise_keywords(values: Iterable[str] | None) -> frozenset[str]:
    if not values:
        return frozenset()
    return frozenset(str(item).strip().lower() for item in values if str(item).strip())


@dataclass(slots=True)
class ClientPreferences:
    """Structured information about a client's goals."""

    face_shape: str | None = None
    hair_length: str | None = None
    hair_texture: str | None = None
    gender: str | None = None
    occasion: str | None = None
    maintenance: str | None = None
    keywords: frozenset[str] = field(default_factory=frozenset)
    avoid: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        object.__setattr__(self, "face_shape", _normalise_value(self.face_shape))
        object.__setattr__(self, "hair_length", _normalise_value(self.hair_length))
        object.__setattr__(self, "hair_texture", _normalise_value(self.hair_texture))
        object.__setattr__(self, "gender", _normalise_value(self.gender))
        object.__setattr__(self, "occasion", _normalise_value(self.occasion))
        object.__setattr__(self, "maintenance", _normalise_value(self.maintenance))
        object.__setattr__(self, "keywords", _normalise_keywords(self.keywords))
        object.__setattr__(self, "avoid", _normalise_keywords(self.avoid))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "ClientPreferences":
        """Create preferences from a loosely structured mapping."""

        data: MutableMapping[str, object] = dict(payload)
        keywords = data.pop("keywords", None) or data.pop("tags", None)
        avoid = data.pop("avoid", None)
        if keywords is not None:
            data["keywords"] = keywords
        if avoid is not None:
            data["avoid"] = avoid
        return cls(**data)  # type: ignore[arg-type]

    def describe(self) -> str:
        """Return a human readable description of the preferences."""

        parts: list[str] = []
        if self.face_shape:
            parts.append(f"face shape {self.face_shape}")
        if self.hair_length:
            parts.append(f"{self.hair_length} length")
        if self.hair_texture:
            parts.append(f"{self.hair_texture} texture")
        if self.gender:
            parts.append(f"for {self.gender} clients")
        if self.occasion:
            parts.append(f"for {self.occasion} occasions")
        if self.maintenance:
            parts.append(f"{self.maintenance} maintenance")
        if self.keywords:
            parts.append("keywords: " + ", ".join(sorted(self.keywords)))
        if self.avoid:
            parts.append("avoid: " + ", ".join(sorted(self.avoid)))
        return "; ".join(parts) if parts else "general preferences"

    def merge_keywords(self, extra: Iterable[str]) -> "ClientPreferences":
        """Return new preferences with additional keyword filters."""

        return ClientPreferences(
            face_shape=self.face_shape,
            hair_length=self.hair_length,
            hair_texture=self.hair_texture,
            gender=self.gender,
            occasion=self.occasion,
            maintenance=self.maintenance,
            keywords=self.keywords | _normalise_keywords(extra),
            avoid=self.avoid,
        )
