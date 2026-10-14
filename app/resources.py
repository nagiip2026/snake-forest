from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from PySide6.QtGui import QImage

logger = logging.getLogger(__name__)


def resource_path(relative_path: str) -> Path:
    """Resolve a bundled asset in development and in a PyInstaller one-file build."""
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return Path(bundle_root) / relative_path
    return Path(__file__).resolve().parents[1] / relative_path


def user_data_dir() -> Path:
    """Use a writable per-user location instead of the executable's folder."""
    if os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
    elif sys.platform == "darwin":
        root = Path.home() / "Library/Application Support"
    else:
        root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    return root / "SnakeForest"


def app_log_path() -> Path:
    return user_data_dir() / "logs" / "snake-forest.log"


class ResourceManager:
    REQUIRED_IMAGES = (
        "forest-background.jpg",
        "logo.png",
        "snake-mascot.png",
        "snake-head.png",
        "snake-body.png",
        "snake-tail.png",
        "forest-fruit.png",
    )
    REQUIRED_SOUNDS = (
        "ui-click.wav",
        "collect.wav",
        "game-start.wav",
        "pause.wav",
        "game-over.wav",
        "high-score.wav",
    )

    def __init__(self) -> None:
        self.images: dict[str, QImage] = {}
        self.pygame_images: dict[str, object] = {}
        self.load_progress: list[tuple[str, int]] = []

    def preload(self, progress_callback=None) -> None:
        images_dir = resource_path("assets/images")
        names = list(self.REQUIRED_IMAGES)
        total = len(names)
        for index, filename in enumerate(names, start=1):
            path = images_dir / filename
            if not path.is_file():
                raise FileNotFoundError(f"Required visual asset is missing: {path}")
            image = QImage(str(path))
            if image.isNull():
                raise ValueError(f"Could not read the visual asset: {filename}")
            self.images[filename] = image
            percentage = round(index / total * 100)
            self.load_progress.append((filename, percentage))
            if progress_callback:
                progress_callback(filename, percentage)
        icon_path = images_dir / "app_icon.ico"
        if not icon_path.is_file():
            raise FileNotFoundError(f"Required application icon is missing: {icon_path}")

        for filename in self.REQUIRED_SOUNDS:
            if not (resource_path("assets/sounds") / filename).is_file():
                logger.warning("Optional sound effect is missing: %s", filename)

    def image(self, filename: str) -> QImage:
        if filename not in self.images:
            path = resource_path(f"assets/images/{filename}")
            image = QImage(str(path))
            if image.isNull():
                raise FileNotFoundError(f"Unable to load image asset: {path}")
            self.images[filename] = image
        return self.images[filename]

    def pygame_image(self, filename: str):
        if filename not in self.pygame_images:
            import pygame

            path = resource_path(f"assets/images/{filename}")
            self.pygame_images[filename] = pygame.image.load(str(path))
        return self.pygame_images[filename]

    def icon_path(self, icon_name: str) -> Path:
        path = resource_path(f"assets/icons/fontawesome/{icon_name}.svg")
        if not path.is_file():
            raise FileNotFoundError(f"Bundled Font Awesome icon not found: {icon_name}")
        return path

    def sound_path(self, filename: str) -> Path:
        return resource_path(f"assets/sounds/{filename}")
