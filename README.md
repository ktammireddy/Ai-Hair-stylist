# AI Hair Stylist

Utilities for running a consultation-style workflow that suggests suitable hairstyles
based on client preferences. The project exposes a small, rule-based recommendation
engine that can be used programmatically or from the command line.

## Features

- Curated catalog of gender-inclusive hairstyles with metadata such as suitable face
  shapes, hair textures, occasions, and maintenance levels.
- `ClientPreferences` model that normalises user input and supports keyword filters
  and "avoid" lists.
- `RecommendationEngine` that scores each hairstyle and provides reasoning for why it
  was suggested.
- Command-line interface (`python -m ai_hair_stylist`) for quick experimentation.

## Usage

```bash
python -m ai_hair_stylist --face-shape oval --hair-texture curly \
  --hair-length medium --keywords curls wash-and-go
```

Use the `--json` flag to produce machine-readable output.

Programmatic usage is just as straightforward:

```python
from ai_hair_stylist import ClientPreferences, HairstyleCatalog, RecommendationEngine

catalog = HairstyleCatalog.default()
preferences = ClientPreferences(face_shape="oval", hair_texture="curly")
engine = RecommendationEngine(catalog)
recommendations = engine.recommend(preferences)
```

## Development

Install dependencies (none beyond the standard library are required) and run the
unit tests with:

```bash
python -m pytest
```

The project targets Python 3.11 or newer.
