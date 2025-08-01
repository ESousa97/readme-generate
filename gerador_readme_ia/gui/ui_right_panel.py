# gerador_readme_ia/gui/ui_right_panel.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from .preview_widget import ReadmePreviewWidget
from .ui_settings_tab import create_settings_tab

def create_right_panel(parent_layout, theme):
    right_widget = QWidget()
    right_layout = QVBoxLayout(right_widget)

    tabs = QTabWidget()

    # Aba de preview
    preview_tab = QWidget()
    preview_layout = QVBoxLayout(preview_tab)
    readme_preview = ReadmePreviewWidget(theme)
    preview_layout.addWidget(readme_preview, 1)

    # Aba de configurações avançadas
    settings_scroll, settings_controls = create_settings_tab()

    # Monta as abas
    tabs.addTab(preview_tab, "README Gerado")
    tabs.addTab(settings_scroll, "Configurações Avançadas")

    right_layout.addWidget(tabs)
    parent_layout.addWidget(right_widget)

    return {
        "widget": right_widget,
        "preview_tabs": tabs,
        "readme_preview": readme_preview,
        # Agora armazenamos o dict de controles sob a chave settings_controls
        "settings_controls": settings_controls
    }
