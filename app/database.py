from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path

from app.config import AppSettings

logger = logging.getLogger(__name__)


class GameDatabase:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS game_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    score INTEGER NOT NULL,
                    food_collected INTEGER NOT NULL,
                    duration_seconds REAL NOT NULL,
                    difficulty TEXT NOT NULL,
                    played_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS app_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )

    def load_settings(self) -> AppSettings:
        try:
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT value FROM app_state WHERE key = 'settings'"
                ).fetchone()
            return AppSettings.from_dict(json.loads(row["value"]) if row else None)
        except (sqlite3.Error, json.JSONDecodeError, TypeError, ValueError):
            logger.exception("Saved settings could not be read; using defaults.")
            return AppSettings()

    def save_settings(self, settings: AppSettings) -> None:
        payload = json.dumps(settings.to_dict())
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO app_state(key, value) VALUES('settings', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (payload,),
            )

    def best_score(self) -> int:
        with self._connect() as connection:
            row = connection.execute("SELECT MAX(score) AS best FROM game_results").fetchone()
        return int(row["best"] or 0)

    def record_game(
        self,
        score: int,
        food_collected: int,
        duration_seconds: float,
        difficulty: str,
    ) -> bool:
        previous_best = self.best_score()
        played_at = datetime.now().astimezone().isoformat(timespec="seconds")
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO game_results(score, food_collected, duration_seconds, difficulty, played_at)
                VALUES(?, ?, ?, ?, ?)
                """,
                (max(0, score), max(0, food_collected), max(0.0, duration_seconds), difficulty, played_at),
            )
        return score > previous_best

    def stats(self) -> dict[str, int | float | str]:
        settings = self.load_settings()
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS total_games,
                       COALESCE(MAX(score), 0) AS best_score,
                       COALESCE((SELECT score FROM game_results ORDER BY id DESC LIMIT 1), 0) AS last_score
                FROM game_results
                """
            ).fetchone()
        best = int(row["best_score"])
        return {
            "total_games": int(row["total_games"]),
            "best_score": best,
            "last_score": int(row["last_score"]),
            "difficulty": settings.difficulty,
            "player_level": max(1, best // 150 + 1),
        }

    def reset_statistics(self) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM game_results")
