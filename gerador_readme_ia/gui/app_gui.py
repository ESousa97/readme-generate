# gerador_readme_ia/gui/app_gui.py
"""Janela principal da aplicação.
Corrigido: fluxo completo de geração de README + integração com logic.py
"""
from __future__ import annotations

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Optional

import darkdetect
import google.generativeai as genai

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QFileDialog,
    QMessageBox,
    QInputDialog,
)
from PyQt5.QtCore import QTimer, Qt, QUrl
from PyQt5.QtGui import QDesktopServices

from ..constants import APP_NAME, APP_VERSION, DEFAULT_GEMINI_MODEL
from ..config_manager import ConfigManager
from ..ia_client.gemini_client import GeminiClient
from ..logger_setup import setup_logging

from .theme import THEMES
from .ui_header import create_header
from .ui_left_panel import create_left_panel
from .ui_right_panel import create_right_panel
from .ui_controls import create_controls
from .menus import create_menus
from .theme_manager import apply_theme
from .worker_manager import run_in_thread
from .widgets import ConsoleWidget, StepIndicator

from ..gui.logic import (
    build_prompt,
    extract_project_data_from_zip,
    clean_readme_content,
)

logger = setup_logging(f"{APP_NAME}.gui", debug=False)
APP_DISPLAY_NAME = APP_NAME


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------
class ReadmeGeneratorGUI(QMainWindow):
    """GUI principal."""

    def __init__(self) -> None:
        super().__init__()

        # --------------------------------------------------------------
        #               Estado / configurações persistentes
        # --------------------------------------------------------------
        self.config_mgr = ConfigManager()
        self.api_key: Optional[str] = self.config_mgr.get_api_key()
        self.model_name: str = self.config_mgr.get_gemini_model() or DEFAULT_GEMINI_MODEL
        self.available_models: list[str] = []
        self.gemini_client: Optional[GeminiClient] = None
        self.zip_file_path: Optional[str] = None
        self.generated_readme: str = ""

        # --------------------------------------------------------------
        #               Qt Window basics
        # --------------------------------------------------------------
        self.setWindowTitle(f"{APP_DISPLAY_NAME} v{APP_VERSION}")
        self.resize(1400, 900)

        # Tema
        self.theme_name = self._detect_system_mode()
        self.theme = THEMES[self.theme_name]

        # Referências de thread
        self._threads: list = []

        # --------------------------------------------------------------
        #               Construção da UI (modular)
        # --------------------------------------------------------------
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        create_header(self.main_layout)
        self.left_panel = create_left_panel(self.main_layout)
        self.right_panel = create_right_panel(self.main_layout, self.theme)
        self.controls = create_controls(self.main_layout)
        create_menus(self)

        apply_theme(self, self.theme_name)

        # --------------------------------------------------------------
        #               Referências úteis de widgets
        # --------------------------------------------------------------
        self._map_widgets()
        self._connect_signals()
        self._update_generate_button_state()

        # Se já havia API Key salva, inicializa cliente
        if self.api_key:
            self._initialize_gemini_client()

        # Verifica configs no background
        QTimer.singleShot(150, self._start_initial_config_check)

    # ------------------------------------------------------------------
    # Widget mapping / signals
    # ------------------------------------------------------------------
    def _map_widgets(self):
        lp = self.left_panel
        self.file_path_label = lp["file_path_label"]
        self.select_file_btn = lp["select_file_btn"]
        self.api_status_label = lp["api_status_label"]
        self.model_label = lp["model_label"]
        self.config_api_btn = lp["config_api_btn"]
        self.config_model_btn = lp["config_model_btn"]
        self.console: ConsoleWidget = lp["console"]

        rp = self.right_panel
        self.preview_tabs = rp["preview_tabs"]
        self.readme_preview = rp["readme_preview"]
        self.settings_controls = rp["settings_controls"]

        cw = self.controls
        self.progress_frame = cw["progress_frame"]
        self.progress_bar = cw["progress_bar"]
        self.progress_label = cw["progress_label"]
        self.save_readme_btn = cw["save_readme_btn"]
        self.generate_btn = cw["generate_btn"]

    def _connect_signals(self):
        self.select_file_btn.clicked.connect(self._select_zip_file)
        self.config_api_btn.clicked.connect(self._prompt_api_key)
        self.config_model_btn.clicked.connect(self._prompt_model_name)
        self.generate_btn.clicked.connect(self._trigger_readme_generation)
        # Enable custom prompt box toggle
        self.settings_controls["custom_prompt_enabled"].toggled.connect(
            self.settings_controls["custom_prompt_text"].setEnabled
        )

    # ------------------------------------------------------------------
    # Util
    # ------------------------------------------------------------------
    @staticmethod
    def _detect_system_mode() -> str:
        try:
            return "dark" if (darkdetect.theme() or "").lower() == "dark" else "light"
        except Exception:
            return "light"

    # ------------------------------------------------------------------
    # Menu actions / simple slots
    # ------------------------------------------------------------------
    def _select_zip_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar arquivo ZIP do projeto",
            str(Path.home()),
            "Arquivos ZIP (*.zip)",
        )
        if path:
            self.zip_file_path = path
            self.file_path_label.setText(os.path.basename(path))
            self.console.append_step("Arquivo ZIP", "success", os.path.basename(path))
            self._update_generate_button_state()

    def _prompt_api_key(self):
        key, ok = QInputDialog.getText(self, "API Key", "Digite sua API Key:")
        if ok and key.strip():
            self.api_key = key.strip()
            self.config_mgr.set_api_key(self.api_key)
            self.console.append_step("API Key", "success", "Configurada")
            self._initialize_gemini_client()

    def _prompt_model_name(self):
        if self.available_models:
            cur = 0
            try:
                cur = self.available_models.index(self.model_name)
            except ValueError:
                pass
            model, ok = QInputDialog.getItem(
                self,
                "Selecionar Modelo Gemini",
                "Modelo:",
                self.available_models,
                current=cur,
                editable=False,
            )
        else:
            model, ok = QInputDialog.getText(
                self, "Modelo Gemini", "Nome do modelo:", text=self.model_name
            )
        if ok and model:
            self.model_name = model
            self.model_label.setText(model)
            self.config_mgr.set_gemini_model(model)
            if self.api_key:
                self._initialize_gemini_client()

    # ------------------------------------------------------------------
    # Theme helpers (called by menus)
    # ------------------------------------------------------------------
    def _switch_theme(self, theme_name: str):
        if theme_name in THEMES:
            self.theme_name = theme_name
            self.theme = THEMES[theme_name]
            apply_theme(self, theme_name)

    def _switch_theme_auto(self):
        self._switch_theme(self._detect_system_mode())

    # ------------------------------------------------------------------
    # Gemini
    # ------------------------------------------------------------------
    def _initialize_gemini_client(self):
        """Cria GeminiClient e carrega modelos disponíveis."""
        try:
            self.gemini_client = GeminiClient(self.api_key, self.model_name)
            self.api_status_label.setText(f"IA Pronta – {self.model_name}")
            self.api_status_label.setStyleSheet(f"color: {self.theme.success};")
            self.generate_btn.setEnabled(bool(self.zip_file_path))
            self._load_available_models()
        except Exception as e:
            logger.error("Erro ao inicializar GeminiClient", exc_info=True)
            self.gemini_client = None
            self.api_status_label.setText("Erro na IA")
            self.api_status_label.setStyleSheet(f"color: {self.theme.error};")
            QMessageBox.critical(self, "Erro na IA", str(e))
            self._update_generate_button_state()

    def _load_available_models(self):
        try:
            data = genai.list_models()  # pode variar conforme lib
            self.available_models = [getattr(m, "name", str(m)) for m in data]
            if DEFAULT_GEMINI_MODEL not in self.available_models:
                self.available_models.insert(0, DEFAULT_GEMINI_MODEL)
        except Exception:
            self.available_models = [DEFAULT_GEMINI_MODEL]

    # ------------------------------------------------------------------
    # Generate README flow
    # ------------------------------------------------------------------
    def _update_generate_button_state(self):
        can = bool(self.gemini_client and self.zip_file_path)
        self.generate_btn.setEnabled(can)

    def _get_advanced_config(self) -> Dict[str, object]:
        sc = self.settings_controls
        return {
            "custom_prompt_enabled": sc["custom_prompt_enabled"].isChecked(),
            "custom_prompt": sc["custom_prompt_text"].toPlainText(),
            "include_tests": sc["include_tests"].isChecked(),
            "include_docs": sc["include_docs"].isChecked(),
            "include_config": sc["include_config"].isChecked(),
            "max_file_size_kb": sc["max_file_size_spin"].value(),
            "max_files": sc["max_files_spin"].value(),
            "readme_style": sc["readme_style_combo"].currentText().lower(),
            "include_badges": sc["include_badges"].isChecked(),
            "include_toc": sc["include_toc"].isChecked(),
            "include_examples": sc["include_examples"].isChecked(),
        }

    # ---------- thread entry ----------
    def _trigger_readme_generation(self):
        if not self.gemini_client or not self.zip_file_path:
            return
        cfg = self._get_advanced_config()
        self.console.append_step("Geração", "progress", "Iniciando…")
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_bar.setValue(0)
        self.generate_btn.setEnabled(False)

        th = run_in_thread(
            self._generate_readme_worker,
            self.zip_file_path,
            cfg,
            callback_slot=self._readme_generation_callback,
            error_slot=self._readme_generation_error,
        )
        self._threads.append(th)

    def _generate_readme_worker(self, progress_cb, step_cb, worker, zip_path, cfg):
        # 1) extrai dados
        project_data = extract_project_data_from_zip(
            zip_path, cfg, progress_cb=progress_cb, step_cb=step_cb
        )
        if worker.is_interruption_requested():
            return None

        # 2) monta prompt
        prompt = build_prompt(project_data, cfg)

        # 3) IA
        step_cb("IA", "progress", "Consultando Gemini…")
        progress_cb("Gerando README…", 85)
        response = self.gemini_client.send_conversational_prompt(prompt)
        readme = clean_readme_content(response or "")
        return readme

    # ---------- callbacks ----------
    def _readme_generation_callback(self, readme_text: str):
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.generate_btn.setEnabled(True)
        if not readme_text:
            self.console.append_step("README", "error", "IA retornou vazio")
            QMessageBox.warning(self, "Falha", "A IA não retornou conteúdo.")
            return
        self.generated_readme = readme_text
        self.readme_preview.set_markdown_content(readme_text)
        self.save_readme_btn.setEnabled(True)
        self.preview_tabs.setCurrentIndex(0)
        self.console.append_step("README", "success", "Gerado com sucesso")

    def _readme_generation_error(self, title, msg):
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.generate_btn.setEnabled(True)
        self.console.append_step("Erro", "error", title)
        QMessageBox.critical(self, title, msg)

    # ------------------------------------------------------------------
    # Initial config loader in background
    # ------------------------------------------------------------------
    def _start_initial_config_check(self):
        th = run_in_thread(
            self._check_initial_config_worker,
            callback_slot=self._check_initial_config_callback,
        )
        self._threads.append(th)

    def _check_initial_config_worker(self, progress_cb, step_cb, worker):
        return {
            "api_key": self.config_mgr.get_api_key(),
            "model_name": self.config_mgr.get_gemini_model(),
        }

    def _check_initial_config_callback(self, res: Dict[str, str]):
        if res.get("api_key"):
            self.api_key = res["api_key"]
            self.api_status_label.setText("API Key configurada ✔︎")
        if res.get("model_name"):
            self.model_name = res["model_name"]
            self.model_label.setText(self.model_name)
        if self.api_key:
            self._initialize_gemini_client()

    # ------------------------------------------------------------------
    # Close event
    # ------------------------------------------------------------------
    def closeEvent(self, evt):
        for th in self._threads:
            if th.isRunning():
                th.quit()
                th.wait(1000)
        if self.gemini_client:
            try:
                self.gemini_client.close()
            except Exception:
                pass
        super().closeEvent(evt)


# ---------------------------------------------------------------------------
# Stand-alone run
# ---------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    win = ReadmeGeneratorGUI()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
