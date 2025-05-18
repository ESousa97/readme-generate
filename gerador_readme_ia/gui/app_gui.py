# gerador_readme_ia/gui/app_gui.py
import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
import traceback
import zipfile
# from io import BytesIO # Não usado diretamente

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QStatusBar, QMenuBar, QMenu, QAction,
    QFileDialog, QMessageBox, QInputDialog, QFrame,
    QProgressBar
)
from PyQt5.QtGui import (
    QFont, QPalette, QColor, QIcon, QKeySequence, QDesktopServices,
    QCloseEvent
)
from PyQt5.QtCore import (
    Qt, pyqtSignal, QObject, QThread, QTimer,
    pyqtSlot, QUrl, QLocale, QTranslator, QLibraryInfo
)

import qtawesome
import darkdetect

from ..config_manager import ConfigManager
from ..ia_client.gemini_client import GeminiClient
from ..logger_setup import setup_logging
from ..constants import (
    DEFAULT_GEMINI_MODEL, PROMPT_README_GENERATION,
    APP_NAME, APP_AUTHOR, APP_VERSION
)

logger = setup_logging(f"{APP_NAME}.gui", app_author=APP_AUTHOR, debug=True)

APP_DISPLAY_NAME = "Gerador de README.md Inteligente"

FONT_FAMILY_DEFAULT = "Segoe UI" if os.name == 'nt' else "Helvetica"
FONT_SIZE_DEFAULT = 10 if os.name == 'nt' else 12
FONT_SIZE_SMALL = FONT_SIZE_DEFAULT - 1

class Theme:
    def __init__(self, bg, text_area_bg, text_area_fg, text_area_insert_bg,
                 user_msg, gemini_msg, system_msg, error_msg, link_preview,
                 status_bar_fg, status_bar_bg, qss_name,
                 selection_bg, selection_fg, icon_color, icon_disabled_color):
        self.bg = bg
        self.text_area_bg = text_area_bg
        self.text_area_fg = text_area_fg
        self.text_area_insert_bg = text_area_insert_bg
        self.user_msg = user_msg
        self.gemini_msg = gemini_msg
        self.system_msg = system_msg
        self.error_msg = error_msg
        self.link_preview = link_preview
        self.status_bar_fg = status_bar_fg
        self.status_bar_bg = status_bar_bg
        self.qss_name = qss_name
        self.selection_bg = selection_bg
        self.selection_fg = selection_fg
        self.icon_color = icon_color
        self.icon_disabled_color = icon_disabled_color

THEME_COLORS = {
    "light": Theme(
        bg="#F0F0F0", text_area_bg="#FFFFFF", text_area_fg="#212121", text_area_insert_bg="#212121",
        user_msg="#0D47A1", gemini_msg="#1B5E20", system_msg="#424242", error_msg="#C62828",
        link_preview="#1565C0", status_bar_fg="#212121", status_bar_bg="#E0E0E0",
        qss_name="light",
        selection_bg="#ADD8E6", selection_fg="#000000", icon_color="#212121", icon_disabled_color="#A0A0A0"
    ),
    "dark": Theme(
        bg="#2B2B2B", text_area_bg="#313335", text_area_fg="#E0E0E0", text_area_insert_bg="#E0E0E0",
        user_msg="#90CAF9", gemini_msg="#A5D6A7", system_msg="#B0BEC5", error_msg="#EF9A9A",
        link_preview="#81D4FA", status_bar_fg="#E0E0E0", status_bar_bg="#3C3F41",
        qss_name="dark",
        selection_bg="#4A6B80", selection_fg="#E0E0E0", icon_color="#E0E0E0", icon_disabled_color="#808080"
    )
}

class IconName:
    GEAR = "fa5s.cog"; KEY = "fa5s.key"; ROBOT = "fa5s.robot"
    UPLOAD = "fa5s.upload"; GENERATE_README = "fa5s.file-alt"
    EXIT = "fa5s.sign-out-alt"
    THEME_LIGHT = "fa5s.sun"; THEME_DARK = "fa5s.moon"; THEME_SYSTEM = "fa5s.desktop"
    INFO_SYMBOL = "ℹ️"; WARNING_SYMBOL = "⚠️"

