from __future__ import annotations

import time
from collections.abc import Callable

import pygame
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, QTimer, Qt, Signal
from PySide6.QtGui import QImage, QPainter, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from app.game_engine import SnakeGameEngine
from app.resources import ResourceManager
from ui.common import (
    FOREST_CARD,
    GOLD,
    LEAF,
    MUTED,
    Panel,
    bind_button_sounds,
    fa_icon,
    format_duration,
    make_button,
    make_icon_button,
)

QT_DIRECTION_KEYS = {
    Qt.Key.Key_Up: "up",
    Qt.Key.Key_W: "up",
    Qt.Key.Key_Down: "down",
    Qt.Key.Key_S: "down",
    Qt.Key.Key_Left: "left",
    Qt.Key.Key_A: "left",
    Qt.Key.Key_Right: "right",
    Qt.Key.Key_D: "right",
}


class GameCanvas(QWidget):
    gameEnded = Signal(int, int, float, str, bool)
    pauseRequested = Signal()

    def __init__(
        self,
        engine: SnakeGameEngine,
        resources: ResourceManager,
        audio,
        settings,
    ) -> None:
        super().__init__()
        self.engine = engine
        self.resources = resources
        self.audio = audio
        self.settings = settings
        self.setMinimumSize(520, 420)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self._last_frame = time.monotonic()
        self._started_at = self._last_frame
        self._reported_end = False
        self._pulse_time = 0.0
        self._background_size: tuple[int, int] | None = None
        self._scaled_background: pygame.Surface | None = None
        self._clock = QTimer(self)
        self._clock.setInterval(16)
        self._clock.timeout.connect(self._advance)
        self._clock.start()

    @property
    def is_paused(self) -> bool:
        return not self.engine.running and not self.engine.game_over

    def _advance(self) -> None:
        now = time.monotonic()
        delta = min(max(0.0, now - self._last_frame), 0.25)
        self._last_frame = now
        self._pulse_time += delta
        events = self.engine.update(delta)
        for event in events:
            if event.kind == "ate":
                self.audio.play("collect")
            elif event.kind == "won":
                self._notify_game_end(True)
            elif event.kind == "game_over":
                self._notify_game_end(False)
        self.update()

    def _notify_game_end(self, won: bool) -> None:
        if self._reported_end:
            return
        self._reported_end = True
        self._clock.stop()
        self.gameEnded.emit(
            self.engine.score,
            self.engine.food_collected,
            self.engine.elapsed_seconds,
            self.engine.difficulty,
            won,
        )

    def pause(self) -> None:
        if self.engine.game_over:
            return
        self.engine.pause()
        self.audio.play("pause")
        self.update()

    def resume(self) -> None:
        if self.engine.game_over:
            return
        self.engine.resume()
        self._last_frame = time.monotonic()
        self._clock.start()
        self.setFocus()
        self.update()

    def restart(self) -> None:
        self.engine.reset()
        self._reported_end = False
        self._started_at = time.monotonic()
        self._last_frame = self._started_at
        self._clock.start()
        self.setFocus()
        self.update()

    def stop(self) -> None:
        self._clock.stop()

    def keyPressEvent(self, event) -> None:
        key = event.key()
        if key in (Qt.Key.Key_Space, Qt.Key.Key_P):
            self.pauseRequested.emit()
            event.accept()
            return
        direction = QT_DIRECTION_KEYS.get(key)
        if direction:
            self.engine.queue_direction(direction)
            event.accept()
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event) -> None:
        self.setFocus()
        super().mousePressEvent(event)

    def paintEvent(self, event) -> None:
        width = max(1, self.width())
        height = max(1, self.height())
        try:
            requested_size = (width, height)
            if self._background_size != requested_size:
                background = self.resources.pygame_image("forest-background.jpg")
                self._scaled_background = pygame.transform.smoothscale(background, requested_size)
                self._background_size = requested_size
            scene = self.engine.render(
                (width, height),
                board_background=self._scaled_background,
                head_sprite=self.resources.pygame_image("snake-head.png"),
                body_sprite=self.resources.pygame_image("snake-body.png"),
                fruit_sprite=self.resources.pygame_image("forest-fruit.png"),
                show_grid=self.settings.show_grid,
                reduced_effects=self.settings.reduced_effects,
                pulse_time=self._pulse_time,
            )
            rgba = pygame.image.tostring(scene, "RGBA")
            image = QImage(
                rgba,
                width,
                height,
                width * 4,
                QImage.Format.Format_RGBA8888,
            ).copy()
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            painter.drawImage(self.rect(), image)
            painter.end()
        except Exception:
            painter = QPainter(self)
            painter.fillRect(self.rect(), Qt.GlobalColor.black)
            painter.end()


