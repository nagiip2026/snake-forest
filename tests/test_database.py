from __future__ import annotations

import json

from app.config import AppSettings
from app.database import GameDatabase


def test_settings_and_game_results_persist(tmp_path) -> None:
    database = GameDatabase(tmp_path / "save" / "game.sqlite3")
    settings = AppSettings(
        difficulty="Hard",
        snake_speed="Fast",
        master_volume=35,
        show_grid=False,
    )
    database.save_settings(settings)
    assert database.load_settings() == settings

    assert database.record_game(50, 5, 38.5, "Hard")
    assert database.record_game(20, 2, 19.0, "Easy") is False
    assert database.best_score() == 50
    assert database.stats()["total_games"] == 2


def test_corrupted_settings_use_safe_defaults(tmp_path) -> None:
    database = GameDatabase(tmp_path / "game.sqlite3")
    with database._connect() as connection:
        connection.execute(
            """
            INSERT INTO app_state(key, value) VALUES('settings', ?)
            """,
            (json.dumps({"difficulty": "impossible", "master_volume": 999}),),
        )
    loaded = database.load_settings()
    assert loaded.difficulty == "Normal"
    assert loaded.snake_speed == "Normal"
    assert loaded.master_volume == 100


def test_reset_statistics_keeps_saved_settings(tmp_path) -> None:
    database = GameDatabase(tmp_path / "game.sqlite3")
    settings = AppSettings(difficulty="Easy")
    database.save_settings(settings)
    database.record_game(90, 9, 40, "Easy")
    database.reset_statistics()
    assert database.stats()["total_games"] == 0
    assert database.load_settings() == settings
