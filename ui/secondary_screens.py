from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from app.config import AppSettings, SNAKE_SPEEDS
from app.resources import ResourceManager
from ui.common import (
    GOLD,
    LEAF,
    ForestBackdrop,
    Panel,
    bind_button_sounds,
    fa_icon,
    make_button,
)


class ScreenShell(ForestBackdrop):
    def __init__(
        self,
        resources: ResourceManager,
        eyebrow: str,
        title: str,
        subtitle: str,
        on_back: Callable[[], None],
        audio,
    ) -> None:
        super().__init__(resources, overlay_alpha=156)
        self.resources = resources
        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(26, 24, 26, 24)
        self.root_layout.setSpacing(20)
        header = QHBoxLayout()
        back = make_button(resources, "Back", "arrow-left", quiet=True)
        back.setMaximumWidth(145)
        back.clicked.connect(on_back)
        header.addWidget(back)
        header.addStretch(1)
        title_stack = QVBoxLayout()
        small = QLabel(eyebrow.upper())
        small.setObjectName("eyebrow")
        name = QLabel(title)
        name.setObjectName("title")
        title_stack.addWidget(small)
        title_stack.addWidget(name)
        header.addLayout(title_stack, 0)
        header.addStretch(1)
        marker = QLabel("SNAKE FOREST")
        marker.setStyleSheet("color: #dce8d6; font-size: 11px; letter-spacing: 2px;")
        header.addWidget(marker)
        self.root_layout.addLayout(header)
        if subtitle:
            detail = QLabel(subtitle)
            detail.setObjectName("subtitle")
            detail.setWordWrap(True)
            self.root_layout.addWidget(detail)
        bind_button_sounds(self, audio)