class Worker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str, str)
    result = pyqtSignal(object)
    progress = pyqtSignal(str, int)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._is_interruption_requested = False

    def request_interruption(self):
        self._is_interruption_requested = True

    def is_interruption_requested(self):
        return self._is_interruption_requested

    @pyqtSlot()
    def run(self):
        logger.debug(f"Worker ({self.func.__name__}): Iniciando execução na thread {QThread.currentThreadId()}.")
        try:
            # self.progress.emit é passado como o primeiro argumento para self.func
            # e as funções worker (como _check_initial_config_worker) recebem isso como 'progress_callback_emitter'
            res = self.func(self.progress.emit, self, *self.args, **self.kwargs)
            logger.debug(f"Worker ({self.func.__name__}): Execução concluída. Resultado: {type(res)}")
            if res is not None and not self.is_interruption_requested():
                self.result.emit(res)
        except Exception as e:
            if not self.is_interruption_requested():
                logger.error(f"Erro na thread worker ({self.func.__name__}): {e}", exc_info=True)
                self.error.emit(f"Erro na Tarefa ({self.func.__name__})", f"Ocorreu um erro: {e}\n\nDetalhes:\n{traceback.format_exc()}")
        finally:
            logger.debug(f"Worker ({self.func.__name__}): Finalizando.")
            self.finished.emit()

