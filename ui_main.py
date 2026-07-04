"""主界面 - 精确还原截图中的 VS Code 风格 Git 管理器"""
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox, Menu
from theme import *
from git_backend import GitBackend, GitFile


class GitManagerApp(ctk.CTk):
    # 统一字体配置
    F = "Microsoft YaHei UI"       # 主字体（中文+西文都能用）
    FM = "Cascadia Code"           # 等宽字体（代码）

    def __init__(self):
        super().__init__()
        self.title("Git Manager - 源代码管理")
        self.geometry("1280x820")
        self.minsize(960, 640)
        self.configure(fg_color=BG_DARK)
        self.git = GitBackend()
        self.repo_opened = False
        self.after(100, self._build_ui)

    def _build_ui(self):
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_icon_bar()
        self._build_source_panel()
        self._build_main_area()
        self._build_status_bar()
        self._show_welcome()

    # ═══════════════════════════════════════════════════════
    # 左侧图标栏
    # ═══════════════════════════════════════════════════════
    def _build_icon_bar(self):
        bar = ctk.CTkFrame(self, width=48, fg_color=BG_SIDEBAR, corner_radius=0)
        bar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        bar.grid_propagate(False)

        icons = [("⑂","源代码管理",True),("🔍","搜索",False),("⊞","扩展",False),("▶","调试",False)]
        for i,(ic,tip,active) in enumerate(icons):
            b = ctk.CTkButton(bar, text=ic, font=(self.F,24), width=48, height=48,
                              fg_color=BG_HOVER if active else "transparent",
                              hover_color=BG_HOVER, text_color=TEXT_WHITE if active else TEXT_SECONDARY,
                              corner_radius=0)
            b.grid(row=i, column=0, sticky="ew", pady=(2,0))

        bar.grid_rowconfigure(len(icons), weight=1)
        ctk.CTkButton(bar, text="⚙", font=(self.F,24), width=48, height=48,
                      fg_color="transparent", hover_color=BG_HOVER,
                      text_color=TEXT_SECONDARY, corner_radius=0).grid(row=len(icons)+1, column=0, sticky="s", pady=(0,10))

    # ═══════════════════════════════════════════════════════
    # 源代码管理面板（左侧）
    # ═══════════════════════════════════════════════════════
    def _build_source_panel(self):
        self.panel = ctk.CTkFrame(self, width=320, fg_color=BG_SIDEBAR, corner_radius=0)
        self.panel.grid(row=0, column=1, rowspan=2, sticky="nsew")
        self.panel.grid_propagate(False)
        self.panel.grid_columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(self.panel, fg_color="transparent", height=36)
        hdr.grid(row=0, column=0, sticky="ew", padx=10, pady=(8,0))
        hdr.grid_propagate(False)
        ctk.CTkLabel(hdr, text="源代码管理", font=(self.F,13,"bold"),
                     text_color=TEXT_PRIMARY).pack(side="left", padx=5)
        ctk.CTkButton(hdr, text="⋯", width=30, height=40, fg_color="transparent",
                      hover_color=BG_HOVER, text_color=TEXT_SECONDARY,
                      font=(self.F,16), command=self._show_more_menu).pack(side="right")

        self.panel_content = ctk.CTkScrollableFrame(self.panel, fg_color="transparent",
            scrollbar_button_color=BG_HOVER, scrollbar_button_hover_color=BG_INPUT)
        self.panel_content.grid(row=1, column=0, sticky="nsew", padx=0, pady=(5,0))
        self.panel.grid_rowconfigure(1, weight=1)
        self.panel_content.grid_columnconfigure(0, weight=1)

        bot = ctk.CTkFrame(self.panel, fg_color=BG_PANEL, height=80, corner_radius=0)
        bot.grid(row=2, column=0, sticky="sew")
        bot.grid_propagate(False)
        self.repo_name_lbl = ctk.CTkLabel(bot, text="▸ 存储库  未打开仓库",
            font=(self.F,14), text_color=TEXT_PRIMARY, anchor="w")
        self.repo_name_lbl.pack(fill="x", padx=10, pady=(8,3))

    # ═══════════════════════════════════════════════════════
    # 右侧主内容区域
    # ═══════════════════════════════════════════════════════
    def _build_main_area(self):
        self.main = ctk.CTkFrame(self, fg_color=BG_EDITOR, corner_radius=0)
        self.main.grid(row=0, column=2, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(0, weight=1)

    # ═══════════════════════════════════════════════════════
    # 底部状态栏
    # ═══════════════════════════════════════════════════════
    def _build_status_bar(self):
        sb = ctk.CTkFrame(self, height=30, fg_color=BG_SIDEBAR, corner_radius=0)
        sb.grid(row=2, column=0, columnspan=3, sticky="sew")
        sb.grid_propagate(False)

        left = ctk.CTkFrame(sb, fg_color="transparent")
        left.pack(side="left", fill="y", padx=5)
        self.branch_lbl = ctk.CTkLabel(left, text="⑂",
                                       font=(self.F,14), text_color=TEXT_PRIMARY)
        self.branch_lbl.pack(side="left", padx=(5,10))
        ctk.CTkLabel(left, text="↻ 0↓ 0↑", font=(self.F,14),
                     text_color=TEXT_PRIMARY).pack(side="left", padx=5)
        ctk.CTkLabel(left, text="⊘ 0 ⚠ 0", font=(self.F,14),
                     text_color=TEXT_PRIMARY).pack(side="left", padx=5)

        right = ctk.CTkFrame(sb, fg_color="transparent")
        right.pack(side="right", fill="y", padx=5)
        ctk.CTkLabel(right, text="MEM 93%", font=(self.F,14),
                     text_color=TEXT_PRIMARY).pack(side="right", padx=5)

    # ═══════════════════════════════════════════════════════
    # 欢迎页面
    # ═══════════════════════════════════════════════════════
    def _show_welcome(self):
        self.repo_opened = False
        for w in self.panel_content.winfo_children(): w.destroy()
        for w in self.main.winfo_children(): w.destroy()

        # 左侧：欢迎页
        center = ctk.CTkFrame(self.panel_content, fg_color="transparent")
        center.pack(fill="x")

        ctk.CTkLabel(center, text="⑂", font=(self.F,42),
                     text_color="#4FC1FF").pack(anchor="center", pady=(24,4))
        ctk.CTkLabel(center, text="Git Manager", font=(self.F,15,"bold"),
                     text_color=TEXT_WHITE).pack(anchor="center", pady=(0,2))
        ctk.CTkLabel(center, text="源代码管理工具",
                     font=(self.F,18), text_color=TEXT_DIM).pack(anchor="center", pady=(0,14))

        ctk.CTkFrame(center, fg_color=SEPARATOR, height=1).pack(fill="x", padx=16, pady=(0,12))

        ctk.CTkButton(center, text="📂  打开项目文件夹", fg_color=BTN_PRIMARY,
            hover_color=BTN_PRIMARY_HOVER, text_color=TEXT_WHITE,
            font=(self.F,11,"bold"), height=44, width=260, corner_radius=6,
            command=self._open_folder).pack(anchor="center", pady=(0,6))
        ctk.CTkLabel(center, text="选择你的项目文件夹以使用分布式版本管理系统",
            font=(self.F,14), text_color=TEXT_DIM, wraplength=240).pack(anchor="center", padx=16)

        ctk.CTkFrame(center, fg_color=SEPARATOR, height=1).pack(fill="x", padx=16, pady=(12,10))

        for icon, title, desc in [("⑂","版本控制","追踪文件变更"),("⊕","分支管理","并行开发"),("↻","远程同步","推拉协作")]:
            r = ctk.CTkFrame(center, fg_color="transparent")
            r.pack(fill="x", padx=14, pady=2)
            ctk.CTkLabel(r, text=icon, font=(self.F,18),
                         text_color="#4FC1FF", width=22).pack(side="left", padx=(0,4), pady=2)
            c = ctk.CTkFrame(r, fg_color="transparent")
            c.pack(side="left", fill="both", expand=True)
            ctk.CTkLabel(c, text=title, font=(self.F,13,"bold"),
                         text_color=TEXT_PRIMARY).pack(anchor="w")
            ctk.CTkLabel(c, text=desc, font=(self.F,14),
                         text_color=TEXT_DIM).pack(anchor="w")

        # 右侧：编辑器装饰
        ph = ctk.CTkFrame(self.main, fg_color=BG_EDITOR, corner_radius=0)
        ph.pack(fill="both", expand=True)
        inner = ctk.CTkFrame(ph, fg_color="transparent")
        inner.place(relx=0.5, rely=0.45, anchor="center")
        ctk.CTkLabel(inner, text="⑂", font=(self.F,56),
                     text_color="#4FC1FF").pack()
        ctk.CTkLabel(inner, text="Open Git Manager", font=(self.F,22,"bold"),
                     text_color=TEXT_WHITE).pack(pady=(12,4))
        ctk.CTkLabel(inner, text="Git GUI Client", font=(self.F,18),
                     text_color=TEXT_DIM).pack(pady=(0,28))

        sc = ctk.CTkFrame(inner, fg_color=BG_PANEL, corner_radius=10, width=280, height=150)
        sc.pack()
        sc.pack_propagate(False)
        ctk.CTkLabel(sc, text="快捷键", font=(self.F,13,"bold"),
                     text_color=TEXT_SECONDARY).pack(padx=(53,16), pady=(10,4), anchor="w")
        for key, desc in [("Ctrl+Enter","提交更改"),("Ctrl+Shift+K","推送"),("Ctrl+T","同步")]:
            r = ctk.CTkFrame(sc, fg_color="transparent")
            r.pack(fill="x", padx=(53,16), pady=1)
            ctk.CTkLabel(r, text=key, font=(self.FM,12,"bold"),
                         text_color="#4FC1FF", width=120, anchor="w").pack(side="left")
            ctk.CTkLabel(r, text=desc, font=(self.F,13),
                         text_color=TEXT_SECONDARY, anchor="w").pack(side="left")

    # ═══════════════════════════════════════════════════════
    # 不是 Git 仓库时的页面（截图13）
    # ═══════════════════════════════════════════════════════
    def _show_not_git_repo(self, folder_name):
        for w in self.panel_content.winfo_children(): w.destroy()
        for w in self.main.winfo_children(): w.destroy()

        ctk.CTkLabel(self.panel_content, text="当前打开的文件夹中没有 Git 存储库。\n可初始化一个仓库。它将实现 Git\n提供支持的源代码管理功能。",
            font=(self.F,18), text_color=TEXT_PRIMARY,
            justify="left", wraplength=280).pack(padx=10, pady=(10,10), anchor="w")
        ctk.CTkButton(self.panel_content, text="初始化仓库", fg_color=BG_INPUT,
            hover_color=BG_HOVER, text_color=TEXT_PRIMARY, font=(self.F,18),
            height=44, width=200, border_width=1, border_color=BORDER_COLOR,
            command=self._init_repo).pack(padx=10, pady=(0,12), anchor="w")
        ctk.CTkLabel(self.panel_content, text="若需详细了解如何在 VS Code 中使用\nGit 和源代码管理参阅我们的文档。",
            font=(self.F,14), text_color=TEXT_DIM,
            justify="left", wraplength=280).pack(padx=10, pady=(0,12), anchor="w")
        ctk.CTkLabel(self.panel_content, text="可以直接将此文件夹发布到 GitHub 仓库。\n发布后，你将有权访问由 Git 和\nGitHub 提供支持的源代码管理功能。",
            font=(self.F,14), text_color=TEXT_DIM,
            justify="left", wraplength=280).pack(padx=10, pady=(0,8), anchor="w")
        ctk.CTkButton(self.panel_content, text="⊕ 发布到 GitHub", fg_color=BG_INPUT,
            hover_color=BG_HOVER, text_color=TEXT_PRIMARY, font=(self.F,18),
            height=44, width=200, border_width=1, border_color=BORDER_COLOR,
            command=self._open_folder).pack(padx=10, pady=(0,10), anchor="w")
        self.repo_name_lbl.configure(text=f"▸ 存储库  {folder_name}")

        ph = ctk.CTkFrame(self.main, fg_color=BG_EDITOR, corner_radius=0)
        ph.pack(fill="both", expand=True)
        ctk.CTkLabel(ph, text="选择文件查看差异", font=(self.F,16),
                     text_color=TEXT_DIM).pack(expand=True)

    # ═══════════════════════════════════════════════════════
    # 仓库视图
    # ═══════════════════════════════════════════════════════
    def _show_repo_view(self):
        self.repo_opened = True
        for w in self.panel_content.winfo_children(): w.destroy()

        ch = ctk.CTkFrame(self.panel_content, fg_color="transparent", height=32)
        ch.pack(fill="x", padx=5, pady=(5,0))
        ch.pack_propagate(False)
        self._collapse_btn = ctk.CTkButton(ch, text="▾ 更改", width=80, height=40,
            fg_color="transparent", hover_color=BG_HOVER, text_color=TEXT_PRIMARY,
            anchor="w", font=(self.F,18), command=self._toggle_files)
        self._collapse_btn.pack(side="left")
        ops = ctk.CTkFrame(ch, fg_color="transparent")
        ops.pack(side="right")
        for txt, cmd in [("✓",self._stage_all),("↻",self._refresh),("⋯",self._show_more_menu)]:
            ctk.CTkButton(ops, text=txt, width=30, height=34, fg_color="transparent",
                hover_color=BG_HOVER, text_color=TEXT_PRIMARY,
                font=(self.F,14), command=cmd).pack(side="left", padx=1)

        ci = ctk.CTkFrame(self.panel_content, fg_color="transparent", height=36)
        ci.pack(fill="x", padx=10, pady=(8,0))
        ci.pack_propagate(False)
        self.commit_entry = ctk.CTkEntry(ci, placeholder_text="提交变更内容...",
            fg_color=BG_INPUT, text_color=TEXT_PRIMARY, border_color=BORDER_COLOR,
            font=(self.F,18), corner_radius=4)
        self.commit_entry.pack(side="left", fill="x", expand=True, padx=(0,5))
        self.commit_entry.bind("<Return>", lambda e: self._commit())
        self.commit_entry.bind("<Control-Return>", lambda e: self._commit())
        ctk.CTkButton(ci, text="✦", width=28, height=40, fg_color=BG_INPUT,
            hover_color=BG_HOVER, text_color=STATUS_ADDED,
            font=(self.F,14), command=self._ai_gen).pack(side="left")

        cb = ctk.CTkFrame(self.panel_content, fg_color="transparent", height=34)
        cb.pack(fill="x", padx=10, pady=(5,0))
        cb.pack_propagate(False)
        self.commit_btn = ctk.CTkButton(cb, text="✓ 提交 Ctrl+Enter", fg_color=BTN_PRIMARY,
            hover_color=BTN_PRIMARY_HOVER, text_color=TEXT_WHITE,
            font=(self.F,12,"bold"), height=36, command=self._commit)
        self.commit_btn.pack(side="left", fill="x", expand=True, padx=(0,3))
        ctk.CTkButton(cb, text="▾", width=28, height=36, fg_color=BTN_PRIMARY,
            hover_color=BTN_PRIMARY_HOVER, text_color=TEXT_WHITE,
            command=self._show_commit_menu).pack(side="right")

        self.files_frame = ctk.CTkFrame(self.panel_content, fg_color="transparent")
        self.files_frame.pack(fill="both", expand=True, padx=0, pady=(5,0))
        self.files_frame.grid_columnconfigure(0, weight=1)

        for w in self.main.winfo_children(): w.destroy()
        ph = ctk.CTkFrame(self.main, fg_color=BG_EDITOR, corner_radius=0)
        ph.pack(fill="both", expand=True)
        ctk.CTkLabel(ph, text="选择文件查看差异", font=(self.F,16),
                     text_color=TEXT_DIM).pack(expand=True)

    def _toggle_files(self):
        if self.files_frame.winfo_viewable():
            self.files_frame.pack_forget()
            self._collapse_btn.configure(text="▸ 更改")
        else:
            self.files_frame.pack(fill="both", expand=True, padx=0, pady=(5,0))
            self._collapse_btn.configure(text="▾ 更改")

    # ═══════════════════════════════════════════════════════
    # Diff 视图
    # ═══════════════════════════════════════════════════════
    def _show_diff_view(self, f: GitFile):
        for w in self.main.winfo_children(): w.destroy()
        tb = ctk.CTkFrame(self.main, fg_color=BG_PANEL, height=42, corner_radius=0)
        tb.pack(fill="x")
        tb.pack_propagate(False)
        ctk.CTkLabel(tb, text=f"  {f.path}  ({f.status_text})",
                     font=(self.FM,15), text_color=TEXT_PRIMARY, anchor="w").pack(side="left", padx=5)
        ctk.CTkButton(tb, text="×", width=30, height=30, fg_color="transparent",
            hover_color=BG_HOVER, text_color=TEXT_SECONDARY,
            command=self._show_repo_view).pack(side="right", padx=5)
        diff = self.git.get_file_diff(f.path, f.staged)
        txt = ctk.CTkTextbox(self.main, fg_color=BG_EDITOR, text_color=TEXT_PRIMARY,
                             font=(self.FM,15), wrap="none")
        txt.pack(fill="both", expand=True, padx=2, pady=2)
        txt.insert("1.0", diff if diff else "没有差异")
        txt.configure(state="disabled")

    # ═══════════════════════════════════════════════════════
    # 文件图标
    # ═══════════════════════════════════════════════════════
    ICON_DIR = os.path.join(os.path.dirname(__file__), "resource", "icon")

    def _get_icon_path(self, path):
        base = os.path.basename(path)
        ext = os.path.splitext(path)[1].lower()
        special = {'.gitignore':'gitignore','Dockerfile':'docker','Makefile':'make','README.md':'md'}
        if base in special: return os.path.join(self.ICON_DIR, special[base]+'.png')
        ext_map = {
            '.py':'py','.js':'js','.ts':'ts','.html':'html','.htm':'html','.css':'css',
            '.json':'json','.md':'md','.txt':'txt','.xml':'xml','.yaml':'yaml','.yml':'yaml',
            '.sh':'sh','.bat':'sh','.go':'go','.java':'java','.c':'c','.cpp':'cpp',
            '.h':'h','.rs':'rs','.rb':'rb','.php':'php','.vue':'vue','.jsx':'jsx',
            '.tsx':'tsx','.sql':'sql','.toml':'toml','.ini':'ini','.cfg':'ini','.log':'log',
        }
        return os.path.join(self.ICON_DIR, ext_map.get(ext,'default')+'.png')

    # ═══════════════════════════════════════════════════════
    # 文件列表
    # ═══════════════════════════════════════════════════════
    def _refresh(self):
        if not self.git.is_git_repo(): return
        self.repo_name_lbl.configure(text=f"▸ 存储库  {os.path.basename(self.git.repo_path)}")
        self.branch_lbl.configure(text=f"⑂ {self.git.get_current_branch()}")
        if not hasattr(self, 'files_frame'): return

        files = self.git.get_changed_files()
        for w in self.files_frame.winfo_children(): w.destroy()

        staged = [f for f in files if f.staged]
        unstaged = [f for f in files if not f.staged]
        row = 0

        if staged:
            hdr = ctk.CTkFrame(self.files_frame, fg_color="transparent", height=32)
            hdr.grid(row=row, column=0, sticky="ew", padx=5)
            hdr.grid_propagate(False)
            ctk.CTkLabel(hdr, text=f"▾ 暂存的更改  {len(staged)}",
                font=(self.F,14), text_color=TEXT_PRIMARY, anchor="w").pack(side="left")
            ctk.CTkButton(hdr, text="−", width=28, height=26, fg_color="transparent",
                hover_color=BG_HOVER, text_color=TEXT_SECONDARY,
                command=self._unstage_all).pack(side="right")
            row += 1
            for f in staged:
                self._file_row(f, row, True); row += 1

        if unstaged:
            hdr = ctk.CTkFrame(self.files_frame, fg_color="transparent", height=32)
            hdr.grid(row=row, column=0, sticky="ew", padx=5, pady=(10,0))
            hdr.grid_propagate(False)
            ctk.CTkLabel(hdr, text=f"▾ 更改  {len(unstaged)}",
                font=(self.F,14), text_color=TEXT_PRIMARY, anchor="w").pack(side="left")
            ctk.CTkButton(hdr, text="+", width=28, height=26, fg_color="transparent",
                hover_color=BG_HOVER, text_color=TEXT_SECONDARY,
                command=self._stage_all).pack(side="right")
            row += 1
            for f in unstaged:
                self._file_row(f, row, False); row += 1

        if not files:
            ctk.CTkLabel(self.files_frame, text="没有更改", font=(self.F,18),
                         text_color=TEXT_DIM).grid(row=0, column=0, pady=20)

        self.commit_btn.configure(
            text=f"✓ 提交 ({len(staged)}) Ctrl+Enter" if staged else "✓ 提交 Ctrl+Enter")

    def _file_row(self, f: GitFile, row: int, staged: bool):
        rf = ctk.CTkFrame(self.files_frame, fg_color="transparent", height=36)
        rf.grid(row=row, column=0, sticky="ew", padx=2, pady=1)
        rf.grid_propagate(False)
        rf.grid_columnconfigure(1, weight=1)

        # 文件类型图标
        icon_path = self._get_icon_path(f.path)
        if os.path.exists(icon_path):
            from PIL import Image
            icon = ctk.CTkImage(light_image=Image.open(icon_path), size=(22, 22))
            ctk.CTkLabel(rf, image=icon, text="", width=22, height=22).grid(
                row=0, column=0, padx=(5,6), pady=5)
        else:
            ctk.CTkLabel(rf, text="··", font=(self.FM,15), text_color="#666",
                         width=18).grid(row=0, column=0, padx=(5,6), pady=5)

        # 文件名
        name = f.path if len(f.path) <= 42 else "..." + f.path[-39:]
        ctk.CTkLabel(rf, text=name, font=(self.F,14), text_color=TEXT_PRIMARY,
                     anchor="w").grid(row=0, column=1, sticky="w", padx=2)

        # 操作按钮
        btns = ctk.CTkFrame(rf, fg_color="transparent")
        btns.grid(row=0, column=2, padx=2)
        ctk.CTkButton(btns, text="◫", width=26, height=26, fg_color="transparent",
            hover_color=BG_HOVER, text_color=TEXT_SECONDARY, font=(self.F,14),
            command=lambda p=f.path: self.git.open_file(p)).pack(side="left", padx=1)
        if staged:
            ctk.CTkButton(btns, text="−", width=26, height=26, fg_color="transparent",
                hover_color=BG_HOVER, text_color=TEXT_SECONDARY, font=(self.F,18),
                command=lambda p=f.path: (self.git.unstage_file(p), self._refresh())).pack(side="left", padx=1)
        else:
            ctk.CTkButton(btns, text="↺", width=26, height=26, fg_color="transparent",
                hover_color=BG_HOVER, text_color=TEXT_SECONDARY, font=(self.F,14),
                command=lambda p=f.path: self._discard(p)).pack(side="left", padx=1)
            ctk.CTkButton(btns, text="+", width=26, height=26, fg_color="transparent",
                hover_color=BG_HOVER, text_color=TEXT_SECONDARY, font=(self.F,18),
                command=lambda p=f.path: (self.git.stage_file(p), self._refresh())).pack(side="left", padx=1)

        # 状态字母在最后
        status_colors = {'M':STATUS_MODIFIED,'A':STATUS_ADDED,'D':STATUS_DELETED,'R':STATUS_RENAMED,'?':STATUS_UNTRACKED}
        ctk.CTkLabel(rf, text=f.status, font=(self.FM,13,"bold"),
                     text_color=status_colors.get(f.status, TEXT_DIM), width=14
                     ).grid(row=0, column=3, padx=(4,8))

        rf.bind("<Enter>", lambda e, r=rf: r.configure(fg_color=BG_HOVER))
        rf.bind("<Leave>", lambda e, r=rf: r.configure(fg_color="transparent"))
        rf.bind("<Double-Button-1>", lambda e, fi=f: self._show_diff_view(fi))
        rf.bind("<Button-3>", lambda e, fi=f, s=staged: self._file_ctx_menu(e, fi, s))

    # ═══════════════════════════════════════════════════════
    # Git 操作
    # ═══════════════════════════════════════════════════════
    def _open_folder(self):
        p = filedialog.askdirectory(title="选择项目文件夹")
        if not p: return
        self.git.repo_path = p
        if self.git.is_git_repo():
            self._show_repo_view(); self._refresh()
        else:
            self._show_not_git_repo(os.path.basename(p))

    def _init_repo(self):
        ok, msg = self.git.init_repo()
        if ok: self._show_repo_view(); self._refresh()

    def _stage_all(self): self.git.stage_all(); self._refresh()
    def _unstage_all(self): self.git.unstage_all(); self._refresh()

    def _discard(self, p):
        if messagebox.askyesno("确认", f"确定丢弃 {p} 的更改？"):
            self.git.discard_file(p); self._refresh()

    def _discard_all(self):
        if messagebox.askyesno("确认", "确定放弃所有更改？"):
            self.git.discard_all(); self._refresh()

    def _commit(self):
        if not hasattr(self,'commit_entry'): return
        msg = self.commit_entry.get().strip()
        if not msg: messagebox.showwarning("提示","请输入提交信息"); return
        ok, r = self.git.commit(msg)
        if ok: self.commit_entry.delete(0,"end"); self._refresh()
        else: messagebox.showerror("提交失败", r)

    def _push(self): self.git.push(); self._refresh()
    def _pull(self): self.git.pull(rebase=False); self._refresh()
    def _pull_rebase(self): self.git.pull(rebase=True); self._refresh()
    def _fetch(self): self.git.fetch(); self._refresh()
    def _sync(self): self.git.sync(); self._refresh()

    def _ai_gen(self):
        if not hasattr(self,'commit_entry'): return
        files = self.git.get_changed_files()
        if files:
            names = [os.path.basename(f.path) for f in files[:3]]
            msg = f"更新: {', '.join(names)}"
            if len(files) > 3: msg += f" 等 {len(files)} 个文件"
            self.commit_entry.delete(0,"end"); self.commit_entry.insert(0, msg)

    # ═══════════════════════════════════════════════════════
    # 菜单
    # ═══════════════════════════════════════════════════════
    def _make_menu(self):
        return Menu(self, tearoff=0, bg=BG_PANEL, fg=TEXT_PRIMARY,
                    activebackground=BG_SELECTED, activeforeground=TEXT_WHITE,
                    borderwidth=1, relief="flat")

    def _show_commit_menu(self):
        m = self._make_menu()
        m.add_command(label="提交", command=self._commit)
        m.add_command(label="提交(修改)", command=self._commit_amend)
        m.add_separator()
        m.add_command(label="提交和推送", command=self._commit_push)
        m.add_command(label="提交和同步", command=self._commit_sync)
        try: m.tk_popup(self.winfo_rootx()+280, self.winfo_rooty()+185)
        finally: m.grab_release()

    def _show_more_menu(self):
        m = self._make_menu()
        m.add_command(label="树结构查看")
        m.add_separator()
        v = Menu(m, tearoff=0, bg=BG_PANEL, fg=TEXT_PRIMARY, activebackground=BG_SELECTED)
        v.add_command(label="按名称排序"); v.add_command(label="按状态排序")
        m.add_cascade(label="查看和排序", menu=v)
        m.add_separator()
        m.add_command(label="拉取", command=self._pull)
        m.add_command(label="推送", command=self._push)
        m.add_command(label="克隆", command=self._clone_dialog)
        m.add_command(label="签出到...", command=self._checkout_dialog)
        m.add_command(label="抓取", command=self._fetch)
        m.add_separator()
        cm = Menu(m, tearoff=0, bg=BG_PANEL, fg=TEXT_PRIMARY, activebackground=BG_SELECTED)
        cm.add_command(label="提交", command=self._commit)
        cm.add_command(label="提交已暂存文件", command=self._commit)
        cm.add_command(label="全部提交    Ctrl+Alt+K", command=self._commit_all)
        cm.add_command(label="撤消上次提交", command=self._undo_last)
        cm.add_separator()
        cm.add_command(label="提交(修改)", command=self._commit_amend)
        cm.add_separator()
        cm.add_command(label="提交(已签收)", command=lambda: self._commit_signed("--signoff"))
        cm.add_command(label="提交(已签名)", command=lambda: self._commit_signed("--gpg-sign"))
        m.add_cascade(label="提交", menu=cm)
        ch = Menu(m, tearoff=0, bg=BG_PANEL, fg=TEXT_PRIMARY, activebackground=BG_SELECTED)
        ch.add_command(label="暂存所有更改", command=self._stage_all)
        ch.add_command(label="取消暂存所有更改", command=self._unstage_all)
        ch.add_command(label="放弃所有更改", command=self._discard_all)
        m.add_cascade(label="更改", menu=ch)
        sp = Menu(m, tearoff=0, bg=BG_PANEL, fg=TEXT_PRIMARY, activebackground=BG_SELECTED)
        sp.add_command(label="同步    Ctrl+T", command=self._sync)
        sp.add_separator()
        sp.add_command(label="拉取", command=self._pull)
        sp.add_command(label="拉取(变基)", command=self._pull_rebase)
        sp.add_separator()
        sp.add_command(label="推送", command=self._push)
        sp.add_separator()
        sp.add_command(label="抓取", command=self._fetch)
        m.add_cascade(label="拉取, 推送", menu=sp)
        bm = Menu(m, tearoff=0, bg=BG_PANEL, fg=TEXT_PRIMARY, activebackground=BG_SELECTED)
        bm.add_command(label="合并...", command=self._merge_dialog)
        bm.add_command(label="变基分支...", command=self._rebase_dialog)
        bm.add_separator()
        bm.add_command(label="创建分支...", command=self._create_branch_dialog)
        bm.add_separator()
        bm.add_command(label="重命名分支...", command=self._rename_branch_dialog)
        bm.add_command(label="删除分支...", command=self._delete_branch_dialog)
        m.add_cascade(label="分支", menu=bm)
        rm = Menu(m, tearoff=0, bg=BG_PANEL, fg=TEXT_PRIMARY, activebackground=BG_SELECTED)
        rm.add_command(label="添加远程存储库...", command=self._add_remote_dialog)
        rm.add_command(label="删除远程存储库", command=self._remove_remote_dialog)
        m.add_cascade(label="远程", menu=rm)
        st = Menu(m, tearoff=0, bg=BG_PANEL, fg=TEXT_PRIMARY, activebackground=BG_SELECTED)
        st.add_command(label="储藏", command=lambda: (self.git.stash(), self._refresh()))
        st.add_command(label="储藏(包含未跟踪)", command=lambda: (self.git.stash(True), self._refresh()))
        st.add_separator()
        st.add_command(label="应用最新储藏", command=lambda: (self.git.stash_apply(), self._refresh()))
        st.add_command(label="弹出最新储藏", command=lambda: (self.git.stash_pop(), self._refresh()))
        st.add_separator()
        st.add_command(label="删除所有储藏...", command=lambda: (self.git.stash_clear(), self._refresh()))
        m.add_cascade(label="存储", menu=st)
        tg = Menu(m, tearoff=0, bg=BG_PANEL, fg=TEXT_PRIMARY, activebackground=BG_SELECTED)
        tg.add_command(label="创建标记...", command=self._create_tag_dialog)
        tg.add_command(label="删除标签...", command=self._delete_tag_dialog)
        tg.add_separator()
        tg.add_command(label="推送标记", command=lambda: (self.git.push_tags(), self._refresh()))
        m.add_cascade(label="标记", menu=tg)
        m.add_separator()
        m.add_command(label="显示 GIT 输出")
        try: m.tk_popup(self.winfo_pointerx(), self.winfo_pointery())
        finally: m.grab_release()

    def _file_ctx_menu(self, event, f, staged):
        m = self._make_menu()
        m.add_command(label="打开文件", command=lambda: self.git.open_file(f.path))
        m.add_command(label="打开差异", command=lambda: self._show_diff_view(f))
        m.add_separator()
        if staged:
            m.add_command(label="取消暂存", command=lambda: (self.git.unstage_file(f.path), self._refresh()))
        else:
            m.add_command(label="暂存文件", command=lambda: (self.git.stage_file(f.path), self._refresh()))
        m.add_command(label="丢弃更改", command=lambda: self._discard(f.path))
        m.add_separator()
        full = os.path.join(self.git.repo_path, f.path)
        m.add_command(label="在资源管理器中显示",
            command=lambda: os.startfile(os.path.dirname(full)) if os.path.exists(full) else None)
        try: m.tk_popup(event.x_root, event.y_root)
        finally: m.grab_release()

    # ═══════════════════════════════════════════════════════
    # 菜单操作
    # ═══════════════════════════════════════════════════════
    def _commit_amend(self):
        msg = self.commit_entry.get().strip() if hasattr(self,'commit_entry') else None
        self.git.commit(msg or "amend", amend=True)
        if hasattr(self,'commit_entry'): self.commit_entry.delete(0,"end")
        self._refresh()

    def _commit_all(self):
        msg = self.commit_entry.get().strip() if hasattr(self,'commit_entry') else "更新所有文件"
        self.git.commit_all(msg)
        if hasattr(self,'commit_entry'): self.commit_entry.delete(0,"end")
        self._refresh()

    def _commit_push(self):
        msg = self.commit_entry.get().strip() if hasattr(self,'commit_entry') else ""
        if not msg: messagebox.showwarning("提示","请输入提交信息"); return
        ok, _ = self.git.commit(msg)
        if ok: self.commit_entry.delete(0,"end"); self.git.push(); self._refresh()

    def _commit_sync(self):
        msg = self.commit_entry.get().strip() if hasattr(self,'commit_entry') else ""
        if not msg: messagebox.showwarning("提示","请输入提交信息"); return
        ok, _ = self.git.commit(msg)
        if ok: self.commit_entry.delete(0,"end"); self.git.sync(); self._refresh()

    def _commit_signed(self, flag):
        msg = self.commit_entry.get().strip() if hasattr(self,'commit_entry') else "Signed"
        self.git._run(['commit', flag, '-m', msg])
        if hasattr(self,'commit_entry'): self.commit_entry.delete(0,"end")
        self._refresh()

    def _undo_last(self): self.git._run(['reset','--soft','HEAD~1']); self._refresh()

    # ═══════════════════════════════════════════════════════
    # 对话框
    # ═══════════════════════════════════════════════════════
    def _dialog(self, title, fields, cb):
        d = ctk.CTkToplevel(self)
        d.title(title); d.geometry("420x220"); d.configure(fg_color=BG_PANEL)
        d.transient(self); d.grab_set()
        entries = {}
        for i,(label,default) in enumerate(fields):
            ctk.CTkLabel(d, text=label, font=(self.F,18),
                         text_color=TEXT_PRIMARY).pack(padx=20, pady=(15 if i==0 else 5,2), anchor="w")
            e = ctk.CTkEntry(d, width=370, height=36, fg_color=BG_INPUT,
                text_color=TEXT_PRIMARY, border_color=BORDER_COLOR, font=(self.F,18))
            e.pack(padx=20, pady=(0,5))
            if default: e.insert(0, default)
            entries[label] = e
        def ok():
            vals = {k: e.get() for k,e in entries.items()}; d.destroy(); cb(vals)
        bf = ctk.CTkFrame(d, fg_color="transparent"); bf.pack(pady=15)
        ctk.CTkButton(bf, text="确定", width=100, height=36, fg_color=BTN_PRIMARY,
            hover_color=BTN_PRIMARY_HOVER, text_color=TEXT_WHITE, command=ok).pack(side="left", padx=5)
        ctk.CTkButton(bf, text="取消", width=100, height=36, fg_color=BG_INPUT,
            hover_color=BG_HOVER, text_color=TEXT_PRIMARY, command=d.destroy).pack(side="left", padx=5)

    def _create_branch_dialog(self):
        self._dialog("创建分支", [("新分支名","")],
            lambda v: (self.git.create_branch(v["新分支名"]), self._refresh()))
    def _rename_branch_dialog(self):
        self._dialog("重命名分支", [("当前名称", self.git.get_current_branch()), ("新名称","")],
            lambda v: (self.git.rename_branch(v["当前名称"], v["新名称"]), self._refresh()))
    def _delete_branch_dialog(self):
        bs = [b.name for b in self.git.get_branches() if not b.is_current and not b.is_remote]
        self._dialog("删除分支", [("分支名", bs[0] if bs else "")],
            lambda v: (self.git.delete_branch(v["分支名"]), self._refresh()))
    def _checkout_dialog(self):
        bs = [b.name for b in self.git.get_branches() if not b.is_current]
        self._dialog("签出到分支", [("分支名", bs[0] if bs else "")],
            lambda v: (self.git.switch_branch(v["分支名"]), self._refresh()))
    def _merge_dialog(self):
        bs = [b.name for b in self.git.get_branches() if not b.is_current and not b.is_remote]
        self._dialog("合并分支", [("分支名", bs[0] if bs else "")],
            lambda v: (self.git.merge(v["分支名"]), self._refresh()))
    def _rebase_dialog(self):
        bs = [b.name for b in self.git.get_branches() if not b.is_current and not b.is_remote]
        self._dialog("变基到分支", [("分支名", bs[0] if bs else "")],
            lambda v: (self.git.rebase(v["分支名"]), self._refresh()))
    def _add_remote_dialog(self):
        self._dialog("添加远程存储库", [("名称","origin"), ("URL","")],
            lambda v: (self.git.add_remote(v["名称"], v["URL"]), self._refresh()))
    def _remove_remote_dialog(self):
        rs = self.git.get_remotes()
        self._dialog("删除远程存储库", [("远程名称", rs[0] if rs else "")],
            lambda v: (self.git.remove_remote(v["远程名称"]), self._refresh()))
    def _create_tag_dialog(self):
        self._dialog("创建标记", [("标签名",""), ("说明","")],
            lambda v: (self.git.create_tag(v["标签名"], v["说明"] or None), self._refresh()))
    def _delete_tag_dialog(self):
        self._dialog("删除标签", [("标签名","")],
            lambda v: (self.git.delete_tag(v["标签名"]), self._refresh()))
    def _clone_dialog(self):
        self._dialog("克隆仓库", [("仓库 URL",""), ("目标文件夹","")],
            lambda v: self.git.clone(v["仓库 URL"], v["目标文件夹"] or None))
