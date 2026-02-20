# gerador_readme_ia/gui/ctk_theme_manager.py
"""
Theme Manager para CustomTkinter com estilo Windows 11
"""

import logging

import customtkinter as ctk
import darkdetect

logger = logging.getLogger(__name__)

# Paleta de cores Windows 11
WINDOWS_11_COLORS = {
    "light": {
        # Cores principais
        "bg_primary": "#FAFAFA",           # Fundo principal
        "bg_secondary": "#F3F3F3",         # Fundo secundário  
        "bg_tertiary": "#FFFFFF",          # Cards/painéis
        "surface": "#FFFFFF",              # Superfícies
        "surface_variant": "#F9F9F9",      # Variações de superfície
        
        # Textos
        "text_primary": "#1C1C1C",         # Texto principal
        "text_secondary": "#616161",       # Texto secundário
        "text_tertiary": "#757575",        # Texto terciário
        "text_disabled": "#BDBDBD",        # Texto desabilitado
        
        # Cores de sistema
        "accent": "#005FB8",               # Azul do Windows 11
        "accent_hover": "#106EBE",         # Hover do accent
        "accent_pressed": "#004578",       # Pressed do accent
        "accent_light": "#E3F2FD",         # Accent claro
        
        # Estados
        "success": "#107C10",              # Verde sucesso
        "warning": "#FF8C00",              # Laranja aviso
        "error": "#D13438",                # Vermelho erro
        "info": "#0078D4",                 # Azul informação
        
        # Bordas e divisores
        "border": "#E5E5E5",               # Bordas padrão
        "border_focus": "#005FB8",         # Bordas em foco
        "divider": "#EDEDED",              # Divisores
        
        # Sombras e elevação
        "shadow": "rgba(0,0,0,0.05)",      # Sombra sutil
        "shadow_strong": "rgba(0,0,0,0.1)", # Sombra forte
        
        # Hover e interação
        "hover": "#F5F5F5",                # Hover genérico
        "pressed": "#EBEBEB",              # Estado pressionado
        "selected": "#E3F2FD",             # Selecionado
        "focus": "#CCE7FF",                # Em foco
    },
    
    "dark": {
        # Cores principais
        "bg_primary": "#202020",           # Fundo principal
        "bg_secondary": "#2C2C2C",         # Fundo secundário
        "bg_tertiary": "#2B2B2B",          # Cards/painéis
        "surface": "#2B2B2B",              # Superfícies
        "surface_variant": "#323232",      # Variações de superfície
        
        # Textos
        "text_primary": "#FFFFFF",         # Texto principal
        "text_secondary": "#E0E0E0",       # Texto secundário
        "text_tertiary": "#BDBDBD",        # Texto terciário
        "text_disabled": "#6D6D6D",        # Texto desabilitado
        
        # Cores de sistema
        "accent": "#60CDFF",               # Azul claro do Windows 11 dark
        "accent_hover": "#4CC2FF",         # Hover do accent
        "accent_pressed": "#0078D4",       # Pressed do accent
        "accent_light": "#1A365D",         # Accent escuro
        
        # Estados
        "success": "#6CCB5F",              # Verde sucesso
        "warning": "#FFB347",              # Laranja aviso
        "error": "#FF6B6B",                # Vermelho erro
        "info": "#60CDFF",                 # Azul informação
        
        # Bordas e divisores
        "border": "#404040",               # Bordas padrão
        "border_focus": "#60CDFF",         # Bordas em foco
        "divider": "#383838",              # Divisores
        
        # Sombras e elevação
        "shadow": "rgba(0,0,0,0.2)",       # Sombra sutil
        "shadow_strong": "rgba(0,0,0,0.4)", # Sombra forte
        
        # Hover e interação
        "hover": "#3C3C3C",                # Hover genérico
        "pressed": "#4A4A4A",              # Estado pressionado
        "selected": "#1A365D",             # Selecionado
        "focus": "#2D5A87",                # Em foco
    }
}

