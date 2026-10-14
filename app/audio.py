from __future__ import annotations

import logging

import pygame

from app.resources import ResourceManager

logger = logging.getLogger(__name__)


class AudioManager:
    def __init__(self, resources: ResourceManager) -> None:
        self.resources = resources
        self.enabled = False
        self.device_available = False
        self.volume = 0.7
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            for name in (
                "ui-click",
                "collect",
                "game-start",
                "pause",
                "game-over",
                "high-score",
            ):
                path = resources.sound_path(f"{name}.wav")
                if path.is_file():
                    try:
                        self.sounds[name] = pygame.mixer.Sound(str(path))
                    except pygame.error:
                        logger.exception("Sound could not be loaded: %s", path)
            self.enabled = bool(self.sounds)
            self.device_available = self.enabled
        except pygame.error:
            logger.exception("Audio device is unavailable; continuing without audio.")

    def configure(self, enabled: bool, volume: int) -> None:
        self.enabled = self.device_available and enabled
        self.volume = max(0, min(100, volume)) / 100
        for sound in self.sounds.values():
            sound.set_volume(self.volume)

    def play(self, name: str) -> None:
        sound = self.sounds.get(name)
        if self.enabled and sound:
            try:
                sound.set_volume(self.volume)
                sound.play()
            except pygame.error:
                logger.exception("Sound playback failed: %s", name)
