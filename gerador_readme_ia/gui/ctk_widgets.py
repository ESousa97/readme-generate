# gerador_readme_ia/gui/ctk_widgets.py
"""
Widgets customizados para interface moderna com CustomTkinter
"""
import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import Optional, Callable, List
import customtkinter as ctk
from datetime import datetime
import re

from .ctk_theme_manager import theme_manager


class ModernFrame(ctk.CTkFrame):
    """Frame moderno com estilo Windows 11"""
    
    def __init__(self, parent, **kwargs):
        # Configurações padrão do Windows 11
        defaults = {
            "corner_radius": 8,
            "border_width": 1,
            "fg_color": theme_manager.get_color("surface"),
            "border_color": theme_manager.get_color("border")
        }
        defaults.update(kwargs)
        super().__init__(parent, **defaults)


class ModernButton(ctk.CTkButton):
    """Botão moderno com estilo Windows 11"""
    
    def __init__(self, parent, **kwargs):
        # Configurações padrão do Windows 11
        defaults = {
            "corner_radius": 6,
            "border_width": 1,
            "fg_color": theme_manager.get_color("accent"),
            "hover_color": theme_manager.get_color("accent_hover"),
            "border_color": theme_manager.get_color("accent"),
            "text_color": "white",
            "font": ctk.CTkFont(family=theme_manager.get_font_family(), size=12)
        }
        defaults.update(kwargs)
        super().__init__(parent, **defaults)


class ModernSection(ctk.CTkFrame):
    """Seção com título e conteúdo, estilo Windows 11"""
    
    def __init__(self, parent, title: str, **kwargs):
        # Frame principal
        defaults = {
            "corner_radius": 8,
            "border_width": 1,
            "fg_color": theme_manager.get_color("surface"),
            "border_color": theme_manager.get_color("border")
        }
        defaults.update(kwargs)
        super().__init__(parent, **defaults)
        
        self.grid_columnconfigure(0, weight=1)
        
        # Título da seção
        title_frame = ctk.CTkFrame(self, fg_color="transparent", height=30)
        title_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text=title,
            font=ctk.CTkFont(
                family=theme_manager.get_font_family(),
                size=14,
                weight="bold"
            ),
            text_color=theme_manager.get_color("text_primary")
        )
        title_label.pack(anchor="w")
        
        # Frame do conteúdo
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.grid_rowconfigure(1, weight=1)


class ModernTextWidget(ctk.CTkTextbox):
    """Widget de texto moderno com funcionalidades extras"""
    
    def __init__(self, parent, font_family=None, placeholder_text="", **kwargs):
        # Configurações padrão
        font_family = font_family or theme_manager.get_font_family()
        defaults = {
            "corner_radius": 6,
            "border_width": 2,
            "fg_color": theme_manager.get_color("surface"),
            "border_color": theme_manager.get_color("border"),
            "text_color": theme_manager.get_color("text_primary"),
            "font": ctk.CTkFont(family=font_family, size=11),
            "scrollbar_button_color": theme_manager.get_color("accent"),
            "scrollbar_button_hover_color": theme_manager.get_color("accent_hover"),
        }
        defaults.update(kwargs)
        super().__init__(parent, **defaults)
        
        self.placeholder_text = placeholder_text
        self._setup_placeholder()
    
    def _setup_placeholder(self):
        """Configura placeholder text"""
        if self.placeholder_text:
            self.insert("1.0", self.placeholder_text)
            self.configure(text_color=theme_manager.get_color("text_tertiary"))
            
            def on_focus_in(event):
                if self.get("1.0", "end-1c") == self.placeholder_text:
                    self.delete("1.0", "end")
                    self.configure(text_color=theme_manager.get_color("text_primary"))
            
            def on_focus_out(event):
                if not self.get("1.0", "end-1c").strip():
                    self.insert("1.0", self.placeholder_text)
                    self.configure(text_color=theme_manager.get_color("text_tertiary"))
            
            self.bind("<FocusIn>", on_focus_in)
            self.bind("<FocusOut>", on_focus_out)
    
    def set_content(self, content: str):
        """Define o conteúdo do widget"""
        self.delete("1.0", "end")
        self.insert("1.0", content)
        self.configure(text_color=theme_manager.get_color("text_primary"))
    
    def get_content(self) -> str:
        """Obtém o conteúdo do widget"""
        content = self.get("1.0", "end-1c")
        if content == self.placeholder_text:
            return ""
        return content


