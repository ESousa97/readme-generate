from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QSplitter, QTextEdit, QTextBrowser,
    QToolBar, QLabel, QPushButton, QComboBox, QApplication
)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QFont

from .markdown_renderer import MarkdownRenderer
from .syntax_highlighter import MarkdownHighlighter

try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    WEB_ENGINE_AVAILABLE = True
except ImportError:
    WEB_ENGINE_AVAILABLE = False


class ReadmePreviewWidget(QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.markdown_renderer = MarkdownRenderer(theme)
        self.raw_markdown = ""
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems(["Visualização", "Código", "Lado a Lado"])
        self.view_mode_combo.currentTextChanged.connect(self.change_view_mode)
        
        toolbar.addWidget(QLabel("Modo:"))
        toolbar.addWidget(self.view_mode_combo)
        toolbar.addSeparator()
        
        self.copy_raw_btn = QPushButton("Copiar Markdown")
        self.copy_raw_btn.clicked.connect(self.copy_raw_markdown)
        self.copy_raw_btn.setEnabled(False)
        
        self.copy_html_btn = QPushButton("Copiar HTML")
        self.copy_html_btn.clicked.connect(self.copy_html)
        self.copy_html_btn.setEnabled(False)
        
        toolbar.addWidget(self.copy_raw_btn)
        toolbar.addWidget(self.copy_html_btn)
        
        layout.addWidget(toolbar)
        
        self.splitter = QSplitter(Qt.Horizontal)
        
        if WEB_ENGINE_AVAILABLE:
            self.web_view = QWebEngineView()
            self.web_view.setContextMenuPolicy(Qt.CustomContextMenu)
        else:
            self.web_view = QTextBrowser()
            self.web_view.setOpenExternalLinks(True)
            
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("JetBrains Mono", 10))
        self.code_editor.setReadOnly(True)
        self.code_editor.setPlaceholderText("O markdown aparecerá aqui...")
        
        self.markdown_highlighter = MarkdownHighlighter(self.code_editor.document(), self.theme)
        
        self.splitter.addWidget(self.web_view)
        self.splitter.addWidget(self.code_editor)
        self.splitter.setSizes([1, 0])
        
        layout.addWidget(self.splitter, 1)
        
    def set_markdown_content(self, markdown_text):
        self.raw_markdown = markdown_text
        self.code_editor.setPlainText(markdown_text)
        html_content = self.markdown_renderer.render_to_html(markdown_text)
        self.web_view.setHtml(html_content)
        
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
            mime_data.setText(self.raw_markdown)  # fallback texto
            clipboard.setMimeData(mime_data)