class StatPill(QFrame):
    def __init__(self, resources: ResourceManager, icon: str, label: str, value: str) -> None:
        super().__init__()
        self.setObjectName("forestCard")
        self.setMinimumWidth(106)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(11, 8, 11, 8)
        layout.setSpacing(8)
        symbol = QLabel()
        symbol.setPixmap(fa_icon(resources, icon, GOLD, 19).pixmap(19, 19))
        layout.addWidget(symbol)
        labels = QVBoxLayout()
        labels.setSpacing(2)
        top = QLabel(label.upper())
        top.setStyleSheet("font-size: 9px; color: #bac9bb; font-weight: 700;")
        number = QLabel(value)
        number.setStyleSheet("font-size: 16px; color: #f4f8f3; font-weight: 750;")
        labels.addWidget(top)
        labels.addWidget(number)
        layout.addLayout(labels, 1)
        self.value_label = number


class OverlayPanel(QWidget):
    def __init__(
        self,
        resources: ResourceManager,
        title: str,
        subtitle: str,
        buttons: list[tuple[str, str, Callable[[], None], bool]],
    ) -> None:
        super().__init__()
        self.setObjectName("overlayShade")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("QWidget#overlayShade { background: rgba(0, 10, 7, 192); }")
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card = QFrame()
        card.setObjectName("forestPanel")
        card.setMaximumWidth(410)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 28, 32, 30)
        card_layout.setSpacing(13)
        eyebrow = QLabel("SNAKE FOREST")
        eyebrow.setObjectName("eyebrow")
        eyebrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        heading = QLabel(title)
        heading.setObjectName("overlayTitle")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        heading.setWordWrap(True)
        detail = QLabel(subtitle)
        detail.setObjectName("subtitle")
        detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        detail.setWordWrap(True)
        card_layout.addWidget(eyebrow)
        card_layout.addWidget(heading)
        card_layout.addWidget(detail)
        card_layout.addSpacing(7)
        for label, icon_name, action, primary in buttons:
            button = make_button(resources, label, icon_name, primary=primary)
            button.clicked.connect(action)
            card_layout.addWidget(button)
        outer.addWidget(card)
        self.card = card
        self.heading = heading
        self.detail = detail


