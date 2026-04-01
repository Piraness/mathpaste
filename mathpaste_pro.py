# 依赖安装提醒：
# pip install PyQt6 latex2mathml

import sys
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPlainTextEdit, QTextBrowser, QPushButton, QSplitter, QLabel,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QMimeData, QTimer
from PyQt6.QtGui import QFont, QIcon, QColor
import latex2mathml.converter

class MathPastePro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MathPaste Pro")
        self.resize(1000, 600)
        self.init_ui()
        self.apply_modern_style()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 核心分割器：左输入，右预览
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- 左侧输入区 ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel("原始 Markdown / LaTeX 文本输入："))
        
        self.input_area = QPlainTextEdit()
        self.input_area.setPlaceholderText("在此粘贴包含公式的文本...\n支持行内公式 $...$ 和独立公式 $$...$$")
        self.input_area.textChanged.connect(self.trigger_preview) # 实时预览
        left_layout.addWidget(self.input_area)
        
        # --- 右侧预览区 ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(QLabel("富文本 / MathML 渲染预览："))
        
        self.preview_area = QTextBrowser()
        self.preview_area.setOpenExternalLinks(True)
        right_layout.addWidget(self.preview_area)

        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(right_widget)
        self.splitter.setSizes([500, 500])
        main_layout.addWidget(self.splitter)

        # --- 底部按钮 ---
        self.copy_btn = QPushButton("清洗并复制到剪贴板")
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.clicked.connect(self.process_and_copy)
        main_layout.addWidget(self.copy_btn)

        # 添加阴影效果增加高级感
        self._add_shadow(self.input_area)
        self._add_shadow(self.preview_area)
        self._add_shadow(self.copy_btn, radius=15, offset_y=3, alpha=20)

    def _add_shadow(self, widget, radius=25, offset_y=6, alpha=10):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(radius)
        shadow.setColor(QColor(0, 0, 0, alpha))
        shadow.setOffset(0, offset_y)
        widget.setGraphicsEffect(shadow)

    def trigger_preview(self):
        """实时触发预览，但不写入剪贴板"""
        self.preview_area.setHtml(self.parse_text_to_html())

    def process_and_copy(self):
        """主执行逻辑：解析、渲染、打入剪贴板"""
        html_content = self.parse_text_to_html()
        if not html_content.strip():
            return
            
        self.preview_area.setHtml(html_content)
        self.inject_to_clipboard(html_content)

    def parse_text_to_html(self):
        """核心正则提取器框架"""
        text = self.input_area.toPlainText()
        if not text:
            return ""

        parts = re.split(r'(\$\$.*?\$\$|\$.*?\$)', text, flags=re.DOTALL)
        
        html_output = []
        
        for part in parts:
            if not part:
                continue
                
            if part.startswith('$$') and part.endswith('$$'):
                latex = part[2:-2].strip()
                try:
                    mathml = latex2mathml.converter.convert(latex)
                    html_output.append(f'<div align="center" style="margin: 10px 0;">{mathml}</div>')
                except Exception as e:
                    html_output.append(f'<div style="color:red; font-weight:bold;">[构建错误: {str(e)}]</div>')
                    
            elif part.startswith('$') and part.endswith('$'):
                latex = part[1:-1].strip()
                try:
                    mathml = latex2mathml.converter.convert(latex)
                    html_output.append(f'<span>{mathml}</span>')
                except Exception as e:
                    html_output.append(f'<span style="color:red; font-weight:bold;">[构建错误: {str(e)}]</span>')
                    
            else:
                safe_text = part.replace('<', '&lt;').replace('>', '&gt;')
                safe_text = safe_text.replace('\n', '<br>')
                html_output.append(f'<span>{safe_text}</span>')
                
        return "".join(html_output)

    def inject_to_clipboard(self, html_content):
        clipboard = QApplication.clipboard()
        mime_data = QMimeData()
        
        word_compatible_html = f"""
        <html>
        <head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head>
        <body>
        {html_content}
        </body>
        </html>
        """
        
        mime_data.setHtml(word_compatible_html)
        mime_data.setText(self.input_area.toPlainText())
        
        clipboard.setMimeData(mime_data)
        self.show_success_feedback()

    def show_success_feedback(self):
        self.copy_btn.setText("✓ 复制成功！快去 Word 粘贴吧")
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #34C759; /* iOS 成功绿 */
                color: white;
                border: none;
                border-radius: 12px;
                padding: 16px;
                font-size: 16px;
                font-weight: 600;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }
        """)
        QTimer.singleShot(2000, self.reset_btn_style)

    def reset_btn_style(self):
        self.copy_btn.setText("清洗并复制到剪贴板")
        self.copy_btn.setStyleSheet(self._btn_default_style)

    def apply_modern_style(self):
        # 苹果风高级UI配色和字体体系
        apple_font = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif'
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: #F5F5F7; }} /* 苹果 macOS 系统背景色 */
            QLabel {{ 
                font-size: 14px; 
                font-weight: 600; 
                color: #86868B; /* 苹果次级灰色 */
                margin-left: 4px;
                margin-bottom: 6px; 
                font-family: {apple_font};
            }}
            QPlainTextEdit, QTextBrowser {{
                background-color: #FFFFFF;
                border: 1px solid #E5E5EA; /* 柔和的边框 */
                border-radius: 12px; /* 更圆润的角 */
                padding: 16px;
                font-size: 15px;
                color: #1D1D1F;
                line-height: 1.6;
                font-family: {apple_font};
            }}
            QPlainTextEdit:focus, QTextBrowser:focus {{ 
                border: 1px solid #007AFF; /* iOS 蓝 */
            }}
            QSplitter::handle {{ background-color: transparent; }}
            
            /* 个性化滚动条 */
            QScrollBar:horizontal {{ height: 0px; }}
            QScrollBar:vertical {{
                background: transparent;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: #D1D1D6;
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #AEAEB2;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        self._btn_default_style = f"""
            QPushButton {{
                background-color: #007AFF; /* 苹果蓝 */
                color: #FFFFFF;
                border: none;
                border-radius: 12px; /* 高级感超大圆角 */
                padding: 16px;
                font-size: 16px;
                font-weight: 600; /* 半粗体 */
                font-family: {apple_font};
            }}
            QPushButton:hover {{ background-color: #0062CC; }}
            QPushButton:pressed {{ background-color: #0056B3; }}
        """
        self.copy_btn.setStyleSheet(self._btn_default_style)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    window = MathPastePro()
    window.show()
    sys.exit(app.exec())
