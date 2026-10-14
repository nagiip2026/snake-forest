from __future__ import annotations

from dataclasses import asdict, dataclass


DIFFICULTIES = ("Easy", "Normal", "Hard")
SNAKE_SPEEDS = ("Slow", "Normal", "Fast")
SNAKE_SPEED_MULTIPLIERS = {"Slow": 1.25, "Normal": 1.0, "Fast": 0.8}


@dataclass
class AppSettings:
    difficulty: str = "Normal"
    snake_speed: str = "Normal"
    master_volume: int = 70
    sound_effects: bool = True
    fullscreen: bool = False
    show_grid: bool = True
    reduced_effects: bool = False

    @classmethod
    def from_dict(cls, values: dict[str, object] | None) -> "AppSettings":
        if not isinstance(values, dict):
            values = {}
        difficulty = str(values.get("difficulty", "Normal"))
        if difficulty not in DIFFICULTIES:
            difficulty = "Normal"
        snake_speed = str(values.get("snake_speed", "Normal"))
        if snake_speed not in SNAKE_SPEEDS:
            snake_speed = "Normal"
        try:
            volume = int(values.get("master_volume", 70))
        except (TypeError, ValueError):
            volume = 70
        sound_effects = values.get("sound_effects", True)
        fullscreen = values.get("fullscreen", False)
        show_grid = values.get("show_grid", True)
        reduced_effects = values.get("reduced_effects", False)

        return cls(
            difficulty=difficulty,
            snake_speed=snake_speed,
            master_volume=max(0, min(100, volume)),
            sound_effects=sound_effects if isinstance(sound_effects, bool) else True,
            fullscreen=fullscreen if isinstance(fullscreen, bool) else False,
            show_grid=show_grid if isinstance(show_grid, bool) else True,
            reduced_effects=reduced_effects if isinstance(reduced_effects, bool) else False,
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