class GameScreen(QWidget):
    gameFinished = Signal(int, int, float, str, bool)
    openSettings = Signal()
    returnHome = Signal()

    def __init__(
        self,
        resources: ResourceManager,
        audio,
        settings,
        high_score: int,
        on_record_game: Callable[[int, int, float, str], tuple[bool, int]],
    ) -> None:
        super().__init__()
        self.resources = resources
        self.audio = audio
        self.settings = settings
        self.high_score = high_score
        self.on_record_game = on_record_game
        self.engine = SnakeGameEngine(
            difficulty=settings.difficulty,
            snake_speed=settings.snake_speed,
        )
        self._game_recorded = False
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 18)
        root.setSpacing(14)

        header = QHBoxLayout()
        header.setSpacing(9)
        logo = QLabel()
        logo.setPixmap(
            QPixmap.fromImage(resources.image("logo.png")).scaled(
                178,
                60,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        logo.setFixedWidth(180)
        header.addWidget(logo)
        self.score_pill = StatPill(resources, "trophy", "Score", "0")
        self.best_pill = StatPill(resources, "medal", "High Score", str(high_score))
        self.food_pill = StatPill(resources, "apple-whole", "Food", "0")
        self.time_pill = StatPill(resources, "clock", "Time", "00:00")
        self.speed_pill = StatPill(resources, "bolt", "Speed", settings.difficulty)
        self.difficulty_pill = StatPill(resources, "bullseye", "Difficulty", settings.difficulty)
        for pill in (
            self.score_pill,
            self.best_pill,
            self.food_pill,
            self.time_pill,
            self.speed_pill,
            self.difficulty_pill,
        ):
            header.addWidget(pill, 1)

        pause_button = make_icon_button(resources, "pause", "Pause game")
        pause_button.clicked.connect(self.toggle_pause)
        restart_button = make_icon_button(resources, "rotate-right", "Restart game")
        restart_button.clicked.connect(self.restart_game)
        home_button = make_icon_button(resources, "house", "Main menu")
        home_button.clicked.connect(self.confirm_home)
        settings_button = make_icon_button(resources, "gear", "Settings")
        settings_button.clicked.connect(self.openSettings.emit)
        for button in (pause_button, restart_button, home_button, settings_button):
            button.setMinimumHeight(44)
            header.addWidget(button)
        root.addLayout(header)

        main_row = QHBoxLayout()
        main_row.setSpacing(14)
        board_frame = QFrame()
        board_frame.setObjectName("forestPanel")
        board_frame.setContentsMargins(6, 6, 6, 6)
        stack = QStackedLayout(board_frame)
        stack.setStackingMode(QStackedLayout.StackingMode.StackAll)
        self.canvas = GameCanvas(self.engine, resources, audio, settings)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        stack.addWidget(self.canvas)
        stack.setCurrentWidget(self.canvas)
        self.pause_overlay = OverlayPanel(
            resources,
            "GAME PAUSED",
            "Take a breath. The forest will wait for you.",
            [
                ("RESUME", "play", self.resume_game, True),
                ("RESTART", "rotate-right", self.restart_game, False),
                ("SETTINGS", "gear", self.openSettings.emit, False),
                ("MAIN MENU", "house", self.confirm_home, False),
            ],
        )
        stack.addWidget(self.pause_overlay)
        self.pause_overlay.hide()
        self.game_over_overlay = OverlayPanel(
            resources,
            "GAME OVER",
            "The trail ends here. Your next run can go further.",
            [
                ("PLAY AGAIN", "rotate-right", self.restart_game, True),
                ("MAIN MENU", "house", self.confirm_home, False),
            ],
        )
        stack.addWidget(self.game_over_overlay)
        self.game_over_overlay.hide()
        main_row.addWidget(board_frame, 1)

        controls = Panel()
        controls.setFixedWidth(256)
        controls_layout = QVBoxLayout(controls)
        controls_layout.setContentsMargins(17, 16, 17, 15)
        controls_layout.setSpacing(12)
        title = QLabel("CONTROLS")
        title.setStyleSheet("color: #dff1bf; font-size: 13px; font-weight: 800;")
        controls_layout.addWidget(title)
        controls_layout.addLayout(self._control_row(resources, "Move", "arrow-left", "↑  ↓  ←  →"))
        controls_layout.addLayout(self._control_row(resources, "Or use", "keyboard", "W  A  S  D"))
        controls_layout.addWidget(self._line())
        controls_layout.addLayout(self._rule_row(resources, "Collect food", "apple-whole"))
        controls_layout.addLayout(self._rule_row(resources, "Avoid the walls", "xmark"))
        controls_layout.addLayout(self._rule_row(resources, "Avoid your body", "circle-question"))
        controls_layout.addStretch(1)
        keep_going = QLabel("KEEP GOING")
        keep_going.setAlignment(Qt.AlignmentFlag.AlignCenter)
        keep_going.setStyleSheet(
            "color: #dff1a1; font-family: Georgia, serif; font-size: 21px; font-weight: 700;"
        )
        controls_layout.addWidget(keep_going)
        inspiration = QLabel("The forest rewards\nthe brave.")
        inspiration.setObjectName("muted")
        inspiration.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls_layout.addWidget(inspiration)
        main_row.addWidget(controls)
        root.addLayout(main_row, 1)

        self.footer = QLabel("Move with the arrow keys or W A S D  ·  Pause with Space or P")
        self.footer.setStyleSheet("color: #bdcfc1; font-size: 11px;")
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.footer)

        self._hud_timer = QTimer(self)
        self._hud_timer.setInterval(100)
        self._hud_timer.timeout.connect(self._update_hud)
        self._hud_timer.start()
        self.canvas.gameEnded.connect(self._handle_game_end)
        self.canvas.pauseRequested.connect(self.toggle_pause)
        bind_button_sounds(self, audio)
        self.audio.play("game-start")

    @staticmethod
    def _line() -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: rgba(177, 208, 160, 0.26);")
        return line

    @staticmethod
    def _control_row(
        resources: ResourceManager,
        label: str,
        icon_name: str,
        keys: str,
    ) -> QHBoxLayout:
        row = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(fa_icon(resources, icon_name, LEAF, 17).pixmap(17, 17))
        row.addWidget(icon)
        text = QLabel(label)
        text.setObjectName("muted")
        row.addWidget(text, 1)
        key_label = QLabel(keys)
        key_label.setStyleSheet(
            "color: #f4f8f3; font-family: Consolas, monospace; font-weight: 800; "
            "background: rgba(1, 16, 11, 180); padding: 5px 8px; border-radius: 6px;"
        )
        row.addWidget(key_label)
        return row

    @staticmethod
    def _rule_row(resources: ResourceManager, label: str, icon_name: str) -> QHBoxLayout:
        row = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(fa_icon(resources, icon_name, GOLD, 20).pixmap(20, 20))
        icon.setFixedWidth(28)
        row.addWidget(icon)
        text = QLabel(label)
        text.setStyleSheet("color: #d9e6d8;")
        row.addWidget(text)
        return row

    def toggle_pause(self) -> None:
        if self.engine.game_over:
            return
        if self.engine.running:
            self.canvas.pause()
            self.pause_overlay.show()
            self.pause_overlay.raise_()
            self.canvas.clearFocus()
        else:
            self.resume_game()

    def resume_game(self) -> None:
        self.game_over_overlay.hide()
        self.pause_overlay.hide()
        self.canvas.resume()

    def restart_game(self) -> None:
        self.pause_overlay.hide()
        self.game_over_overlay.hide()
        self._game_recorded = False
        self.canvas.restart()
        if hasattr(self, "_celebration"):
            self._celebration.stop()
        self.game_over_overlay.card.setObjectName("forestPanel")
        self.game_over_overlay.heading.setText("GAME OVER")
        self.game_over_overlay.heading.setWordWrap(True)
        self.game_over_overlay.detail.setText("The trail ends here. A deeper run is just ahead.")
        self.audio.play("game-start")
        self.high_score = max(self.high_score, self.engine.score)
        self.best_pill.value_label.setText(str(self.high_score))

    def confirm_home(self) -> None:
        self.canvas.stop()
        self._hud_timer.stop()
        self.returnHome.emit()

    def _update_hud(self) -> None:
        self.score_pill.value_label.setText(str(self.engine.score))
        self.food_pill.value_label.setText(str(self.engine.food_collected))
        self.time_pill.value_label.setText(format_duration(self.engine.elapsed_seconds))
        self.speed_pill.value_label.setText(self.engine.speed_label)

    def _handle_game_end(
        self,
        score: int,
        food_collected: int,
        duration: float,
        difficulty: str,
        won: bool,
    ) -> None:
        if self._game_recorded:
            return
        self._game_recorded = True
        new_high, previous_best = self.on_record_game(score, food_collected, duration, difficulty)
        self.high_score = max(previous_best, score)
        self.best_pill.value_label.setText(str(self.high_score))
        self.audio.play("high-score" if new_high else "game-over")
        title = "NEW HIGH SCORE!" if new_high else ("FOREST CHAMPION" if won else "GAME OVER")
        subtitle = (
            f"Final score  {score}     ·     Previous best  {previous_best}\n"
            f"Fruit  {food_collected}   ·   Time  {format_duration(duration)}   ·   {difficulty}\n"
            f"{'A new high score!' if new_high else 'Best run: ' + str(self.high_score)}"
        )
        if won:
            subtitle += "\nYou filled every open cell in the forest."
        self.game_over_overlay.heading.setText(title)
        self.game_over_overlay.heading.setWordWrap(not new_high)
        self.game_over_overlay.detail.setText(subtitle)
        if new_high:
            self.game_over_overlay.card.setObjectName("celebrationPanel")
        self.game_over_overlay.show()
        self.game_over_overlay.raise_()
        if new_high:
            final_geometry = self.game_over_overlay.card.geometry()
            self._celebration = QPropertyAnimation(self.game_over_overlay.card, b"geometry", self)
            self._celebration.setDuration(360)
            self._celebration.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._celebration.setStartValue(final_geometry.translated(0, 12))
            self._celebration.setEndValue(final_geometry)
            self._celebration.start()
        self.pause_overlay.hide()

    def update_settings(self, settings) -> None:
        self.settings = settings
        self.engine.set_difficulty(settings.difficulty)
        self.engine.set_snake_speed(settings.snake_speed)
        self.difficulty_pill.value_label.setText(settings.difficulty)
        self.speed_pill.value_label.setText(self.engine.speed_label)
