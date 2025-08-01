import re
import markdown
import logging

logger = logging.getLogger(__name__)

try:
    from markdown.extensions import codehilite, fenced_code, tables, toc
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False


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
        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>{github_css}</style>
</head>
<body>
<div class="markdown-body">
{content}
</div>
</body>
</html>"""
    
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