class SettingsScreen(ScreenShell):
    def __init__(
        self,
        resources: ResourceManager,
        settings: AppSettings,
        on_back: Callable[[], None],
        on_save: Callable[[AppSettings], None],
        on_reset_statistics: Callable[[], None],
        audio,
    ) -> None:
        super().__init__(
            resources,
            "MAKE IT YOURS",
            "Settings",
            "Choose how the forest feels and how your game responds.",
            on_back,
            audio,
        )
        self.current_settings = settings
        self.on_save = on_save
        self.on_reset_statistics = on_reset_statistics
        body = QHBoxLayout()
        body.setSpacing(16)

        gameplay = Panel()
        gameplay_layout = QVBoxLayout(gameplay)
        gameplay_layout.setContentsMargins(24, 22, 24, 22)
        gameplay_layout.setSpacing(15)
        gameplay_title = QLabel("GAMEPLAY")
        gameplay_title.setStyleSheet("color: #dff1bf; font-size: 13px; font-weight: 800;")
        gameplay_layout.addWidget(gameplay_title)
        difficulty_row = QHBoxLayout()
        difficulty_label = QLabel("Difficulty")
        difficulty_label.setObjectName("muted")
        difficulty_row.addWidget(difficulty_label, 1)
        self.difficulty = QComboBox()
        self.difficulty.addItems(["Easy", "Normal", "Hard"])
        self.difficulty.setCurrentText(settings.difficulty)
        self.difficulty.setMinimumWidth(175)
        difficulty_row.addWidget(self.difficulty)
        gameplay_layout.addLayout(difficulty_row)

        speed_row = QHBoxLayout()
        speed_label = QLabel("Snake speed")
        speed_label.setObjectName("muted")
        speed_row.addWidget(speed_label, 1)
        self.snake_speed = QComboBox()
        self.snake_speed.addItems(SNAKE_SPEEDS)
        self.snake_speed.setCurrentText(settings.snake_speed)
        self.snake_speed.setMinimumWidth(175)
        speed_row.addWidget(self.snake_speed)
        gameplay_layout.addLayout(speed_row)

        self.fullscreen = QCheckBox("Start in fullscreen")
        self.fullscreen.setChecked(settings.fullscreen)
        self.show_grid = QCheckBox("Show the board grid")
        self.show_grid.setChecked(settings.show_grid)
        self.reduced_effects = QCheckBox("Reduce visual effects")
        self.reduced_effects.setChecked(settings.reduced_effects)
        for checkbox in (self.fullscreen, self.show_grid, self.reduced_effects):
            gameplay_layout.addWidget(checkbox)
        gameplay_layout.addSpacing(8)
        note = QLabel("Controls")
        note.setStyleSheet("font-weight: 750; color: #dcead7;")
        gameplay_layout.addWidget(note)
        keys = QLabel("Arrow keys or W A S D to move\nSpace or P to pause / resume")
        keys.setObjectName("muted")
        gameplay_layout.addWidget(keys)
        gameplay_layout.addStretch(1)
        body.addWidget(gameplay, 1)

        audio_panel = Panel()
        audio_layout = QVBoxLayout(audio_panel)
        audio_layout.setContentsMargins(24, 22, 24, 22)
        audio_layout.setSpacing(15)
        audio_title = QLabel("SOUND")
        audio_title.setStyleSheet("color: #dff1bf; font-size: 13px; font-weight: 800;")
        audio_layout.addWidget(audio_title)
        self.effects = QCheckBox("Sound effects")
        self.effects.setChecked(settings.sound_effects)
        audio_layout.addWidget(self.effects)
        volume_row = QHBoxLayout()
        volume_label = QLabel("Master volume")
        volume_label.setObjectName("muted")
        volume_row.addWidget(volume_label, 1)
        self.volume_value = QLabel(f"{settings.master_volume}%")
        self.volume_value.setStyleSheet("color: #e3f4d5; font-weight: 750;")
        volume_row.addWidget(self.volume_value)
        audio_layout.addLayout(volume_row)
        self.volume = QSlider(Qt.Orientation.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(settings.master_volume)
        self.volume.valueChanged.connect(lambda value: self.volume_value.setText(f"{value}%"))
        audio_layout.addWidget(self.volume)
        audio_note = QLabel("Original game sounds are stored with the app and work offline.")
        audio_note.setWordWrap(True)
        audio_note.setObjectName("muted")
        audio_layout.addWidget(audio_note)
        audio_layout.addStretch(1)
        body.addWidget(audio_panel, 1)

        self.root_layout.addLayout(body, 1)
        bottom = QHBoxLayout()
        reset = make_button(resources, "Reset Statistics", "rotate-right", quiet=True)
        reset.clicked.connect(self._confirm_reset)
        bottom.addWidget(reset)
        bottom.addStretch(1)
        save = make_button(resources, "SAVE SETTINGS", "circle-check", primary=True)
        save.setMinimumWidth(220)
        save.clicked.connect(self._save)
        bottom.addWidget(save)
        self.root_layout.addLayout(bottom)

    def _save(self) -> None:
        self.current_settings = AppSettings(
            difficulty=self.difficulty.currentText(),
            snake_speed=self.snake_speed.currentText(),
            master_volume=self.volume.value(),
            sound_effects=self.effects.isChecked(),
            fullscreen=self.fullscreen.isChecked(),
            show_grid=self.show_grid.isChecked(),
            reduced_effects=self.reduced_effects.isChecked(),
        )
        self.on_save(self.current_settings)

    def _confirm_reset(self) -> None:
        result = QMessageBox.question(
            self,
            "Reset game statistics?",
            "This permanently clears your saved scores and game history. Your settings will stay unchanged.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if result == QMessageBox.StandardButton.Yes:
            self.on_reset_statistics()


class HowToPlayScreen(ScreenShell):
    def __init__(
        self,
        resources: ResourceManager,
        on_back: Callable[[], None],
        audio,
    ) -> None:
        super().__init__(
            resources,
            "TRAIL GUIDE",
            "How to Play",
            "Grow your snake, collect forest fruit, and keep clear of the edges.",
            on_back,
            audio,
        )
        instructions = [
            ("Move up", "arrow-up", "↑  or  W"),
            ("Move down", "arrow-down", "↓  or  S"),
            ("Move left", "arrow-left", "←  or  A"),
            ("Move right", "arrow-right", "→  or  D"),
            ("Collect glowing fruit", "apple-whole", "10 points per fruit"),
            ("Avoid the forest walls", "xmark", "A wall collision ends the run"),
            ("Avoid your own body", "circle-question", "You cannot reverse direction"),
            ("Pause or resume", "pause", "Space  or  P"),
        ]
        cards = QFrame()
        cards.setObjectName("forestPanel")
        rows = QVBoxLayout(cards)
        rows.setContentsMargins(24, 20, 24, 20)
        rows.setSpacing(2)
        for index, (label, icon_name, key) in enumerate(instructions):
            row = QHBoxLayout()
            row.setContentsMargins(6, 10, 6, 10)
            icon = QLabel()
            icon.setPixmap(fa_icon(resources, icon_name, GOLD if index >= 4 else LEAF, 21).pixmap(21, 21))
            icon.setFixedWidth(36)
            row.addWidget(icon)
            title = QLabel(label)
            title.setStyleSheet("color: #f2f7ed; font-size: 15px; font-weight: 700;")
            row.addWidget(title, 1)
            hint = QLabel(key)
            hint.setStyleSheet(
                "color: #c0d5bf; font-family: Consolas, monospace; font-size: 12px; "
                "background: rgba(2, 17, 11, 140); padding: 6px 10px; border-radius: 7px;"
            )
            row.addWidget(hint)
            rows.addLayout(row)
            if index < len(instructions) - 1:
                line = QFrame()
                line.setFrameShape(QFrame.Shape.HLine)
                line.setStyleSheet("color: rgba(177, 208, 160, 0.18);")
                rows.addWidget(line)
        self.root_layout.addWidget(cards, 1)


