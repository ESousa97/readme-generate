# gerador_readme_ia/gui/app_gui.py
"""
Interface principal modernizada com CustomTkinter estilo Windows 11
"""
from __future__ import annotations

import os
import sys
import logging
import threading
import tkinter as tk
from pathlib import Path
from typing import Dict, Optional, Callable
from tkinter import filedialog, messagebox

import customtkinter as ctk
import darkdetect
import google.generativeai as genai

from ..constants import APP_NAME, APP_VERSION, APP_DISPLAY_NAME, DEFAULT_GEMINI_MODEL
from ..config_manager import ConfigManager
from ..ia_client.gemini_client import GeminiClient, QuotaExceededException
from ..logger_setup import setup_logging

from .ctk_theme_manager import theme_manager
from .ctk_widgets import *
from .logic import (
    build_prompt,
    extract_project_data_from_zip,
    clean_readme_content,
)

logger = setup_logging(f"{APP_NAME}.gui", debug=False)


class ReadmeGeneratorApp(ctk.CTk):
    """Interface principal modernizada com CustomTkinter"""

    def __init__(self):
        super().__init__()

        # Configurações iniciais
        self.title(f"{APP_DISPLAY_NAME} v{APP_VERSION}")
        self.geometry("1400x900")
        self.minsize(1200, 700)
        
        # Configurar ícone se disponível
        try:
            icon_path = Path(__file__).parent.parent / "assets" / "icon.ico"
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except:
            pass

        # Estado da aplicação
        self.config_mgr = ConfigManager()
        self.api_key: Optional[str] = None
        self.model_name: str = self.config_mgr.get_gemini_model() or DEFAULT_GEMINI_MODEL
        self.available_models: list[str] = []
        self.gemini_client: Optional[GeminiClient] = None
        self.zip_file_path: Optional[str] = None
        self.generated_readme: str = ""
        
        # Estados de validação
        self._api_key_validated = False
        self._models_loaded = False
        
        # Controle de threads
        self._active_threads: list = []

        # Interface
        self._setup_ui()
        self._load_initial_config()

        # Bind do fechamento
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_ui(self):
        """Configura a interface principal"""
        # Layout principal em grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        self._create_header()
        
        # Conteúdo principal
        self._create_main_content()
        
        # Footer com controles
        self._create_footer()

    def _create_header(self):
        """Cria o cabeçalho da aplicação"""
        header_frame = ModernFrame(self, corner_radius=0, height=80)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Ícone e título
        icon_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        icon_frame.grid(row=0, column=0, sticky="w", padx=20, pady=20)
        
        # Ícone placeholder (você pode substituir por um ícone real)
        icon_label = ctk.CTkLabel(
            icon_frame, 
            text="🤖", 
            font=ctk.CTkFont(size=32)
        )
        icon_label.pack(side="left", padx=(0, 15))
        
        # Título e subtítulo
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=1, sticky="w", pady=20)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text=APP_DISPLAY_NAME,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=theme_manager.get_color("text_primary")
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Gere documentações profissionais automaticamente com IA",
            font=ctk.CTkFont(size=12),
            text_color=theme_manager.get_color("text_secondary")
        )
        subtitle_label.pack(anchor="w")
        
        # Controles do tema
        theme_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        theme_frame.grid(row=0, column=2, sticky="e", padx=20, pady=20)
        
        self.theme_switch = ctk.CTkSwitch(
            theme_frame,
            text="Tema Escuro",
            command=self._toggle_theme,
            width=100
        )
        self.theme_switch.pack()
        
        # Definir estado inicial do switch
        if theme_manager.current_theme == "dark":
            self.theme_switch.select()

    def _create_main_content(self):
        """Cria o conteúdo principal"""
        main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        main_frame.grid_columnconfigure(1, weight=2)  # Área de preview maior
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Painel esquerdo
        self._create_left_panel(main_frame)
        
        # Painel direito
        self._create_right_panel(main_frame)

    def _create_left_panel(self, parent):
        """Cria o painel esquerdo com controles"""
        left_frame = ModernFrame(parent, width=380)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_frame.grid_columnconfigure(0, weight=1)
        
        # Seção do arquivo
        file_section = self._create_file_section(left_frame)
        file_section.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Seção de configuração
        config_section = self._create_config_section(left_frame)
        config_section.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        # Console compacto
        console_section = self._create_console_section(left_frame)
        console_section.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        left_frame.grid_rowconfigure(2, weight=1)

    def _create_file_section(self, parent):
        """Seção de seleção de arquivo"""
        section = ModernSection(parent, title="Arquivo do Projeto")
        
        # Path do arquivo
        self.file_path_var = tk.StringVar(value="Nenhum arquivo selecionado")
        path_label = ctk.CTkLabel(
            section.content_frame,
            textvariable=self.file_path_var,
            font=ctk.CTkFont(size=11),
            text_color=theme_manager.get_color("text_secondary"),
            wraplength=320
        )
        path_label.pack(fill="x", pady=(0, 10))
        
        # Botão de seleção
        self.select_file_btn = ModernButton(
            section.content_frame,
            text="Selecionar Arquivo ZIP",
            command=self._select_zip_file,
            width=300,
            height=40
        )
        self.select_file_btn.pack(fill="x")
        
        return section

    def _create_config_section(self, parent):
        """Seção de configuração da IA"""
        section = ModernSection(parent, title="Configuração da IA")
        
        # Status da API
        status_frame = ctk.CTkFrame(section.content_frame, fg_color="transparent")
        status_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            status_frame,
            text="Status:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(anchor="w")
        
        self.api_status_var = tk.StringVar(value="API Key não configurada")
        self.api_status_label = ctk.CTkLabel(
            status_frame,
            textvariable=self.api_status_var,
            font=ctk.CTkFont(size=11),
            text_color=theme_manager.get_color("error")
        )
        self.api_status_label.pack(anchor="w")
        
        # Modelo atual
        model_frame = ctk.CTkFrame(section.content_frame, fg_color="transparent")
        model_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            model_frame,
            text="Modelo:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(anchor="w")
        
        self.model_var = tk.StringVar(value=self.model_name)
        model_label = ctk.CTkLabel(
            model_frame,
            textvariable=self.model_var,
            font=ctk.CTkFont(size=11),
            text_color=theme_manager.get_color("text_secondary")
        )
        model_label.pack(anchor="w")
        
        # Botões de configuração
        buttons_frame = ctk.CTkFrame(section.content_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")
        buttons_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.config_api_btn = ModernButton(
            buttons_frame,
            text="API Key",
            command=self._configure_api_key,
            width=140,
            height=35
        )
        self.config_api_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        self.config_model_btn = ModernButton(
            buttons_frame,
            text="Modelo",
            command=self._configure_model,
            width=140,
            height=35
        )
        self.config_model_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
        return section

    def _create_console_section(self, parent):
        """Console compacto de operações"""
        section = ModernSection(parent, title="Console")
        
        # Console text widget
        self.console = ConsoleWidget(section.content_frame)
        self.console.pack(fill="both", expand=True)
        
        return section

    def _create_right_panel(self, parent):
        """Cria o painel direito com preview e configurações"""
        right_frame = ModernFrame(parent)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=1)
        
        # Tabs para preview e configurações
        self.tabview = ctk.CTkTabview(right_frame, corner_radius=8)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Tab de preview
        preview_tab = self.tabview.add("README Gerado")
        self._create_preview_tab(preview_tab)
        
        # Tab de configurações
        settings_tab = self.tabview.add("Configurações Avançadas")
        self._create_settings_tab(settings_tab)

    def _create_preview_tab(self, parent):
        """Tab de preview do README"""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        
        # Toolbar do preview
        toolbar = ctk.CTkFrame(parent, height=50)
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        toolbar.grid_columnconfigure(2, weight=1)
        
        # Modo de visualização
        view_label = ctk.CTkLabel(toolbar, text="Modo:", font=ctk.CTkFont(size=11))
        view_label.grid(row=0, column=0, padx=10, pady=12)
        
        self.view_mode = ctk.CTkSegmentedButton(
            toolbar,
            values=["Preview", "Código", "Lado a Lado"],
            command=self._change_view_mode,
            width=250
        )
        self.view_mode.set("Preview")
        self.view_mode.grid(row=0, column=1, padx=5, pady=12)
        
        # Botões de ação
        actions_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        actions_frame.grid(row=0, column=3, padx=10, pady=8, sticky="e")
        
        copy_btn = ModernButton(
            actions_frame,
            text="Copiar",
            command=self._copy_readme,
            width=80,
            height=30
        )
        copy_btn.pack(side="left", padx=(0, 5))
        
        self.save_readme_btn = ModernButton(
            actions_frame,
            text="Salvar",
            command=self._save_readme,
            width=80,
            height=30
        )
        self.save_readme_btn.pack(side="left")
        self.save_readme_btn.configure(state="disabled")
        
        # Área de preview
        self.preview_container = ctk.CTkFrame(parent)
        self.preview_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.preview_container.grid_columnconfigure((0, 1), weight=1)
        self.preview_container.grid_rowconfigure(0, weight=1)
        
        # Preview renderizado
        self.readme_preview = ModernTextWidget(self.preview_container, wrap="word")
        self.readme_preview.grid(row=0, column=0, sticky="nsew", padx=(5, 2), pady=5)
        
        # Editor de código
        self.code_editor = ModernTextWidget(
            self.preview_container, 
            wrap="none",
            font_family=theme_manager.get_mono_font_family()
        )
        self.code_editor.grid(row=0, column=1, sticky="nsew", padx=(2, 5), pady=5)
        self.code_editor.grid_remove()  # Inicialmente oculto

    def _create_settings_tab(self, parent):
        """Tab de configurações avançadas"""
        # Scrollable frame para as configurações
        settings_scroll = ctk.CTkScrollableFrame(parent, label_text="Configurações de Geração")
        settings_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        settings_scroll.grid_columnconfigure(0, weight=1)
        
        # Seção de prompt personalizado
        prompt_section = self._create_prompt_section(settings_scroll)
        prompt_section.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        # Seção de filtros
        filter_section = self._create_filter_section(settings_scroll)
        filter_section.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        
        # Seção de estilo
        style_section = self._create_style_section(settings_scroll)
        style_section.grid(row=2, column=0, sticky="ew", pady=(0, 15))

    def _create_prompt_section(self, parent):
        """Seção de prompt personalizado"""
        section = ModernSection(parent, title="Prompt Personalizado")
        
        # Switch para ativar prompt customizado
        self.custom_prompt_enabled = ctk.CTkSwitch(
            section.content_frame,
            text="Usar prompt personalizado",
            command=self._toggle_custom_prompt
        )
        self.custom_prompt_enabled.pack(anchor="w", pady=(0, 10))
        
        # Área de texto para o prompt
        self.custom_prompt_text = ModernTextWidget(
            section.content_frame,
            height=120,
            placeholder_text="Digite instruções específicas para a IA..."
        )
        self.custom_prompt_text.pack(fill="x", pady=(0, 10))
        self.custom_prompt_text.configure(state="disabled")
        
        return section

    def _create_filter_section(self, parent):
        """Seção de filtros de arquivo"""
        section = ModernSection(parent, title="Filtros de Arquivo")
        
        # Checkboxes de filtros
        filters_frame = ctk.CTkFrame(section.content_frame, fg_color="transparent")
        filters_frame.pack(fill="x", pady=(0, 15))
        filters_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.include_tests = ctk.CTkCheckBox(filters_frame, text="Incluir testes")
        self.include_tests.grid(row=0, column=0, sticky="w", pady=2)
        self.include_tests.select()
        
        self.include_docs = ctk.CTkCheckBox(filters_frame, text="Incluir documentação")
        self.include_docs.grid(row=0, column=1, sticky="w", pady=2)
        self.include_docs.select()
        
        self.include_config = ctk.CTkCheckBox(filters_frame, text="Incluir configurações")
        self.include_config.grid(row=1, column=0, sticky="w", pady=2)
        self.include_config.select()
        
        # Configurações numéricas
        numeric_frame = ctk.CTkFrame(section.content_frame, fg_color="transparent")
        numeric_frame.pack(fill="x")
        numeric_frame.grid_columnconfigure(1, weight=1)
        
        # Tamanho máximo de arquivo
        size_label = ctk.CTkLabel(numeric_frame, text="Tamanho máx. por arquivo (KB):")
        size_label.grid(row=0, column=0, sticky="w", pady=5)
        
        self.max_file_size = ctk.CTkEntry(numeric_frame, width=100, placeholder_text="5")
        self.max_file_size.grid(row=0, column=1, sticky="e", pady=5)
        self.max_file_size.insert(0, "5")
        
        # Máximo de arquivos
        files_label = ctk.CTkLabel(numeric_frame, text="Máximo de arquivos:")
        files_label.grid(row=1, column=0, sticky="w", pady=5)
        
        self.max_files = ctk.CTkEntry(numeric_frame, width=100, placeholder_text="30")
        self.max_files.grid(row=1, column=1, sticky="e", pady=5)
        self.max_files.insert(0, "30")
        
        return section

    def _create_style_section(self, parent):
        """Seção de estilo do README"""
        section = ModernSection(parent, title="Estilo do README")
        
        # Selector de estilo
        style_frame = ctk.CTkFrame(section.content_frame, fg_color="transparent")
        style_frame.pack(fill="x", pady=(0, 15))
        style_frame.grid_columnconfigure(1, weight=1)
        
        style_label = ctk.CTkLabel(style_frame, text="Estilo:")
        style_label.grid(row=0, column=0, sticky="w", pady=5)
        
        self.readme_style = ctk.CTkComboBox(
            style_frame,
            values=["Profissional", "Detalhado", "Minimalista", "Tutorial", "Open Source"],
            width=200
        )
        self.readme_style.grid(row=0, column=1, sticky="e", pady=5)
        self.readme_style.set("Profissional")
        
        # Opções adicionais
        options_frame = ctk.CTkFrame(section.content_frame, fg_color="transparent")
        options_frame.pack(fill="x")
        options_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.include_badges = ctk.CTkCheckBox(options_frame, text="Incluir badges")
        self.include_badges.grid(row=0, column=0, sticky="w", pady=2)
        self.include_badges.select()
        
        self.include_toc = ctk.CTkCheckBox(options_frame, text="Incluir índice")
        self.include_toc.grid(row=0, column=1, sticky="w", pady=2)
        self.include_toc.select()
        
        self.include_examples = ctk.CTkCheckBox(options_frame, text="Incluir exemplos")
        self.include_examples.grid(row=1, column=0, sticky="w", pady=2)
        self.include_examples.select()
        
        return section

    def _create_footer(self):
        """Cria o footer com controles de geração"""
        footer = ModernFrame(self, corner_radius=0, height=80)
        footer.grid(row=2, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        footer.grid_columnconfigure(0, weight=1)
        
        # Conteúdo do footer
        content_frame = ctk.CTkFrame(footer, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Progress bar (inicialmente oculto)
        self.progress_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.progress_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=theme_manager.get_color("text_secondary")
        )
        self.progress_label.grid(row=0, column=0, sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=8)
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        self.progress_bar.set(0)
        
        # Ocultar progress inicialmente
        self.progress_frame.grid_remove()
        
        # Botão principal de geração
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.grid(row=1, column=0)
        
        self.generate_btn = ModernButton(
            button_frame,
            text="Gerar README",
            command=self._generate_readme,
            width=250,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.generate_btn.pack()
        self.generate_btn.configure(state="disabled")

    # Event handlers
    def _toggle_theme(self):
        """Alterna o tema da aplicação"""
        theme_manager.switch_theme()
        # Força um refresh da interface
        self.update()

    def _change_view_mode(self, mode):
        """Altera o modo de visualização do preview"""
        if mode == "Preview":
            self.readme_preview.grid()
            self.code_editor.grid_remove()
            self.preview_container.grid_columnconfigure(0, weight=1)
            self.preview_container.grid_columnconfigure(1, weight=0)
        elif mode == "Código":
            self.readme_preview.grid_remove()
            self.code_editor.grid()
            self.preview_container.grid_columnconfigure(0, weight=0)
            self.preview_container.grid_columnconfigure(1, weight=1)
        elif mode == "Lado a Lado":
            self.readme_preview.grid()
            self.code_editor.grid()
            self.preview_container.grid_columnconfigure((0, 1), weight=1)

    def _toggle_custom_prompt(self):
        """Ativa/desativa o prompt personalizado"""
        if self.custom_prompt_enabled.get():
            self.custom_prompt_text.configure(state="normal")
        else:
            self.custom_prompt_text.configure(state="disabled")

    def _select_zip_file(self):
        """Seleciona arquivo ZIP do projeto"""
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo ZIP do projeto",
            initialdir=str(Path.home()),
            filetypes=[("Arquivos ZIP", "*.zip")]
        )
        
        if file_path:
            self.zip_file_path = file_path
            filename = os.path.basename(file_path)
            self.file_path_var.set(filename)
            self.console.append_step("Arquivo", "success", filename)
            self._update_generate_button_state()

    def _configure_api_key(self):
        """Configura a API Key do Gemini"""
        dialog = APIKeyDialog(self, self.api_key or "")
        if dialog.result:
            self.api_key = dialog.result
            self.config_mgr.set_api_key(self.api_key)
            self.console.append_step("API Key", "progress", "Validando...")
            self._validate_api_key_async()

    def _configure_model(self):
        """Configura o modelo Gemini"""
        if not self._models_loaded or not self.available_models:
            messagebox.showwarning(
                "Modelos não carregados",
                "Configure uma API Key válida primeiro para carregar a lista de modelos."
            )
            return
        
        dialog = ModelSelectionDialog(self, self.available_models, self.model_name)
        if dialog.result:
            self.model_name = dialog.result
            self.model_var.set(self.model_name)
            self.config_mgr.set_gemini_model(self.model_name)
            self.console.append_step("Modelo", "success", self.model_name)
            if self.api_key:
                self._initialize_gemini_client()

    def _generate_readme(self):
        """Inicia a geração do README"""
        if not self._can_generate():
            return
        
        # Configurar interface para geração
        self.generate_btn.configure(state="disabled", text="Gerando...")
        self.progress_frame.grid()
        self.progress_bar.set(0)
        self.progress_label.configure(text="Preparando...")
        
        # Obter configurações
        config = self._get_generation_config()
        
        # Iniciar geração em thread separada
        self.console.append_step("Geração", "progress", "Iniciando...")
        thread = threading.Thread(
            target=self._generate_readme_worker,
            args=(self.zip_file_path, config),
            daemon=True
        )
        thread.start()
        self._active_threads.append(thread)

    def _generate_readme_worker(self, zip_path: str, config: Dict):
        """Worker thread para gerar README"""
        try:
            # Atualizar progress
            self.after(0, lambda: self._update_progress("Extraindo dados do projeto", 10))
            
            # Extrair dados
            project_data = extract_project_data_from_zip(zip_path, config)
            
            # Montar prompt
            self.after(0, lambda: self._update_progress("Preparando prompt para IA", 40))
            prompt = build_prompt(project_data, config)
            
            # Gerar com IA
            self.after(0, lambda: self._update_progress("Consultando Gemini AI", 70))
            if not self.gemini_client:
                raise Exception("Cliente Gemini não está disponível")
            
            response = self.gemini_client.send_conversational_prompt(prompt)
            
            # Processar resposta
            self.after(0, lambda: self._update_progress("Finalizando", 95))
            readme = clean_readme_content(response or "")
            
            # Sucesso
            self.after(0, lambda: self._generation_success(readme))
            
        except QuotaExceededException as e:
            self.after(0, lambda: self._generation_quota_error(e))
        except Exception as e:
            self.after(0, lambda: self._generation_error(str(e)))

    def _update_progress(self, message: str, value: int):
        """Atualiza a barra de progresso"""
        self.progress_label.configure(text=message)
        self.progress_bar.set(value / 100)
        self.update_idletasks()

    def _generation_success(self, readme_text: str):
        """Callback para geração bem-sucedida"""
        self.progress_frame.grid_remove()
        self.generate_btn.configure(state="normal", text="Gerar README")
        
        if not readme_text:
            self.console.append_step("README", "error", "IA retornou conteúdo vazio")
            messagebox.showwarning("Falha", "A IA não retornou conteúdo.")
            return
        
        self.generated_readme = readme_text
        self.readme_preview.set_content(readme_text)
        self.code_editor.set_content(readme_text)
        self.save_readme_btn.configure(state="normal")
        self.tabview.set("README Gerado")
        self.console.append_step("README", "success", "Gerado com sucesso")

    def _generation_quota_error(self, error: QuotaExceededException):
        """Callback para erro de quota"""
        self.progress_frame.grid_remove()
        self.generate_btn.configure(state="normal", text="Gerar README")
        self.console.append_step("Quota", "error", f"Limite excedido: {error.model_name}")
        
        QuotaExceededDialog(self, error.model_name, self._configure_model)

    def _generation_error(self, error_msg: str):
        """Callback para erro geral"""
        self.progress_frame.grid_remove()
        self.generate_btn.configure(state="normal", text="Gerar README")
        self.console.append_step("Erro", "error", "Falha na geração")
        messagebox.showerror("Erro na Geração", f"Erro ao gerar README:\n\n{error_msg}")

    def _save_readme(self):
        """Salva o README gerado"""
        if not self.generated_readme:
            messagebox.showwarning("Aviso", "Nenhum README foi gerado ainda.")
            return
        
        default_name = "README.md"
        if self.zip_file_path:
            base_name = os.path.splitext(os.path.basename(self.zip_file_path))[0]
            default_name = f"{base_name}_README.md"
        
        file_path = filedialog.asksaveasfilename(
            title="Salvar README",
            defaultextension=".md",
            initialname=default_name,
            filetypes=[("Markdown", "*.md"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.generated_readme)
                messagebox.showinfo("Sucesso", f"README salvo em:\n{file_path}")
                self.console.append_step("Arquivo", "success", f"Salvo: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo:\n{e}")
                self.console.append_step("Arquivo", "error", f"Erro ao salvar: {e}")

    def _copy_readme(self):
        """Copia o README para área de transferência"""
        if not self.generated_readme:
            messagebox.showwarning("Aviso", "Nenhum README foi gerado ainda.")
            return
        
        self.clipboard_clear()
        self.clipboard_append(self.generated_readme)
        messagebox.showinfo("Copiado", "README copiado para a área de transferência!")
        self.console.append_step("Clipboard", "success", "README copiado")

    # Validation and state management
    def _validate_api_key_async(self):
        """Valida API Key em thread separada"""
        if not self.api_key:
            return
        
        thread = threading.Thread(
            target=self._validate_api_key_worker,
            daemon=True
        )
        thread.start()
        self._active_threads.append(thread)

    def _validate_api_key_worker(self):
        """Worker para validar API Key"""
        try:
            genai.configure(api_key=self.api_key)
            
            # Carregar modelos disponíveis
            models_data = list(genai.list_models())
            available_models = []
            
            for model in models_data:
                if hasattr(model, 'name'):
                    model_name = model.name
                    display_name = model_name.replace('models/', '') if model_name.startswith('models/') else model_name
                    if hasattr(model, 'supported_generation_methods'):
                        if 'generateContent' in model.supported_generation_methods:
                            available_models.append(display_name)
                    else:
                        available_models.append(display_name)
            
            if not available_models:
                self.after(0, lambda: self._api_validation_failed("Nenhum modelo disponível"))
                return
            
            # Testar conexão
            test_model = None
            preferred_models = ['gemini-1.5-flash', 'gemini-1.0-pro', 'gemini-1.5-pro']
            for preferred in preferred_models:
                if preferred in available_models:
                    test_model = f'models/{preferred}'
                    break
            
            if not test_model and available_models:
                test_model = f'models/{available_models[0]}'
            
            if test_model:
                model = genai.GenerativeModel(test_model)
                response = model.generate_content(
                    "Test",
                    generation_config=genai.types.GenerationConfig(max_output_tokens=5)
                )
            
            # Sucesso
            self.after(0, lambda: self._api_validation_success(available_models))
            
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                self.after(0, lambda: self._api_validation_quota_error())
            else:
                self.after(0, lambda: self._api_validation_failed(error_msg))

    def _api_validation_success(self, models: list[str]):
        """Callback para validação bem-sucedida"""
        self._api_key_validated = True
        self._models_loaded = True
        self.available_models = models
        
        self.api_status_var.set("IA Pronta")
        self.api_status_label.configure(text_color=theme_manager.get_color("success"))
        self.console.append_step("API Key", "success", "Validada")
        self.console.append_step("Modelos", "success", f"{len(models)} modelos carregados")
        
        # Verificar modelo atual
        if self.model_name not in models and models:
            self.model_name = models[0]
            self.model_var.set(self.model_name)
            self.config_mgr.set_gemini_model(self.model_name)
        
        self._initialize_gemini_client()

    def _api_validation_failed(self, error_msg: str):
        """Callback para falha na validação"""
        self._api_key_validated = False
        self._models_loaded = False
        self.available_models = []
        self.gemini_client = None
        
        self.api_status_var.set("API Key inválida")
        self.api_status_label.configure(text_color=theme_manager.get_color("error"))
        self.console.append_step("API Key", "error", "Validação falhou")
        
        messagebox.showerror(
            "API Key Inválida",
            f"Erro ao validar API Key:\n\n{error_msg}\n\nVerifique:\n• Se a chave está correta\n• Se você tem acesso aos modelos Gemini"
        )
        self._update_generate_button_state()

    def _api_validation_quota_error(self):
        """Callback para erro de quota na validação"""
        self._api_key_validated = False
        self._models_loaded = False
        self.available_models = []
        self.gemini_client = None
        
        self.api_status_var.set("Quota excedida")
        self.api_status_label.configure(text_color=theme_manager.get_color("warning"))
        self.console.append_step("API Key", "warning", "Quota excedida")
        
        QuotaExceededDialog(self, "API", self._configure_api_key)
        self._update_generate_button_state()

    def _initialize_gemini_client(self):
        """Inicializa o cliente Gemini"""
        if not self._api_key_validated or not self.api_key:
            return
        
        try:
            model_name = self.model_name
            if not model_name.startswith('models/'):
                model_name = f'models/{model_name}'
            
            self.gemini_client = GeminiClient(self.api_key, model_name)
            self.console.append_step("Cliente IA", "success", f"Inicializado: {self.model_name}")
            self._update_generate_button_state()
            
        except QuotaExceededException as e:
            self.gemini_client = None
            self.console.append_step("Cliente IA", "error", f"Quota excedida: {e.model_name}")
            QuotaExceededDialog(self, e.model_name, self._configure_model)
            self._update_generate_button_state()
            
        except Exception as e:
            self.gemini_client = None
            self.console.append_step("Cliente IA", "error", "Falha na inicialização")
            messagebox.showerror("Erro na IA", f"Erro ao inicializar cliente:\n{str(e)}")
            self._update_generate_button_state()

    def _can_generate(self) -> bool:
        """Verifica se pode gerar README"""
        return (
            self._api_key_validated and
            self._models_loaded and
            self.gemini_client is not None and
            bool(self.zip_file_path)
        )

    def _update_generate_button_state(self):
        """Atualiza estado do botão de geração"""
        if self._can_generate():
            self.generate_btn.configure(state="normal", text="Gerar README")
        else:
            self.generate_btn.configure(state="disabled", text="Gerar README (Indisponível)")

    def _get_generation_config(self) -> Dict:
        """Obtém configuração para geração"""
        try:
            max_file_size = int(self.max_file_size.get() or "5")
            max_files = int(self.max_files.get() or "30")
        except ValueError:
            max_file_size = 5
            max_files = 30
        
        return {
            "custom_prompt_enabled": self.custom_prompt_enabled.get(),
            "custom_prompt": self.custom_prompt_text.get("1.0", "end-1c"),
            "include_tests": self.include_tests.get(),
            "include_docs": self.include_docs.get(), 
            "include_config": self.include_config.get(),
            "max_file_size_kb": max_file_size,
            "max_files": max_files,
            "readme_style": self.readme_style.get().lower(),
            "include_badges": self.include_badges.get(),
            "include_toc": self.include_toc.get(),
            "include_examples": self.include_examples.get(),
        }

    def _load_initial_config(self):
        """Carrega configuração inicial"""
        saved_api_key = self.config_mgr.get_api_key()
        if saved_api_key:
            self.api_key = saved_api_key
            self.console.append_step("Configuração", "info", "API Key encontrada")
            self._validate_api_key_async()
        else:
            self.console.append_step("Configuração", "info", "Configure uma API Key para começar")

    def _on_closing(self):
        """Cleanup ao fechar aplicação"""
        # Aguardar threads ativas
        for thread in self._active_threads:
            if thread.is_alive():
                thread.join(timeout=1)
        
        if self.gemini_client:
            try:
                self.gemini_client.close()
            except:
                pass
        
        self.destroy()


def main():
    """Função principal"""
    app = ReadmeGeneratorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
    