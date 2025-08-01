import os

# Definições de fontes e tamanhos usados no app, adaptados para Windows e outros sistemas
FONT_FAMILY_DEFAULT = "Inter" if os.name == 'nt' else "SF Pro Display"
FONT_FAMILY_MONO = "JetBrains Mono" if os.name == 'nt' else "Monaco"

FONT_SIZE_DEFAULT = 10 if os.name == 'nt' else 12
FONT_SIZE_SMALL = FONT_SIZE_DEFAULT - 1
FONT_SIZE_LARGE = FONT_SIZE_DEFAULT + 2


class ModernTheme:
    def __init__(self, name, colors):
        self.name = name
        self.bg_primary = colors['bg_primary']
        self.bg_secondary = colors['bg_secondary'] 
        self.bg_tertiary = colors['bg_tertiary']
        self.surface = colors['surface']
        self.surface_variant = colors['surface_variant']
        self.text_primary = colors['text_primary']
        self.text_secondary = colors['text_secondary']
        self.text_accent = colors['text_accent']
        self.accent = colors['accent']
        self.accent_variant = colors['accent_variant']
        self.success = colors['success']
        self.warning = colors['warning']
        self.error = colors['error']
        self.border = colors['border']
        self.shadow = colors['shadow']


THEMES = {
    "light": ModernTheme("light", {
        'bg_primary': '#FAFAFA',
        'bg_secondary': '#FFFFFF',
        'bg_tertiary': '#F5F5F7',
        'surface': '#FFFFFF',
        'surface_variant': '#F8F9FA',
        'text_primary': '#1D1D1F',
        'text_secondary': '#6E6E73',
        'text_accent': '#007AFF',
        'accent': '#007AFF',
        'accent_variant': '#0066CC',
        'success': '#34C759',
        'warning': '#FF9500',
        'error': '#FF3B30',
        'border': '#E5E5E7',
        'shadow': 'rgba(0,0,0,0.1)'
    }),
    "dark": ModernTheme("dark", {
        'bg_primary': '#0D1117',
        'bg_secondary': '#161B22',
        'bg_tertiary': '#21262D',
        'surface': '#21262D',
        'surface_variant': '#30363D',
        'text_primary': '#F0F6FC',
        'text_secondary': '#8B949E',
        'text_accent': '#58A6FF',
        'accent': '#58A6FF',
        'accent_variant': '#4184E4',
        'success': '#3FB950',
        'warning': '#D29922',
        'error': '#F85149',
        'border': '#30363D',
        'shadow': 'rgba(0,0,0,0.3)'
    })
}
