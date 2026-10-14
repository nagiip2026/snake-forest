from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)

from app.resources import ResourceManager
from ui.common import (
    EMERALD,
    GOLD,
    LEAF,
    MUTED,
    ForestBackdrop,
    ImageView,
    Panel,
    bind_button_sounds,
    fa_icon,
    make_button,
    make_icon_button,
)


class MetricCard(QFrame):
    def __init__(self, resources: ResourceManager, title: str, value: str, icon_name: str) -> None:
        super().__init__()
        self.setObjectName("forestCard")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)
        icon = QLabel()
        icon.setPixmap(fa_icon(resources, icon_name, GOLD, 24).pixmap(24, 24))
        icon.setFixedWidth(28)
        layout.addWidget(icon, 0, Qt.AlignmentFlag.AlignVCenter)
        text = QVBoxLayout()
        text.setSpacing(4)
        name = QLabel(title.upper())
        name.setStyleSheet("font-size: 10px; color: #bdd0bf; font-weight: 700;")
        number = QLabel(value)
        number.setStyleSheet("font-size: 22px; color: #f3fbef; font-weight: 750;")
        text.addWidget(name)
        text.addWidget(number)
        layout.addLayout(text, 1)
        self.value_label = number


class DashboardScreen(ForestBackdrop):
    def __init__(
        self,
        resources: ResourceManager,
        stats: dict[str, int | float | str],
        difficulty: str,
        on_navigate: Callable[[str], None],
        on_quit: Callable[[], None],
        on_toggle_sound: Callable[[], None],
        sound_enabled: bool,
        audio,
    ) -> None:
        super().__init__(resources, overlay_alpha=132)
        self.resources = resources
        self.stats = stats
        self.difficulty = difficulty
        root = QHBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(18)

        sidebar = QFrame()
        sidebar.setObjectName("forestPanel")
        sidebar.setFixedWidth(218)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(13, 18, 13, 16)
        side.setSpacing(9)
        logo = ImageView(resources.image("logo.png"), maximum_height=100)
        side.addWidget(logo)
        brand_note = QLabel("THE WILD IS CALLING")
        brand_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_note.setStyleSheet("color: #a4d77a; font-size: 9px; letter-spacing: 1.5px;")
        side.addWidget(brand_note)
        side.addSpacing(12)

        navigation = [
            ("Home", "house", "home"),
            ("Play Now", "play", "play"),
            ("How to Play", "circle-question", "how-to-play"),
            ("Settings", "gear", "settings"),
        ]
        for label, icon_name, key in navigation:
            button = make_button(resources, label, icon_name, quiet=True)
            button.setObjectName("navButton")
            button.setProperty("active", key == "home")
            button.clicked.connect(lambda _checked=False, destination=key: on_navigate(destination))
            side.addWidget(button)

        side.addStretch(1)
        quit_button = make_button(resources, "Quit Game", "xmark", quiet=True)
        quit_button.setObjectName("navButton")
        quit_button.clicked.connect(on_quit)
        side.addWidget(quit_button)
        version = QLabel("SNAKE FOREST  •  v1.0.0")
        version.setStyleSheet("color: #98ac9b; font-size: 10px;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side.addWidget(version)
        root.addWidget(sidebar)

        center = QWidget()
        center.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 4, 0, 0)
        center_layout.setSpacing(16)

        top_actions = QHBoxLayout()
        welcome = QLabel("WELCOME BACK, TRAILBLAZER")
        welcome.setStyleSheet("color: #d7e4cf; font-size: 11px; letter-spacing: 1.5px;")
        top_actions.addWidget(welcome)
        top_actions.addStretch(1)
        self.sound_button = make_icon_button(
            resources,
            "volume-high" if sound_enabled else "volume-xmark",
            "Toggle sound",
        )
        self.sound_button.clicked.connect(on_toggle_sound)
        top_actions.addWidget(self.sound_button)
        quick_settings = make_icon_button(resources, "gear", "Open settings")
        quick_settings.clicked.connect(lambda: on_navigate("settings"))
        top_actions.addWidget(quick_settings)
        center_layout.addLayout(top_actions)

        intro_row = QHBoxLayout()
        intro_copy = QVBoxLayout()
        intro_copy.setSpacing(9)
        eyebrow = QLabel("A LIVING FOREST ARCADE")
        eyebrow.setObjectName("eyebrow")
        intro_copy.addWidget(eyebrow)
        logo_title = ImageView(resources.image("logo.png"), maximum_height=176)
        logo_title.setMaximumWidth(590)
        intro_copy.addWidget(logo_title, 1)
        desc = QLabel(
            "Enter a living forest where every move matters. Collect glowing fruits, "
            "grow your snake, master your reflexes, and become the ultimate forest champion."
        )
        desc.setObjectName("subtitle")
        desc.setWordWrap(True)
        desc.setMaximumWidth(650)
        intro_copy.addWidget(desc)
        difficulty_badge = QLabel(f"CURRENT TRAIL  ·  {difficulty.upper()}")
        difficulty_badge.setStyleSheet(
            "color: #d9eeaf; font-size: 11px; font-weight: 800; letter-spacing: 1px;"
        )
        intro_copy.addWidget(difficulty_badge)
        intro_row.addLayout(intro_copy, 6)

        mascot = ImageView(resources.image("snake-mascot.png"), maximum_width=330, maximum_height=345)
        mascot.setMinimumWidth(190)
        intro_row.addWidget(mascot, 4)
        center_layout.addLayout(intro_row, 4)

        play_row = QHBoxLayout()
        play = make_button(resources, "PLAY NOW", "play", primary=True)
        play.setMinimumSize(255, 64)
        play.clicked.connect(lambda: on_navigate("play"))
        play_row.addWidget(play)
        howto = make_button(resources, "How to Play", "keyboard", quiet=True)
        howto.setMinimumHeight(56)
        howto.clicked.connect(lambda: on_navigate("how-to-play"))
        play_row.addWidget(howto)
        play_row.addStretch(1)
        center_layout.addLayout(play_row)

        stat_row = QHBoxLayout()
        stat_row.setSpacing(10)
        self.metric_cards: dict[str, MetricCard] = {}
        metric_data = [
            ("Best Score", str(stats["best_score"]), "trophy", "best_score"),
            ("Last Score", str(stats["last_score"]), "medal", "last_score"),
            ("Games Played", str(stats["total_games"]), "chart-bar", "total_games"),
            ("Difficulty", difficulty, "bullseye", "difficulty"),
            ("Player Level", str(stats["player_level"]), "circle-check", "player_level"),
        ]
        for title, value, icon_name, key in metric_data:
            card = MetricCard(resources, title, value, icon_name)
            self.metric_cards[key] = card
            stat_row.addWidget(card, 1)
        center_layout.addLayout(stat_row)
        root.addWidget(center, 1)

        sidebar_stats = Panel()
        sidebar_stats.setFixedWidth(248)
        stats_layout = QVBoxLayout(sidebar_stats)
        stats_layout.setContentsMargins(17, 16, 17, 15)
        stats_layout.setSpacing(11)
        title_row = QHBoxLayout()
        crown = QLabel()
        crown.setPixmap(fa_icon(resources, "trophy", GOLD, 20).pixmap(20, 20))
        title_row.addWidget(crown)
        stats_title = QLabel("GAME STATS")
        stats_title.setStyleSheet("font-size: 12px; font-weight: 800; letter-spacing: 1px;")
        title_row.addWidget(stats_title, 1)
        stats_layout.addLayout(title_row)
        stats_layout.addWidget(self._divider())
        stat_lines = [
            ("trophy", "Best Score", str(stats["best_score"])),
            ("medal", "Last Score", str(stats["last_score"])),
            ("gamepad", "Total Games", str(stats["total_games"])),
            ("bullseye", "Current Difficulty", str(stats["difficulty"])),
            ("chart-bar", "Player Level", str(stats["player_level"])),
        ]
        for icon_name, title, value in stat_lines:
            stats_layout.addLayout(self._stat_line(resources, icon_name, title, value))
        stats_layout.addStretch(1)
        note = QLabel("Small moves.\nBig dreams.")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note.setStyleSheet(
            "color: #e7c864; font-family: Georgia, serif; font-size: 22px; "
            "font-weight: 700; font-style: italic;"
        )
        stats_layout.addWidget(note)
        root.addWidget(sidebar_stats)

        bind_button_sounds(self, audio)

    def update_sound_button(self, enabled: bool) -> None:
        name = "volume-high" if enabled else "volume-xmark"
        self.sound_button.setIcon(fa_icon(self.resources, name, "#f4f8f3"))

    @staticmethod
    def _divider() -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: rgba(177, 208, 160, 0.25);")
        return line

    @staticmethod
    def _stat_line(resources: ResourceManager, icon_name: str, name: str, value: str) -> QHBoxLayout:
        row = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(fa_icon(resources, icon_name, GOLD, 16).pixmap(16, 16))
        row.addWidget(icon)
        label = QLabel(name)
        label.setStyleSheet("color: #d4e0d3; font-size: 12px;")
        row.addWidget(label, 1)
        val = QLabel(value)
        val.setStyleSheet("color: #f4f8f3; font-weight: 750;")
        row.addWidget(val)
        return row
