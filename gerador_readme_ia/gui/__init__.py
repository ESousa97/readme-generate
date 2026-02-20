# gerador_readme_ia/gui/__init__.py
"""Módulo GUI modernizado com CustomTkinter para o Gerador de README IA"""

from .app_gui import ReadmeGeneratorApp
from .ctk_theme_manager import Windows11ThemeManager, theme_manager
from .ctk_widgets import (
    APIKeyDialog,
    ConsoleWidget,
    InfoCard,
    ModelSelectionDialog,
    ModernButton,
    ModernFrame,
    ModernSection,
    ModernTextWidget,
    ProgressDialog,
    QuotaExceededDialog,
)

__all__ = [
    'ReadmeGeneratorApp',
    'theme_manager',
    'Windows11ThemeManager',
    'ModernFrame',
    'ModernButton', 
    'ModernSection',
    'ModernTextWidget',
    'ConsoleWidget',
    'APIKeyDialog',
    'ModelSelectionDialog',
    'QuotaExceededDialog',
    'ProgressDialog',
    'InfoCard'
]