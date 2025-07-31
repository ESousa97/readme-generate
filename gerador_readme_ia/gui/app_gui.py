# gerador_readme_ia/gui/app_gui.py

import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
import traceback
import zipfile
import tempfile
import base64
import re

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QStatusBar, QMenuBar, QMenu, QAction,
    QFileDialog, QMessageBox, QInputDialog, QFrame, QProgressBar,
    QSplitter, QTabWidget, QGroupBox, QGridLayout,
    QPlainTextEdit, QCheckBox, QSlider, QSpinBox, QComboBox, QToolBar,
    QScrollArea, QTextBrowser
)
from PyQt5.QtGui import (
    QFont, QPalette, QColor, QIcon, QKeySequence, QDesktopServices,
    QPixmap, QPainter, QLinearGradient, QBrush, QPen,
    QFontMetrics, QSyntaxHighlighter, QTextCharFormat, QTextDocument,
    QTextCursor, QClipboard
)
from PyQt5.QtCore import (
    Qt, pyqtSignal, QObject, QThread, QTimer, pyqtSlot, QUrl, 
    QLocale, QTranslator, QLibraryInfo, QPropertyAnimation, 
    QEasingCurve, QSize, QMimeData
)

try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    from PyQt5.QtWebChannel import QWebChannel
    WEB_ENGINE_AVAILABLE = True
except ImportError:
    WEB_ENGINE_AVAILABLE = False

import qtawesome
import darkdetect

try:
    import markdown
    from markdown.extensions import codehilite, fenced_code, tables, toc
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

from ..config_manager import ConfigManager
from ..ia_client.gemini_client import GeminiClient
from ..logger_setup import setup_logging
from ..constants import (
    DEFAULT_GEMINI_MODEL, PROMPT_README_GENERATION,
    APP_NAME, APP_AUTHOR, APP_VERSION
)

logger = setup_logging(f"{APP_NAME}.gui", app_author=APP_AUTHOR, debug=True)

APP_DISPLAY_NAME = "Gerador de README.md Inteligente"

# Definição das fontes usadas no app, diferenciando Windows e outros sistemas
FONT_FAMILY_DEFAULT = "Inter" if os.name == 'nt' else "SF Pro Display"
FONT_FAMILY_MONO = "JetBrains Mono" if os.name == 'nt' else "Monaco"
FONT_SIZE_DEFAULT = 10 if os.name == 'nt' else 12
FONT_SIZE_SMALL = FONT_SIZE_DEFAULT - 1
FONT_SIZE_LARGE = FONT_SIZE_DEFAULT + 2


