from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QByteArray, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.resources import ResourceManager

FOREST = "#06150f"
FOREST_PANEL = "rgba(4, 22, 16, 222)"
FOREST_CARD = "rgba(6, 31, 22, 224)"
EMERALD = "#0db96e"
LEAF = "#a5e779"
GOLD = "#e7bc51"
TEXT = "#f4f8f3"
MUTED = "#a9bcb0"

APP_STYLESHEET = """
QWidget {
    color: #f4f8f3;
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 14px;
}
QMainWindow, QDialog {
    background: #06150f;
}
QStatusBar {
    color: #c5d4c9;
    background: rgba(3, 18, 13, 210);
    border: none;
}
QFrame#forestPanel, QFrame#forestCard, QFrame#glassPanel {
    border: 1px solid rgba(153, 204, 150, 0.32);
    border-radius: 18px;
}
QFrame#forestPanel { background: rgba(4, 22, 16, 228); }
QFrame#forestCard { background: rgba(6, 31, 22, 230); }
QFrame#glassPanel { background: rgba(0, 18, 12, 185); }
QFrame#celebrationPanel {
    background: rgba(9, 36, 21, 246);
    border: 2px solid #edcd67;
    border-radius: 18px;
}
QLabel#eyebrow {
    color: #a5e779;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
}
QLabel#title {
    color: #f8fbf5;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 36px;
    font-weight: 700;
}
QLabel#overlayTitle {
    color: #f8fbf5;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 28px;
    font-weight: 700;
}
QLabel#subtitle { color: #c5d4c9; font-size: 15px; }
QLabel#muted { color: #a9bcb0; }
QPushButton {
    color: #edf5ec;
    background: rgba(14, 51, 36, 225);
    border: 1px solid rgba(153, 204, 150, 0.35);
    border-radius: 12px;
    padding: 11px 16px;
    font-weight: 650;
    text-align: left;
}
QPushButton:hover {
    background: rgba(28, 93, 57, 235);
    border-color: #82ce74;
}
QPushButton:pressed { background: #0d442d; }
QPushButton:disabled { color: #718178; background: rgba(24, 38, 30, 180); }
QPushButton#primaryButton {
    color: #ffffff;
    background: #087b4a;
    border: 2px solid #9ddd71;
    border-radius: 17px;
    padding: 15px 24px;
    font-size: 17px;
    font-weight: 800;
}
QPushButton#primaryButton:hover {
    background: #0e9b5c;
    border-color: #d9f29d;
}
QPushButton#navButton {
    background: transparent;
    border: 1px solid transparent;
    padding: 12px 14px;
}
QPushButton#navButton:hover, QPushButton#navButton[active="true"] {
    background: rgba(15, 92, 56, 215);
    border-color: rgba(114, 203, 110, 0.65);
}
QPushButton#quietButton {
    background: rgba(4, 27, 18, 170);
    border: 1px solid rgba(137, 182, 129, 0.22);
}
QLineEdit, QComboBox, QSpinBox {
    color: #f4f8f3;
    background: rgba(2, 19, 13, 235);
    border: 1px solid rgba(150, 197, 145, 0.45);
    border-radius: 9px;
    padding: 8px 10px;
    min-height: 24px;
}
QComboBox QAbstractItemView {
    color: #f4f8f3;
    background: #092219;
    selection-background-color: #136d43;
}
QSlider::groove:horizontal {
    height: 7px;
    border-radius: 3px;
    background: #20382c;
}
QSlider::sub-page:horizontal {
    border-radius: 3px;
    background: #1dbb70;
}
QSlider::handle:horizontal {
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
    background: #ddf29a;
}
QCheckBox { spacing: 10px; }
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1px solid #72917a;
    background: #10261b;
}
QCheckBox::indicator:checked { background: #13a864; border-color: #9ddd71; }
QTableWidget {
    color: #eff7ed;
    background: rgba(4, 23, 16, 220);
    alternate-background-color: rgba(17, 53, 36, 185);
    gridline-color: rgba(158, 202, 149, 0.22);
    border: 1px solid rgba(153, 204, 150, 0.32);
    border-radius: 12px;
}
QHeaderView::section {
    color: #d9eacb;
    background: rgba(11, 53, 35, 240);
    border: none;
    padding: 10px;
    font-weight: 700;
}
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: rgba(135, 184, 128, 0.45);
    min-height: 30px;
    border-radius: 4px;
}
"""


