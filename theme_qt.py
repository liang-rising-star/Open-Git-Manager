"""深色主题 QSS 样式表"""
import os

ICON_DIR = os.path.join(os.path.dirname(__file__), "resource", "icon")

DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #1e1e1e;
    color: #cccccc;
    font-family: "Microsoft YaHei UI";
    font-size: 13px;
}

/* 左侧图标栏 */
#icon_bar {
    background-color: #252526;
    border: none;
}
#icon_bar QPushButton {
    background-color: transparent;
    color: #969696;
    border: none;
    font-size: 20px;
}
#icon_bar QPushButton:hover {
    background-color: #37373d;
}
#icon_bar QPushButton[active="true"] {
    color: #00d2ff;
    background-color: #37373d;
}

/* 源代码管理面板 */
#source_panel {
    background-color: #252526;
    border: none;
}
#source_panel QLabel {
    color: #cccccc;
}
#panel_title {
    font-size: 14px;
    font-weight: bold;
    color: #cccccc;
}
#section_header {
    font-size: 12px;
    color: #969696;
}

/* 输入框 */
QLineEdit {
    background-color: #3c3c3c;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    color: #cccccc;
    padding: 6px 10px;
    font-size: 13px;
}
QLineEdit:focus {
    border-color: #007fd4;
}
QLineEdit::placeholder {
    color: #969696;
}

/* 按钮 */
QPushButton {
    border: none;
    border-radius: 4px;
    padding: 6px 16px;
    font-size: 13px;
}
#commit_btn {
    background-color: #0e639c;
    color: #ffffff;
    font-weight: bold;
    padding: 8px 16px;
}
#commit_btn:hover {
    background-color: #1177bb;
}
#commit_btn:disabled {
    background-color: #3c3c3c;
    color: #6a6a6a;
}
#green_btn {
    background-color: #238636;
    color: #ffffff;
}
#green_btn:hover {
    background-color: #2ea043;
}
#outline_btn {
    background-color: transparent;
    border: 1px solid #3c3c3c;
    color: #cccccc;
}
#outline_btn:hover {
    background-color: #37373d;
}
#small_btn {
    background-color: transparent;
    color: #969696;
    padding: 2px 6px;
    font-size: 14px;
}
#small_btn:hover {
    background-color: #37373d;
    color: #cccccc;
}

/* 文件列表 */
QTreeWidget {
    background-color: transparent;
    border: none;
    outline: none;
    font-size: 12px;
}
QTreeWidget::item {
    padding: 4px 0;
    border: none;
}
QTreeWidget::item:selected {
    background-color: #04395e;
}
QTreeWidget::item:hover {
    background-color: #37373d;
}
QTreeWidget::branch {
    background: transparent;
}

/* 状态栏 */
#status_bar {
    background-color: #252526;
    border: none;
    font-size: 11px;
    color: #969696;
}

/* 分隔线 */
#separator {
    background-color: #3c3c3c;
    max-height: 1px;
}

/* Diff 视图 */
QPlainTextEdit {
    background-color: #1e1e1e;
    color: #cccccc;
    border: none;
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 12px;
    padding: 8px;
}

/* 右键菜单 */
QMenu {
    background-color: #2d2d2d;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 24px 6px 12px;
    color: #cccccc;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #04395e;
}
QMenu::separator {
    height: 1px;
    background-color: #3c3c3c;
    margin: 4px 8px;
}
QMenu::item:disabled {
    color: #6a6a6a;
}

/* 滚动条 */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
}
QScrollBar::handle:vertical {
    background: #424242;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: #555;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: transparent;
    height: 8px;
}
QScrollBar::handle:horizontal {
    background: #424242;
    border-radius: 4px;
    min-width: 20px;
}

/* 复选框 */
QCheckBox {
    color: #cccccc;
    spacing: 8px;
    font-size: 12px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #3c3c3c;
    border-radius: 3px;
    background: transparent;
}
QCheckBox::indicator:checked {
    background-color: #0e639c;
    border-color: #0e639c;
}

/* Tab */
QTabWidget::pane {
    border: none;
}
"""