# Classe para renderização de Markdown igual ao GitHub
class MarkdownRenderer:
    def __init__(self, theme):
        self.theme = theme
        self.setup_extensions()
        
    def setup_extensions(self):
        if MARKDOWN_AVAILABLE:
            self.md = markdown.Markdown(
                extensions=[
                    'fenced_code',
                    'tables',
                    'toc',
                    'codehilite',
                    'nl2br',
                    'sane_lists'
                ],
                extension_configs={
                    'codehilite': {
                        'css_class': 'highlight',
                        'use_pygments': False,
                        'noclasses': True
                    }
                }
            )
        else:
            self.md = None
    
    def render_to_html(self, markdown_text):
        if not MARKDOWN_AVAILABLE or not self.md:
            return self._fallback_render(markdown_text)
        
        try:
            html_content = self.md.convert(markdown_text)
            return self._wrap_with_github_style(html_content)
        except Exception as e:
            logger.error(f"Erro ao renderizar markdown: {e}")
            return self._fallback_render(markdown_text)
    
    def _fallback_render(self, text):
        # Renderização básica para quando markdown não está disponível
        html = text.replace('\n', '<br>')
        html = re.sub(r'# (.*)', r'<h1>\1</h1>', html)
        html = re.sub(r'## (.*)', r'<h2>\1</h2>', html)
        html = re.sub(r'### (.*)', r'<h3>\1</h3>', html)
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
        return self._wrap_with_github_style(html)
    
    def _wrap_with_github_style(self, content):
        github_css = self._get_github_css()
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                {github_css}
            </style>
        </head>
        <body>
            <div class="markdown-body">
                {content}
            </div>
        </body>
        </html>
        """
    
    def _get_github_css(self):
        # CSS baseado no GitHub para renderização fiel
        if self.theme.name == "dark":
            return """
                body {
                    margin: 0;
                    padding: 16px;
                    background-color: #0d1117;
                    color: #c9d1d9;
                    font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
                    font-size: 16px;
                    line-height: 1.5;
                }
                .markdown-body {
                    max-width: none;
                    background-color: #0d1117;
                    color: #c9d1d9;
                }
                .markdown-body h1, .markdown-body h2 {
                    border-bottom: 1px solid #21262d;
                    padding-bottom: 0.3em;
                }
                .markdown-body h1 {
                    font-size: 2em;
                    font-weight: 600;
                    margin-bottom: 16px;
                    color: #f0f6fc;
                }
                .markdown-body h2 {
                    font-size: 1.5em;
                    font-weight: 600;
                    margin-bottom: 16px;
                    color: #f0f6fc;
                }
                .markdown-body h3 {
                    font-size: 1.25em;
                    font-weight: 600;
                    margin-bottom: 16px;
                    color: #f0f6fc;
                }
                .markdown-body p {
                    margin-bottom: 16px;
                }
                .markdown-body code {
                    background-color: rgba(110,118,129,0.4);
                    border-radius: 6px;
                    font-size: 85%;
                    margin: 0;
                    padding: 0.2em 0.4em;
                    font-family: ui-monospace,SFMono-Regular,"SF Mono",Consolas,"Liberation Mono",Menlo,monospace;
                }
                .markdown-body pre {
                    background-color: #161b22;
                    border-radius: 6px;
                    font-size: 85%;
                    line-height: 1.45;
                    overflow: auto;
                    padding: 16px;
                    margin-bottom: 16px;
                }
                .markdown-body pre code {
                    background-color: transparent;
                    border: 0;
                    display: inline;
                    line-height: inherit;
                    margin: 0;
                    overflow: visible;
                    padding: 0;
                    word-wrap: normal;
                }
                .markdown-body blockquote {
                    border-left: 0.25em solid #30363d;
                    color: #8b949e;
                    margin: 0 0 16px 0;
                    padding: 0 1em;
                }
                .markdown-body table {
                    border-collapse: collapse;
                    border-spacing: 0;
                    display: block;
                    margin-bottom: 16px;
                    overflow: auto;
                    width: max-content;
                    max-width: 100%;
                }
                .markdown-body table th {
                    background-color: #161b22;
                    border: 1px solid #30363d;
                    font-weight: 600;
                    padding: 6px 13px;
                }
                .markdown-body table td {
                    border: 1px solid #30363d;
                    padding: 6px 13px;
                }
                .markdown-body ul, .markdown-body ol {
                    margin-bottom: 16px;
                    padding-left: 2em;
                }
                .markdown-body li {
                    margin-bottom: 0.25em;
                }
                .markdown-body a {
                    color: #58a6ff;
                    text-decoration: none;
                }
                .markdown-body a:hover {
                    text-decoration: underline;
                }
                .markdown-body hr {
                    background-color: #21262d;
                    border: 0;
                    height: 0.25em;
                    margin: 24px 0;
                    padding: 0;
                }
            """
        else:
            return """
                body {
                    margin: 0;
                    padding: 16px;
                    background-color: #ffffff;
                    color: #24292f;
                    font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
                    font-size: 16px;
                    line-height: 1.5;
                }
                .markdown-body {
                    max-width: none;
                    background-color: #ffffff;
                    color: #24292f;
                }
                .markdown-body h1, .markdown-body h2 {
                    border-bottom: 1px solid #d0d7de;
                    padding-bottom: 0.3em;
                }
                .markdown-body h1 {
                    font-size: 2em;
                    font-weight: 600;
                    margin-bottom: 16px;
                    color: #24292f;
                }
                .markdown-body h2 {
                    font-size: 1.5em;
                    font-weight: 600;
                    margin-bottom: 16px;
                    color: #24292f;
                }
                .markdown-body h3 {
                    font-size: 1.25em;
                    font-weight: 600;
                    margin-bottom: 16px;
                    color: #24292f;
                }
                .markdown-body p {
                    margin-bottom: 16px;
                }
                .markdown-body code {
                    background-color: rgba(175,184,193,0.2);
                    border-radius: 6px;
                    font-size: 85%;
                    margin: 0;
                    padding: 0.2em 0.4em;
                    font-family: ui-monospace,SFMono-Regular,"SF Mono",Consolas,"Liberation Mono",Menlo,monospace;
                }
                .markdown-body pre {
                    background-color: #f6f8fa;
                    border-radius: 6px;
                    font-size: 85%;
                    line-height: 1.45;
                    overflow: auto;
                    padding: 16px;
                    margin-bottom: 16px;
                }
                .markdown-body pre code {
                    background-color: transparent;
                    border: 0;
                    display: inline;
                    line-height: inherit;
                    margin: 0;
                    overflow: visible;
                    padding: 0;
                    word-wrap: normal;
                }
                .markdown-body blockquote {
                    border-left: 0.25em solid #d0d7de;
                    color: #656d76;
                    margin: 0 0 16px 0;
                    padding: 0 1em;
                }
                .markdown-body table {
                    border-collapse: collapse;
                    border-spacing: 0;
                    display: block;
                    margin-bottom: 16px;
                    overflow: auto;
                    width: max-content;
                    max-width: 100%;
                }
                .markdown-body table th {
                    background-color: #f6f8fa;
                    border: 1px solid #d0d7de;
                    font-weight: 600;
                    padding: 6px 13px;
                }
                .markdown-body table td {
                    border: 1px solid #d0d7de;
                    padding: 6px 13px;
                }
                .markdown-body ul, .markdown-body ol {
                    margin-bottom: 16px;
                    padding-left: 2em;
                }
                .markdown-body li {
                    margin-bottom: 0.25em;
                }
                .markdown-body a {
                    color: #0969da;
                    text-decoration: none;
                }
                .markdown-body a:hover {
                    text-decoration: underline;
                }
                .markdown-body hr {
                    background-color: #d0d7de;
                    border: 0;
                    height: 0.25em;
                    margin: 24px 0;
                    padding: 0;
                }
            """


# Widget para preview do README com renderização GitHub-style
class ReadmePreviewWidget(QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.markdown_renderer = MarkdownRenderer(theme)
        self.raw_markdown = ""
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar com controles
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # Toggle para modo de visualização
        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems(["Visualização", "Código", "Lado a Lado"])
        self.view_mode_combo.currentTextChanged.connect(self.change_view_mode)
        
        toolbar.addWidget(QLabel("Modo:"))
        toolbar.addWidget(self.view_mode_combo)
        toolbar.addSeparator()
        
        # Botões de ação
        self.copy_raw_btn = QPushButton("Copiar Markdown")
        self.copy_raw_btn.clicked.connect(self.copy_raw_markdown)
        self.copy_raw_btn.setEnabled(False)
        
        self.copy_html_btn = QPushButton("Copiar HTML")
        self.copy_html_btn.clicked.connect(self.copy_html)
        self.copy_html_btn.setEnabled(False)
        
        toolbar.addWidget(self.copy_raw_btn)
        toolbar.addWidget(self.copy_html_btn)
        
        layout.addWidget(toolbar)
        
        # Container principal com splitter
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Visualizador renderizado
        if WEB_ENGINE_AVAILABLE:
            self.web_view = QWebEngineView()
            self.web_view.setContextMenuPolicy(Qt.CustomContextMenu)
        else:
            # Fallback para QTextBrowser se WebEngine não disponível
            self.web_view = QTextBrowser()
            self.web_view.setOpenExternalLinks(True)
            
        # Editor de código raw
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont(FONT_FAMILY_MONO, FONT_SIZE_DEFAULT))
        self.code_editor.setReadOnly(True)
        self.code_editor.setPlaceholderText("O markdown aparecerá aqui...")
        
        # Aplica syntax highlighting
        self.markdown_highlighter = MarkdownHighlighter(self.code_editor.document(), self.theme)
        
        self.splitter.addWidget(self.web_view)
        self.splitter.addWidget(self.code_editor)
        self.splitter.setSizes([1, 0])  # Inicialmente só mostra preview
        
        layout.addWidget(self.splitter, 1)
        
    def set_markdown_content(self, markdown_text):
        self.raw_markdown = markdown_text
        self.code_editor.setPlainText(markdown_text)
        
        # Renderiza HTML
        html_content = self.markdown_renderer.render_to_html(markdown_text)
        
        if WEB_ENGINE_AVAILABLE:
            self.web_view.setHtml(html_content)
        else:
            self.web_view.setHtml(html_content)
            
        # Habilita botões
        self.copy_raw_btn.setEnabled(bool(markdown_text))
        self.copy_html_btn.setEnabled(bool(markdown_text))
        
    def change_view_mode(self, mode):
        if mode == "Visualização":
            self.splitter.setSizes([1, 0])
        elif mode == "Código":
            self.splitter.setSizes([0, 1])
        elif mode == "Lado a Lado":
            self.splitter.setSizes([1, 1])
            
    def copy_raw_markdown(self):
        if self.raw_markdown:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.raw_markdown)
            
    def copy_html(self):
        if self.raw_markdown:
            html = self.markdown_renderer.render_to_html(self.raw_markdown)
            clipboard = QApplication.clipboard()
            mime_data = QMimeData()
            mime_data.setHtml(html)
            mime_data.setText(self.raw_markdown)  # Fallback texto
            clipboard.setMimeData(mime_data)


# Classe para definir temas modernos de cores
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


# Definição dos temas claro e escuro com cores específicas
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


# Classe para realce de sintaxe Markdown no editor de texto
class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent, theme):
        super().__init__(parent)
        self.theme = theme
        self._setup_highlighting_rules()

    def _setup_highlighting_rules(self):
        self.highlighting_rules = []
        
        # Regra para cabeçalhos (# ...), usa cor de destaque do tema
        header_format = QTextCharFormat()
        header_format.setForeground(QColor(self.theme.accent))
        header_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((r'^#{1,6}\s.*', header_format))
        
        # Negrito (**texto**)
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((r'\*\*.*?\*\*', bold_format))
        
        # Itálico (*texto*)
        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        self.highlighting_rules.append((r'\*.*?\*', italic_format))
        
        # Blocos de código (``` ... ``` e `...`)
        code_format = QTextCharFormat()
        code_format.setBackground(QColor(self.theme.surface_variant))
        code_format.setForeground(QColor(self.theme.text_accent))
        code_format.setFontFamily(FONT_FAMILY_MONO)
        self.highlighting_rules.append((r'```.*?```', code_format))
        self.highlighting_rules.append((r'`.*?`', code_format))

    def highlightBlock(self, text):
        import re
        for pattern, format_obj in self.highlighting_rules:
            for match in re.finditer(pattern, text, re.MULTILINE):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format_obj)


# Botão com animação simples (ex: efeito hover com animação da geometria)
class AnimatedButton(QPushButton):
    def __init__(self, text, icon=None, parent=None):
        super().__init__(text, parent)
        if icon:
            self.setIcon(icon)
        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        
        # Configuração da animação para hover (pode ser expandida futuramente)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)


# Componente visual que mostra o progresso em passos numerados com círculos e linhas
class StepIndicator(QWidget):
    def __init__(self, steps, parent=None):
        super().__init__(parent)
        self.steps = steps
        self.current_step = 0
        self.setFixedHeight(60)
        self.setMinimumWidth(400)
        
    def set_current_step(self, step):
        self.current_step = step
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Definições básicas para o desenho dos passos
        step_size = 30
        step_spacing = (self.width() - len(self.steps) * step_size) // (len(self.steps) - 1) if len(self.steps) > 1 else 0
        y_center = self.height() // 2
        
        for i, step in enumerate(self.steps):
            x = i * (step_size + step_spacing) + step_size // 2
            
            # Desenha a linha conectando o passo atual ao próximo
            if i < len(self.steps) - 1:
                next_x = (i + 1) * (step_size + step_spacing) + step_size // 2
                if i < self.current_step:
                    painter.setPen(QPen(QColor("#007AFF"), 3))  # Linha azul para passos concluídos
                else:
                    painter.setPen(QPen(QColor("#E5E5E7"), 2))  # Linha cinza para passos futuros
                painter.drawLine(x + step_size//2, y_center, next_x - step_size//2, y_center)
            
            # Desenha o círculo representando o passo
            if i <= self.current_step:
                painter.setBrush(QBrush(QColor("#007AFF")))  # Azul para passos concluídos/atuais
                painter.setPen(QPen(QColor("#007AFF"), 2))
            else:
                painter.setBrush(QBrush(QColor("#F5F5F7")))  # Cinza claro para passos futuros
                painter.setPen(QPen(QColor("#E5E5E7"), 2))
                
            painter.drawEllipse(x - step_size//2, y_center - step_size//2, step_size, step_size)
            
            # Número dentro do círculo
            painter.setPen(QPen(QColor("white" if i <= self.current_step else "#8B949E")))
            painter.setFont(QFont(FONT_FAMILY_DEFAULT, 10, QFont.Bold))
            painter.drawText(x - 5, y_center + 5, str(i + 1))
            
            # Texto do nome do passo abaixo do círculo
            painter.setPen(QPen(QColor("#1D1D1F" if i <= self.current_step else "#8B949E")))
            painter.setFont(QFont(FONT_FAMILY_DEFAULT, 8))
            fm = QFontMetrics(painter.font())
            text_width = fm.width(step)
            painter.drawText(x - text_width//2, y_center + 25, step)


# Widget de console para exibir mensagens com histórico e formatação simples
class ConsoleWidget(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)  # Somente leitura, para uso como log de mensagens
        self.setMaximumBlockCount(1000)  # Limita o tamanho do histórico para evitar uso excessivo de memória
        self.setFont(QFont(FONT_FAMILY_MONO, FONT_SIZE_SMALL))
        
    def append_step(self, step_name, status="info", details=""):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Cores para cada tipo de status da mensagem
        colors = {
            "info": "#007AFF",
            "success": "#34C759", 
            "warning": "#FF9500",
            "error": "#FF3B30",
            "progress": "#8B949E"
        }
        
        color = colors.get(status, "#007AFF")
        
        # Símbolos substituídos por texto simples para evitar emojis
        symbols = {
            "info": "[INFO]",
            "success": "[OK]",
            "warning": "[ATENÇÃO]", 
            "error": "[ERRO]",
            "progress": "[PROGRESSO]"
        }
        
        symbol = symbols.get(status, "[INFO]")
        
        formatted_message = f"[{timestamp}] {symbol} {step_name}"
        if details:
            formatted_message += f" - {details}"
            
        self.appendPlainText(formatted_message)
        
        # Scroll automático para a última mensagem
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


# Classe Worker para executar tarefas em segundo plano (threads) sem travar a interface
class Worker(QObject):
    # Sinais para comunicar progresso, erro, conclusão e atualizações para a interface
    finished = pyqtSignal()
    error = pyqtSignal(str, str)
    result = pyqtSignal(object)
    progress = pyqtSignal(str, int)
    step_update = pyqtSignal(str, str, str)  # nome do passo, status e detalhes

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
            # Executa a função passada com callbacks para progresso e atualização de passo
            res = self.func(self.progress.emit, self.step_update.emit, self, *self.args, **self.kwargs)
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


# Janela principal da aplicação, herda de QMainWindow
class ReadmeGeneratorGUI(QMainWindow):
    # Sinais para comunicação interna e atualização da interface
    log_message_signal = pyqtSignal(str, str, str, bool)
    update_status_signal = pyqtSignal(str)
    enable_buttons_signal = pyqtSignal(bool)
    progress_bar_update_signal = pyqtSignal(str, int)
    step_indicator_signal = pyqtSignal(int)
    console_update_signal = pyqtSignal(str, str, str)

    def __init__(self):
        super().__init__()
        logger.info(f"Iniciando {APP_DISPLAY_NAME} GUI...")
        
        # Detecta o tema atual do sistema (claro/escuro)
        self.current_mode = self._detect_system_mode()
        self.theme = THEMES[self.current_mode]
        
        # Mapeia threads para controle e interrupção
        self.worker_threads_map: Dict[QThread, Worker] = {}
        
        # Cliente da API Gemini (IA)
        self.gemini_client: Optional[GeminiClient] = None
        
        # Configurações iniciais
        self.api_key: Optional[str] = None
        self.model_name: str = DEFAULT_GEMINI_MODEL
        self.zip_file_path: Optional[str] = None
        self.output_directory: str = os.path.expanduser("~")  # pasta padrão para salvar
        self.generated_readme: str = ""

        # Configura janela e interface
        self._setup_window()
        self._init_ui()
        self._apply_theme()
        self._connect_signals()
        
        # Configura gerenciador de configuração e carrega valores salvos
        self.config_mgr = ConfigManager()
        self.api_key = self.config_mgr.get_api_key()
        self.model_name = self.config_mgr.get_gemini_model() or DEFAULT_GEMINI_MODEL

        # Verifica configuração inicial com atraso para não travar interface no start
        QTimer.singleShot(150, self._check_initial_config_threaded)

    def _detect_system_mode(self) -> str:
        # Tenta detectar o tema do sistema via darkdetect, retorna "dark" ou "light"
        try:
            mode = darkdetect.theme()
            return "dark" if mode and mode.lower() == "dark" else "light"
        except Exception as e:
            logger.warning(f"Não foi possível detectar o tema do sistema: {e}. Usando modo claro.")
            return "light"

    def _setup_window(self):
        # Configurações básicas da janela principal: título, tamanho, centralização e ícone
        self.setWindowTitle(f"{APP_DISPLAY_NAME} v{APP_VERSION}")
        self.setMinimumSize(1200, 800)
        
        # Centralizar a janela na tela principal
        screen = QApplication.primaryScreen()
        if screen:
            screen_rect = screen.availableGeometry()
            width, height = 1400, 900
            x = screen_rect.center().x() - width // 2
            y = screen_rect.center().y() - height // 2
            self.setGeometry(x, y, width, height)
        
        # Ícone do app (ícone do robô azul)
        self.setWindowIcon(qtawesome.icon("fa5s.robot", color=self.theme.accent))

    def _init_ui(self):
        # Cria o widget central da janela e o layout principal vertical
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Criação dos principais componentes da interface
        self._create_header(main_layout)            # Cabeçalho com logo e título
        self._create_step_indicator(main_layout)    # Indicador visual dos passos do processo
        self._create_main_area(main_layout)         # Área principal com painel esquerdo e direito (splitter)
        self._create_controls(main_layout)          # Controles inferiores (botões, progresso)
        self._create_menus()                         # Barra de menus
        self._create_status_bar()                    # Barra de status

    def _create_header(self, parent_layout):
        # Cria o cabeçalho superior com logo e título/subtítulo
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_layout = QHBoxLayout(header_frame)
        
        # Ícone do app no cabeçalho
        icon_label = QLabel()
        icon_pixmap = qtawesome.icon("fa5s.robot", color=self.theme.accent).pixmap(48, 48)
        icon_label.setPixmap(icon_pixmap)
        
        # Título principal e subtítulo
        title_layout = QVBoxLayout()
        title_label = QLabel(APP_DISPLAY_NAME)
        title_label.setFont(QFont(FONT_FAMILY_DEFAULT, FONT_SIZE_LARGE + 4, QFont.Bold))
        
        subtitle_label = QLabel("Gere documentações profissionais automaticamente com IA")
        subtitle_label.setFont(QFont(FONT_FAMILY_DEFAULT, FONT_SIZE_DEFAULT))
        subtitle_label.setStyleSheet(f"color: {self.theme.text_secondary};")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        header_layout.addWidget(icon_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        parent_layout.addWidget(header_frame)

    def _create_step_indicator(self, parent_layout):
        # Cria a barra que mostra o progresso dos passos do processo
        steps_frame = QFrame()
        steps_layout = QHBoxLayout(steps_frame)
        
        # Lista dos nomes dos passos
        steps = ["Selecionar ZIP", "Configurar IA", "Extrair Dados", "Gerar README", "Finalizar"]
        self.step_indicator = StepIndicator(steps)
        
        steps_layout.addStretch()
        steps_layout.addWidget(self.step_indicator)
        steps_layout.addStretch()
        
        parent_layout.addWidget(steps_frame)

    def _create_main_area(self, parent_layout):
        # Área principal dividida em dois painéis (esquerdo: controles e console, direito: preview do README)
        main_splitter = QSplitter(Qt.Horizontal)
        
        left_panel = self._create_left_panel()
        right_panel = self._create_right_panel()
        
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([400, 800])  # Define proporção inicial das colunas
        
        parent_layout.addWidget(main_splitter, 1)

    def _create_left_panel(self):
        # Painel esquerdo com seleção de arquivo, configurações e console
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Grupo para seleção do arquivo ZIP
        file_group = QGroupBox("Arquivo do Projeto")
        file_layout = QVBoxLayout(file_group)
        
        # Label para mostrar o caminho do arquivo selecionado
        self.file_path_label = QLabel("Nenhum arquivo selecionado")
        self.file_path_label.setStyleSheet(f"color: {self.theme.text_secondary}; padding: 8px;")
        self.file_path_label.setWordWrap(True)
        
        # Botão para selecionar arquivo ZIP
        self.select_file_btn = AnimatedButton("Selecionar Arquivo ZIP")
        self.select_file_btn.clicked.connect(self._select_zip_file)
        
        file_layout.addWidget(self.file_path_label)
        file_layout.addWidget(self.select_file_btn)
        
        # Grupo para configurações da API e modelo
        config_group = QGroupBox("Configurações")
        config_layout = QGridLayout(config_group)
        
        # Label para status da API Key
        self.api_status_label = QLabel("API Key não configurada")
        config_layout.addWidget(QLabel("Status IA:"), 0, 0)
        config_layout.addWidget(self.api_status_label, 0, 1)
        
        # Label para mostrar o modelo atual
        self.model_label = QLabel(DEFAULT_GEMINI_MODEL)
        config_layout.addWidget(QLabel("Modelo:"), 1, 0)
        config_layout.addWidget(self.model_label, 1, 1)
        
        # Botões para configuração da API e do modelo
        config_buttons_layout = QHBoxLayout()
        
        self.config_api_btn = QPushButton("Configurar API")
        self.config_api_btn.clicked.connect(self._prompt_api_key)
        
        self.config_model_btn = QPushButton("Modelo")
        self.config_model_btn.clicked.connect(self._prompt_model_name)
        
        config_buttons_layout.addWidget(self.config_api_btn)
        config_buttons_layout.addWidget(self.config_model_btn)
        config_layout.addLayout(config_buttons_layout, 2, 0, 1, 2)
        
        # Grupo para o console de saída de mensagens
        console_group = QGroupBox("Console de Operações")
        console_layout = QVBoxLayout(console_group)
        
        self.console = ConsoleWidget()
        console_layout.addWidget(self.console)
        
        # Adiciona todos os grupos ao layout do painel esquerdo
        left_layout.addWidget(file_group)
        left_layout.addWidget(config_group)
        left_layout.addWidget(console_group, 1)  # Console ocupa espaço restante
        
        return left_widget

    def _create_right_panel(self):
        # Painel direito com visualização do README melhorada
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.preview_tabs = QTabWidget()
        
        # Aba para pré-visualização do README gerado (MELHORADA)
        preview_tab = QWidget()
        preview_layout = QVBoxLayout(preview_tab)
        
        # Widget de preview melhorado com renderização GitHub-style
        self.readme_preview = ReadmePreviewWidget(self.theme)
        preview_layout.addWidget(self.readme_preview, 1)
        
        # Aba para configurações avançadas
        settings_tab = self._create_settings_tab()
        
        self.preview_tabs.addTab(preview_tab, "README Gerado")
        self.preview_tabs.addTab(settings_tab, "Configurações Avançadas")
        
        right_layout.addWidget(self.preview_tabs)
        
        return right_widget

    def _create_settings_tab(self):
        # Aba com configurações avançadas para geração do README
        settings_widget = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidget(settings_widget)
        scroll_area.setWidgetResizable(True)
        
        layout = QVBoxLayout(settings_widget)
        
        # Seção de Personalização do Prompt
        prompt_group = QGroupBox("Personalização do Prompt")
        prompt_layout = QVBoxLayout(prompt_group)
        
        self.custom_prompt_enabled = QCheckBox("Usar prompt personalizado")
        self.custom_prompt_text = QTextEdit()
        self.custom_prompt_text.setPlaceholderText("Digite aqui instruções específicas para a IA...")
        self.custom_prompt_text.setMaximumHeight(150)
        self.custom_prompt_text.setEnabled(False)
        
        self.custom_prompt_enabled.toggled.connect(self.custom_prompt_text.setEnabled)
        
        prompt_layout.addWidget(self.custom_prompt_enabled)
        prompt_layout.addWidget(self.custom_prompt_text)
        
        # Seção de Filtros de Arquivo
        filter_group = QGroupBox("Filtros de Arquivo")
        filter_layout = QVBoxLayout(filter_group)
        
        self.include_tests = QCheckBox("Incluir arquivos de teste")
        self.include_tests.setChecked(True)
        
        self.include_docs = QCheckBox("Incluir documentação existente")
        self.include_docs.setChecked(True)
        
        self.include_config = QCheckBox("Incluir arquivos de configuração")
        self.include_config.setChecked(True)
        
        self.max_file_size_label = QLabel("Tamanho máximo por arquivo (KB):")
        self.max_file_size_spin = QSpinBox()
        self.max_file_size_spin.setRange(1, 100)
        self.max_file_size_spin.setValue(5)
        self.max_file_size_spin.setSuffix(" KB")
        
        self.max_files_label = QLabel("Máximo de arquivos para análise:")
        self.max_files_spin = QSpinBox()
        self.max_files_spin.setRange(5, 100)
        self.max_files_spin.setValue(30)
        
        filter_layout.addWidget(self.include_tests)
        filter_layout.addWidget(self.include_docs)
        filter_layout.addWidget(self.include_config)
        filter_layout.addWidget(self.max_file_size_label)
        filter_layout.addWidget(self.max_file_size_spin)
        filter_layout.addWidget(self.max_files_label)
        filter_layout.addWidget(self.max_files_spin)
        
        # Seção de Estilo do README
        style_group = QGroupBox("Estilo do README")
        style_layout = QVBoxLayout(style_group)
        
        self.readme_style_label = QLabel("Estilo:")
        self.readme_style_combo = QComboBox()
        self.readme_style_combo.addItems([
            "Profissional",
            "Detalhado",
            "Minimalista", 
            "Tutorial",
            "Open Source"
        ])
        
        self.include_badges = QCheckBox("Incluir badges")
        self.include_badges.setChecked(True)
        
        self.include_toc = QCheckBox("Incluir índice (TOC)")
        self.include_toc.setChecked(True)
        
        self.include_examples = QCheckBox("Incluir exemplos de uso")
        self.include_examples.setChecked(True)
        
        style_layout.addWidget(self.readme_style_label)
        style_layout.addWidget(self.readme_style_combo)
        style_layout.addWidget(self.include_badges)
        style_layout.addWidget(self.include_toc)
        style_layout.addWidget(self.include_examples)
        
        # Adiciona grupos ao layout
        layout.addWidget(prompt_group)
        layout.addWidget(filter_group)
        layout.addWidget(style_group)
        layout.addStretch()
        
        return scroll_area

    def _create_controls(self, parent_layout):
        # Área inferior com barra de progresso e botão para gerar README
        controls_frame = QFrame()
        controls_frame.setFixedHeight(80)
        controls_layout = QHBoxLayout(controls_frame)
        
        # Container para progresso
        self.progress_frame = QFrame()
        progress_layout = QVBoxLayout(self.progress_frame)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        
        self.progress_label = QLabel("")
        self.progress_label.setFont(QFont(FONT_FAMILY_DEFAULT, FONT_SIZE_SMALL))
        self.progress_label.setVisible(False)
        
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        # Botão para salvar README
        self.save_readme_btn = AnimatedButton("Salvar README")
        self.save_readme_btn.clicked.connect(self._save_readme)
        self.save_readme_btn.setEnabled(False)
        
        # Botão principal para disparar a geração do README
        self.generate_btn = AnimatedButton("Gerar README")
        self.generate_btn.setMinimumWidth(200)
        self.generate_btn.setFont(QFont(FONT_FAMILY_DEFAULT, FONT_SIZE_DEFAULT, QFont.Bold))
        self.generate_btn.clicked.connect(self._trigger_readme_generation)
        self.generate_btn.setEnabled(False)  # Só habilita após arquivo e API configurados
        
        buttons_layout.addWidget(self.save_readme_btn)
        buttons_layout.addWidget(self.generate_btn)
        
        controls_layout.addWidget(self.progress_frame, 1)
        controls_layout.addStretch()
        controls_layout.addLayout(buttons_layout)
        
        parent_layout.addWidget(controls_frame)

    def _create_menus(self):
        # Cria a barra de menus no topo da janela
        menubar = self.menuBar()
        
        # Menu Arquivo com ações abrir, salvar e sair
        file_menu = menubar.addMenu("&Arquivo")
        
        open_action = QAction("Abrir ZIP...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self._select_zip_file)
        
        save_action = QAction("Salvar README...", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self._save_readme)
        
        export_menu = file_menu.addMenu("Exportar")
        
        export_md_action = QAction("Markdown (.md)", self)
        export_md_action.triggered.connect(self._export_markdown)
        
        export_html_action = QAction("HTML (.html)", self)
        export_html_action.triggered.connect(self._export_html)
        
        export_pdf_action = QAction("PDF (.pdf)", self)
        export_pdf_action.triggered.connect(self._export_pdf)
        
        export_menu.addAction(export_md_action)
        export_menu.addAction(export_html_action)
        export_menu.addAction(export_pdf_action)
        
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(save_action)
        file_menu.addMenu(export_menu)
        file_menu.addSeparator()
        
        exit_action = QAction("Sair", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Editar
        edit_menu = menubar.addMenu("&Editar")
        
        copy_action = QAction("Copiar README", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self._copy_readme)
        
        edit_menu.addAction(copy_action)
        
        # Menu Configurações para API Key e modelo
        config_menu = menubar.addMenu("&Configurações")
        
        api_action = QAction("Configurar API Key", self)
        api_action.triggered.connect(self._prompt_api_key)
        
        model_action = QAction("Selecionar Modelo", self)
        model_action.triggered.connect(self._prompt_model_name)
        
        config_menu.addAction(api_action)
        config_menu.addAction(model_action)
        
        # Menu Visual para trocar tema claro/escuro
        view_menu = menubar.addMenu("&Visual")
        
        light_action = QAction("Tema Claro", self)
        light_action.triggered.connect(lambda: self._switch_theme("light"))
        
        dark_action = QAction("Tema Escuro", self)
        dark_action.triggered.connect(lambda: self._switch_theme("dark"))
        
        auto_action = QAction("Tema Automático", self)
        auto_action.triggered.connect(self._switch_theme_auto)
        
        view_menu.addAction(light_action)
        view_menu.addAction(dark_action)
        view_menu.addSeparator()
        view_menu.addAction(auto_action)
        
        # Menu Ajuda
        help_menu = menubar.addMenu("&Ajuda")
        
        about_action = QAction("Sobre", self)
        about_action.triggered.connect(self._show_about)
        
        help_action = QAction("Ajuda", self)
        help_action.triggered.connect(self._show_help)
        
        help_menu.addAction(about_action)
        help_menu.addAction(help_action)

    def _create_status_bar(self):
        # Barra de status inferior para mostrar mensagens rápidas
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.status_label = QLabel("Pronto")
        self.status_label.setFont(QFont(FONT_FAMILY_DEFAULT, FONT_SIZE_SMALL))
        
        self.status_bar.addWidget(self.status_label, 1)

    def _apply_theme(self):
        # Aplica CSS para cores, bordas e estilos baseados no tema selecionado
        style = f"""
        QMainWindow {{
            background-color: {self.theme.bg_primary};
            color: {self.theme.text_primary};
        }}
        
        QWidget {{
            background-color: {self.theme.bg_primary};
            color: {self.theme.text_primary};
        }}
        
        QGroupBox {{
            font-weight: bold;
            border: 2px solid {self.theme.border};
            border-radius: 8px;
            margin-top: 8px;
            background-color: {self.theme.surface};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px 0 8px;
            background-color: {self.theme.surface};
        }}
        
        QPushButton {{
            background-color: {self.theme.surface};
            border: 1px solid {self.theme.border};
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
        }}
        
        QPushButton:hover {{
            background-color: {self.theme.surface_variant};
            border-color: {self.theme.accent};
        }}
        
        QPushButton:pressed {{
            background-color: {self.theme.accent};
            color: white;
        }}
        
        QPushButton:disabled {{
            background-color: {self.theme.surface_variant};
            color: {self.theme.text_secondary};
            border-color: {self.theme.border};
        }}
        
        QTextEdit, QPlainTextEdit {{
            background-color: {self.theme.bg_secondary};
            border: 1px solid {self.theme.border};
            border-radius: 6px;
            padding: 8px;
            selection-background-color: {self.theme.accent};
        }}
        
        QTabWidget::pane {{
            border: 1px solid {self.theme.border};
            border-radius: 6px;
            background-color: {self.theme.surface};
        }}
        
        QTabBar::tab {{
            background-color: {self.theme.surface_variant};
            border: 1px solid {self.theme.border};
            padding: 8px 16px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {self.theme.accent};
            color: white;
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {self.theme.surface};
        }}
        
        QProgressBar {{
            border: none;
            border-radius: 3px;
            background-color: {self.theme.surface_variant};
        }}
        
        QProgressBar::chunk {{
            background-color: {self.theme.accent};
            border-radius: 3px;
        }}
        
        QSplitter::handle {{
            background-color: {self.theme.border};
        }}
        
        QSplitter::handle:horizontal {{
            width: 2px;
        }}
        
        QSplitter::handle:vertical {{
            height: 2px;
        }}
        
        QStatusBar {{
            background-color: {self.theme.surface};
            border-top: 1px solid {self.theme.border};
        }}
        
        QMenuBar {{
            background-color: {self.theme.surface};
            border-bottom: 1px solid {self.theme.border};
        }}
        
        QMenuBar::item {{
            padding: 4px 8px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {self.theme.accent};
            color: white;
        }}
        
        QMenu {{
            background-color: {self.theme.surface};
            border: 1px solid {self.theme.border};
            border-radius: 6px;
        }}
        
        QMenu::item {{
            padding: 6px 20px;
        }}
        
        QMenu::item:selected {{
            background-color: {self.theme.accent};
            color: white;
        }}
        
        QComboBox {{
            background-color: {self.theme.surface};
            border: 1px solid {self.theme.border};
            border-radius: 4px;
            padding: 4px 8px;
            min-width: 100px;
        }}
        
        QComboBox:hover {{
            border-color: {self.theme.accent};
        }}
        
        QComboBox::drop-down {{
            border: none;
        }}
        
        QComboBox::down-arrow {{
            width: 12px;
            height: 12px;
        }}
        
        QSpinBox {{
            background-color: {self.theme.surface};
            border: 1px solid {self.theme.border};
            border-radius: 4px;
            padding: 4px;
        }}
        
        QCheckBox {{
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 2px solid {self.theme.border};
            border-radius: 3px;
            background-color: {self.theme.surface};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {self.theme.accent};
            border-color: {self.theme.accent};
        }}
        
        QScrollArea {{
            border: none;
            background-color: {self.theme.bg_primary};
        }}
        
        QToolBar {{
            background-color: {self.theme.surface};
            border: 1px solid {self.theme.border};
            border-radius: 4px;
            spacing: 8px;
            padding: 4px;
        }}
        """
        
        self.setStyleSheet(style)

    def _connect_signals(self):
        # Conecta os sinais internos para atualizar UI em threads
        self.console_update_signal.connect(self._update_console)
        self.step_indicator_signal.connect(self._update_step_indicator)
        self.progress_bar_update_signal.connect(self._update_progress_bar)
        self.update_status_signal.connect(self._update_status)
        self.enable_buttons_signal.connect(self._enable_buttons)

    def _switch_theme(self, theme_name):
        # Altera tema para claro ou escuro e reaplica os estilos
        if theme_name in THEMES:
            self.current_mode = theme_name
            self.theme = THEMES[theme_name]
            self._apply_theme()
            # Atualiza o renderer do markdown com o novo tema
            self.readme_preview.markdown_renderer.theme = self.theme
            # Recria o realce de sintaxe com o novo tema
            self.readme_preview.markdown_highlighter = MarkdownHighlighter(
                self.readme_preview.code_editor.document(), self.theme
            )
            # Re-renderiza o conteúdo atual se houver
            if self.generated_readme:
                self.readme_preview.set_markdown_content(self.generated_readme)
            logger.info(f"Tema alterado para: {theme_name}")

    def _switch_theme_auto(self):
        # Detecta e aplica tema automaticamente baseado no sistema
        detected_theme = self._detect_system_mode()
        self._switch_theme(detected_theme)

    # Slots para atualização da interface chamados a partir de threads
    @pyqtSlot(str, str, str)
    def _update_console(self, step_name, status, details):
        self.console.append_step(step_name, status, details)

    @pyqtSlot(int)
    def _update_step_indicator(self, step):
        self.step_indicator.set_current_step(step)

    @pyqtSlot(str, int)
    def _update_progress_bar(self, message, value):
        if message and value > 0:
            self.progress_frame.setVisible(True)
            self.progress_label.setVisible(True)
            self.progress_bar.setVisible(True)
            self.progress_label.setText(message)
            self.progress_bar.setValue(value)
        else:
            self.progress_frame.setVisible(False)

    @pyqtSlot(str)
    def _update_status(self, message):
        self.status_label.setText(message)

    @pyqtSlot(bool)
    def _enable_buttons(self, enabled):
        # Habilita ou desabilita botões de acordo com estado atual e pré-condições
        self.select_file_btn.setEnabled(enabled)
        self.generate_btn.setEnabled(enabled and self.gemini_client is not None and self.zip_file_path is not None)

    # Métodos para interações do usuário e controle da aplicação

    def _select_zip_file(self):
        # Abre diálogo para selecionar arquivo ZIP do projeto
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Selecionar arquivo ZIP do projeto", 
            self.output_directory, 
            "Arquivos ZIP (*.zip);;Todos os arquivos (*.*)"
        )
        
        if file_path:
            self.zip_file_path = file_path
            self.file_path_label.setText(f"{os.path.basename(file_path)}")
            self.file_path_label.setStyleSheet(f"color: {self.theme.text_primary}; padding: 8px; font-weight: 500;")
            self.console_update_signal.emit("Arquivo Selecionado", "success", os.path.basename(file_path))
            self.step_indicator_signal.emit(0)
            self._update_generate_button_state()

    def _update_generate_button_state(self):
        # Atualiza se o botão "Gerar README" deve estar habilitado
        can_generate = (self.zip_file_path is not None and self.gemini_client is not None)
        self.generate_btn.setEnabled(can_generate)
        
        if can_generate:
            self.generate_btn.setText("Gerar README")
            self.generate_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.theme.accent};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 12px 24px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {self.theme.accent_variant};
                }}
            """)

    def _prompt_api_key(self):
        # Exibe diálogo para configuração da API Key do Google Gemini
        current_key = self.api_key or ""
        masked_key = "..." + current_key[-4:] if len(current_key) > 4 else ""
        
        key, ok = QInputDialog.getText(
            self, 
            "Configurar API Key do Google Gemini",
            f"Digite sua API Key:\n(Atual: {masked_key if current_key else 'Não configurada'})",
            text=""
        )
        
        if ok and key.strip():
            self.api_key = key.strip()
            self.config_mgr.set_api_key(self.api_key)
            self.console_update_signal.emit("API Key", "success", "Configurada com sucesso")
            self._initialize_gemini_client_threaded()

    def _prompt_model_name(self):
        # Exibe diálogo para selecionar o modelo Gemini
        current_model = self.model_name or DEFAULT_GEMINI_MODEL
        
        model, ok = QInputDialog.getText(
            self,
            "Selecionar Modelo Gemini", 
            "Nome do modelo:",
            text=current_model
        )
        
        if ok and model.strip() and model.strip() != self.model_name:
            self.model_name = model.strip()
            self.config_mgr.set_gemini_model(self.model_name)
            self.model_label.setText(self.model_name)
            self.console_update_signal.emit("Modelo", "info", f"Alterado para {self.model_name}")
            self._initialize_gemini_client_threaded()

    def _save_readme(self):
        # Salva o README gerado em arquivo no disco
        if not self.generated_readme:
            QMessageBox.warning(self, "Aviso", "Nenhum README foi gerado ainda.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar README",
            os.path.join(self.output_directory, "README.md"),
            "Markdown (*.md);;Todos os arquivos (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.generated_readme)
                self.console_update_signal.emit("README Salvo", "success", os.path.basename(file_path))
                QMessageBox.information(self, "Sucesso", f"README salvo em:\n{file_path}")
                
                # Abre a pasta contendo o arquivo salvo
                QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(file_path)))
                
            except Exception as e:
                logger.error(f"Erro ao salvar README: {e}")
                QMessageBox.critical(self, "Erro", f"Erro ao salvar arquivo:\n{e}")

    def _copy_readme(self):
        # Copia o conteúdo do README para a área de transferência mantendo formatação
        self.readme_preview.copy_raw_markdown()
        self.console_update_signal.emit("README", "success", "Copiado para área de transferência")

    def _export_markdown(self):
        # Exporta como arquivo Markdown
        self._save_readme()

    def _export_html(self):
        # Exporta como HTML renderizado
        if not self.generated_readme:
            QMessageBox.warning(self, "Aviso", "Nenhum README foi gerado ainda.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar como HTML",
            os.path.join(self.output_directory, "README.html"),
            "HTML (*.html);;Todos os arquivos (*.*)"
        )
        
        if file_path:
            try:
                html_content = self.readme_preview.markdown_renderer.render_to_html(self.generated_readme)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                self.console_update_signal.emit("HTML Exportado", "success", os.path.basename(file_path))
                QMessageBox.information(self, "Sucesso", f"HTML exportado para:\n{file_path}")
                QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(file_path)))
            except Exception as e:
                logger.error(f"Erro ao exportar HTML: {e}")
                QMessageBox.critical(self, "Erro", f"Erro ao exportar HTML:\n{e}")

    def _export_pdf(self):
        # Placeholder para exportação PDF
        QMessageBox.information(
            self, 
            "Funcionalidade em Desenvolvimento", 
            "A exportação para PDF será implementada em breve!\n\n"
            "Por enquanto, você pode:\n"
            "1. Exportar como HTML\n"
            "2. Abrir o HTML no navegador\n"
            "3. Usar 'Imprimir' > 'Salvar como PDF'"
        )

    def _show_about(self):
        # Mostra diálogo sobre a aplicação
        about_text = f"""
        <h2>{APP_DISPLAY_NAME}</h2>
        <p><b>Versão:</b> {APP_VERSION}</p>
        <p><b>Autor:</b> {APP_AUTHOR}</p>
        
        <p>Uma ferramenta inteligente para gerar documentação README.md 
        profissional automaticamente usando IA.</p>
        
        <p><b>Recursos:</b></p>
        <ul>
        <li>Análise automática de projetos</li>
        <li>Geração com IA Google Gemini</li>
        <li>Preview renderizado estilo GitHub</li>
        <li>Múltiplos formatos de exportação</li>
        <li>Interface moderna e intuitiva</li>
        </ul>
        
        <p><b>Dependências principais:</b></p>
        <ul>
        <li>PyQt5 - Interface gráfica</li>
        <li>Google Gemini API - IA generativa</li>
        <li>Python Markdown - Renderização</li>
        </ul>
        """
        
        QMessageBox.about(self, "Sobre", about_text)

    def _show_help(self):
        # Mostra janela de ajuda
        help_text = """
        <h3>Como usar o Gerador de README</h3>
        
        <h4>1. Configuração inicial:</h4>
        <ul>
        <li>Configure sua API Key do Google Gemini</li>
        <li>Selecione o modelo desejado (padrão: gemini-pro)</li>
        </ul>
        
        <h4>2. Seleção do projeto:</h4>
        <ul>
        <li>Clique em "Selecionar Arquivo ZIP"</li>
        <li>Escolha o arquivo ZIP do seu projeto</li>
        </ul>
        
        <h4>3. Configurações avançadas (opcional):</h4>
        <ul>
        <li>Acesse a aba "Configurações Avançadas"</li>
        <li>Personalize filtros de arquivo</li>
        <li>Ajuste o estilo do README</li>
        <li>Configure prompts personalizados</li>
        </ul>
        
        <h4>4. Geração:</h4>
        <ul>
        <li>Clique em "Gerar README"</li>
        <li>Aguarde o processamento</li>
        <li>Visualize o resultado na aba "README Gerado"</li>
        </ul>
        
        <h4>5. Exportação:</h4>
        <ul>
        <li>Salve como Markdown (.md)</li>
        <li>Exporte como HTML renderizado</li>
        <li>Copie para área de transferência</li>
        </ul>
        
        <h4>Dicas:</h4>
        <ul>
        <li>Use o modo "Lado a Lado" para comparar código e preview</li>
        <li>Experimente diferentes estilos de README</li>
        <li>Configure filtros para otimizar a análise</li>
        </ul>
        """
        
        QMessageBox.about(self, "Ajuda", help_text)

    # Métodos relacionados ao processamento em threads para não travar a UI

    def _check_initial_config_threaded(self):
        # Inicia verificação das configurações iniciais em thread separada
        self.console_update_signal.emit("Inicializando", "info", "Verificando configurações...")
        self._run_in_thread(
            self._check_initial_config_worker,
            callback_slot=self._check_initial_config_callback
        )

    def _check_initial_config_worker(self, progress_cb, step_cb, worker):
        # Worker que carrega as configurações (API Key e modelo) do arquivo local
        step_cb("Carregando Configurações", "progress", "")
        progress_cb("Verificando configurações...", 20)
        
        api_key = self.config_mgr.get_api_key()
        model_name = self.config_mgr.get_gemini_model() or DEFAULT_GEMINI_MODEL
        
        progress_cb("Configurações carregadas", 100)
        step_cb("Configurações", "success", "Carregadas com sucesso")
        
        return {"api_key": api_key, "model_name": model_name}

    def _check_initial_config_callback(self, result):
        # Callback após carregar configurações, atualiza UI e estado interno
        self.api_key = result.get("api_key")
        self.model_name = result.get("model_name", DEFAULT_GEMINI_MODEL)
        self.model_label.setText(self.model_name)
        
        if self.api_key:
            self.api_status_label.setText("API Key configurada")
            self.api_status_label.setStyleSheet(f"color: {self.theme.success};")
            self._initialize_gemini_client_threaded()
        else:
            self.api_status_label.setText("API Key não configurada")
            self.api_status_label.setStyleSheet(f"color: {self.theme.error};")
            self.console_update_signal.emit("API Key", "warning", "Não configurada - clique em 'Configurar API'")

    def _initialize_gemini_client_threaded(self):
        # Inicializa o cliente da API Gemini em uma thread separada para não travar a UI
        if not self.api_key:
            return
            
        self.console_update_signal.emit("IA Gemini", "progress", "Inicializando...")
        self.step_indicator_signal.emit(1)
        self._run_in_thread(
            self._initialize_gemini_client_worker,
            callback_slot=self._initialize_gemini_client_callback,
            error_slot=self._gemini_init_error
        )

    def _initialize_gemini_client_worker(self, progress_cb, step_cb, worker):
        # Worker que cria o cliente Gemini e testa conexão
        step_cb("Conectando IA", "progress", "Inicializando cliente Gemini...")
        progress_cb("Conectando à IA Gemini...", 30)
        
        try:
            client = GeminiClient(api_key=self.api_key, model_name=self.model_name)
            progress_cb("Testando conexão...", 70)
            
            if client.test_connection():
                progress_cb("IA Gemini conectada!", 100)
                step_cb("IA Gemini", "success", f"Conectada - Modelo: {self.model_name}")
                return client
            else:
                raise ConnectionError("Falha no teste de conexão")
                
        except Exception as e:
            step_cb("IA Gemini", "error", f"Erro: {str(e)}")
            raise

    def _initialize_gemini_client_callback(self, client):
        # Callback para configurar cliente Gemini após criação com sucesso
        self.gemini_client = client
        self.api_status_label.setText(f"IA Pronta - {self.model_name}")
        self.api_status_label.setStyleSheet(f"color: {self.theme.success};")
        self._update_generate_button_state()

    def _gemini_init_error(self, title, message):
        # Trata erro na inicialização do cliente Gemini
        self.gemini_client = None
        self.api_status_label.setText("Erro na IA")
        self.api_status_label.setStyleSheet(f"color: {self.theme.error};")
        self.console_update_signal.emit("IA Gemini", "error", "Falha na inicialização")
        QMessageBox.critical(self, title, message)

    def _trigger_readme_generation(self):
        # Inicia o processo de geração do README em thread separada
        if not self.zip_file_path or not self.gemini_client:
            return
            
        self.enable_buttons_signal.emit(False)
        self.console_update_signal.emit("Geração", "progress", "Iniciando geração do README...")
        self.step_indicator_signal.emit(2)
        
        # Coleta configurações avançadas
        config = self._get_advanced_config()
        
        self._run_in_thread(
            self._generate_readme_worker,
            self.zip_file_path,
            config,
            callback_slot=self._readme_generation_callback,
            error_slot=self._readme_generation_error
        )

    def _get_advanced_config(self):
        # Coleta configurações da aba de configurações avançadas
        return {
            "custom_prompt_enabled": self.custom_prompt_enabled.isChecked(),
            "custom_prompt": self.custom_prompt_text.toPlainText(),
            "include_tests": self.include_tests.isChecked(),
            "include_docs": self.include_docs.isChecked(),
            "include_config": self.include_config.isChecked(),
            "max_file_size_kb": self.max_file_size_spin.value(),
            "max_files": self.max_files_spin.value(),
            "readme_style": self.readme_style_combo.currentText(),
            "include_badges": self.include_badges.isChecked(),
            "include_toc": self.include_toc.isChecked(),
            "include_examples": self.include_examples.isChecked()
        }

    def _generate_readme_worker(self, progress_cb, step_cb, worker, zip_path, config):
        # Worker que extrai dados do ZIP e gera README usando IA
        step_cb("Extraindo Dados", "progress", "Analisando arquivo ZIP...")
        progress_cb("Extraindo dados do projeto...", 10)
        
        # Extrai dados do arquivo ZIP para envio à IA
        project_data = self._extract_project_data_from_zip(progress_cb, step_cb, worker, zip_path, config)
        if not project_data or worker.is_interruption_requested():
            return None
            
        step_cb("Enviando para IA", "progress", "Processando com Gemini...")
        self.step_indicator_signal.emit(3)
        progress_cb("Gerando README com IA...", 70)
        
        # Gera o README enviando prompt para a IA
        try:
            prompt = self._build_prompt(project_data, config)
            readme_content = self.gemini_client.send_conversational_prompt(prompt)
            
            if readme_content:
                progress_cb("README gerado com sucesso!", 100)
                step_cb("README", "success", "Gerado com sucesso")
                self.step_indicator_signal.emit(4)
                return readme_content
            else:
                raise ValueError("IA retornou conteúdo vazio")
                
        except Exception as e:
            step_cb("IA Gemini", "error", f"Erro na geração: {str(e)}")
            raise

    def _build_prompt(self, project_data, config):
        # Constrói prompt personalizado baseado nas configurações
        base_prompt = PROMPT_README_GENERATION
        
        if config["custom_prompt_enabled"] and config["custom_prompt"].strip():
            # Usa prompt personalizado
            custom_instructions = config["custom_prompt"].strip()
            prompt = f"""
            {custom_instructions}
            
            Dados do projeto:
            {project_data}
            """
        else:
            # Usa prompt padrão com customizações
            style_instructions = {
                "Profissional": "Crie um README profissional e conciso, focado em clareza e objetividade.",
                "Detalhado": "Crie um README detalhado e abrangente, explicando todos os aspectos do projeto.",
                "Minimalista": "Crie um README minimalista e direto, apenas com informações essenciais.",
                "Tutorial": "Crie um README no estilo tutorial, com exemplos práticos e explicações passo a passo.",
                "Open Source": "Crie um README para projeto open source, incluindo informações sobre contribuição e licença."
            }
            
            style_instruction = style_instructions.get(config["readme_style"], "")
            
            additional_instructions = []
            if config["include_badges"]:
                additional_instructions.append("Inclua badges relevantes (build status, version, license, etc.)")
            if config["include_toc"]:
                additional_instructions.append("Inclua um índice (Table of Contents)")
            if config["include_examples"]:
                additional_instructions.append("Inclua exemplos práticos de uso")
                
            extra_instructions = ". ".join(additional_instructions)
            if extra_instructions:
                extra_instructions = f"\n\nInstruções adicionais: {extra_instructions}."
            
            prompt = f"""
            {base_prompt}
            
            Estilo desejado: {style_instruction}
            {extra_instructions}
            
            Dados do projeto:
            {{project_data}}
            """.format(project_data=project_data)
        
        return prompt

    # ADICIONE AQUI O NOVO MÉTODO:
    def _clean_readme_content(self, raw_content):
        """
        Remove marcações de código Markdown que podem vir da IA
        e limpa o conteúdo para exibição adequada
        """
        if not raw_content:
            return ""
        
        content = raw_content.strip()
        
        # Remove marcações de código Markdown no início e fim
        # Padrões comuns que a IA pode retornar:
        # ```markdown ... ```
        # ```md ... ```
        # ``` ... ```
        
        # Remove markdown code block no início
        if content.startswith('```'):
            # Encontra a primeira quebra de linha após ```
            first_newline = content.find('\n')
            if first_newline != -1:
                content = content[first_newline + 1:]
        
        # Remove markdown code block no final
        if content.endswith('```'):
            # Encontra a última ocorrência de ``` e remove
            last_backticks = content.rfind('```')
            if last_backticks != -1:
                content = content[:last_backticks]
        
        # Remove linhas extras em branco no início e fim
        content = content.strip()
        
        return content

    # Depois, MODIFIQUE o método _readme_generation_callback existente:
    def _readme_generation_callback(self, readme_content):
        # Callback após gerar README com sucesso, atualiza editor e UI
        self.enable_buttons_signal.emit(True)
        
        if readme_content:
            # ADICIONE ESTA LINHA - limpa o conteúdo antes de usar
            cleaned_content = self._clean_readme_content(readme_content)
            self.generated_readme = cleaned_content  # MUDE de readme_content para cleaned_content
            
            # Atualiza o preview widget com o novo conteúdo limpo
            self.readme_preview.set_markdown_content(cleaned_content)  # MUDE aqui também
            
            # Habilita botão de salvar
            self.save_readme_btn.setEnabled(True)
            
            # Mostra aba do README
            self.preview_tabs.setCurrentIndex(0)
            
            self.console_update_signal.emit("Finalizado", "success", "README gerado com sucesso!")
            QMessageBox.information(self, "Sucesso!", "README gerado com sucesso!\nVocê pode visualizar, editar e salvar o resultado.")
            
        else:
            self.console_update_signal.emit("Geração", "error", "Falha na geração do README")

    def _extract_project_data_from_zip(self, progress_cb, step_cb, worker, zip_path, config):
        """Extrai dados do arquivo ZIP para análise, usando configurações avançadas"""
        try:
            step_cb("Analisando ZIP", "progress", "Lendo estrutura do arquivo...")
            
            data_parts = []
            with zipfile.ZipFile(zip_path, 'r') as zf:
                file_list = zf.infolist()
                
                # Lista estrutura do projeto
                data_parts.append("=== ESTRUTURA DO PROJETO ===\n")
                for item in file_list[:50]:  # Limita para evitar sobrecarga
                    if worker.is_interruption_requested():
                        return None
                    data_parts.append(f"{'[DIR]' if item.is_dir() else '[ARQ]'} {item.filename}\n")
                
                progress_cb("Extraindo conteúdo dos arquivos...", 30)
                step_cb("Extraindo Código", "progress", "Lendo arquivos de código...")
                
                # Extensões relevantes para análise
                code_extensions = {'.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.cs', '.go', '.rb', '.php', '.swift', '.kt', '.rs', '.html', '.css', '.scss', '.md', '.json', '.xml', '.yaml', '.yml', '.sh', '.bat'}
                config_files = {'requirements.txt', 'package.json', 'pom.xml', 'build.gradle', 'setup.py', 'dockerfile', 'docker-compose.yml', '.gitignore', 'license', 'contributing.md', 'readme.md'}
                
                # Aplica filtros baseados nas configurações
                content_files = []
                for item in file_list:
                    if not item.is_dir():
                        ext = os.path.splitext(item.filename)[1].lower()
                        name = os.path.basename(item.filename).lower()
                        path_lower = item.filename.lower()
                        
                        # Filtros de inclusão
                        should_include = False
                        
                        if ext in code_extensions or name in config_files:
                            should_include = True
                            
                        # Filtros específicos
                        if not config["include_tests"] and any(test_indicator in path_lower for test_indicator in ['test', 'spec', '__pycache__']):
                            should_include = False
                            
                        if not config["include_docs"] and any(doc_indicator in path_lower for doc_indicator in ['doc', 'docs', 'documentation']):
                            should_include = False
                            
                        if not config["include_config"] and any(config_indicator in path_lower for config_indicator in ['config', 'conf', '.env', 'settings']):
                            should_include = False
                            
                        if should_include:
                            content_files.append(item)
                
                data_parts.append("\n=== CONTEÚDO DOS ARQUIVOS ===\n")
                
                max_files = config["max_files"]
                max_file_size = config["max_file_size_kb"] * 1024  # Converte para bytes
                
                for i, item in enumerate(content_files[:max_files]):
                    if worker.is_interruption_requested():
                        return None
                        
                    try:
                        with zf.open(item) as file_in_zip:
                            content_bytes = file_in_zip.read()
                            try:
                                content = content_bytes.decode('utf-8')
                            except:
                                content = content_bytes.decode('latin-1', errors='ignore')
                            
                            if len(content_bytes) > max_file_size:
                                # Trunca arquivo se muito grande
                                content = content[:max_file_size//2] + "\n[...ARQUIVO TRUNCADO...]"
                            
                            data_parts.append(f"\n--- {item.filename} ---\n")
                            data_parts.append(content)
                            data_parts.append("\n")
                            
                    except Exception as e:
                        data_parts.append(f"\n--- {item.filename} ---\n[ERRO AO LER: {e}]\n")
                    
                    # Atualiza progresso a cada 5 arquivos processados
                    if i % 5 == 0:
                        progress = 30 + int(30 * (i + 1) / min(len(content_files), max_files))
                        progress_cb(f"Processando: {os.path.basename(item.filename)}", progress)
                
                step_cb("Dados Extraídos", "success", f"{min(len(content_files), max_files)} arquivos analisados")
                return "".join(data_parts)
                
        except Exception as e:
            step_cb("Extração", "error", f"Erro ao processar ZIP: {str(e)}")
            raise

    def _readme_generation_callback(self, readme_content):
        # Callback após gerar README com sucesso, atualiza editor e UI
        self.enable_buttons_signal.emit(True)
        
        if readme_content:
            self.generated_readme = readme_content
            
            # Atualiza o preview widget com o novo conteúdo
            self.readme_preview.set_markdown_content(readme_content)
            
            # Habilita botão de salvar
            self.save_readme_btn.setEnabled(True)
            
            # Mostra aba do README
            self.preview_tabs.setCurrentIndex(0)
            
            self.console_update_signal.emit("Finalizado", "success", "README gerado com sucesso!")
            QMessageBox.information(self, "Sucesso!", "README gerado com sucesso!\nVocê pode visualizar, editar e salvar o resultado.")
            
        else:
            self.console_update_signal.emit("Geração", "error", "Falha na geração do README")

    def _readme_generation_error(self, title, message):
        # Trata erro ocorrido durante a geração do README
        self.enable_buttons_signal.emit(True)
        self.console_update_signal.emit("Erro", "error", "Falha na geração do README")
        QMessageBox.critical(self, title, message)

    def _run_in_thread(self, func, *args, callback_slot=None, error_slot=None, **kwargs):
        # Método genérico para rodar função em thread sem travar UI
        thread = QThread()
        worker = Worker(func, *args, **kwargs)
        worker.moveToThread(thread)
        
        # Conecta sinais para controle de ciclo da thread e comunicação
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        
        if callback_slot:
            worker.result.connect(callback_slot)
        
        if error_slot:
            worker.error.connect(error_slot)
        else:
            worker.error.connect(self._generic_error_handler)
        
        worker.progress.connect(self.progress_bar_update_signal)
        worker.step_update.connect(self.console_update_signal)
        
        thread.started.connect(worker.run)
        thread.start()
        
        # Guarda referência para controlar interrupção ou encerramento futuro
        self.worker_threads_map[thread] = worker
        
        return thread

    def _generic_error_handler(self, title, message):
        # Handler padrão para erros não tratados
        logger.error(f"Erro genérico: {title} - {message}")
        QMessageBox.critical(self, title, message)

    def closeEvent(self, event):
        # Método chamado ao fechar a janela principal, limpa recursos e threads
        logger.info("Fechando aplicação...")
        
        # Solicita parada das threads em execução
        for thread, worker in list(self.worker_threads_map.items()):
            if thread.isRunning():
                worker.request_interruption()
                thread.quit()
                if not thread.wait(2000):
                    thread.terminate()
        
        # Fecha cliente Gemini se existir
        if self.gemini_client:
            self.gemini_client.close()
        
        super().closeEvent(event)


def main():
    # Função principal para rodar a aplicação standalone
    app = QApplication(sys.argv)
    
    # Configurações para melhor suporte a alta resolução (DPI)
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Configura tradução para a localidade do sistema
    translator = QTranslator()
    locale = QLocale.system().name()
    if translator.load(f"qtbase_{locale}", QLibraryInfo.location(QLibraryInfo.TranslationsPath)):
        app.installTranslator(translator)
    
    # Cria e mostra a janela principal da aplicação
    window = ReadmeGeneratorGUI()
    window.show()
    
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
    