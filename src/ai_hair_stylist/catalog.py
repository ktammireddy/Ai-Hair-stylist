"""Data structures for the hairstyle catalog."""
from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Mapping, Sequence
import json

_PACKAGE_DATA = resources.files(__package__) / "data"


@dataclass(frozen=True, slots=True)
class Hairstyle:
    """Represents a single hairstyle entry."""

    name: str
    description: str
    face_shapes: frozenset[str]
    hair_lengths: frozenset[str]
    hair_textures: frozenset[str]
    genders: frozenset[str]
    occasions: frozenset[str]
    maintenance: str
    tags: frozenset[str]

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> "Hairstyle":
        """Create a ``Hairstyle`` from a mapping, normalising values."""

        def _as_frozenset(key: str) -> frozenset[str]:
            values = data.get(key, [])
            if isinstance(values, str):
                values = [values]
            return frozenset(str(item).lower() for item in values)

        return cls(
            name=str(data["name"]).strip(),
            description=str(data.get("description", "")).strip(),
            face_shapes=_as_frozenset("face_shapes"),
            hair_lengths=_as_frozenset("hair_lengths"),
            hair_textures=_as_frozenset("hair_textures"),
            genders=_as_frozenset("genders"),
            occasions=_as_frozenset("occasions"),
            maintenance=str(data.get("maintenance", "medium")).lower(),
            tags=_as_frozenset("tags"),
        )

    def to_dict(self) -> Dict[str, object]:
        """Return a JSON serialisable dictionary representation."""

        return {
            "name": self.name,
            "description": self.description,
            "face_shapes": sorted(self.face_shapes),
            "hair_lengths": sorted(self.hair_lengths),
            "hair_textures": sorted(self.hair_textures),
            "genders": sorted(self.genders),
            "occasions": sorted(self.occasions),
            "maintenance": self.maintenance,
            "tags": sorted(self.tags),
        }


class HairstyleCatalog:
    """Container for available hairstyles."""

    def __init__(self, hairstyles: Iterable[Hairstyle]):
        self._by_name: Dict[str, Hairstyle] = {}
        for style in hairstyles:
            key = style.name.lower()
            if key in self._by_name:
                raise ValueError(f"Duplicate hairstyle: {style.name}")
            self._by_name[key] = style

    def __iter__(self) -> Iterator[Hairstyle]:
        return iter(self._by_name.values())

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._by_name)

    def __contains__(self, name: object) -> bool:  # pragma: no cover - trivial
        return isinstance(name, str) and name.lower() in self._by_name

    def find(self, name: str) -> Hairstyle:
        """Return a hairstyle by name, raising ``KeyError`` if missing."""

        try:
            return self._by_name[name.lower()]
        except KeyError as exc:  # pragma: no cover - exercised indirectly
            raise KeyError(f"Unknown hairstyle: {name}") from exc

    @classmethod
    def from_records(cls, records: Sequence[Mapping[str, object]]) -> "HairstyleCatalog":
        return cls(Hairstyle.from_mapping(record) for record in records)

    @classmethod
    def from_file(cls, path: Path | str) -> "HairstyleCatalog":
        data = json.loads(Path(path).read_text(encoding="utf8"))
        if not isinstance(data, list):  # pragma: no cover - defensive
            raise ValueError("Hairstyle catalog file must contain a list")
        return cls.from_records(data)

    @classmethod
    def default(cls) -> "HairstyleCatalog":
        """Load the bundled hairstyle catalog."""

        with resources.as_file(_PACKAGE_DATA / "hairstyles.json") as file_path:
            return cls.from_file(file_path)

    def to_list(self) -> List[Dict[str, object]]:
        """Return the catalog as list of dictionaries."""

        return [style.to_dict() for style in self]
