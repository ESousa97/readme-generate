import re
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from .theme import FONT_FAMILY_MONO

class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent, theme):
        super().__init__(parent)
        self.theme = theme
        self._setup_highlighting_rules()

    def _setup_highlighting_rules(self):
        self.highlighting_rules = []
        
        header_format = QTextCharFormat()
        header_format.setForeground(QColor(self.theme.accent))
        header_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((r'^#{1,6}\s.*', header_format))
        
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((r'\*\*.*?\*\*', bold_format))
        
        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        self.highlighting_rules.append((r'\*.*?\*', italic_format))
        
        code_format = QTextCharFormat()
        code_format.setBackground(QColor(self.theme.surface_variant))
        code_format.setForeground(QColor(self.theme.text_accent))
        code_format.setFontFamily(FONT_FAMILY_MONO)
        self.highlighting_rules.append((r'```.*?```', code_format))
        self.highlighting_rules.append((r'`.*?`', code_format))

    def highlightBlock(self, text):
        for pattern, format_obj in self.highlighting_rules:
            for match in re.finditer(pattern, text, re.MULTILINE):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format_obj)
