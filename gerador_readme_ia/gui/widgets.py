from PyQt5.QtWidgets import QPushButton, QWidget, QPlainTextEdit
from PyQt5.QtGui import QFont, QPainter, QPen, QBrush, QColor, QFontMetrics
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve

from .theme import FONT_FAMILY_DEFAULT, FONT_FAMILY_MONO, FONT_SIZE_DEFAULT, FONT_SIZE_SMALL

class AnimatedButton(QPushButton):
    def __init__(self, text, icon=None, parent=None):
        super().__init__(text, parent)
        if icon:
            self.setIcon(icon)
        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)


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
        
        step_size = 30
        step_spacing = (self.width() - len(self.steps) * step_size) // (len(self.steps) - 1) if len(self.steps) > 1 else 0
        y_center = self.height() // 2
        
        for i, step in enumerate(self.steps):
            x = i * (step_size + step_spacing) + step_size // 2
            
            if i < len(self.steps) - 1:
                next_x = (i + 1) * (step_size + step_spacing) + step_size // 2
                if i < self.current_step:
                    painter.setPen(QPen(QColor("#007AFF"), 3))
                else:
                    painter.setPen(QPen(QColor("#E5E5E7"), 2))
                painter.drawLine(x + step_size//2, y_center, next_x - step_size//2, y_center)
            
            if i <= self.current_step:
                painter.setBrush(QBrush(QColor("#007AFF")))
                painter.setPen(QPen(QColor("#007AFF"), 2))
            else:
                painter.setBrush(QBrush(QColor("#F5F5F7")))
                painter.setPen(QPen(QColor("#E5E5E7"), 2))
                
            painter.drawEllipse(x - step_size//2, y_center - step_size//2, step_size, step_size)
            
            painter.setPen(QPen(QColor("white" if i <= self.current_step else "#8B949E")))
            painter.setFont(QFont(FONT_FAMILY_DEFAULT, 10, QFont.Bold))
            painter.drawText(x - 5, y_center + 5, str(i + 1))
            
            painter.setPen(QPen(QColor("#1D1D1F" if i <= self.current_step else "#8B949E")))
            painter.setFont(QFont(FONT_FAMILY_DEFAULT, 8))
            fm = QFontMetrics(painter.font())
            text_width = fm.width(step)
            painter.drawText(x - text_width//2, y_center + 25, step)


class ConsoleWidget(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMaximumBlockCount(1000)
        self.setFont(QFont(FONT_FAMILY_MONO, FONT_SIZE_SMALL))
        
    def append_step(self, step_name, status="info", details=""):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        colors = {
            "info": "#007AFF",
            "success": "#34C759", 
            "warning": "#FF9500",
            "error": "#FF3B30",
            "progress": "#8B949E"
        }
        
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
        
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
