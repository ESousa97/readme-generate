# gerador_readme_ia/gui/theme_manager.py

from .theme import THEMES, FONT_FAMILY_DEFAULT, FONT_FAMILY_MONO, FONT_SIZE_DEFAULT, FONT_SIZE_SMALL

def apply_theme(window, theme_name):
    theme = THEMES.get(theme_name)
    if not theme:
        theme = THEMES["light"]

    style = f"""
    QMainWindow {{
        background-color: {theme.bg_primary};
        color: {theme.text_primary};
    }}
    QWidget {{
        background-color: {theme.bg_primary};
        color: {theme.text_primary};
    }}
    QGroupBox {{
        font-weight: bold;
        border: 2px solid {theme.border};
        border-radius: 8px;
        margin-top: 8px;
        background-color: {theme.surface};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 8px 0 8px;
        background-color: {theme.surface};
    }}
    QPushButton {{
        background-color: {theme.surface};
        border: 1px solid {theme.border};
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: {theme.surface_variant};
        border-color: {theme.accent};
    }}
    QPushButton:pressed {{
        background-color: {theme.accent};
        color: white;
    }}
    QPushButton:disabled {{
        background-color: {theme.surface_variant};
        color: {theme.text_secondary};
        border-color: {theme.border};
    }}
    QTextEdit, QPlainTextEdit {{
        background-color: {theme.bg_secondary};
        border: 1px solid {theme.border};
        border-radius: 6px;
        padding: 8px;
        selection-background-color: {theme.accent};
    }}
    QTabWidget::pane {{
        border: 1px solid {theme.border};
        border-radius: 6px;
        background-color: {theme.surface};
    }}
    QTabBar::tab {{
        background-color: {theme.surface_variant};
        border: 1px solid {theme.border};
        padding: 8px 16px;
        margin-right: 2px;
    }}
    QTabBar::tab:selected {{
        background-color: {theme.accent};
        color: white;
    }}
    QTabBar::tab:hover:!selected {{
        background-color: {theme.surface};
    }}
    QProgressBar {{
        border: none;
        border-radius: 3px;
        background-color: {theme.surface_variant};
    }}
    QProgressBar::chunk {{
        background-color: {theme.accent};
        border-radius: 3px;
    }}
    QSplitter::handle {{
        background-color: {theme.border};
    }}
    QSplitter::handle:horizontal {{
        width: 2px;
    }}
    QSplitter::handle:vertical {{
        height: 2px;
    }}
    QStatusBar {{
        background-color: {theme.surface};
        border-top: 1px solid {theme.border};
    }}
    QMenuBar {{
        background-color: {theme.surface};
        border-bottom: 1px solid {theme.border};
    }}
    QMenuBar::item {{
        padding: 4px 8px;
    }}
    QMenuBar::item:selected {{
        background-color: {theme.accent};
        color: white;
    }}
    QMenu {{
        background-color: {theme.surface};
        border: 1px solid {theme.border};
        border-radius: 6px;
    }}
    QMenu::item {{
        padding: 6px 20px;
    }}
    QMenu::item:selected {{
        background-color: {theme.accent};
        color: white;
    }}
    QComboBox {{
        background-color: {theme.surface};
        border: 1px solid {theme.border};
        border-radius: 4px;
        padding: 4px 8px;
        min-width: 100px;
    }}
    QComboBox:hover {{
        border-color: {theme.accent};
    }}
    QComboBox::drop-down {{
        border: none;
    }}
    QComboBox::down-arrow {{
        width: 12px;
        height: 12px;
    }}
    QSpinBox {{
        background-color: {theme.surface};
        border: 1px solid {theme.border};
        border-radius: 4px;
        padding: 4px;
    }}
    QCheckBox {{
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border: 2px solid {theme.border};
        border-radius: 3px;
        background-color: {theme.surface};
    }}
    QCheckBox::indicator:checked {{
        background-color: {theme.accent};
        border-color: {theme.accent};
    }}
    QScrollArea {{
        border: none;
        background-color: {theme.bg_primary};
    }}
    QToolBar {{
        background-color: {theme.surface};
        border: 1px solid {theme.border};
        border-radius: 4px;
        spacing: 8px;
        padding: 4px;
    }}
    """
    window.setStyleSheet(style)
