"""Git 图形化管理软件 - 主入口"""
import sys
import os
import customtkinter as ctk
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
from ui_main import GitManagerApp

if __name__ == "__main__":
    app = GitManagerApp()
    app.mainloop()
