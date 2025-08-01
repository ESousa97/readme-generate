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

from ..constants import APP_NAME, APP_VERSION, APP_DISPLAY_NAME, DEFAULT_GEMINI_MODEL
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


class ReadmeGeneratorGUI(QMainWindow):
    """GUI principal."""

    def __init__(self) -> None:
        super().__init__()

        # Estado / configurações persistentes
        self.config_mgr = ConfigManager()
        self.api_key: Optional[str] = None  # Será carregada depois
        self.model_name: str = self.config_mgr.get_gemini_model() or DEFAULT_GEMINI_MODEL
        self.available_models: list[str] = []
        self.gemini_client: Optional[GeminiClient] = None
        self.zip_file_path: Optional[str] = None
        self.generated_readme: str = ""
        
        # Flags de estado
        self._api_key_validated = False
        self._models_loaded = False

        # Qt Window basics
        self.setWindowTitle(f"{APP_DISPLAY_NAME} v{APP_VERSION}")
        self.resize(1400, 900)

        # Tema
        self.theme_name = self._detect_system_mode()
        self.theme = THEMES[self.theme_name]

        # Referências de thread
        self._threads: list = []

        # Construção da UI (modular)
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

        # Referências úteis de widgets
        self._map_widgets()
        self._connect_signals()
        
        # Estado inicial - botão desabilitado até validação completa
        self._update_generate_button_state()
        self._update_ui_status()

        # Carrega configuração no background
        QTimer.singleShot(150, self._start_initial_config_check)

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
        self.save_readme_btn.clicked.connect(self._save_readme)
        # Enable custom prompt box toggle
        self.settings_controls["custom_prompt_enabled"].toggled.connect(
            self.settings_controls["custom_prompt_text"].setEnabled
        )

    @staticmethod
    def _detect_system_mode() -> str:
        try:
            return "dark" if (darkdetect.theme() or "").lower() == "dark" else "light"
        except Exception:
            return "light"

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
        key, ok = QInputDialog.getText(
            self, 
            "API Key do Google Gemini", 
            "Digite sua API Key do Google Gemini:\n(Obtenha em: https://aistudio.google.com/app/apikey)",
            text=self.api_key or ""
        )
        if ok and key.strip():
            self.api_key = key.strip()
            self.config_mgr.set_api_key(self.api_key)
            self.console.append_step("API Key", "progress", "Validando...")
            self._api_key_validated = False
            self._models_loaded = False
            self._update_generate_button_state()
            self._validate_api_key_async()

    def _prompt_model_name(self):
        if not self._models_loaded or not self.available_models:
            QMessageBox.warning(
                self, 
                "Modelos não carregados", 
                "Configure uma API Key válida primeiro para carregar a lista de modelos."
            )
            return
            
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
            self.console.append_step("Modelo", "success", model)
            if self.api_key:
                self._initialize_gemini_client()

    def _validate_api_key_async(self):
        """Valida a API Key em thread separada"""
        if not self.api_key:
            return
            
        th = run_in_thread(
            self._validate_api_key_worker,
            self.api_key,
            callback_slot=self._api_key_validation_callback,
            error_slot=self._api_key_validation_error,
        )
        self._threads.append(th)

    def _validate_api_key_worker(self, progress_cb, step_cb, worker, api_key):
        """Worker para validar API Key"""
        try:
            step_cb("API", "progress", "Configurando cliente...")
            genai.configure(api_key=api_key)
            
            step_cb("Modelos", "progress", "Carregando lista...")
            # Primeiro carrega lista de modelos disponíveis
            try:
                models_data = list(genai.list_models())
            except Exception as e:
                error_str = str(e).lower()
                if "quota" in error_str or "429" in str(e):
                    return {
                        'valid': False, 
                        'models': [],
                        'quota_exceeded': True,
                        'message': 'Quota da API excedida. Aguarde ou verifique seu plano de cobrança.'
                    }
                elif "403" in str(e):
                    return {
                        'valid': False, 
                        'models': [],
                        'quota_exceeded': False,
                        'message': 'API Key sem permissões adequadas. Verifique se a chave tem acesso aos modelos Gemini.'
                    }
                raise
            
            available_models = []
            working_models = []
            
            for model in models_data:
                if hasattr(model, 'name'):
                    model_name = model.name
                    display_name = model_name.replace('models/', '') if model_name.startswith('models/') else model_name
                    available_models.append(display_name)
                    
                    # Verificar se suporta generateContent
                    if hasattr(model, 'supported_generation_methods'):
                        if 'generateContent' in model.supported_generation_methods:
                            working_models.append(model_name)
                    else:
                        working_models.append(model_name)
            
            if not available_models:
                return {
                    'valid': False, 
                    'models': [],
                    'quota_exceeded': False,
                    'message': 'Nenhum modelo disponível encontrado para esta API Key'
                }
            
            # Testar conexão com um modelo disponível
            test_model = None
            if working_models:
                # Priorizar modelos conhecidos
                preferred_models = ['models/gemini-1.5-flash', 'models/gemini-1.0-pro', 'models/gemini-1.5-pro']
                for preferred in preferred_models:
                    if preferred in working_models:
                        test_model = preferred
                        break
                
                if not test_model:
                    test_model = working_models[0]
            
            if test_model:
                step_cb("API", "progress", f"Testando conexão...")
                try:
                    model = genai.GenerativeModel(test_model)
                    response = model.generate_content(
                        "Hi", 
                        generation_config=genai.types.GenerationConfig(
                            max_output_tokens=5,
                            temperature=0.1
                        )
                    )
                    # Se chegou até aqui, API Key é válida
                except Exception as e:
                    error_str = str(e).lower()
                    if "quota" in error_str or "429" in str(e):
                        return {
                            'valid': False, 
                            'models': available_models,
                            'quota_exceeded': True,
                            'message': 'API Key válida, mas quota excedida. Aguarde ou atualize seu plano.'
                        }
                    elif "404" in str(e):
                        # Modelo específico não encontrado, mas API Key pode ser válida
                        pass
                    else:
                        raise
            
            return {
                'valid': True, 
                'models': available_models,
                'working_models': working_models,
                'quota_exceeded': False,
                'message': 'API Key validada com sucesso'
            }
            
        except Exception as e:
            error_str = str(e).lower()
            if "quota" in error_str or "429" in str(e):
                return {
                    'valid': False, 
                    'models': [],
                    'quota_exceeded': True,
                    'message': 'Quota da API excedida. Verifique seu plano de cobrança no Google AI Studio.'
                }
            elif "403" in str(e):
                return {
                    'valid': False, 
                    'models': [],
                    'quota_exceeded': False,
                    'message': 'API Key sem permissões adequadas ou inválida.'
                }
            elif "401" in str(e):
                return {
                    'valid': False, 
                    'models': [],
                    'quota_exceeded': False,
                    'message': 'API Key inválida ou expirada.'
                }
            else:
                return {
                    'valid': False, 
                    'models': [],
                    'quota_exceeded': False,
                    'message': f'Erro na validação: {str(e)}'
                }

    def _api_key_validation_callback(self, result):
        """Callback para validação da API Key"""
        if result['valid']:
            self._api_key_validated = True
            self.available_models = result['models']  # Nomes limpos para display
            self._models_loaded = True
            
            self.console.append_step("API Key", "success", "Validada")
            self.console.append_step("Modelos", "success", f"{len(self.available_models)} modelos carregados")
            
            # Verificar se o modelo atual está na lista
            current_model = self.model_name
            if current_model.startswith('models/'):
                current_model = current_model.replace('models/', '')
                
            if current_model not in self.available_models:
                # Usar primeiro modelo disponível se o atual não estiver na lista
                if self.available_models:
                    self.model_name = self.available_models[0]
                    self.model_label.setText(self.model_name)
                    self.config_mgr.set_gemini_model(self.model_name)
                    self.console.append_step("Modelo", "info", f"Modelo alterado para {self.model_name}")
            
            # Inicializa o cliente Gemini
            self._initialize_gemini_client()
        else:
            self._api_key_validated = False
            self._models_loaded = False
            self.available_models = []
            self.gemini_client = None
            
            self.console.append_step("API Key", "error", "Problema na validação")
            
            # Tratamento especial para quota excedida
            if result.get('quota_exceeded'):
                self._show_quota_exceeded_dialog(result['message'])
            else:
                QMessageBox.critical(
                    self, 
                    "API Key Inválida", 
                    f"Erro ao validar API Key:\n\n{result['message']}\n\nVerifique:\n• Se a chave está correta\n• Se você tem acesso aos modelos Gemini\n• Sua quota da API"
                )
        
        self._update_generate_button_state()
        self._update_ui_status()

    def _show_quota_exceeded_dialog(self, message):
        """Mostra diálogo específico para quota excedida"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Quota da API Excedida")
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText("Sua quota da API Google Gemini foi excedida.")
        msg_box.setDetailedText(message)
        
        detailed_info = """
