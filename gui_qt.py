"""PyQt6 版 Git 管理器 - 像素级移植 tkinter 版"""
import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QPushButton, QLineEdit, QTreeWidget, QTreeWidgetItem,
    QPlainTextEdit, QScrollArea, QMenu, QCheckBox, QSizePolicy, QStatusBar
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QColor, QFont, QAction, QCursor

from theme_qt import DARK_STYLE, ICON_DIR
from git_backend import GitBackend, GitFile

F = "Microsoft YaHei UI"
FM = "Cascadia Code"


def get_icon(name):
    path = os.path.join(ICON_DIR, f"{name}.png")
    return QIcon(path) if os.path.exists(path) else QIcon()


class GitManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Git Manager - 源代码管理")
        self.setGeometry(100, 100, 1280, 820)
        self.setMinimumSize(960, 640)
        self.git = GitBackend()
        self.repo_opened = False
        self._build_ui()
        self._show_welcome()

    def _build_ui(self):
        central = QWidget()
        central.setStyleSheet("background-color: #1e1e1e;")
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 左侧图标栏
        self._build_icon_bar(layout)
        # 源代码管理面板
        self._build_source_panel(layout)
        # 右侧主区域
        self._build_main_area(layout)
        # 状态栏
        self._build_status_bar()

    def _build_icon_bar(self, parent):
        bar = QFrame()
        bar.setFixedWidth(48)
        bar.setStyleSheet("background-color: #252526; border: none;")
        lay = QVBoxLayout(bar)
        lay.setContentsMargins(0, 4, 0, 0)
        lay.setSpacing(1)

        for ic, active in [("⑂", True), ("🔍", False), ("⊞", False), ("▶", False)]:
            b = QPushButton(ic)
            b.setFixedSize(48, 48)
            b.setStyleSheet(f"""
                QPushButton {{ background: {'#37373d' if active else 'transparent'}; color: {'#ffffff' if active else '#969696'}; border: none; font-size: 20px; }}
                QPushButton:hover {{ background: #37373d; }}
            """)
            lay.addWidget(b)

        lay.addStretch()
        s = QPushButton("⚙")
        s.setFixedSize(48, 48)
        s.setStyleSheet("QPushButton { background: transparent; color: #969696; border: none; font-size: 20px; } QPushButton:hover { background: #37373d; }")
        lay.addWidget(s)
        parent.addWidget(bar)

    def _build_source_panel(self, parent):
        self.panel = QFrame()
        self.panel.setFixedWidth(340)
        self.panel.setStyleSheet("background-color: #252526; border: none;")
        lay = QVBoxLayout(self.panel)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # 标题行
        hdr = QHBoxLayout()
        hdr.setContentsMargins(12, 10, 12, 4)
        t = QLabel("源代码管理")
        t.setStyleSheet(f"font-family: '{F}'; font-size: 14px; font-weight: bold; color: #cccccc;")
        hdr.addWidget(t)
        hdr.addStretch()
        mb = QPushButton("⋯")
        mb.setFixedSize(30, 30)
        mb.setStyleSheet("QPushButton { background: transparent; color: #969696; border: none; font-size: 16px; } QPushButton:hover { background: #37373d; }")
        mb.clicked.connect(self._show_more_menu)
        hdr.addWidget(mb)
        lay.addLayout(hdr)

        # 内容区
        self.panel_scroll = QScrollArea()
        self.panel_scroll.setWidgetResizable(True)
        self.panel_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.panel_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.panel_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; } QScrollBar:vertical { background: transparent; width: 8px; } QScrollBar::handle:vertical { background: #424242; border-radius: 4px; min-height: 20px; }")
        self.panel_content = QWidget()
        self.panel_content.setStyleSheet("background: transparent;")
        self.panel_layout = QVBoxLayout(self.panel_content)
        self.panel_layout.setContentsMargins(8, 0, 8, 0)
        self.panel_layout.setSpacing(0)
        self.panel_scroll.setWidget(self.panel_content)
        lay.addWidget(self.panel_scroll, 1)

        # 底部面板
        bot = QFrame()
        bot.setFixedHeight(140)
        bot.setStyleSheet("background-color: #2d2d2d;")
        bot_lay = QVBoxLayout(bot)
        bot_lay.setContentsMargins(12, 8, 12, 6)
        bot_lay.setSpacing(2)
        self.repo_name_lbl = QLabel("▸ 存储库  未打开仓库")
        self.repo_name_lbl.setStyleSheet(f"font-family: '{F}'; font-size: 14px; color: #cccccc;")
        bot_lay.addWidget(self.repo_name_lbl)

        # 远程存储库
        rh = QHBoxLayout()
        rl = QLabel("远程存储库")
        rl.setStyleSheet(f"font-family: '{F}'; font-size: 11px; font-weight: bold; color: #969696;")
        rh.addWidget(rl)
        rh.addStretch()
        rb = QPushButton("刷新")
        rb.setStyleSheet("QPushButton { background: transparent; color: #969696; font-size: 10px; border: none; } QPushButton:hover { color: #cccccc; }")
        rb.setFixedWidth(40)
        rh.addWidget(rb)
        bot_lay.addLayout(rh)

        self.remote_scroll = QScrollArea()
        self.remote_scroll.setWidgetResizable(True)
        self.remote_scroll.setFixedHeight(20)
        self.remote_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.remote_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        self.remote_list_w = QWidget()
        self.remote_list_w.setStyleSheet("background: transparent;")
        self.remote_list_lay = QVBoxLayout(self.remote_list_w)
        self.remote_list_lay.setContentsMargins(0, 0, 0, 0)
        self.remote_list_lay.setSpacing(0)
        self.remote_scroll.setWidget(self.remote_list_w)
        bot_lay.addWidget(self.remote_scroll)

        # 推送按钮
        pf = QHBoxLayout()
        pf.setSpacing(4)
        pb1 = QPushButton("推送选中")
        pb1.setStyleSheet(f"QPushButton {{ background: #0e639c; color: white; border: none; border-radius: 4px; font-family: '{F}'; font-size: 10px; padding: 4px 12px; }} QPushButton:hover {{ background: #1177bb; }}")
        pb1.setFixedHeight(24)
        pb1.clicked.connect(self._push_selected)
        pf.addWidget(pb1)
        pb2 = QPushButton("全部推送")
        pb2.setStyleSheet(f"QPushButton {{ background: #238636; color: white; border: none; border-radius: 4px; font-family: '{F}'; font-size: 10px; padding: 4px 12px; }} QPushButton:hover {{ background: #2ea043; }}")
        pb2.setFixedHeight(24)
        pb2.clicked.connect(self._push_all_remotes)
        pf.addWidget(pb2)
        bot_lay.addLayout(pf)
        self.remote_checkboxes = []

        lay.addWidget(bot)
        parent.addWidget(self.panel)

    def _build_main_area(self, parent):
        self.main_frame = QFrame()
        self.main_frame.setStyleSheet("background-color: #1e1e1e;")
        self.main_layout = QVBoxLayout(self.main_frame)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        parent.addWidget(self.main_frame, 1)

    def _build_status_bar(self):
        sb = self.statusBar()
        sb.setFixedHeight(28)
        sb.setStyleSheet("background-color: #252526; border: none;")
        self.branch_icon_lbl = QLabel("⑂")
        self.branch_icon_lbl.setStyleSheet(f"font-family: '{F}'; font-size: 22px; color: #cccccc; padding: 0 4px 0 8px;")
        sb.addWidget(self.branch_icon_lbl)
        self.branch_lbl = QLabel("")
        self.branch_lbl.setStyleSheet(f"font-family: '{F}'; font-size: 14px; color: #cccccc; padding: 0 8px 0 2px;")
        sb.addWidget(self.branch_lbl)
        s1 = QLabel("↻ 0↓ 0↑")
        s1.setStyleSheet(f"font-family: '{F}'; font-size: 14px; color: #cccccc; padding: 0 6px;")
        sb.addWidget(s1)
        s2 = QLabel("⊘ 0 ⚠ 0")
        s2.setStyleSheet(f"font-family: '{F}'; font-size: 14px; color: #cccccc; padding: 0 6px;")
        sb.addWidget(s2)
        sb.addPermanentWidget(s2)
        mem = QLabel("MEM 93%")
        mem.setStyleSheet(f"font-family: '{F}'; font-size: 14px; color: #cccccc; padding: 0 12px;")
        sb.addPermanentWidget(mem)

    # ═══════════════════════════════════════════════════════
    # 欢迎页
    # ═══════════════════════════════════════════════════════
    def _show_welcome(self):
        self.repo_opened = False
        self._clear_panel()
        self._clear_main()

        # 左侧面板内容
        self.panel_layout.addSpacing(24)
        ic = QLabel("⑂")
        ic.setStyleSheet("font-size: 42px; color: #4FC1FF;")
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.panel_layout.addWidget(ic)

        n = QLabel("Git Manager")
        n.setStyleSheet(f"font-family: '{F}'; font-size: 15px; font-weight: bold; color: #ffffff;")
        n.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.panel_layout.addWidget(n)

        s = QLabel("源代码管理工具")
        s.setStyleSheet(f"font-family: '{F}'; font-size: 18px; color: #6a6a6a;")
        s.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.panel_layout.addWidget(s)
        self.panel_layout.addSpacing(14)

        self._add_separator()

        btn = QPushButton("📂  打开项目文件夹")
        btn.setFixedHeight(44)
        btn.setStyleSheet(f"QPushButton {{ background: #0e639c; color: white; border: none; border-radius: 6px; font-family: '{F}'; font-size: 11px; font-weight: bold; }} QPushButton:hover {{ background: #1177bb; }}")
        btn.clicked.connect(self._open_folder)
        self.panel_layout.addWidget(btn)
        self.panel_layout.addSpacing(6)

        h = QLabel("选择你的项目文件夹以使用分布式版本管理系统")
        h.setStyleSheet(f"font-family: '{F}'; font-size: 14px; color: #6a6a6a;")
        h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h.setWordWrap(True)
        self.panel_layout.addWidget(h)
        self.panel_layout.addSpacing(12)

        self._add_separator()
        self.panel_layout.addSpacing(10)

        for icon, title, desc in [("⑂","版本控制","追踪文件变更"),("⊕","分支管理","并行开发"),("↻","远程同步","推拉协作")]:
            row = QHBoxLayout()
            row.setSpacing(4)
            ic_lbl = QLabel(icon)
            ic_lbl.setStyleSheet(f"font-size: 18px; color: #4FC1FF;")
            ic_lbl.setFixedWidth(22)
            row.addWidget(ic_lbl)
            col = QVBoxLayout()
            col.setSpacing(0)
            t = QLabel(title)
            t.setStyleSheet(f"font-family: '{F}'; font-size: 13px; font-weight: bold; color: #cccccc;")
            d = QLabel(desc)
            d.setStyleSheet(f"font-family: '{F}'; font-size: 14px; color: #6a6a6a;")
            col.addWidget(t)
            col.addWidget(d)
            row.addLayout(col, 1)
            self.panel_layout.addLayout(row)
            self.panel_layout.addSpacing(2)

        self.panel_layout.addStretch()

        # 右侧主区域 - 使用容器确保居中
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.setSpacing(0)

        ri = QLabel("⑂")
        ri.setStyleSheet("font-size: 56px; color: #4FC1FF;")
        ri.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(ri)
        container_layout.addSpacing(8)

        rn = QLabel("Open Git Manager")
        rn.setStyleSheet(f"font-family: '{F}'; font-size: 22px; font-weight: bold; color: #ffffff;")
        rn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(rn)
        container_layout.addSpacing(4)

        rs = QLabel("Git GUI Client")
        rs.setStyleSheet(f"font-family: '{F}'; font-size: 18px; color: #6a6a6a;")
        rs.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(rs)
        container_layout.addSpacing(28)

        # 快捷键卡片
        sc = QFrame()
        sc.setFixedWidth(280)
        sc.setFixedHeight(150)
        sc.setStyleSheet("background-color: #2d2d2d; border-radius: 10px;")
        sc_lay = QVBoxLayout(sc)
        sc_lay.setContentsMargins(53, 10, 16, 10)
        sc_lay.setSpacing(4)
        sc_t = QLabel("快捷键")
        sc_t.setStyleSheet(f"font-family: '{F}'; font-size: 13px; font-weight: bold; color: #969696;")
        sc_lay.addWidget(sc_t)
        for key, desc in [("Ctrl+Enter","提交更改"),("Ctrl+Shift+K","推送"),("Ctrl+T","同步")]:
            row = QHBoxLayout()
            row.setSpacing(0)
            k = QLabel(key)
            k.setFixedWidth(120)
            k.setStyleSheet(f"font-family: '{FM}'; font-size: 12px; font-weight: bold; color: #4FC1FF;")
            row.addWidget(k)
            v = QLabel(desc)
            v.setStyleSheet(f"font-family: '{F}'; font-size: 13px; color: #969696;")
            row.addWidget(v)
            row.addStretch()
            sc_lay.addLayout(row)
        container_layout.addWidget(sc)
        container_layout.addStretch()

        self.main_layout.addWidget(container)

    def _add_separator(self):
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #3c3c3c;")
        self.panel_layout.addWidget(sep)

    # ═══════════════════════════════════════════════════════
    # 不是 Git 仓库
    # ═══════════════════════════════════════════════════════
    def _show_not_git_repo(self, name):
        self._clear_panel()
        self._clear_main()
        info = QLabel("当前打开的文件夹中没有 Git 存储库。\n可初始化一个仓库。它将实现 Git\n提供支持的源代码管理功能。")
        info.setStyleSheet(f"font-family: '{F}'; font-size: 15px; color: #cccccc;")
        info.setWordWrap(True)
        self.panel_layout.addWidget(info)
        self.panel_layout.addSpacing(8)

        init_btn = QPushButton("初始化仓库")
        init_btn.setFixedHeight(42)
        init_btn.setStyleSheet(f"QPushButton {{ background: transparent; border: 1px solid #3c3c3c; border-radius: 4px; color: #cccccc; font-family: '{F}'; font-size: 15px; }} QPushButton:hover {{ background: #37373d; }}")
        init_btn.clicked.connect(self._init_repo)
        self.panel_layout.addWidget(init_btn)
        self.panel_layout.addSpacing(12)

        gh_info = QLabel("可以直接将此文件夹发布到 GitHub 仓库。\n发布后，你将有权访问由 Git 和\nGitHub 提供支持的源代码管理功能。")
        gh_info.setStyleSheet(f"font-family: '{F}'; font-size: 13px; color: #6a6a6a;")
        gh_info.setWordWrap(True)
        self.panel_layout.addWidget(gh_info)
        self.panel_layout.addSpacing(8)

        gh_btn = QPushButton("  发布到 GitHub")
        gh_btn.setFixedHeight(42)
        gh_icon_path = os.path.join(os.path.dirname(__file__), "resource", "system", "icon", "GitHub", "github.png")
        if os.path.exists(gh_icon_path):
            gh_btn.setIcon(QIcon(gh_icon_path))
            gh_btn.setIconSize(QSize(28, 28))
        gh_btn.setStyleSheet(f"QPushButton {{ background: transparent; border: 1px solid #3c3c3c; border-radius: 4px; color: #cccccc; font-family: '{F}'; font-size: 15px; text-align: left; padding-left: 12px; }} QPushButton:hover {{ background: #37373d; }}")
        gh_btn.clicked.connect(self._open_folder)
        self.panel_layout.addWidget(gh_btn)
        self.panel_layout.addStretch()
        self.repo_name_lbl.setText(f"▸ 存储库  {name}")

        ph = QLabel("选择文件查看差异")
        ph.setStyleSheet(f"font-family: '{F}'; font-size: 16px; color: #6a6a6a;")
        ph.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(ph)

    # ═══════════════════════════════════════════════════════
    # 仓库视图
    # ═══════════════════════════════════════════════════════
    def _show_repo_view(self):
        self.repo_opened = True
        self._clear_panel()

        # 更改标题栏
        ch = QHBoxLayout()
        ch.setContentsMargins(4, 5, 4, 0)
        ch.setSpacing(0)
        self._collapse_btn = QPushButton("▾ 更改")
        self._collapse_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: #cccccc; border: none; font-family: '{F}'; font-size: 18px; text-align: left; padding: 4px 8px; }} QPushButton:hover {{ background: #37373d; }}")
        self._collapse_btn.clicked.connect(self._toggle_files)
        ch.addWidget(self._collapse_btn)
        ch.addStretch()
        for txt, cmd in [("✓",self._stage_all),("↻",self._refresh),("⋯",self._show_more_menu)]:
            b = QPushButton(txt)
            b.setFixedSize(30, 34)
            b.setStyleSheet(f"QPushButton {{ background: transparent; color: #cccccc; border: none; font-family: '{F}'; font-size: 14px; }} QPushButton:hover {{ background: #37373d; }}")
            b.clicked.connect(cmd)
            ch.addWidget(b)
        self.panel_layout.addLayout(ch)

        # 输入框
        ci = QHBoxLayout()
        ci.setContentsMargins(4, 8, 4, 0)
        self.commit_entry = QLineEdit()
        self.commit_entry.setPlaceholderText("提交变更内容...")
        self.commit_entry.setStyleSheet(f"QLineEdit {{ background: #3c3c3c; border: 1px solid #3c3c3c; border-radius: 4px; color: #cccccc; padding: 8px 10px; font-family: '{F}'; font-size: 18px; }} QLineEdit:focus {{ border-color: #007fd4; }}")
        self.commit_entry.returnPressed.connect(self._commit)
        ci.addWidget(self.commit_entry, 1)
        ai = QPushButton("✦")
        ai.setFixedSize(28, 40)
        ai.setStyleSheet(f"QPushButton {{ background: #3c3c3c; color: #73c991; border: none; font-size: 14px; }} QPushButton:hover {{ background: #454545; }}")
        ai.clicked.connect(self._ai_gen)
        ci.addWidget(ai)
        self.panel_layout.addLayout(ci)

        # 提交按钮
        cb = QHBoxLayout()
        cb.setContentsMargins(4, 5, 4, 0)
        self.commit_btn = QPushButton("✓ 提交 Ctrl+Enter")
        self.commit_btn.setFixedHeight(36)
        self.commit_btn.setStyleSheet(f"QPushButton {{ background: #0e639c; color: white; border: none; border-radius: 4px; font-family: '{F}'; font-size: 12px; font-weight: bold; }} QPushButton:hover {{ background: #1177bb; }}")
        self.commit_btn.clicked.connect(self._commit)
        cb.addWidget(self.commit_btn, 1)
        drop = QPushButton("▾")
        drop.setFixedSize(28, 36)
        drop.setStyleSheet(f"QPushButton {{ background: #0e639c; color: white; border: none; border-radius: 4px; font-size: 12px; }} QPushButton:hover {{ background: #1177bb; }}")
        drop.clicked.connect(self._show_commit_menu)
        cb.addWidget(drop)
        self.panel_layout.addLayout(cb)
        self.panel_layout.addSpacing(4)

        # 文件树
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderHidden(True)
        self.file_tree.setRootIsDecorated(False)
        self.file_tree.setIndentation(0)
        self.file_tree.setAnimated(False)
        self.file_tree.setUniformRowHeights(True)
        self.file_tree.setFrameShape(QFrame.Shape.NoFrame)
        self.file_tree.setStyleSheet(f"""
            QTreeWidget {{ background: transparent; border: none; outline: none; font-family: '{F}'; font-size: 12px; }}
            QTreeWidget::item {{ padding: 5px 0; border: none; }}
            QTreeWidget::item:selected {{ background: #04395e; }}
            QTreeWidget::item:hover {{ background: #37373d; }}
        """)
        self.file_tree.itemDoubleClicked.connect(self._on_file_double_click)
        self.file_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self._on_file_context_menu)
        self.panel_layout.addWidget(self.file_tree, 1)

        # 右侧
        self._clear_main()
        ph = QLabel("选择文件查看差异")
        ph.setStyleSheet(f"font-family: '{F}'; font-size: 16px; color: #6a6a6a;")
        ph.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(ph)
        self._refresh()

    def _toggle_files(self):
        if self.file_tree.isVisible():
            self.file_tree.hide()
            self._collapse_btn.setText("▸ 更改")
        else:
            self.file_tree.show()
            self._collapse_btn.setText("▾ 更改")

    # ═══════════════════════════════════════════════════════
    # Diff 视图
    # ═══════════════════════════════════════════════════════
    def _show_diff(self, f: GitFile):
        self._clear_main()
        tb = QHBoxLayout()
        tb.setContentsMargins(8, 6, 8, 6)
        path_lbl = QLabel(f"  {f.path}  ({f.status_text})")
        path_lbl.setStyleSheet(f"font-family: '{FM}'; font-size: 15px; color: #cccccc;")
        tb.addWidget(path_lbl)
        tb.addStretch()
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: #969696; border: none; font-size: 16px; }} QPushButton:hover {{ background: #37373d; }}")
        close_btn.clicked.connect(self._show_repo_view)
        tb.addWidget(close_btn)
        self.main_layout.addLayout(tb)

        diff = self.git.get_file_diff(f.path, f.staged)
        diff_view = QPlainTextEdit()
        diff_view.setPlainText(diff if diff else "没有差异")
        diff_view.setReadOnly(True)
        diff_view.setStyleSheet(f"QPlainTextEdit {{ background: #1e1e1e; color: #cccccc; border: none; font-family: '{FM}'; font-size: 15px; padding: 8px; }}")
        self.main_layout.addWidget(diff_view, 1)

    # ═══════════════════════════════════════════════════════
    # 文件列表
    # ═══════════════════════════════════════════════════════
    def _get_icon_name(self, path):
        base = os.path.basename(path)
        ext = os.path.splitext(path)[1].lower()
        special = {'.gitignore':'gitignore','Dockerfile':'docker','Makefile':'make','README.md':'md'}
        if base in special: return special[base]
        ext_map = {
            '.py':'py','.js':'js','.ts':'ts','.html':'html','.htm':'html','.css':'css',
            '.json':'json','.md':'md','.txt':'txt','.xml':'xml','.yaml':'yaml','.yml':'yaml',
            '.sh':'sh','.go':'go','.java':'java','.c':'c','.cpp':'cpp','.h':'h',
            '.rs':'rs','.rb':'rb','.php':'php','.vue':'vue','.jsx':'jsx','.tsx':'tsx',
            '.sql':'sql','.toml':'toml','.ini':'ini','.log':'log',
        }
        return ext_map.get(ext, 'default')

    def _refresh(self):
        if not self.git.is_git_repo(): return
        branch, files, remotes = self.git.get_all_info()
        self.repo_name_lbl.setText(f"▸ 存储库  {os.path.basename(self.git.repo_path)}")
        self.branch_lbl.setText(branch)
        if not hasattr(self, 'file_tree'): return

        self.file_tree.clear()
        staged = [f for f in files if f.staged]
        unstaged = [f for f in files if not f.staged]
        sc = {'M':'#e2c08d','A':'#73c991','D':'#f47067','R':'#82aaff','?':'#c59fff'}

        for group, items, label in [("staged", staged, "暂存的更改"), ("unstaged", unstaged, "更改")]:
            if not items: continue
            hdr = QTreeWidgetItem(self.file_tree)
            hdr.setText(0, f"▾ {label}  {len(items)}")
            hdr.setForeground(0, QColor("#969696"))
            hdr.setFlags(Qt.ItemFlag.NoItemFlags)
            for f in items:
                item = QTreeWidgetItem(hdr)
                item.setText(0, f"  {f.path}")
                item.setForeground(0, QColor("#cccccc"))
                item.setIcon(0, get_icon(self._get_icon_name(f.path)))
                item.setData(0, Qt.ItemDataRole.UserRole, f)

        self.file_tree.expandAll()
        self._refresh_remotes(remotes)

    def _refresh_remotes(self, remotes=None):
        if remotes is None:
            _, _, remotes = self.git.get_all_info()
        for i in reversed(range(self.remote_list_lay.count())):
            w = self.remote_list_lay.itemAt(i).widget()
            if w: w.deleteLater()
        self.remote_checkboxes = []
        if not remotes:
            n = QLabel("无远程仓库")
            n.setStyleSheet(f"font-family: '{F}'; font-size: 10px; color: #6a6a6a;")
            self.remote_list_lay.addWidget(n)
            return
        branch = self.git.get_current_branch()
        for r in remotes:
            cb = QCheckBox(f"{r}  ({branch})")
            cb.setChecked(True)
            self.remote_list_lay.addWidget(cb)
            self.remote_checkboxes.append((r, cb))

    # ═══════════════════════════════════════════════════════
    # 事件
    # ═══════════════════════════════════════════════════════
    def _on_file_double_click(self, item, col):
        f = item.data(0, Qt.ItemDataRole.UserRole)
        if f: self._show_diff(f)

    def _on_file_context_menu(self, pos):
        item = self.file_tree.itemAt(pos)
        if not item: return
        f = item.data(0, Qt.ItemDataRole.UserRole)
        if not f: return
        menu = QMenu(self)
        menu.addAction("打开文件", lambda: self.git.open_file(f.path))
        menu.addAction("打开差异", lambda: self._show_diff(f))
        menu.addSeparator()
        if f.staged:
            menu.addAction("取消暂存", lambda: (self.git.unstage_file(f.path), self._refresh()))
        else:
            menu.addAction("暂存文件", lambda: (self.git.stage_file(f.path), self._refresh()))
        menu.addAction("丢弃更改", lambda: self._discard(f.path))
        menu.addSeparator()
        full = os.path.join(self.git.repo_path, f.path)
        menu.addAction("在资源管理器中显示",
            lambda: os.startfile(os.path.dirname(full)) if os.path.exists(full) else None)
        menu.exec(self.file_tree.viewport().mapToGlobal(pos))

    # ═══════════════════════════════════════════════════════
    # Git 操作
    # ═══════════════════════════════════════════════════════
    def _open_folder(self):
        from PyQt6.QtWidgets import QFileDialog
        p = QFileDialog.getExistingDirectory(self, "选择项目文件夹")
        if not p: return
        self.git.repo_path = p
        if self.git.is_git_repo(): self._show_repo_view()
        else: self._show_not_git_repo(os.path.basename(p))

    def _init_repo(self):
        ok, _ = self.git.init_repo()
        if ok: self._show_repo_view()

    def _stage_all(self): self.git.stage_all(); self._refresh()
    def _unstage_all(self): self.git.unstage_all(); self._refresh()

    def _discard(self, p):
        from PyQt6.QtWidgets import QMessageBox
        if QMessageBox.question(self, "确认", f"确定丢弃 {p} 的更改？") == QMessageBox.StandardButton.Yes:
            self.git.discard_file(p); self._refresh()

    def _commit(self):
        msg = self.commit_entry.text().strip()
        if not msg: return
        ok, _ = self.git.commit(msg)
        if ok: self.commit_entry.clear(); self._refresh()

    def _push(self): self.git.push(); self._refresh()
    def _pull(self): self.git.pull(); self._refresh()
    def _pull_rebase(self): self.git.pull(rebase=True); self._refresh()
    def _fetch(self): self.git.fetch(); self._refresh()
    def _sync(self): self.git.sync(); self._refresh()

    def _push_selected(self):
        branch = self.git.get_current_branch()
        for remote, cb in self.remote_checkboxes:
            if cb.isChecked():
                self.git.push(remote, branch)
        self._refresh()

    def _push_all_remotes(self):
        branch = self.git.get_current_branch()
        for remote, _ in self.remote_checkboxes:
            self.git.push(remote, branch)
        self._refresh()

    def _ai_gen(self):
        files = self.git.get_changed_files()
        if files:
            names = [os.path.basename(f.path) for f in files[:3]]
            msg = f"更新: {', '.join(names)}"
            if len(files) > 3: msg += f" 等 {len(files)} 个文件"
            self.commit_entry.setText(msg)

    def _commit_amend(self):
        msg = self.commit_entry.text().strip() or None
        self.git.commit(msg or "amend", amend=True)
        self.commit_entry.clear(); self._refresh()

    def _commit_all(self):
        msg = self.commit_entry.text().strip() or "更新所有文件"
        self.git.commit_all(msg); self.commit_entry.clear(); self._refresh()

    def _commit_push(self):
        msg = self.commit_entry.text().strip()
        if not msg: return
        if self.git.commit(msg)[0]:
            self.commit_entry.clear(); self.git.push(); self._refresh()

    def _commit_sync(self):
        msg = self.commit_entry.text().strip()
        if not msg: return
        if self.git.commit(msg)[0]:
            self.commit_entry.clear(); self.git.sync(); self._refresh()

    def _commit_signed(self, flag):
        msg = self.commit_entry.text().strip() or "Signed"
        self.git._run(['commit', flag, '-m', msg])
        self.commit_entry.clear(); self._refresh()

    def _undo_last(self): self.git._run(['reset','--soft','HEAD~1']); self._refresh()

    # ═══════════════════════════════════════════════════════
    # 菜单
    # ═══════════════════════════════════════════════════════
    def _show_commit_menu(self):
        menu = QMenu(self)
        menu.addAction("提交", self._commit)
        menu.addAction("提交(修改)", self._commit_amend)
        menu.addSeparator()
        menu.addAction("提交和推送", self._commit_push)
        menu.addAction("提交和同步", self._commit_sync)
        menu.exec(QCursor.pos())

    def _show_more_menu(self):
        menu = QMenu(self)
        menu.addAction("树结构查看")
        menu.addSeparator()
        sm = menu.addMenu("查看和排序")
        sm.addAction("按名称排序"); sm.addAction("按状态排序")
        menu.addSeparator()
        menu.addAction("拉取", self._pull)
        menu.addAction("推送", self._push)
        menu.addAction("克隆", self._clone_dialog)
        menu.addAction("签出到...", self._checkout_dialog)
        menu.addAction("抓取", self._fetch)
        menu.addSeparator()
        cm = menu.addMenu("提交")
        cm.addAction("提交", self._commit)
        cm.addAction("提交已暂存文件", self._commit)
        cm.addAction("全部提交", self._commit_all)
        cm.addAction("撤消上次提交", self._undo_last)
        cm.addSeparator()
        cm.addAction("提交(修改)", self._commit_amend)
        cm.addSeparator()
        cm.addAction("提交(已签收)", lambda: self._commit_signed("--signoff"))
        cm.addAction("提交(已签名)", lambda: self._commit_signed("--gpg-sign"))
        ch = menu.addMenu("更改")
        ch.addAction("暂存所有更改", self._stage_all)
        ch.addAction("取消暂存所有更改", self._unstage_all)
        ch.addAction("放弃所有更改", self._discard_all)
        sp = menu.addMenu("拉取, 推送")
        sp.addAction("同步", self._sync); sp.addSeparator()
        sp.addAction("拉取", self._pull)
        sp.addAction("拉取(变基)", self._pull_rebase)
        sp.addSeparator(); sp.addAction("推送", self._push)
        sp.addSeparator(); sp.addAction("抓取", self._fetch)
        bm = menu.addMenu("分支")
        bm.addAction("合并...", self._merge_dialog)
        bm.addAction("变基分支...", self._rebase_dialog)
        bm.addSeparator()
        bm.addAction("创建分支...", self._create_branch_dialog)
        bm.addSeparator()
        bm.addAction("重命名分支...", self._rename_branch_dialog)
        bm.addAction("删除分支...", self._delete_branch_dialog)
        rm = menu.addMenu("远程")
        rm.addAction("添加远程存储库...", self._add_remote_dialog)
        rm.addAction("删除远程存储库", self._remove_remote_dialog)
        st = menu.addMenu("存储")
        st.addAction("储藏", lambda: (self.git.stash(), self._refresh()))
        st.addAction("储藏(包含未跟踪)", lambda: (self.git.stash(True), self._refresh()))
        st.addSeparator()
        st.addAction("应用最新储藏", lambda: (self.git.stash_apply(), self._refresh()))
        st.addAction("弹出最新储藏", lambda: (self.git.stash_pop(), self._refresh()))
        st.addSeparator()
        st.addAction("删除所有储藏...", lambda: (self.git.stash_clear(), self._refresh()))
        tg = menu.addMenu("标记")
        tg.addAction("创建标记...", self._create_tag_dialog)
        tg.addAction("删除标签...", self._delete_tag_dialog)
        tg.addSeparator()
        tg.addAction("推送标记", lambda: (self.git.push_tags(), self._refresh()))
        menu.addSeparator()
        menu.addAction("显示 GIT 输出")
        menu.exec(QCursor.pos())

    # ═══════════════════════════════════════════════════════
    # 对话框
    # ═══════════════════════════════════════════════════════
    def _dialog(self, title, fields, cb):
        from PyQt6.QtWidgets import QInputDialog
        vals = []
        for label, default in fields:
            text, ok = QInputDialog.getText(self, title, label, text=default)
            if not ok: return
            vals.append(text)
        cb(vals)

    def _create_branch_dialog(self):
        self._dialog("创建分支", [("新分支名","")], lambda v: (self.git.create_branch(v[0]), self._refresh()))
    def _rename_branch_dialog(self):
        self._dialog("重命名分支", [("当前名称", self.git.get_current_branch()), ("新名称","")], lambda v: (self.git.rename_branch(v[0], v[1]), self._refresh()))
    def _delete_branch_dialog(self):
        bs = [b.name for b in self.git.get_branches() if not b.is_current and not b.is_remote]
        self._dialog("删除分支", [("分支名", bs[0] if bs else "")], lambda v: (self.git.delete_branch(v[0]), self._refresh()))
    def _checkout_dialog(self):
        bs = [b.name for b in self.git.get_branches() if not b.is_current]
        self._dialog("签出到分支", [("分支名", bs[0] if bs else "")], lambda v: (self.git.switch_branch(v[0]), self._refresh()))
    def _merge_dialog(self):
        bs = [b.name for b in self.git.get_branches() if not b.is_current and not b.is_remote]
        self._dialog("合并分支", [("分支名", bs[0] if bs else "")], lambda v: (self.git.merge(v[0]), self._refresh()))
    def _rebase_dialog(self):
        bs = [b.name for b in self.git.get_branches() if not b.is_current and not b.is_remote]
        self._dialog("变基到分支", [("分支名", bs[0] if bs else "")], lambda v: (self.git.rebase(v[0]), self._refresh()))
    def _add_remote_dialog(self):
        self._dialog("添加远程存储库", [("名称","origin"), ("URL","")], lambda v: (self.git.add_remote(v[0], v[1]), self._refresh()))
    def _remove_remote_dialog(self):
        rs = self.git.get_remotes()
        self._dialog("删除远程存储库", [("远程名称", rs[0] if rs else "")], lambda v: (self.git.remove_remote(v[0]), self._refresh()))
    def _create_tag_dialog(self):
        self._dialog("创建标记", [("标签名",""), ("说明","")], lambda v: (self.git.create_tag(v[0], v[1] or None), self._refresh()))
    def _delete_tag_dialog(self):
        self._dialog("删除标签", [("标签名","")], lambda v: (self.git.delete_tag(v[0]), self._refresh()))
    def _clone_dialog(self):
        self._dialog("克隆仓库", [("仓库 URL",""), ("目标文件夹","")], lambda v: self.git.clone(v[0], v[1] or None))

    # ═══════════════════════════════════════════════════════
    # 清理
    # ═══════════════════════════════════════════════════════
    def _clear_panel(self):
        while self.panel_layout.count():
            item = self.panel_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            elif item.layout(): self._clear_layout(item.layout())

    def _clear_main(self):
        """安全清理主区域，保留布局对象"""
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
            if item.widget(): item.widget().deleteLater()
            elif item.layout(): self._clear_layout(item.layout())


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_STYLE)
    window = GitManagerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
