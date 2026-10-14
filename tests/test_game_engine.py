from __future__ import annotations

import random

from app.game_engine import SnakeGameEngine


def engine(**kwargs) -> SnakeGameEngine:
    return SnakeGameEngine(rng=random.Random(4), **kwargs)


def test_start_has_safe_snake_and_food() -> None:
    game = engine()
    assert len(game.snake) == 4
    assert game.food is not None
    assert game.food not in game.snake
    assert game.score == 0


def test_opposite_direction_is_rejected() -> None:
    game = engine()
    assert not game.queue_direction("left")
    assert game.queue_direction("up")
    game.step()
    assert game.direction == "up"


def test_collecting_food_grows_and_scores() -> None:
    game = engine()
    game.food = (game.snake[0][0] + 1, game.snake[0][1])
    previous_length = len(game.snake)
    previous_interval = game.step_interval_ms
    result = game.step()
    assert result is not None
    assert result.kind == "ate"
    assert len(game.snake) == previous_length + 1
    assert game.step_interval_ms < previous_interval
    assert game.food_collected == 1
    assert game.score == 10
    assert game.food not in game.snake


def test_wall_collision_ends_the_run() -> None:
    game = engine(width=8, height=8)
    game.snake = [(7, 4), (6, 4), (5, 4), (4, 4)]
    game.direction = "right"
    game.queued_direction = "right"
    result = game.step()
    assert result is not None
    assert result.kind == "game_over"
    assert game.game_over
    assert not game.running


def test_self_collision_ends_the_run() -> None:
    game = engine()
    game.snake = [(3, 3), (4, 3), (4, 4), (3, 4), (2, 4)]
    game.direction = "right"
    game.queued_direction = "down"
    result = game.step()
    assert result is not None
    assert result.kind == "game_over"


def test_vacating_tail_cell_is_safe_without_growth() -> None:
    game = engine()
    game.snake = [(3, 3), (3, 4), (2, 4), (2, 3)]
    game.direction = "left"
    game.queued_direction = "left"
    result = game.step()
    assert result is None
    assert game.snake[0] == (2, 3)
    assert not game.game_over


def test_difficulty_changes_real_movement_interval() -> None:
    game = engine(difficulty="Easy")
    easy = game.step_interval_ms
    game.set_difficulty("Normal")
    normal = game.step_interval_ms
    game.set_difficulty("Hard")
    hard = game.step_interval_ms
    assert easy > normal > hard


def test_speed_starts_slower_and_growth_speedup_has_a_cap() -> None:
    game = engine()
    assert game.step_interval_ms == 160.0

    game.snake.extend((index, 0) for index in range(100))
    assert game.step_interval_ms == 160.0 * 0.65


def test_selectable_snake_speed_changes_movement_interval() -> None:
    game = engine()
    normal = game.step_interval_ms
    game.set_snake_speed("Slow")
    slow = game.step_interval_ms
    game.set_snake_speed("Fast")
    fast = game.step_interval_ms
    assert slow > normal > fast


def test_paused_game_does_not_advance() -> None:
    game = engine()
    before = list(game.snake)
    game.pause()
    assert game.update(0.8) == []
    assert game.snake == before
    assert game.elapsed_seconds == 0
