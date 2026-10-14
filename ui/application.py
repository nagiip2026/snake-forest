from __future__ import annotations

import logging

from PySide6.QtCore import QPropertyAnimation, QThread, QTimer, Qt
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
)

from app.audio import AudioManager
from app.config import AppSettings
from app.database import GameDatabase
from app.resources import ResourceManager, user_data_dir
from ui.common import APP_STYLESHEET
from ui.dashboard import DashboardScreen
from ui.game_screen import GameScreen
from ui.secondary_screens import HowToPlayScreen, SettingsScreen
from ui.splash import SplashLoader, SplashScreen

logger = logging.getLogger(__name__)


class SnakeForestWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Snake Forest")
        self.setMinimumSize(1280, 720)
        self.resize(1536, 960)
        self.setStyleSheet(APP_STYLESHEET)

        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)
        self.resources: ResourceManager | None = None
        self.database: GameDatabase | None = None
        self.settings = AppSettings()
        self.audio: AudioManager | None = None
        self.dashboard: DashboardScreen | None = None
        self.game_screen: GameScreen | None = None
        self.current_key = "splash"
        self.settings_return_key = "home"
        self._transition_animation: QPropertyAnimation | None = None
        self._startup_ready = False
        self._splash_minimum_elapsed = False
        self._splash_timer_started = False
        self._startup_data: tuple[ResourceManager, GameDatabase, AppSettings] | None = None
        self._splash_timer = QTimer(self)
        self._splash_timer.setSingleShot(True)
        self._splash_timer.setInterval(5000)
        self._splash_timer.timeout.connect(self._on_splash_minimum_elapsed)
        self._loader_thread = QThread(self)
        self._loader = SplashLoader()
        self._loader.moveToThread(self._loader_thread)
        self.splash = SplashScreen(ResourceManager())
        self._page_registry: dict[str, object] = {"splash": self.splash}
        self.pages.addWidget(self.splash)
        self.pages.setCurrentWidget(self.splash)
        self._loader_thread.started.connect(self._loader.run)
        self._loader.progress.connect(self.splash.set_progress)
        self._loader.finished.connect(self._on_loaded)
        self._loader.failed.connect(self._on_load_failed)
        self._loader.finished.connect(self._loader_thread.quit)
        self._loader.failed.connect(self._loader_thread.quit)
        self._loader_thread.finished.connect(self._loader.deleteLater)
        self._loader_thread.start()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if not self._splash_timer_started:
            self._splash_timer_started = True
            self._splash_timer.start()

    def _on_loaded(self, resources: ResourceManager, database: GameDatabase, settings: AppSettings) -> None:
        self._startup_ready = True
        self._startup_data = (resources, database, settings)
        self._finish_startup_if_ready()

    def _on_splash_minimum_elapsed(self) -> None:
        self._splash_minimum_elapsed = True
        self._finish_startup_if_ready()

    def _finish_startup_if_ready(self) -> None:
        if not self._startup_ready or not self._splash_minimum_elapsed or self._startup_data is None:
            return
        resources, database, settings = self._startup_data
        self._startup_data = None
        try:
            self.resources = resources
            self.database = database
            self.settings = settings
            self.audio = AudioManager(resources)
            self._configure_audio()
            self._build_dashboard()
            self._set_page("home", self.dashboard, replace=True)
            if self.settings.fullscreen:
                self.showFullScreen()
        except Exception as error:
            logger.exception("The main screen could not be opened.")
            self._on_load_failed(str(error))

    def _on_load_failed(self, message: str) -> None:
        logger.error("Snake Forest could not complete startup: %s", message)
        QMessageBox.critical(
            self,
            "Snake Forest could not start",
            "Some required game resources could not be loaded.\n\n"
            f"{message}\n\n"
            "Check the installation files and start the game again.",
        )
        self.close()

    def _require_services(self) -> tuple[ResourceManager, GameDatabase, AudioManager]:
        if self.resources is None or self.database is None or self.audio is None:
            raise RuntimeError("The game is still loading.")
        return self.resources, self.database, self.audio

    def _build_dashboard(self) -> None:
        resources, database, audio = self._require_services()
        self.dashboard = DashboardScreen(
            resources,
            database.stats(),
            self.settings.difficulty,
            self.navigate,
            self.close,
            self.toggle_sound,
            self.settings.sound_effects,
            audio,
        )

    def navigate(self, destination: str) -> None:
        if self.resources is None:
            return
        if destination == "play":
            self._start_game()
        elif destination == "home":
            self._build_dashboard()
            self._set_page("home", self.dashboard, replace=True)
        elif destination == "settings":
            self._open_settings()
        elif destination == "how-to-play":
            self._show_how_to_play()

    def _start_game(self) -> None:
        resources, database, audio = self._require_services()
        if self.game_screen:
            self.game_screen.canvas.stop()
            self.game_screen._hud_timer.stop()
        self.game_screen = GameScreen(
            resources,
            audio,
            self.settings,
            database.best_score(),
            self._record_game,
        )
        self.game_screen.openSettings.connect(self._open_settings)
        self.game_screen.returnHome.connect(lambda: self.navigate("home"))
        self._set_page("game", self.game_screen, replace=True)
        self.game_screen.canvas.setFocus()

    def _open_settings(self) -> None:
        resources, database, audio = self._require_services()
        if self.current_key == "game" and self.game_screen:
            self.settings_return_key = "game"
            if self.game_screen.engine.running:
                self.game_screen.canvas.pause()
                self.game_screen.pause_overlay.show()
        else:
            self.settings_return_key = "home"
        page = SettingsScreen(
            resources,
            self.settings,
            self._return_from_settings,
            self._save_settings,
            self._reset_statistics,
            audio,
        )
        self._set_page("settings", page, replace=True)

    def _return_from_settings(self) -> None:
        if self.settings_return_key == "game" and self.game_screen:
            self._set_page("game", self.game_screen)
        else:
            self.navigate("home")

    def _show_how_to_play(self) -> None:
        resources, _, audio = self._require_services()
        page = HowToPlayScreen(
            resources,
            lambda: self.navigate("home"),
            audio,
        )
        self._set_page("how-to-play", page, replace=True)

    def _set_page(self, key: str, page, *, replace: bool = False) -> None:
        if page is None:
            return
        if replace:
            old_page = self._page_registry.get(key)
            if old_page is not None and old_page is not page:
                self.pages.removeWidget(old_page)
                old_page.deleteLater()
        if self.pages.indexOf(page) == -1:
            self.pages.addWidget(page)
        self.pages.setCurrentWidget(page)
        self.current_key = key
        self._page_registry[key] = page
        if key != "game":
            if self._transition_animation is not None:
                self._transition_animation.stop()
                self._transition_animation.deleteLater()
            effect = QGraphicsOpacityEffect(page)
            page.setGraphicsEffect(effect)
            effect.setOpacity(0.0)
            animation = QPropertyAnimation(effect, b"opacity", self)
            animation.setDuration(240)
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
            self._transition_animation = animation
            animation.start()

    def _record_game(
        self,
        score: int,
        food_collected: int,
        duration: float,
        difficulty: str,
    ) -> tuple[bool, int]:
        if self.database is None:
            return False, 0
        previous_best = self.database.best_score()
        was_new_best = self.database.record_game(score, food_collected, duration, difficulty)
        return was_new_best, previous_best

    def _save_settings(self, settings: AppSettings) -> None:
        _, database, audio = self._require_services()
        self.settings = settings
        database.save_settings(settings)
        self._configure_audio()
        if self.game_screen:
            self.game_screen.update_settings(settings)
        if settings.fullscreen and not self.isFullScreen():
            self.showFullScreen()
        elif not settings.fullscreen and self.isFullScreen():
            self.showNormal()
        self.statusBar().showMessage("Settings saved", 2500)

    def _configure_audio(self) -> None:
        if self.audio:
            self.audio.configure(self.settings.sound_effects, self.settings.master_volume)

    def toggle_sound(self) -> None:
        self.settings.sound_effects = not self.settings.sound_effects
        if self.database:
            self.database.save_settings(self.settings)
        self._configure_audio()
        if self.dashboard:
            self.dashboard.update_sound_button(self.settings.sound_effects)
        if self.settings.sound_effects and self.audio:
            self.audio.play("ui-click")

    def _reset_statistics(self) -> None:
        if self.database:
            self.database.reset_statistics()
        QMessageBox.information(
            self,
            "Statistics reset",
            "Your saved scores and game history have been cleared.",
        )
        self._build_dashboard()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showNormal()
                self.settings.fullscreen = False
            else:
                self.showFullScreen()
                self.settings.fullscreen = True
            if self.database:
                self.database.save_settings(self.settings)
            event.accept()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event) -> None:
        if self.game_screen:
            self.game_screen.canvas.stop()
            self.game_screen._hud_timer.stop()
        if self._loader_thread.isRunning():
            self._loader_thread.quit()
            self._loader_thread.wait(1200)
        event.accept()