def fa_icon(resources: ResourceManager, name: str, color: str = TEXT, size: int = 20) -> QIcon:
    icon_path = resources.icon_path(name)
    svg = icon_path.read_text(encoding="utf-8")
    svg = svg.replace(
        "<svg ",
        f'<svg fill="{color}" width="{size}" height="{size}" ',
        1,
    )
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    canvas = QImage(size * 2, size * 2, QImage.Format.Format_ARGB32_Premultiplied)
    canvas.fill(Qt.GlobalColor.transparent)
    painter = QPainter(canvas)
    renderer.render(painter)
    painter.end()
    return QIcon(QPixmap.fromImage(canvas))


def make_button(
    resources: ResourceManager,
    label: str,
    icon_name: str | None = None,
    *,
    primary: bool = False,
    quiet: bool = False,
) -> QPushButton:
    button = QPushButton(label)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setMinimumHeight(46)
    if primary:
        button.setObjectName("primaryButton")
    elif quiet:
        button.setObjectName("quietButton")
    if icon_name:
        button.setIcon(fa_icon(resources, icon_name, LEAF if not primary else TEXT))
        button.setIconSize(QSize(20, 20))
    return button


def make_icon_button(
    resources: ResourceManager,
    icon_name: str,
    label: str,
    *,
    color: str = TEXT,
) -> QPushButton:
    button = QPushButton()
    button.setToolTip(label)
    button.setAccessibleName(label)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setObjectName("quietButton")
    button.setIcon(fa_icon(resources, icon_name, color))
    button.setIconSize(QSize(22, 22))
    button.setFixedSize(46, 44)
    return button


def bind_button_sounds(widget: QWidget, audio) -> None:
    for button in widget.findChildren(QPushButton):
        button.clicked.connect(lambda _checked=False, manager=audio: manager.play("ui-click"))


class ForestBackdrop(QFrame):
    def __init__(self, resources: ResourceManager, overlay_alpha: int = 155) -> None:
        super().__init__()
        self.resources = resources
        self.overlay_alpha = overlay_alpha
        self.setObjectName("forestBackdrop")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        image = self.resources.image("forest-background.jpg")
        source = image.size()
        scale = max(self.width() / source.width(), self.height() / source.height())
        scaled = image.scaled(
            round(source.width() * scale),
            round(source.height() * scale),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2
        painter.drawImage(x, y, scaled)
        painter.fillRect(self.rect(), QColor(1, 12, 9, self.overlay_alpha))
        painter.end()
        super().paintEvent(event)


class Panel(QFrame):
    def __init__(self, *, glass: bool = False) -> None:
        super().__init__()
        self.setObjectName("glassPanel" if glass else "forestPanel")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)


class Heading(QWidget):
    def __init__(self, eyebrow: str, title: str, subtitle: str = "") -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(7)
        small = QLabel(eyebrow.upper())
        small.setObjectName("eyebrow")
        heading = QLabel(title)
        heading.setObjectName("title")
        layout.addWidget(small)
        layout.addWidget(heading)
        if subtitle:
            detail = QLabel(subtitle)
            detail.setObjectName("subtitle")
            detail.setWordWrap(True)
            layout.addWidget(detail)


def picture_label(
    image: QImage,
    *,
    width: int | None = None,
    height: int | None = None,
    alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter,
) -> QLabel:
    label = QLabel()
    label.setAlignment(alignment)
    label.setMinimumSize(1, 1)
    label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    label.setPixmap(QPixmap.fromImage(image))
    if width:
        label.setMaximumWidth(width)
    if height:
        label.setMaximumHeight(height)
    label.setScaledContents(False)
    return label


class ImageView(QLabel):
    def __init__(
        self,
        image: QImage,
        *,
        maximum_width: int | None = None,
        maximum_height: int | None = None,
    ) -> None:
        super().__init__()
        self.source_image = image
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(1, 1)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        if maximum_width:
            self.setMaximumWidth(maximum_width)
        if maximum_height:
            self.setMaximumHeight(maximum_height)
        self._update_pixmap()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._update_pixmap()

    def _update_pixmap(self) -> None:
        if self.width() < 2 or self.height() < 2:
            return
        scaled = self.source_image.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(QPixmap.fromImage(scaled))


def format_duration(seconds: float) -> str:
    total = max(0, int(seconds))
    minutes, remain = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02}:{minutes:02}:{remain:02}"
    return f"{minutes:02}:{remain:02}"
