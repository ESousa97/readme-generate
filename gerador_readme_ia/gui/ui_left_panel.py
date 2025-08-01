# gerador_readme_ia/gui/ui_left_panel.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QLabel, QPushButton, QHBoxLayout, QGridLayout
)
from .widgets import AnimatedButton, ConsoleWidget

def create_left_panel(parent_layout):
    left_widget = QWidget()
    left_layout = QVBoxLayout(left_widget)

    file_group = QGroupBox("Arquivo do Projeto")
    file_layout = QVBoxLayout(file_group)
    file_path_label = QLabel("Nenhum arquivo selecionado")
    file_layout.addWidget(file_path_label)
    select_file_btn = AnimatedButton("Selecionar Arquivo ZIP")
    file_layout.addWidget(select_file_btn)

    config_group = QGroupBox("Configurações")
    config_layout = QGridLayout(config_group)
    api_status_label = QLabel("API Key não configurada")
    config_layout.addWidget(QLabel("Status IA:"), 0, 0)
    config_layout.addWidget(api_status_label, 0, 1)
    model_label = QLabel("gemini-2.0-flash")
    config_layout.addWidget(QLabel("Modelo:"), 1, 0)
    config_layout.addWidget(model_label, 1, 1)

    config_buttons_layout = QHBoxLayout()
    config_api_btn = QPushButton("Configurar API")
    config_model_btn = QPushButton("Modelo")
    config_buttons_layout.addWidget(config_api_btn)
    config_buttons_layout.addWidget(config_model_btn)
    config_layout.addLayout(config_buttons_layout, 2, 0, 1, 2)

    console_group = QGroupBox("Console de Operações")
    console_layout = QVBoxLayout(console_group)
    console = ConsoleWidget()
    console_layout.addWidget(console)

    left_layout.addWidget(file_group)
    left_layout.addWidget(config_group)
    left_layout.addWidget(console_group, 1)
    parent_layout.addWidget(left_widget)

    # Retorna widgets para conectar sinais e atualizar
    return {
        "widget": left_widget,
        "file_path_label": file_path_label,
        "select_file_btn": select_file_btn,
        "api_status_label": api_status_label,
        "model_label": model_label,
        "config_api_btn": config_api_btn,
        "config_model_btn": config_model_btn,
        "console": console
    }
