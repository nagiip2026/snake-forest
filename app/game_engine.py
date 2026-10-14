from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Iterable

import pygame

from app.config import SNAKE_SPEED_MULTIPLIERS


Point = tuple[int, int]
DIRECTION_VECTORS: dict[str, Point] = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}
OPPOSITE = {
    "up": "down",
    "down": "up",
    "left": "right",
    "right": "left",
}
BASE_STEP_MS = {"Easy": 210.0, "Normal": 160.0, "Hard": 120.0}
GROWTH_SPEEDUP_MS = 1.5
MIN_STEP_RATIO = 0.65


@dataclass(frozen=True)
class GameEvent:
    kind: str
    score: int


class SnakeGameEngine:
    """Deterministic grid movement and Pygame board rendering."""

    def __init__(
        self,
        width: int = 26,
        height: int = 18,
        difficulty: str = "Normal",
        snake_speed: str = "Normal",
        rng: random.Random | None = None,
    ) -> None:
        if width < 8 or height < 8:
            raise ValueError("The board must be at least 8 by 8 cells.")
        self.width = width
        self.height = height
        self.rng = rng or random.Random()
        self.difficulty = difficulty if difficulty in BASE_STEP_MS else "Normal"
        self.snake_speed = (
            snake_speed if snake_speed in SNAKE_SPEED_MULTIPLIERS else "Normal"
        )
        self._sprite_cache: dict[tuple[int, int, int], pygame.Surface] = {}
        self.reset()

    def reset(self) -> None:
        center_x = self.width // 2
        center_y = self.height // 2
        self.snake: list[Point] = [
            (center_x, center_y),
            (center_x - 1, center_y),
            (center_x - 2, center_y),
            (center_x - 3, center_y),
        ]
        self.direction = "right"
        self.queued_direction = "right"
        self.food: Point | None = None
        self.food_collected = 0
        self.elapsed_seconds = 0.0
        self.accumulator_ms = 0.0
        self.running = True
        self.game_over = False
        self.won = False
        self.last_event: GameEvent | None = None
        self._spawn_food()

    @property
    def score(self) -> int:
        return self.food_collected * 10

    @property
    def speed_label(self) -> str:
        return f"{1000 / self.step_interval_ms:.1f} c/s"

    @property
    def step_interval_ms(self) -> float:
        base = BASE_STEP_MS[self.difficulty] * SNAKE_SPEED_MULTIPLIERS[self.snake_speed]
        growth = max(0, len(self.snake) - 4)
        return max(base * MIN_STEP_RATIO, base - growth * GROWTH_SPEEDUP_MS)

    def set_difficulty(self, difficulty: str) -> None:
        if difficulty not in BASE_STEP_MS:
            raise ValueError(f"Unknown difficulty: {difficulty}")
        self.difficulty = difficulty

    def set_snake_speed(self, snake_speed: str) -> None:
        if snake_speed not in SNAKE_SPEED_MULTIPLIERS:
            raise ValueError(f"Unknown snake speed: {snake_speed}")
        self.snake_speed = snake_speed

    def queue_direction(self, direction: str) -> bool:
        if direction not in DIRECTION_VECTORS or self.game_over or not self.running:
            return False
        if direction == OPPOSITE[self.direction]:
            return False
        self.queued_direction = direction
        return True

    def pause(self) -> None:
        if not self.game_over:
            self.running = False

    def resume(self) -> None:
        if not self.game_over:
            self.running = True

    def update(self, delta_seconds: float) -> list[GameEvent]:
        """Advance the game using elapsed time; independent of render FPS."""
        if not self.running or self.game_over or delta_seconds <= 0:
            return []
        delta_seconds = min(delta_seconds, 0.25)
        self.elapsed_seconds += delta_seconds
        self.accumulator_ms += delta_seconds * 1000
        events: list[GameEvent] = []
        while self.accumulator_ms >= self.step_interval_ms and self.running:
            self.accumulator_ms -= self.step_interval_ms
            event = self.step()
            if event:
                events.append(event)
        return events

    def step(self) -> GameEvent | None:
        if self.game_over or not self.running:
            return None
        self.direction = self.queued_direction
        dx, dy = DIRECTION_VECTORS[self.direction]
        head_x, head_y = self.snake[0]
        next_head = (head_x + dx, head_y + dy)
        will_grow = next_head == self.food
        body_to_check = self.snake if will_grow else self.snake[:-1]

        if (
            next_head[0] < 0
            or next_head[0] >= self.width
            or next_head[1] < 0
            or next_head[1] >= self.height
            or next_head in body_to_check
        ):
            self.game_over = True
            self.running = False
            self.last_event = GameEvent("game_over", self.score)
            return self.last_event

        self.snake.insert(0, next_head)
        if will_grow:
            self.food_collected += 1
            self._spawn_food()
            if self.food is None:
                self.won = True
                self.game_over = True
                self.running = False
                self.last_event = GameEvent("won", self.score)
            else:
                self.last_event = GameEvent("ate", self.score)
            return self.last_event

        self.snake.pop()
        self.last_event = None
        return None

    def _spawn_food(self) -> None:
        occupied = set(self.snake)
        free_cells = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in occupied
        ]
        self.food = self.rng.choice(free_cells) if free_cells else None

    def render(
        self,
        size: tuple[int, int],
        *,
        board_background: pygame.Surface | None = None,
        head_sprite: pygame.Surface | None = None,
        body_sprite: pygame.Surface | None = None,
        fruit_sprite: pygame.Surface | None = None,
        show_grid: bool = True,
        reduced_effects: bool = False,
        pulse_time: float = 0.0,
    ) -> pygame.Surface:
        width, height = max(1, size[0]), max(1, size[1])
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill((5, 24, 17, 255))

        if board_background:
            background = (
                board_background
                if board_background.get_size() == (width, height)
                else pygame.transform.smoothscale(board_background, (width, height))
            )
            surface.blit(background, (0, 0))
        shade = pygame.Surface((width, height), pygame.SRCALPHA)
        shade.fill((0, 18, 11, 214))
        surface.blit(shade, (0, 0))

        cell = min(width / self.width, height / self.height)
        board_width = cell * self.width
        board_height = cell * self.height
        origin_x = (width - board_width) / 2
        origin_y = (height - board_height) / 2
        cell_px = max(1, int(cell))

        if show_grid:
            for column in range(self.width + 1):
                x = round(origin_x + column * cell)
                pygame.draw.line(
                    surface,
                    (104, 165, 111, 42),
                    (x, round(origin_y)),
                    (x, round(origin_y + board_height)),
                    1,
                )
            for row in range(self.height + 1):
                y = round(origin_y + row * cell)
                pygame.draw.line(
                    surface,
                    (104, 165, 111, 42),
                    (round(origin_x), y),
                    (round(origin_x + board_width), y),
                    1,
                )

        if self.food:
            food_rect = self._cell_rect(self.food, cell, origin_x, origin_y)
            scale = 0.8 if reduced_effects else 0.82 + math.sin(pulse_time * 4.0) * 0.04
            fruit_size = max(9, round(cell * scale))
            center = food_rect.center
            if not reduced_effects:
                glow = pygame.Surface((cell_px * 2, cell_px * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    glow,
                    (250, 133, 34, 38),
                    (glow.get_width() // 2, glow.get_height() // 2),
                    max(4, cell_px // 2),
                )
                surface.blit(glow, glow.get_rect(center=center))
            if fruit_sprite:
                sprite = self._sprite_variant(fruit_sprite, fruit_size, 0)
                surface.blit(sprite, sprite.get_rect(center=center))
            else:
                pygame.draw.circle(surface, (237, 84, 40), center, max(4, fruit_size // 2))

        for index, segment in reversed(list(enumerate(self.snake[1:], start=1))):
            rect = self._cell_rect(segment, cell, origin_x, origin_y)
            inset = max(1, int(cell * 0.035))
            inner = rect.inflate(-inset * 2, -inset * 2)
            if body_sprite:
                body = self._sprite_variant(body_sprite, cell_px, 0)
                surface.blit(body, body.get_rect(center=rect.center))
            else:
                fill = (26, 142 + (index % 3) * 12, 70)
                pygame.draw.rect(surface, fill, inner, border_radius=max(3, cell_px // 3))
                pygame.draw.rect(
                    surface,
                    (123, 221, 105),
                    inner,
                    width=max(1, cell_px // 12),
                    border_radius=max(3, cell_px // 3),
                )

        head = self.snake[0]
        head_rect = self._cell_rect(head, cell, origin_x, origin_y)
        head_size = max(9, round(cell * 1.13))
        center = head_rect.center
        if not reduced_effects:
            pygame.draw.circle(surface, (62, 218, 112, 95), center, max(4, round(cell * 0.62)), 2)
        if head_sprite:
            image = self._sprite_variant(head_sprite, head_size, 0)
            surface.blit(image, image.get_rect(center=center))
        else:
            pygame.draw.circle(surface, (117, 221, 84), center, head_size // 2)

        pygame.draw.rect(
            surface,
            (154, 198, 112),
            pygame.Rect(round(origin_x), round(origin_y), round(board_width), round(board_height)),
            width=max(2, round(cell * 0.07)),
            border_radius=max(8, round(cell * 0.55)),
        )
        return surface

    def _sprite_variant(
        self,
        sprite: pygame.Surface,
        size: int,
        rotation: int,
    ) -> pygame.Surface:
        key = (id(sprite), size, rotation)
        if key not in self._sprite_cache:
            scaled = pygame.transform.smoothscale(sprite, (size, size))
            self._sprite_cache[key] = pygame.transform.rotate(scaled, rotation) if rotation else scaled
        return self._sprite_cache[key]

    @staticmethod
    def _cell_rect(point: Point, cell: float, origin_x: float, origin_y: float):
        x, y = point
        return pygame.Rect(
            round(origin_x + x * cell),
            round(origin_y + y * cell),
            max(1, round(cell)),
            max(1, round(cell)),
        )


def direction_for_key(key: int) -> str | None:
    return {
        pygame.K_UP: "up",
        pygame.K_w: "up",
        pygame.K_DOWN: "down",
        pygame.K_s: "down",
        pygame.K_LEFT: "left",
        pygame.K_a: "left",
        pygame.K_RIGHT: "right",
        pygame.K_d: "right",
    }.get(key)