class ConsoleWidget(ctk.CTkTextbox):
    """Console de log compacto e moderno"""
    
    def __init__(self, parent, **kwargs):
        defaults = {
            "corner_radius": 6,
            "border_width": 1,
            "fg_color": theme_manager.get_color("bg_secondary"),
            "border_color": theme_manager.get_color("border"),
            "text_color": theme_manager.get_color("text_primary"),
            "font": ctk.CTkFont(
                family=theme_manager.get_mono_font_family(),
                size=10
            ),
            "height": 150,
            "state": "disabled"
        }
        defaults.update(kwargs)
        super().__init__(parent, **defaults)
        
        self.configure(state="disabled")
    
    def append_step(self, step_name: str, status: str = "info", details: str = ""):
        """Adiciona um step ao console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        status_colors = {
            "info": theme_manager.get_color("info"),
            "success": theme_manager.get_color("success"),
            "warning": theme_manager.get_color("warning"),
            "error": theme_manager.get_color("error"),
            "progress": theme_manager.get_color("text_secondary")
        }
        
        status_symbols = {
            "info": "[INFO]",
            "success": "[OK]",
            "warning": "[ATEN]",
            "error": "[ERRO]",
            "progress": "[PROC]"
        }
        
        symbol = status_symbols.get(status, "[INFO]")
        message = f"[{timestamp}] {symbol} {step_name}"
        if details:
            message += f" - {details}"
        
        self.configure(state="normal")
        self.insert("end", message + "\n")
        self.configure(state="disabled")
        self.see("end")
    
    def clear(self):
        """Limpa o console"""
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")


class APIKeyDialog:
    """Diálogo para configuração da API Key"""
    
    def __init__(self, parent, current_key: str = ""):
        self.result = None
        
        # Criar janela modal
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Configurar API Key do Google Gemini")
        self.dialog.geometry("500x300")
        self.dialog.resizable(False, False)
        
        # Centralizar na tela
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Layout principal
        main_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="API Key do Google Gemini",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Instruções
        info_text = """Para usar este aplicativo, você precisa de uma API Key do Google Gemini.