class ReadmeGeneratorGUI(QMainWindow):
    log_message_signal = pyqtSignal(str, str, str, bool)
    update_status_signal = pyqtSignal(str)
    enable_buttons_signal = pyqtSignal(bool)
    progress_bar_update_signal = pyqtSignal(str, int)

    def __init__(self):
        super().__init__()
        logger.info(f"Inicializando {APP_DISPLAY_NAME} GUI...")
        self.current_mode = self._detect_system_mode()
        self.theme = THEME_COLORS[self.current_mode]
        self.worker_threads_map: Dict[QThread, Worker] = {}
        self.gemini_client: Optional[GeminiClient] = None
        self.api_key: Optional[str] = None
        self.model_name: str = DEFAULT_GEMINI_MODEL
        self.zip_file_path: Optional[str] = None
        self.output_directory: str = os.path.expanduser("~")

        self._apply_stylesheet()
        self.setWindowTitle(f"{APP_DISPLAY_NAME} v{APP_VERSION}")

        desired_width, desired_height = 1000, 700
        screen = QApplication.primaryScreen()
        if screen:
            screen_rect = screen.availableGeometry()
            self.setGeometry(
                max(screen_rect.left(), screen_rect.center().x() - desired_width // 2),
                max(screen_rect.top(), screen_rect.center().y() - desired_height // 2),
                desired_width, desired_height
            )
        else:
            self.setGeometry(100, 100, desired_width, desired_height)
        
        self.setMinimumSize(700, 500)
        self.setWindowIcon(qtawesome.icon(IconName.ROBOT, color=self.theme.icon_color))

        self.config_mgr = ConfigManager()
        self.api_key = self.config_mgr.get_api_key()
        self.model_name = self.config_mgr.get_gemini_model() or DEFAULT_GEMINI_MODEL

        self._init_ui()
        self._connect_signals()
        self._update_ui_for_theme()

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximumHeight(18)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        self.statusBar.addPermanentWidget(self.progress_bar, 1)

        QTimer.singleShot(150, self._check_initial_config_threaded)
        self.log_message_signal.emit("Sistema", f"Bem-vindo ao {APP_DISPLAY_NAME}!", "system", False)

    def _connect_signals(self):
        self.log_message_signal.connect(self._log_message_slot)
        self.update_status_signal.connect(self._update_status_bar_slot)
        self.enable_buttons_signal.connect(self._enable_buttons_slot)
        self.progress_bar_update_signal.connect(self._update_progress_bar)

    def _get_current_theme_palette(self) -> Theme:
        return THEME_COLORS[self.current_mode]

    def _detect_system_mode(self) -> str:
        try:
            mode = darkdetect.theme()
            return "dark" if mode and mode.lower() == "dark" else "light"
        except Exception as e:
            logger.warning(f"Não foi possível detectar o tema do sistema: {e}. Usando modo claro.")
            return "light"

    def _init_ui(self):
        self.main_widget = QWidget()
        self.main_widget.setObjectName("main_widget")
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        self._create_menus()
        self._create_control_section()
        self._create_log_section()
        self._create_status_bar()

    def _create_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&Arquivo")
        self._populate_menu(file_menu, [
            (IconName.UPLOAD, "Selecionar Diretório de Saída...", self._select_output_directory, QKeySequence("Ctrl+Shift+O")),
            (None, None, None, None),
            (IconName.KEY, "Configurar API Key...", self._prompt_api_key, QKeySequence("Ctrl+K")),
            (IconName.ROBOT, "Selecionar Modelo Gemini...", self._prompt_model_name, QKeySequence("Ctrl+M")),
            (None, None, None, None),
            (IconName.EXIT, "Sair", self.close, QKeySequence.Quit)
        ])
        visual_menu = menubar.addMenu("&Visual")
        self._populate_menu(visual_menu, [
            (IconName.THEME_LIGHT, "Tema Claro", lambda: self._switch_theme("light"), None),
            (IconName.THEME_DARK, "Tema Escuro", lambda: self._switch_theme("dark"), None),
            (IconName.THEME_SYSTEM, "Padrão do Sistema", lambda: self._switch_theme(self._detect_system_mode()), None)
        ])

    def _populate_menu(self, menu: QMenu, actions_data: list):
        icon_color = self.theme.icon_color
        for icon_name, text, slot, shortcut_str in actions_data:
            if icon_name is None: menu.addSeparator(); continue
            action_icon = qtawesome.icon(icon_name, color=icon_color) if icon_name else QIcon()
            action = QAction(action_icon, text, self)
            if slot: action.triggered.connect(slot)
            if shortcut_str: action.setShortcut(QKeySequence(shortcut_str))
            action.setData(icon_name)
            menu.addAction(action)

    def _update_menu_icons(self):
        self.menuBar().clear()
        self._create_menus()
        if hasattr(self, 'status_bar_label') and self.status_bar_label:
             self.statusBar.showMessage(self.status_bar_label.text() or "Pronto.", 0)

    def _create_control_section(self):
        control_frame = QFrame(); control_frame.setObjectName("ControlFrame")
        control_layout = QVBoxLayout(control_frame); control_layout.setContentsMargins(0,0,0,0); control_layout.setSpacing(8)
        self.upload_button = QPushButton(qtawesome.icon(IconName.UPLOAD, color=self.theme.icon_color), " Selecionar Arquivo .zip do Projeto")
        self.upload_button.setObjectName("upload_button"); self.upload_button.clicked.connect(self._select_zip_file); self.upload_button.setFixedHeight(35)
        control_layout.addWidget(self.upload_button)
        self.generate_readme_button = QPushButton(qtawesome.icon(IconName.GENERATE_README, color=self.theme.icon_color), " Gerar README.md")
        self.generate_readme_button.setObjectName("generate_readme_button"); self.generate_readme_button.setProperty("class", "accent")
        self.generate_readme_button.clicked.connect(self._trigger_readme_generation); self.generate_readme_button.setEnabled(False); self.generate_readme_button.setFixedHeight(35)
        control_layout.addWidget(self.generate_readme_button)
        self.main_layout.addWidget(control_frame)

    def _create_log_section(self):
        log_label = QLabel("Log de Operações:"); log_label.setFont(QFont(FONT_FAMILY_DEFAULT, FONT_SIZE_DEFAULT, QFont.Bold))
        self.conversation_log = QTextEdit(); self.conversation_log.setReadOnly(True); self.conversation_log.setFont(QFont(FONT_FAMILY_DEFAULT, FONT_SIZE_DEFAULT))
        self.conversation_log.setObjectName("ConversationLog"); self.conversation_log.setLineWrapMode(QTextEdit.WidgetWidth)
        self.main_layout.addWidget(log_label); self.main_layout.addWidget(self.conversation_log, 1)

    def _create_status_bar(self):
        self.statusBar = QStatusBar(); self.setStatusBar(self.statusBar)
        self.status_bar_label = QLabel("Pronto."); self.status_bar_label.setFont(QFont(FONT_FAMILY_DEFAULT, FONT_SIZE_SMALL)); self.status_bar_label.setObjectName("StatusBarLabel")
        self.statusBar.addWidget(self.status_bar_label, 1)

    def _switch_theme(self, mode: str):
        if mode not in THEME_COLORS or self.current_mode == mode: return
        self.current_mode = mode; self.theme = THEME_COLORS[self.current_mode]
        self._apply_stylesheet(); self._update_ui_for_theme()
        self.log_message_signal.emit("Sistema", f"Visual alterado para: Modo {mode.capitalize()}", "system", False)

    def _apply_stylesheet(self):
        palette = self.theme
        qss = f""" O SEU QSS COMPLETO AQUI ... """ # O QSS é longo, então o omiti para brevidade, mas use o que você tinha
        self.setStyleSheet(qss)
        qtawesome.set_defaults(color=palette.icon_color, color_disabled=palette.icon_disabled_color)
        logger.info(f"Stylesheet para modo '{self.current_mode}' aplicada.")

    def _update_ui_for_theme(self):
        palette = self.theme; icon_color = palette.icon_color
        for widget in [self.conversation_log]:
            if widget: p = widget.palette(); p.setColor(QPalette.Text, QColor(palette.text_area_fg)); p.setColor(QPalette.Base, QColor(palette.text_area_bg)); widget.setPalette(p)
        for btn_widget, icon_name in [(self.upload_button, IconName.UPLOAD), (self.generate_readme_button, IconName.GENERATE_README)]:
            if hasattr(self, btn_widget.objectName()):
                try: btn_widget.setIcon(qtawesome.icon(icon_name, color=icon_color))
                except Exception as e: logger.warning(f"Erro ao atualizar ícone {btn_widget.objectName()}: {e}")
        self._update_menu_icons()

    def _reset_document_state_internal(self):
        self.zip_file_path = None; self.generate_readme_button.setEnabled(False)
        self.log_message_signal.emit("Sistema", "Estado resetado.", "system", False)

    def _select_zip_file(self):
        fpath, _ = QFileDialog.getOpenFileName(self, "Selecionar .zip", self.output_directory, "*.zip;;*.*")
        if fpath: self.zip_file_path = fpath; self.log_message_signal.emit("Sistema", f"Arquivo: {fpath}", "system", False); self.generate_readme_button.setEnabled(self.gemini_client is not None)
        else: self.log_message_signal.emit("Sistema", "Seleção de .zip cancelada.", "system", False)

    def _select_output_directory(self):
        dpath = QFileDialog.getExistingDirectory(self, "Diretório de Saída", self.output_directory)
        if dpath: self.output_directory = dpath; self.log_message_signal.emit("Sistema", f"Saída em: {dpath}", "system", False)
        else: self.log_message_signal.emit("Sistema", "Seleção de diretório cancelada.", "system", False)

    def _extract_project_data_from_zip(self, progress_cb_emitter, worker: Worker, zip_path: str) -> Optional[str]:
        logger.debug(f"Extraindo de: {zip_path}")
        progress_cb_emitter("Analisando .zip...", 5)
        data, max_len, max_files = [], 5000, 50
        inc_count, code_ext, cfg_files = 0, {'.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.cs', '.go', '.rb', '.php', '.swift', '.kt', '.rs', '.html', '.css', '.scss', '.md', '.json', '.xml', '.yaml', '.yml', '.sh', '.bat'}, {'requirements.txt', 'package.json', 'pom.xml', 'build.gradle', 'setup.py', 'dockerfile', 'docker-compose.yml', '.gitignore', 'license', 'contributing.md'}
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                infos = zf.infolist(); data.append("Estrutura:\n")
                for item in infos:
                    if worker.is_interruption_requested(): logger.info("Extração ZIP interrompida."); return None
                    data.append(f"- {item.filename}{' (dir)' if item.is_dir() else ''}\n")
                    if len(data) % 50 == 0: QApplication.processEvents()
                data.append("\nConteúdo Selecionado:\n"); progress_cb_emitter("Extraindo conteúdo...", 20)
                content_files = [i for i in infos if not i.is_dir() and (os.path.splitext(i.filename)[1].lower() in code_ext or os.path.basename(i.filename).lower() in cfg_files)]
                total_content_files = len(content_files)
                for i, item in enumerate(content_files):
                    if worker.is_interruption_requested(): logger.info("Extração conteúdo ZIP interrompida."); return None
                    if inc_count >= max_files: logger.info(f"Limite de {max_files} arquivos para conteúdo atingido."); break
                    fname = item.filename
                    try:
                        with zf.open(item) as f_in_zip:
                            bytes_ = f_in_zip.read(); content = "[Erro Decodificação]"
                            try: content = bytes_.decode('utf-8')
                            except: content = bytes_.decode('latin-1', errors='ignore')
                            data.append(f"\n--- Arquivo: {fname} ---\n{content[:max_len]}{'[...TRUNCADO...]' if len(content) > max_len else ''}\n")
                            inc_count += 1
                    except Exception as ef: logger.warning(f"Erro lendo {fname}: {ef}"); data.append(f"\n--- Arquivo: {fname} ---\n[Erro Leitura: {ef}]\n")
                    if total_content_files > 0: progress_cb_emitter(f"Extraindo: {os.path.basename(fname)}", 20 + int(60 * ((i + 1) / total_content_files)))
                    if i % 10 == 0: QApplication.processEvents()
            logger.info(f"Extração ZIP concluída. {inc_count} arquivos com conteúdo."); return "".join(data)
        except zipfile.BadZipFile: logger.error(f"ZIP inválido: {zip_path}", True); self.log_message_signal.emit("Erro", f"ZIP corrompido: {os.path.basename(zip_path)}", "error", False); return None
        except Exception as e: logger.error(f"Erro processando ZIP {zip_path}: {e}", True); self.log_message_signal.emit("Erro", f"Erro no ZIP: {e}", "error", False); return None

    def _trigger_readme_generation(self):
        if not self.zip_file_path: QMessageBox.warning(self, "ZIP Necessário", "Selecione um .zip."); return
        if not self.gemini_client: QMessageBox.critical(self, "IA Offline", "Cliente Gemini não inicializado."); self._check_initial_config_threaded(); return
        self.enable_buttons_signal.emit(False); self.progress_bar_update_signal.emit("Gerando README...", 0)
        self._run_in_thread(self._worker_generate_readme, self.zip_file_path, callback_slot=self._on_readme_generation_finished, error_slot=self._on_readme_generation_error)

    def _worker_generate_readme(self, progress_cb_emitter, worker: Worker, zip_path: str) -> Optional[str]:
        logger.info(f"Worker README para {zip_path}"); self.log_message_signal.emit("IA", "Extraindo dados do .zip...", "system", False)
        data_str = self._extract_project_data_from_zip(progress_cb_emitter, worker, zip_path)
        if worker.is_interruption_requested(): logger.info("Geração README interrompida (extração)."); return None
        if not data_str: raise ValueError("Falha ao extrair dados do .zip.")
        progress_cb_emitter("Enviando para IA Gemini...", 80); self.log_message_signal.emit("IA", "Enviando para Gemini...", "system", False)
        prompt = PROMPT_README_GENERATION.format(project_data=data_str)
        try:
            content = self.gemini_client.send_conversational_prompt(prompt) # type: ignore
            if worker.is_interruption_requested(): logger.info("Geração README interrompida (IA)."); return None
            if content: progress_cb_emitter("README recebido!", 95); self.log_message_signal.emit("IA", "README gerado.", "gemini", False); return content
            else: logger.error("Gemini retornou vazio."); raise ValueError("IA não gerou README.")
        except Exception as e:
            if worker.is_interruption_requested(): logger.info(f"Geração README interrompida, erro ignorado: {e}"); return None
            logger.error(f"Erro comunicação Gemini: {e}", True); raise

    def _on_readme_generation_finished(self, content: Optional[str]):
        self.enable_buttons_signal.emit(True); self.progress_bar_update_signal.emit("Concluído!", 100)
        QTimer.singleShot(2000, lambda: self.progress_bar_update_signal.emit("", 0))
        if content and self.zip_file_path:
            from ..utils.file_helper import get_readme_output_filename
            out_path = get_readme_output_filename(os.path.basename(self.zip_file_path), self.output_directory)
            try:
                with open(out_path, "w", encoding="utf-8") as f: f.write(content)
                self.log_message_signal.emit("Sistema", f"README salvo: {out_path}", "system", False)
                QMessageBox.information(self, "Sucesso!", f"README.md salvo em:\n{out_path}")
                QDesktopServices.openUrl(QUrl.fromLocalFile(self.output_directory)); QDesktopServices.openUrl(QUrl.fromLocalFile(out_path))
            except Exception as e: logger.error(f"Erro salvando README: {e}", True); QMessageBox.critical(self, "Erro Salvar", f"Não salvou README:\n{e}")
        elif not content: self.log_message_signal.emit("Erro", "Falha gerar README (vazio/interrompido).", "error", False)

    def _on_readme_generation_error(self, title: str, message: str):
        self.enable_buttons_signal.emit(True); self.progress_bar_update_signal.emit("Falha geração", 0)
        self.log_message_signal.emit("Erro", f"{title}: {message}", "error", False); QMessageBox.critical(self, title, message)

    def _check_initial_config_threaded(self):
        logger.debug("Disparando _check_initial_config_threaded")
        self._run_in_thread(self._check_initial_config_worker, callback_slot=self._check_initial_config_callback, error_slot=self._generic_worker_error_handler)

    def _check_initial_config_worker(self, progress_cb_emitter, worker: Worker):
        logger.info(">>> _check_initial_config_worker: INÍCIO")
        progress_cb_emitter("Verificando configs...", 20) # Corrigido aqui
        api_key = self.config_mgr.get_api_key()
        model_name = self.config_mgr.get_gemini_model() or DEFAULT_GEMINI_MODEL
        progress_cb_emitter("Configs verificadas.", 80) # Corrigido aqui
        logger.info(">>> _check_initial_config_worker: FIM")
        return {"api_key": api_key, "model_name": model_name}

    def _check_initial_config_callback(self, result: Dict):
        logger.info(f"_check_initial_config_callback: {result}")
        self.progress_bar_update_signal.emit("Config. carregadas",100)
        QTimer.singleShot(1000, lambda: self.progress_bar_update_signal.emit("",0))
        self.api_key = result.get("api_key"); self.model_name = result.get("model_name", DEFAULT_GEMINI_MODEL)
        if not self.api_key: self._prompt_api_key()
        else: self._initialize_gemini_client_threaded()

    def _prompt_api_key(self):
        key, ok = QInputDialog.getText(self, f"{IconName.KEY} API Key", "Sua API Key Google Gemini:", text=self.api_key or "")
        if ok and key and key.strip(): self.api_key = key.strip(); self.config_mgr.set_api_key(self.api_key); self._initialize_gemini_client_threaded()
        elif ok and not (key and key.strip()) and not self.api_key:
            QMessageBox.warning(self, "API Key Necessária", "API Key é necessária."); self.update_status_signal.emit("API Key não configurada."); self.generate_readme_button.setEnabled(False)
        elif not ok and self.api_key: self._initialize_gemini_client_threaded()

    def _prompt_model_name(self):
        curr_model = self.model_name or DEFAULT_GEMINI_MODEL
        new_model, ok = QInputDialog.getText(self, f"{IconName.ROBOT} Modelo Gemini", "Modelo Gemini:", text=curr_model)
        if ok and new_model and new_model.strip() and new_model.strip() != self.model_name:
            self.model_name = new_model.strip(); self.config_mgr.set_gemini_model(self.model_name); self._initialize_gemini_client_threaded()

    def _initialize_gemini_client_threaded(self):
        logger.debug(f"Disparando init IA. Key: {'OK' if self.api_key else 'NÃO'}, Modelo: {self.model_name}")
        if self.api_key and self.model_name:
            self.update_status_signal.emit(f"Iniciando IA ({self.model_name})..."); self.progress_bar_update_signal.emit("Conectando à IA...", 10)
            self._run_in_thread(self._initialize_gemini_client_worker, callback_slot=self._initialize_gemini_client_callback, error_slot=self._generic_worker_error_handler)
        else:
            msg = f"IA não pode iniciar: {'API Key' if not self.api_key else ''}{' e ' if not self.api_key and not self.model_name else ''}{'Modelo' if not self.model_name else ''} faltando."
            self.log_message_signal.emit("Erro", msg, "error", False); self.update_status_signal.emit("Aguardando config API/Modelo...")
            self.generate_readme_button.setEnabled(False); self.progress_bar_update_signal.emit("", 0)

    def _initialize_gemini_client_worker(self, progress_cb_emitter, worker: Worker) -> GeminiClient:
        logger.info(">>> Worker Init IA: INÍCIO")
        try:
            progress_cb_emitter("Conectando Gemini...", 20) # Corrigido
            key, model = self.api_key, self.model_name
            if not key: raise ValueError("API Key não definida.")
            if not model: raise ValueError("Modelo Gemini não definido.")
            logger.info(f">>> Worker Init IA: Criando Cliente Gemini (modelo: {model})")
            client = GeminiClient(api_key=key, model_name=model)
            logger.info(">>> Worker Init IA: Cliente Gemini CRIADO.")
            progress_cb_emitter("Testando conexão...", 60) # Corrigido
            logger.info(">>> Worker Init IA: Testando conexão client.test_connection()...")
            if not client.test_connection(): raise ConnectionError(f"Falha teste conexão {model} (retorno False).")
            logger.info(">>> Worker Init IA: Teste conexão OK.")
            progress_cb_emitter("Conexão Gemini OK.", 90) # Corrigido
            logger.info(">>> Worker Init IA: Retornando cliente.")
            return client
        except Exception as e: logger.error(f">>> Worker Init IA: EXCEÇÃO: {type(e).__name__} - {e}", True); raise
        finally: logger.info(">>> Worker Init IA: FIM")

    def _initialize_gemini_client_callback(self, client: Optional[GeminiClient]):
        logger.info(f"Callback Init IA: Resultado '{type(client)}'")
        if isinstance(client, GeminiClient):
            self.gemini_client = client
            self.log_message_signal.emit("Sistema", f"IA pronta! Modelo: '{client.model_name}'.", "system", False)
            self.update_status_signal.emit(f"Pronto. IA: {client.model_name}")
            self.generate_readme_button.setEnabled(self.zip_file_path is not None)
            self.progress_bar_update_signal.emit("IA Pronta!", 100)
        else:
            self.progress_bar_update_signal.emit("Falha na IA", 0)
            if client is not None: self._generic_worker_error_handler("Erro Init IA", f"Resultado inesperado: {type(client)}")
        QTimer.singleShot(2000, lambda: self.progress_bar_update_signal.emit("",0))

    def _generic_worker_error_handler(self, title: str, message: str):
        logger.error(f"Erro Worker: Título='{title}', Mensagem='{message}'")
        self.progress_bar_update_signal.emit(title.split(':')[0], 0)
        self.log_message_signal.emit("Erro", f"{title}: {message.splitlines()[0]}", "error", False)
        QMessageBox.critical(self, title, message)
        self.enable_buttons_signal.emit(True)
        if any(term in title for term in ["Gemini", "IA", "Conexão"]):
            self.gemini_client = None; self.generate_readme_button.setEnabled(False)
            self.update_status_signal.emit("Erro IA. Verifique config/conexão.")

    @pyqtSlot(str, str, str, bool)
    def _log_message_slot(self, prefix: str, message: str, msg_type: str, is_user_input: bool):
        ts = datetime.now().strftime("%H:%M:%S"); palette = self._get_current_theme_palette()
        colors = {"user":palette.user_msg, "gemini":palette.gemini_msg, "system":palette.system_msg, "error":palette.error_msg}
        color = colors.get(msg_type, palette.text_area_fg)
        fmt_msg = f'<span style="color: {palette.system_msg};">{ts}</span> <b style="color: {color};">[{prefix}]</b>: <span style="color: {color};">{message.replace("<", "&lt;").replace(">", "&gt;")}</span>'
        self.conversation_log.append(fmt_msg)

    @pyqtSlot(str)
    def _update_status_bar_slot(self, message: str): self.status_bar_label.setText(message)

    @pyqtSlot(bool)
    def _enable_buttons_slot(self, enable: bool):
        self.upload_button.setEnabled(enable)
        self.generate_readme_button.setEnabled(enable and self.gemini_client is not None and self.zip_file_path is not None)

    @pyqtSlot(str, int)
    def _update_progress_bar(self, message: str, value: int):
        if not message and value == 0: self.progress_bar.setVisible(False); return
        self.progress_bar.setVisible(True); self.progress_bar.setFormat(f"{message} %p%"); self.progress_bar.setValue(value)
        if value == 100 and ("Concluído" in message or "Pronta" in message): QTimer.singleShot(2500, lambda: self.progress_bar.setVisible(False))
        elif value == 0 and not message: self.progress_bar.setVisible(False)

    def _run_in_thread(self, func, *args, callback_slot=None, error_slot=None, **kwargs):
        thread = QThread(); worker = Worker(func, *args, **kwargs); worker.moveToThread(thread)
        worker.finished.connect(thread.quit); worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater); thread.finished.connect(lambda t=thread: self.worker_threads_map.pop(t, None))
        if callback_slot: worker.result.connect(callback_slot)
        err_slot = error_slot if error_slot else self._generic_worker_error_handler
        worker.error.connect(err_slot); worker.progress.connect(self.progress_bar_update_signal)
        thread.started.connect(worker.run); thread.start()
        self.worker_threads_map[thread] = worker; return thread

    def closeEvent(self, event: QCloseEvent):
        logger.info("Fechando. Limpando threads...")
        if not self.worker_threads_map:
            logger.info("Nenhuma thread ativa."); super().closeEvent(event); return
        
        active_threads = list(self.worker_threads_map.keys())
        logger.info(f"Aguardando {len(active_threads)} thread(s)...")
        for thread in active_threads:
            worker = self.worker_threads_map.get(thread)
            if thread.isRunning():
                logger.info(f"Thread {id(thread)} rodando. Solicitando interrupção...")
                if worker: worker.request_interruption()
                thread.quit()
                if not thread.wait(1500):
                    logger.warning(f"Thread {id(thread)} não finalizou. Terminando...")
                    thread.terminate(); thread.wait(500)
                else: logger.info(f"Thread {id(thread)} finalizada.")
            else: logger.info(f"Thread {id(thread)} não rodando.")
        self.worker_threads_map.clear()
        if self.gemini_client: self.gemini_client.close()
        logger.info("closeEvent concluído."); super().closeEvent(event)

if __name__ == '__main__':
    if hasattr(Qt, 'AA_EnableHighDpiScaling'): QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'): QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    translator = QTranslator()
    locale = QLocale.system().name()
    if not translator.load(f"qtbase_{locale}", QLibraryInfo.location(QLibraryInfo.TranslationsPath)):
        if "_" in locale: translator.load(f"qtbase_{locale.split('_')[0]}", QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(translator)
    main_window = ReadmeGeneratorGUI()
    main_window.show()
    sys.exit(app.exec_())