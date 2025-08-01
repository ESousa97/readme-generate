# gerador_readme_ia/gui/ui_controls.py

from PyQt5.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QProgressBar, QLabel, QPushButton
from PyQt5.QtGui import QFont
from .widgets import AnimatedButton
from .theme import FONT_FAMILY_DEFAULT, FONT_SIZE_DEFAULT, FONT_SIZE_SMALL

def create_controls(parent_layout):
    controls_frame = QFrame()
    controls_frame.setFixedHeight(80)
    controls_layout = QHBoxLayout(controls_frame)

    progress_frame = QFrame()
    progress_layout = QVBoxLayout(progress_frame)
    progress_layout.setContentsMargins(0, 0, 0, 0)

    progress_bar = QProgressBar()
    progress_bar.setFixedHeight(6)
    progress_bar.setTextVisible(False)
    progress_bar.setVisible(False)

    progress_label = QLabel("")
    progress_label.setFont(QFont(FONT_FAMILY_DEFAULT, FONT_SIZE_SMALL))
    progress_label.setVisible(False)

    progress_layout.addWidget(progress_label)
    progress_layout.addWidget(progress_bar)

    buttons_layout = QHBoxLayout()
    save_readme_btn = AnimatedButton("Salvar README")
    save_readme_btn.setEnabled(False)
    generate_btn = AnimatedButton("Gerar README")
    generate_btn.setMinimumWidth(200)
    generate_btn.setFont(QFont(FONT_FAMILY_DEFAULT, FONT_SIZE_DEFAULT, QFont.Bold))
    generate_btn.setEnabled(False)

    buttons_layout.addWidget(save_readme_btn)
    buttons_layout.addWidget(generate_btn)

    controls_layout.addWidget(progress_frame, 1)
    controls_layout.addStretch()
    controls_layout.addLayout(buttons_layout)

    parent_layout.addWidget(controls_frame)

    return {
        "progress_frame": progress_frame,
        "progress_bar": progress_bar,
        "progress_label": progress_label,
        "save_readme_btn": save_readme_btn,
        "generate_btn": generate_btn
    }