SOLUÇÕES POSSÍVEIS:

1. AGUARDAR RENOVAÇÃO:
   • Quotas gratuitas se renovam mensalmente
   • Aguarde até o próximo ciclo de cobrança

2. VERIFICAR SEU PLANO:
   • Acesse: https://aistudio.google.com/app/apikey
   • Verifique seus limites de uso
   • Considere upgrader para plano pago

3. QUOTA DIÁRIA:
   • Se você tem quota diária, aguarde 24h
   • Tente novamente amanhã

4. GERENCIAR USO:
   • Use o modelo com moderação
   • Evite prompts muito longos
   • Considere usar modelos menores como gemini-1.0-pro

Para mais informações sobre limites e preços:
https://ai.google.dev/pricing
        """
        
        msg_box.setInformativeText(detailed_info)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def _api_key_validation_error(self, title, msg):
        """Error callback para validação da API Key"""
        self._api_key_validated = False
        self._models_loaded = False
        self.available_models = []
        self.gemini_client = None
        
        self.console.append_step("API Key", "error", "Erro na validação")
        self._update_generate_button_state()
        self._update_ui_status()
        
        QMessageBox.critical(self, title, msg)

    def _initialize_gemini_client(self):
        """Cria GeminiClient após validação"""
        if not self._api_key_validated or not self.api_key:
            return
            
        try:
            # Usar nome do modelo com prefixo models/ se necessário
            model_name_for_client = self.model_name
            if not model_name_for_client.startswith('models/'):
                model_name_for_client = f'models/{model_name_for_client}'
            
            self.gemini_client = GeminiClient(self.api_key, model_name_for_client)
            self.console.append_step("Cliente IA", "success", f"Inicializado com {self.model_name}")
            self._update_generate_button_state()
            self._update_ui_status()
        except Exception as e:
            logger.error("Erro ao inicializar GeminiClient", exc_info=True)
            self.gemini_client = None
            self.console.append_step("Cliente IA", "error", "Falha na inicialização")
            
            error_msg = str(e)
            if "404" in error_msg:
                error_msg = f"Modelo '{self.model_name}' não encontrado ou não suportado."
            elif "403" in error_msg:
                error_msg = "Sem permissões para usar este modelo."
            
            QMessageBox.critical(self, "Erro na IA", f"Erro ao inicializar cliente:\n{error_msg}")
            self._update_generate_button_state()
            self._update_ui_status()

    def _update_generate_button_state(self):
        """Atualiza estado do botão Gerar README"""
        can_generate = (
            self._api_key_validated and 
            self._models_loaded and 
            self.gemini_client is not None and 
            bool(self.zip_file_path)
        )
        self.generate_btn.setEnabled(can_generate)
        
        if can_generate:
            self.generate_btn.setText("Gerar README")
        else:
            reasons = []
            if not self._api_key_validated:
                reasons.append("API Key não validada")
            if not self._models_loaded:
                reasons.append("Modelos não carregados")
            if not self.zip_file_path:
                reasons.append("Arquivo ZIP não selecionado")
            
            tooltip = "Requisitos faltantes:\n• " + "\n• ".join(reasons)
            self.generate_btn.setToolTip(tooltip)
            self.generate_btn.setText("Gerar README (Indisponível)")

    def _update_ui_status(self):
        """Atualiza labels de status na UI"""
        if self._api_key_validated and self.gemini_client:
            self.api_status_label.setText(f"IA Pronta – {self.model_name}")
            self.api_status_label.setStyleSheet(f"color: {self.theme.success};")
        elif self.api_key:
            self.api_status_label.setText("Validando API Key...")
            self.api_status_label.setStyleSheet(f"color: {self.theme.warning};")
        else:
            self.api_status_label.setText("API Key não configurada")
            self.api_status_label.setStyleSheet(f"color: {self.theme.error};")

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

    def _trigger_readme_generation(self):
        """Inicia geração do README"""
        # Validação dupla de segurança
        if not self._api_key_validated or not self.gemini_client or not self.zip_file_path:
            QMessageBox.warning(
                self, 
                "Geração não disponível", 
                "Configure uma API Key válida e selecione um arquivo ZIP primeiro."
            )
            return
            
        cfg = self._get_advanced_config()
        self.console.append_step("Geração", "progress", "Iniciando…")
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_bar.setValue(0)
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("Gerando...")

        th = run_in_thread(
            self._generate_readme_worker,
            self.zip_file_path,
            cfg,
            callback_slot=self._readme_generation_callback,
            error_slot=self._readme_generation_error,
        )
        self._threads.append(th)

    def _generate_readme_worker(self, progress_cb, step_cb, worker, zip_path, cfg):
        """Worker para gerar README"""
        try:
            # 1) extrai dados
            step_cb("Extração", "progress", "Analisando ZIP...")
            progress_cb("Extraindo dados do projeto", 10)
            project_data = extract_project_data_from_zip(
                zip_path, cfg, progress_cb=progress_cb, step_cb=step_cb
            )
            
            if worker.is_interruption_requested():
                return None

            # 2) monta prompt
            step_cb("Prompt", "progress", "Preparando prompt...")
            progress_cb("Montando prompt para IA", 70)
            prompt = build_prompt(project_data, cfg)

            # 3) IA
            step_cb("IA", "progress", "Consultando Gemini…")
            progress_cb("Gerando README com IA", 85)
            
            if not self.gemini_client:
                raise Exception("Cliente Gemini não está disponível")
                
            response = self.gemini_client.send_conversational_prompt(prompt)
            
            step_cb("Finalização", "progress", "Processando resposta...")
            progress_cb("Finalizando", 95)
            readme = clean_readme_content(response or "")
            
            progress_cb("Concluído", 100)
            return readme
            
        except Exception as e:
            step_cb("Erro", "error", str(e))
            raise

    def _readme_generation_callback(self, readme_text: str):
        """Callback para geração do README"""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("Gerar README")
        
        if not readme_text:
            self.console.append_step("README", "error", "IA retornou vazio")
            QMessageBox.warning(self, "Falha", "A IA não retornou conteúdo.")
            return
            
        self.generated_readme = readme_text
        self.readme_preview.set_markdown_content(readme_text)
        self.save_readme_btn.setEnabled(True)
        self.preview_tabs.setCurrentIndex(0)  # Mostra aba de preview
        self.console.append_step("README", "success", "Gerado com sucesso")

    def _readme_generation_error(self, title, msg):
        """Error callback para geração do README"""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("Gerar README")
        self.console.append_step("Erro", "error", title)
        QMessageBox.critical(self, title, msg)

    def _start_initial_config_check(self):
        """Carrega configuração inicial"""
        saved_api_key = self.config_mgr.get_api_key()
        if saved_api_key:
            self.api_key = saved_api_key
            self.console.append_step("Configuração", "info", "API Key encontrada")
            self._validate_api_key_async()
        else:
            self.console.append_step("Configuração", "info", "Configure uma API Key para começar")
            self._update_ui_status()

    # Menu methods
    def _save_readme(self):
        """Salva o README gerado em arquivo."""
        if not self.generated_readme:
            QMessageBox.warning(self, "Aviso", "Nenhum README foi gerado ainda.")
            return
        
        default_name = "README.md"
        if self.zip_file_path:
            base_name = os.path.splitext(os.path.basename(self.zip_file_path))[0]
            default_name = f"{base_name}_README.md"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar README", default_name, "Markdown (*.md);;Todos os arquivos (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.generated_readme)
                QMessageBox.information(self, "Sucesso", f"README salvo em:\n{file_path}")
                self.console.append_step("Arquivo", "success", f"Salvo: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar arquivo:\n{e}")
                self.console.append_step("Arquivo", "error", f"Erro ao salvar: {e}")

    def _export_markdown(self):
        """Exporta como Markdown."""
        self._save_readme()

    def _export_html(self):
        """Exporta como HTML."""
        if not self.generated_readme:
            QMessageBox.warning(self, "Aviso", "Nenhum README foi gerado ainda.")
            return
        
        default_name = "README.html"
        if self.zip_file_path:
            base_name = os.path.splitext(os.path.basename(self.zip_file_path))[0]
            default_name = f"{base_name}_README.html"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar como HTML", default_name, "HTML (*.html);;Todos os arquivos (*)"
        )
        
        if file_path:
            try:
                html_content = self.readme_preview.markdown_renderer.render_to_html(self.generated_readme)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                QMessageBox.information(self, "Sucesso", f"HTML exportado para:\n{file_path}")
                self.console.append_step("Export", "success", f"HTML: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar HTML:\n{e}")
                self.console.append_step("Export", "error", f"Erro HTML: {e}")

    def _export_pdf(self):
        """Exporta como PDF."""
        QMessageBox.information(self, "Funcionalidade", 
                               "Exportação para PDF será implementada em versão futura.\n"
                               "Por enquanto, use 'Exportar HTML' e imprima como PDF no navegador.")

    def _copy_readme(self):
        """Copia o README para a área de transferência."""
        if not self.generated_readme:
            QMessageBox.warning(self, "Aviso", "Nenhum README foi gerado ainda.")
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(self.generated_readme)
        QMessageBox.information(self, "Copiado", "README copiado para a área de transferência!")
        self.console.append_step("Clipboard", "success", "README copiado")

    def _show_about(self):
        """Mostra informações sobre o aplicativo."""
        about_text = f"""
        <h2>{APP_DISPLAY_NAME}</h2>
        <p><b>Versão:</b> {APP_VERSION}</p>
        <p><b>Descrição:</b> Gerador inteligente de documentação README.md usando IA</p>
        <p><b>Tecnologias:</b> Python, PyQt5, Google Gemini AI</p>
        <p><b>Autor:</b> Desenvolvido com ❤️ para a comunidade</p>
        <hr>
        <p><small>Este software utiliza a API do Google Gemini para gerar documentação inteligente e profissional.</small></p>
        """
        QMessageBox.about(self, f"Sobre - {APP_DISPLAY_NAME}", about_text)

    def _show_help(self):
        """Mostra ajuda do aplicativo."""
        help_text = """
        <h3>Como usar o Gerador de README IA:</h3>
        <ol>
        <li><b>Configure sua API Key:</b> Vá em Configurações → Configurar API Key</li>
        <li><b>Selecione um arquivo ZIP:</b> Use o botão "Selecionar Arquivo ZIP"</li>
        <li><b>Ajuste as configurações:</b> Na aba "Configurações Avançadas"</li>
        <li><b>Gere o README:</b> Clique em "Gerar README"</li>
        <li><b>Salve o resultado:</b> Use "Salvar README" ou Ctrl+S</li>
        </ol>
        
        <h4>Dicas:</h4>
        <ul>
        <li>O ZIP deve conter o código-fonte do seu projeto</li>
        <li>Arquivos muito grandes são truncados automaticamente</li>
        <li>Use prompts personalizados para necessidades específicas</li>
        </ul>
        """
        QMessageBox.information(self, "Ajuda", help_text)

    def _switch_theme(self, theme_name: str):
        if theme_name in THEMES:
            self.theme_name = theme_name
            self.theme = THEMES[theme_name]
            apply_theme(self, theme_name)

    def _switch_theme_auto(self):
        self._switch_theme(self._detect_system_mode())

    def closeEvent(self, evt):
        """Cleanup ao fechar aplicação"""
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


def main():
    app = QApplication(sys.argv)
    win = ReadmeGeneratorGUI()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
    