class Windows11ThemeManager:
    """Gerenciador de temas estilo Windows 11 para CustomTkinter"""
    
    def __init__(self):
        self.current_theme = self._detect_system_theme()
        self.colors = WINDOWS_11_COLORS[self.current_theme]
        self._setup_customtkinter_theme()
    
    def _detect_system_theme(self) -> str:
        """Detecta o tema do sistema"""
        try:
            return "dark" if darkdetect.isDark() else "light"
        except Exception:
            return "light"
    
    def _setup_customtkinter_theme(self):
        """Configura o tema global do CustomTkinter"""
        ctk.set_appearance_mode(self.current_theme)
        
        # Tema customizado baseado no Windows 11
        custom_theme = {
            "CTk": {
                "fg_color": [self.colors["bg_primary"], self.colors["bg_primary"]]
            },
            "CTkToplevel": {
                "fg_color": [self.colors["bg_primary"], self.colors["bg_primary"]]
            },
            "CTkFrame": {
                "corner_radius": 8,
                "border_width": 1,
                "fg_color": [self.colors["surface"], self.colors["surface"]],
                "border_color": [self.colors["border"], self.colors["border"]]
            },
            "CTkButton": {
                "corner_radius": 6,
                "border_width": 1,
                "fg_color": [self.colors["accent"], self.colors["accent"]],
                "hover_color": [self.colors["accent_hover"], self.colors["accent_hover"]],
                "border_color": [self.colors["accent"], self.colors["accent"]],
                "text_color": ["white", "white"],
                "text_color_disabled": [self.colors["text_disabled"], self.colors["text_disabled"]]
            },
            "CTkLabel": {
                "corner_radius": 0,
                "fg_color": "transparent",
                "text_color": [self.colors["text_primary"], self.colors["text_primary"]]
            },
            "CTkEntry": {
                "corner_radius": 6,
                "border_width": 2,
                "fg_color": [self.colors["surface"], self.colors["surface"]],
                "border_color": [self.colors["border"], self.colors["border"]],
                "text_color": [self.colors["text_primary"], self.colors["text_primary"]],
                "placeholder_text_color": [self.colors["text_tertiary"], self.colors["text_tertiary"]]
            },
            "CTkTextbox": {
                "corner_radius": 6,
                "border_width": 2,
                "fg_color": [self.colors["surface"], self.colors["surface"]],
                "border_color": [self.colors["border"], self.colors["border"]],
                "text_color": [self.colors["text_primary"], self.colors["text_primary"]],
                "scrollbar_button_color": [self.colors["accent"], self.colors["accent"]],
                "scrollbar_button_hover_color": [self.colors["accent_hover"], self.colors["accent_hover"]]
            },
            "CTkScrollbar": {
                "corner_radius": 4,
                "border_spacing": 4,
                "fg_color": "transparent",
                "button_color": [self.colors["text_tertiary"], self.colors["text_tertiary"]],
                "button_hover_color": [self.colors["accent"], self.colors["accent"]]
            },
            "CTkCheckBox": {
                "corner_radius": 4,
                "border_width": 2,
                "fg_color": [self.colors["accent"], self.colors["accent"]],
                "border_color": [self.colors["border"], self.colors["border"]],
                "hover_color": [self.colors["accent_hover"], self.colors["accent_hover"]],
                "checkmark_color": ["white", "white"],
                "text_color": [self.colors["text_primary"], self.colors["text_primary"]],
                "text_color_disabled": [self.colors["text_disabled"], self.colors["text_disabled"]]
            },
            "CTkSwitch": {
                "corner_radius": 12,
                "border_width": 2,
                "button_length": 0,
                "fg_color": [self.colors["border"], self.colors["border"]],
                "progress_color": [self.colors["accent"], self.colors["accent"]],
                "button_color": ["white", "white"],
                "button_hover_color": [self.colors["hover"], self.colors["hover"]],
                "text_color": [self.colors["text_primary"], self.colors["text_primary"]],
                "text_color_disabled": [self.colors["text_disabled"], self.colors["text_disabled"]]
            },
            "CTkRadioButton": {
                "corner_radius": 10,
                "border_width_checked": 6,
                "border_width_unchecked": 3,
                "fg_color": [self.colors["accent"], self.colors["accent"]],
                "border_color": [self.colors["border"], self.colors["border"]],
                "hover_color": [self.colors["accent_hover"], self.colors["accent_hover"]],
                "text_color": [self.colors["text_primary"], self.colors["text_primary"]],
                "text_color_disabled": [self.colors["text_disabled"], self.colors["text_disabled"]]
            },
            "CTkProgressBar": {
                "corner_radius": 4,
                "border_width": 0,
                "fg_color": [self.colors["border"], self.colors["border"]],
                "progress_color": [self.colors["accent"], self.colors["accent"]]
            },
            "CTkSlider": {
                "corner_radius": 4,
                "button_corner_radius": 10,
                "border_width": 1,
                "button_length": 20,
                "fg_color": [self.colors["border"], self.colors["border"]],
                "progress_color": [self.colors["accent"], self.colors["accent"]],
                "button_color": [self.colors["accent"], self.colors["accent"]],
                "button_hover_color": [self.colors["accent_hover"], self.colors["accent_hover"]]
            },
            "CTkOptionMenu": {
                "corner_radius": 6,
                "fg_color": [self.colors["surface"], self.colors["surface"]],
                "button_color": [self.colors["accent"], self.colors["accent"]],
                "button_hover_color": [self.colors["accent_hover"], self.colors["accent_hover"]],
                "text_color": [self.colors["text_primary"], self.colors["text_primary"]],
                "text_color_disabled": [self.colors["text_disabled"], self.colors["text_disabled"]]
            },
            "CTkComboBox": {
                "corner_radius": 6,
                "border_width": 2,
                "fg_color": [self.colors["surface"], self.colors["surface"]],
                "border_color": [self.colors["border"], self.colors["border"]],
                "button_color": [self.colors["accent"], self.colors["accent"]],
                "button_hover_color": [self.colors["accent_hover"], self.colors["accent_hover"]],
                "text_color": [self.colors["text_primary"], self.colors["text_primary"]],
                "text_color_disabled": [self.colors["text_disabled"], self.colors["text_disabled"]]
            },
            "CTkScrollableFrame": {
                "corner_radius": 8,
                "border_width": 1,
                "fg_color": [self.colors["surface"], self.colors["surface"]],
                "border_color": [self.colors["border"], self.colors["border"]]
            },
            "CTkSegmentedButton": {
                "corner_radius": 6,
                "border_width": 2,
                "fg_color": [self.colors["surface"], self.colors["surface"]],
                "selected_color": [self.colors["accent"], self.colors["accent"]],
                "selected_hover_color": [self.colors["accent_hover"], self.colors["accent_hover"]],
                "unselected_color": [self.colors["surface"], self.colors["surface"]],
                "unselected_hover_color": [self.colors["hover"], self.colors["hover"]],
                "text_color": [self.colors["text_primary"], self.colors["text_primary"]],
                "text_color_disabled": [self.colors["text_disabled"], self.colors["text_disabled"]]
            },
            "CTkTabview": {
                "corner_radius": 8,
                "border_width": 1,
                "fg_color": [self.colors["surface"], self.colors["surface"]],
                "border_color": [self.colors["border"], self.colors["border"]],
                "segmented_button_fg_color": [self.colors["bg_secondary"], self.colors["bg_secondary"]],
                "segmented_button_selected_color": [self.colors["accent"], self.colors["accent"]],
                "segmented_button_selected_hover_color": [self.colors["accent_hover"], self.colors["accent_hover"]],
                "segmented_button_unselected_color": [self.colors["bg_secondary"], self.colors["bg_secondary"]],
                "segmented_button_unselected_hover_color": [self.colors["hover"], self.colors["hover"]],
                "text_color": [self.colors["text_primary"], self.colors["text_primary"]],
                "text_color_disabled": [self.colors["text_disabled"], self.colors["text_disabled"]]
            }
        }
        
        _ = custom_theme

        # Aplicar o tema customizado
        try:
            ctk.deactivate_automatic_dpi_awareness()
        except Exception:
            logger.debug("Falha ao desativar DPI awareness automático.", exc_info=True)
    
    def switch_theme(self, theme_name: str = None):
        """Alterna entre temas"""
        if theme_name is None:
            self.current_theme = "dark" if self.current_theme == "light" else "light"
        else:
            self.current_theme = theme_name
        
        self.colors = WINDOWS_11_COLORS[self.current_theme]
        ctk.set_appearance_mode(self.current_theme)
        self._setup_customtkinter_theme()
    
    def get_color(self, color_key: str) -> str:
        """Obtém uma cor do tema atual"""
        return self.colors.get(color_key, "#000000")
    
    def get_font_family(self) -> str:
        """Retorna a fonte padrão do Windows 11"""
        return "Segoe UI"
    
    def get_mono_font_family(self) -> str:
        """Retorna a fonte monospace do Windows 11"""
        return "Consolas"

# Instância global do gerenciador de temas
theme_manager = Windows11ThemeManager()
