from ai_hair_stylist import (
    ClientPreferences,
    HairstyleCatalog,
    RecommendationEngine,
    recommend_hairstyles,
)


def test_default_catalog_loads() -> None:
    catalog = HairstyleCatalog.default()
    assert len(list(catalog)) == 10
    style = catalog.find("Curly Shag")
    assert "curly" in style.hair_textures
    assert "wash-and-go" in style.tags


def test_engine_ranks_by_preferences() -> None:
    catalog = HairstyleCatalog.default()
    preferences = ClientPreferences(
        face_shape="oval",
        hair_length="medium",
        hair_texture="curly",
        gender="female",
        occasion="creative",
        maintenance="low",
        keywords={"curls", "wash-and-go"},
    )

    engine = RecommendationEngine(catalog)
    recommendations = engine.recommend(preferences, limit=2)
    assert recommendations
    top = recommendations[0]
    assert top.hairstyle.name == "Curly Shag"
    assert top.score > 0
    assert any("curls" in reason for reason in top.reasons)


def test_avoid_tags_remove_options() -> None:
    catalog = HairstyleCatalog.default()
    preferences = ClientPreferences(
        hair_length="long",
        hair_texture="wavy",
        maintenance="medium",
        keywords={"face-framing"},
        avoid={"heat-styling"},
    )

    results = recommend_hairstyles(preferences, catalog=catalog, limit=5)
    assert results
    names = [rec.hairstyle.name for rec in results]
    assert "Sleek Ponytail" not in names


def test_preferences_from_dict_handles_aliases() -> None:
    preferences = ClientPreferences.from_dict(
        {
            "face_shape": "Heart",
            "hair_length": "Short",
            "tags": ["Volume"],
            "avoid": ["heat-styling", "bold"],
        }
    )
    assert preferences.face_shape == "heart"
    assert preferences.hair_length == "short"
    assert preferences.keywords == frozenset({"volume"})
    assert "bold" in preferences.avoid