1. Acesse: https://aistudio.google.com/app/apikey
2. Crie uma nova API Key ou use uma existente
3. Cole a chave no campo abaixo"""
        
        info_label = ctk.CTkLabel(
            main_frame,
            text=info_text,
            font=ctk.CTkFont(size=11),
            justify="left",
            text_color=theme_manager.get_color("text_secondary")
        )
        info_label.pack(pady=(0, 20), anchor="w")
        
        # Campo de entrada
        self.key_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Cole sua API Key aqui...",
            width=460,
            height=40,
            show="*"
        )
        self.key_entry.pack(pady=(0, 20))
        
        if current_key:
            self.key_entry.insert(0, current_key)
        
        # Botões
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(pady=(0, 10))
        
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            command=self._cancel,
            width=100,
            fg_color=theme_manager.get_color("text_tertiary"),
            hover_color=theme_manager.get_color("text_secondary")
        )
        cancel_btn.pack(side="left", padx=(0, 10))
        
        ok_btn = ModernButton(
            buttons_frame,
            text="Salvar",
            command=self._ok,
            width=100
        )
        ok_btn.pack(side="left")
        
        # Binds
        self.dialog.bind("<Return>", lambda e: self._ok())
        self.dialog.bind("<Escape>", lambda e: self._cancel())
        self.key_entry.focus()
        
        # Aguardar resultado
        self.dialog.wait_window()
    
    def _ok(self):
        key = self.key_entry.get().strip()
        if key:
            self.result = key
        self.dialog.destroy()
    
    def _cancel(self):
        self.dialog.destroy()


class ModelSelectionDialog:
    """Diálogo para seleção de modelo"""
    
    def __init__(self, parent, models: List[str], current_model: str):
        self.result = None
        
        # Criar janela modal
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Selecionar Modelo Gemini")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # Centralizar
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Layout principal
        main_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="Selecionar Modelo Gemini",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Lista de modelos
        self.model_var = tk.StringVar(value=current_model)
        
        models_frame = ctk.CTkScrollableFrame(main_frame, label_text="Modelos Disponíveis")
        models_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        for model in models:
            radio_btn = ctk.CTkRadioButton(
                models_frame,
                text=model,
                variable=self.model_var,
                value=model
            )
            radio_btn.pack(anchor="w", pady=2)
        
        # Botões
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack()
        
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            command=self._cancel,
            width=100,
            fg_color=theme_manager.get_color("text_tertiary"),
            hover_color=theme_manager.get_color("text_secondary")
        )
        cancel_btn.pack(side="left", padx=(0, 10))
        
        ok_btn = ModernButton(
            buttons_frame,
            text="Selecionar",
            command=self._ok,
            width=100
        )
        ok_btn.pack(side="left")
        
        # Binds
        self.dialog.bind("<Return>", lambda e: self._ok())
        self.dialog.bind("<Escape>", lambda e: self._cancel())
        
        # Aguardar resultado
        self.dialog.wait_window()
    
    def _ok(self):
        self.result = self.model_var.get()
        self.dialog.destroy()
    
    def _cancel(self):
        self.dialog.destroy()


class QuotaExceededDialog:
    """Diálogo especializado para quota excedida"""
    
    def __init__(self, parent, model_name: str, change_model_callback: Callable):
        # Criar janela modal
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Quota da API Excedida")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # Centralizar
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Layout principal
        main_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Ícone de aviso
        warning_label = ctk.CTkLabel(
            main_frame,
            text="⚠️",
            font=ctk.CTkFont(size=32)
        )
        warning_label.pack(pady=(0, 15))
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="Quota da API Excedida",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=theme_manager.get_color("warning")
        )
        title_label.pack(pady=(0, 15))
        
        # Descrição do problema
        problem_text = f"A quota do modelo '{model_name}' foi excedida."
        problem_label = ctk.CTkLabel(
            main_frame,
            text=problem_text,
            font=ctk.CTkFont(size=12),
            text_color=theme_manager.get_color("text_primary")
        )
        problem_label.pack(pady=(0, 20))
        
        # Soluções
        solutions_frame = ctk.CTkScrollableFrame(main_frame, label_text="Soluções Possíveis")
        solutions_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        solutions = [
            "• Experimente outro modelo (gemini-1.0-pro, gemini-1.5-flash)",
            "• Aguarde a renovação da quota (geralmente mensal)",
            "• Verifique seus limites no Google AI Studio",
            "• Considere upgrade para plano pago se disponível",
            "• Use o modelo com moderação para conservar quota"
        ]
        
        for solution in solutions:
            solution_label = ctk.CTkLabel(
                solutions_frame,
                text=solution,
                font=ctk.CTkFont(size=11),
                text_color=theme_manager.get_color("text_secondary"),
                anchor="w",
                justify="left"
            )
            solution_label.pack(fill="x", pady=2, padx=10)
        
        # Links úteis
        links_label = ctk.CTkLabel(
            main_frame,
            text="Links úteis:\n• Google AI Studio: https://aistudio.google.com\n• Documentação: https://ai.google.dev/pricing",
            font=ctk.CTkFont(size=10),
            text_color=theme_manager.get_color("accent"),
            justify="left"
        )
        links_label.pack(pady=(0, 15))
        
        # Botões de ação
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack()
        
        change_btn = ModernButton(
            buttons_frame,
            text="Trocar Modelo",
            command=lambda: self._change_model(change_model_callback),
            width=120
        )
        change_btn.pack(side="left", padx=(0, 10))
        
        ok_btn = ctk.CTkButton(
            buttons_frame,
            text="Entendi",
            command=self._close,
            width=100,
            fg_color=theme_manager.get_color("text_tertiary"),
            hover_color=theme_manager.get_color("text_secondary")
        )
        ok_btn.pack(side="left")
        
        # Aguardar fechamento
        self.dialog.wait_window()
    
    def _change_model(self, callback):
        self.dialog.destroy()
        callback()
    
    def _close(self):
        self.dialog.destroy()


class ProgressDialog:
    """Diálogo de progresso para operações longas"""
    
    def __init__(self, parent, title: str = "Processando..."):
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        
        # Centralizar
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Remover botão de fechar
        self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Layout
        main_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Label de status
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Iniciando...",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=(0, 15))
        
        # Barra de progresso
        self.progress_bar = ctk.CTkProgressBar(main_frame, width=360)
        self.progress_bar.pack(pady=(0, 10))
        self.progress_bar.set(0)
        
        # Label de porcentagem
        self.percent_label = ctk.CTkLabel(
            main_frame,
            text="0%",
            font=ctk.CTkFont(size=10),
            text_color=theme_manager.get_color("text_secondary")
        )
        self.percent_label.pack()
    
    def update_progress(self, message: str, value: int):
        """Atualiza o progresso"""
        self.status_label.configure(text=message)
        self.progress_bar.set(value / 100)
        self.percent_label.configure(text=f"{value}%")
        self.dialog.update_idletasks()
    
    def close(self):
        """Fecha o diálogo"""
        self.dialog.destroy()


class InfoCard(ctk.CTkFrame):
    """Card informativo estilo Windows 11"""
    
    def __init__(self, parent, title: str, value: str, icon: str = "", color: str = None, **kwargs):
        # Configurações padrão
        defaults = {
            "corner_radius": 8,
            "border_width": 1,
            "fg_color": theme_manager.get_color("surface"),
            "border_color": theme_manager.get_color("border"),
            "height": 80
        }
        defaults.update(kwargs)
        super().__init__(parent, **defaults)
        
        # Layout interno
        self.grid_columnconfigure(1, weight=1)
        
        # Ícone (se fornecido)
        if icon:
            icon_label = ctk.CTkLabel(
                self,
                text=icon,
                font=ctk.CTkFont(size=24),
                text_color=color or theme_manager.get_color("accent")
            )
            icon_label.grid(row=0, column=0, rowspan=2, padx=15, pady=15, sticky="w")
        
        # Título
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=theme_manager.get_color("text_secondary"),
            anchor="w"
        )
        title_label.grid(row=0, column=1, sticky="ew", padx=(0 if icon else 15, 15), pady=(15, 0))
        
        # Valor
        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=color or theme_manager.get_color("text_primary"),
            anchor="w"
        )
        self.value_label.grid(row=1, column=1, sticky="ew", padx=(0 if icon else 15, 15), pady=(0, 15))
    
    def update_value(self, new_value: str, color: str = None):
        """Atualiza o valor do card"""
        self.value_label.configure(
            text=new_value,
            text_color=color or theme_manager.get_color("text_primary")
        )
        