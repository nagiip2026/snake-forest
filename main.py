from __future__ import annotations

import logging
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.resources import ResourceManager, app_log_path, resource_path
from ui.application import SnakeForestWindow


def configure_logging() -> None:
    log_path = app_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=str(log_path),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        encoding="utf-8",
    )


def verify_bundle() -> int:
    """Check that a frozen one-file build contains its runtime assets."""
    configure_logging()
    bundle_root = getattr(sys, "_MEIPASS", None)
    if not getattr(sys, "frozen", False) or not bundle_root:
        logging.error("Bundle verification must run from the packaged EXE.")
        return 2

    try:
        resources = ResourceManager()
        resources.preload()
        for filename in ResourceManager.REQUIRED_IMAGES:
            resources.pygame_image(filename)
        for filename in ResourceManager.REQUIRED_SOUNDS:
            if not resources.sound_path(filename).is_file():
                raise FileNotFoundError(f"Required sound is missing from the bundle: {filename}")
        if not resources.icon_path("play").is_file():
            raise FileNotFoundError("The bundled play icon is missing.")
    except Exception:
        logging.exception("The one-file application is missing a runtime asset.")
        return 1

    logging.info("Standalone one-file bundle and its runtime assets were verified.")
    return 0


def main() -> int:
    if "--verify-bundle" in sys.argv[1:]:
        return verify_bundle()

    configure_logging()
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    application = QApplication(sys.argv)
    application.setApplicationName("Snake Forest")
    application.setOrganizationName("Snake Forest Studio")
    application.setApplicationVersion("1.0.0")
    application.setStyle("Fusion")

    icon_path = resource_path("assets/images/app_icon.ico")
    if icon_path.exists():
        application.setWindowIcon(QIcon(str(icon_path)))

    window = SnakeForestWindow()
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
