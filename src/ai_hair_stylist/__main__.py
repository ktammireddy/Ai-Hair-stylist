"""Simple command line interface for generating hairstyle recommendations."""
from __future__ import annotations

import argparse
import json
from typing import Any

from . import ClientPreferences, HairstyleCatalog, RecommendationEngine


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--face-shape")
    parser.add_argument("--hair-length")
    parser.add_argument("--hair-texture")
    parser.add_argument("--gender")
    parser.add_argument("--occasion")
    parser.add_argument("--maintenance")
    parser.add_argument(
        "--keywords",
        nargs="*",
        help="Desired features such as volume or protective",
    )
    parser.add_argument(
        "--avoid",
        nargs="*",
        help="Tags to avoid such as heat-styling",
    )
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument(
        "--json", dest="as_json", action="store_true", help="Output as JSON"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    catalog = HairstyleCatalog.default()
    preferences = ClientPreferences(
        face_shape=args.face_shape,
        hair_length=args.hair_length,
        hair_texture=args.hair_texture,
        gender=args.gender,
        occasion=args.occasion,
        maintenance=args.maintenance,
        keywords=args.keywords,
        avoid=args.avoid,
    )
    engine = RecommendationEngine(catalog)
    recommendations = engine.recommend(preferences, limit=args.limit)

    if args.as_json:
        payload: list[dict[str, Any]] = [
            {
                "name": rec.hairstyle.name,
                "description": rec.hairstyle.description,
                "score": rec.score,
                "reasons": list(rec.reasons),
            }
            for rec in recommendations
        ]
        print(json.dumps(payload, indent=2))
    else:
        if not recommendations:
            print("No matching hairstyles found.")
        for rec in recommendations:
            print(f"- {rec.hairstyle.name} (score {rec.score:.2f})")
            if rec.reasons:
                for reason in rec.reasons:
                    print(f"    • {reason}")
            print(f"    {rec.hairstyle.description}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
