from __future__ import annotations

import logging
import pygame
from PySide6.QtCore import QObject, Qt, Signal, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from app.database import GameDatabase
from app.game_engine import SnakeGameEngine
from app.resources import ResourceManager, user_data_dir
from ui.common import ForestBackdrop, Panel, TEXT

logger = logging.getLogger(__name__)


class SplashLoader(QObject):
    progress = Signal(str, int)
    finished = Signal(object, object, object)
    failed = Signal(str)

    @Slot()
    def run(self) -> None:
        try:
            self.progress.emit("Initializing application", 8)
            user_data_dir().mkdir(parents=True, exist_ok=True)

            resources = ResourceManager()
            self.progress.emit("Loading visual assets", 18)
            resources.preload()
            self.progress.emit("Loading visual assets", 43)

            self.progress.emit("Initializing game engine", 54)
            engine = SnakeGameEngine()
            engine.render((160, 110))

            self.progress.emit("Loading saved settings", 72)
            database = GameDatabase(user_data_dir() / "snake-forest.sqlite3")
            settings = database.load_settings()

            self.progress.emit("Preparing game resources", 90)
            icon_path = resources.icon_path("play")
            if not icon_path.is_file():
                raise FileNotFoundError("Bundled Font Awesome assets are incomplete.")
            for sound_path in resources.REQUIRED_SOUNDS:
                if not resources.sound_path(sound_path).is_file():
                    logger.warning("Optional sound asset missing: %s", sound_path)

            self.progress.emit("Ready", 100)
            self.finished.emit(resources, database, settings)
        except Exception as error:
            logger.exception("Application startup failed.")
            self.failed.emit(str(error))


class SplashScreen(ForestBackdrop):
    def __init__(self, resources: ResourceManager) -> None:
        super().__init__(resources, overlay_alpha=94)
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 34, 48, 34)
        root.setSpacing(20)
        root.addStretch(1)

        center = QFrame()
        center.setStyleSheet("background: rgba(3, 18, 13, 110); border: none;")
        content = QVBoxLayout(center)
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content.setSpacing(10)
        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setPixmap(
            QPixmap.fromImage(resources.image("logo.png")).scaled(
                720,
                290,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        content.addWidget(logo, 0, Qt.AlignmentFlag.AlignCenter)
        tagline = QLabel("Enter the wild. Challenge your instincts.")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setStyleSheet("color: #f2e7bb; font: 600 17px 'Segoe UI';")
        content.addWidget(tagline)
        message = QLabel("Preparing your adventure...")
        message.setObjectName("muted")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content.addWidget(message)

        progress_row = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(17)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar { background: rgba(6, 23, 16, 210); border: 1px solid #a2bf88;
                           border-radius: 8px; }
            QProgressBar::chunk { border-radius: 7px; background: #19c274; }
            """
        )
        self.percentage = QLabel("0%")
        self.percentage.setFixedWidth(48)
        progress_row.addWidget(self.progress_bar, 1)
        progress_row.addWidget(self.percentage)
        content.addLayout(progress_row)

        self.steps = QLabel(
            "◌  Initializing application     ›     ◌  Loading visual assets     ›     "
            "◌  Initializing game engine     ›     ◌  Loading saved settings"
        )
        self.steps.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.steps.setWordWrap(True)
        self.steps.setStyleSheet("color: #d4e1d5; font-size: 12px;")
        content.addWidget(self.steps)

        root.addWidget(center, 0)
        root.addStretch(1)

        footer = QLabel("SNAKE FOREST  •  WINDOWS DESKTOP GAME")
        footer.setStyleSheet("color: rgba(232, 243, 227, 0.68); letter-spacing: 2px;")
        root.addWidget(footer, 0, Qt.AlignmentFlag.AlignCenter)
        self._status = message

    def set_progress(self, message: str, percentage: int) -> None:
        self._status.setText(message + "...")
        self.progress_bar.setValue(percentage)
        self.percentage.setText(f"{percentage}%")
