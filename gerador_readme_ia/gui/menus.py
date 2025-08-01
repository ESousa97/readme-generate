# gerador_readme_ia/gui/menus.py

from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices

def create_menus(window):
    menubar = window.menuBar()

    file_menu = menubar.addMenu("&Arquivo")

    open_action = QAction("Abrir ZIP...", window)
    open_action.setShortcut(QKeySequence.Open)
    open_action.triggered.connect(window._select_zip_file)

    save_action = QAction("Salvar README...", window)
    save_action.setShortcut(QKeySequence.Save)
    save_action.triggered.connect(window._save_readme)

    export_menu = file_menu.addMenu("Exportar")

    export_md_action = QAction("Markdown (.md)", window)
    export_md_action.triggered.connect(window._export_markdown)

    export_html_action = QAction("HTML (.html)", window)
    export_html_action.triggered.connect(window._export_html)

    export_pdf_action = QAction("PDF (.pdf)", window)
    export_pdf_action.triggered.connect(window._export_pdf)

    export_menu.addAction(export_md_action)
    export_menu.addAction(export_html_action)
    export_menu.addAction(export_pdf_action)

    file_menu.addAction(open_action)
    file_menu.addSeparator()
    file_menu.addAction(save_action)
    file_menu.addMenu(export_menu)
    file_menu.addSeparator()

    exit_action = QAction("Sair", window)
    exit_action.setShortcut(QKeySequence.Quit)
    exit_action.triggered.connect(window.close)
    file_menu.addAction(exit_action)

    edit_menu = menubar.addMenu("&Editar")

    copy_action = QAction("Copiar README", window)
    copy_action.setShortcut(QKeySequence.Copy)
    copy_action.triggered.connect(window._copy_readme)

    edit_menu.addAction(copy_action)

    config_menu = menubar.addMenu("&Configurações")

    api_action = QAction("Configurar API Key", window)
    api_action.triggered.connect(window._prompt_api_key)

    model_action = QAction("Selecionar Modelo", window)
    model_action.triggered.connect(window._prompt_model_name)

    config_menu.addAction(api_action)
    config_menu.addAction(model_action)

    view_menu = menubar.addMenu("&Visual")

    light_action = QAction("Tema Claro", window)
    light_action.triggered.connect(lambda: window._switch_theme("light"))

    dark_action = QAction("Tema Escuro", window)
    dark_action.triggered.connect(lambda: window._switch_theme("dark"))

    auto_action = QAction("Tema Automático", window)
    auto_action.triggered.connect(window._switch_theme_auto)

    view_menu.addAction(light_action)
    view_menu.addAction(dark_action)
    view_menu.addSeparator()
    view_menu.addAction(auto_action)

    help_menu = menubar.addMenu("&Ajuda")

    about_action = QAction("Sobre", window)
    about_action.triggered.connect(window._show_about)

    help_action = QAction("Ajuda", window)
    help_action.triggered.connect(window._show_help)

    help_menu.addAction(about_action)
    help_menu.addAction(help_action)
