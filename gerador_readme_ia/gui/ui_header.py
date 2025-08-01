# gerador_readme_ia/gui/ui_header.py

from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout
from PyQt5.QtGui import QFont
import qtawesome

from ..constants import APP_DISPLAY_NAME
from .theme import THEMES, FONT_FAMILY_DEFAULT, FONT_SIZE_LARGE, FONT_SIZE_DEFAULT

def create_header(parent_layout):
    theme = THEMES.get("light")  # ideal passar tema como parâmetro

    header_frame = QFrame()
    header_frame.setFixedHeight(80)
    header_layout = QHBoxLayout(header_frame)

    icon_label = QLabel()
    icon_pixmap = qtawesome.icon("fa5s.robot", color=theme.accent).pixmap(48, 48)
    icon_label.setPixmap(icon_pixmap)

    title_layout = QVBoxLayout()
    title_label = QLabel(APP_DISPLAY_NAME)
    title_label.setFont(QFont(FONT_FAMILY_DEFAULT, FONT_SIZE_LARGE + 4, QFont.Bold))
    subtitle_label = QLabel("Gere documentações profissionais automaticamente com IA")
    subtitle_label.setFont(QFont(FONT_FAMILY_DEFAULT, FONT_SIZE_DEFAULT))
    subtitle_label.setStyleSheet(f"color: {theme.text_secondary};")

    title_layout.addWidget(title_label)
    title_layout.addWidget(subtitle_label)

    header_layout.addWidget(icon_label)
    header_layout.addLayout(title_layout)
    header_layout.addStretch()

    parent_layout.addWidget(header_frame)
