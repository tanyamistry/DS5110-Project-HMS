import tkinter as tk
from tkinter import ttk

PRIMARY_COLOR = "#1F6FEB"  
BG_COLOR = "#F4F6FB"        
DANGER_COLOR = "#D64545"

def apply_theme(root: tk.Misc) -> None:
    root.configure(bg=BG_COLOR)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("TFrame", background=BG_COLOR)
    style.configure("TLabel", background=BG_COLOR, foreground="#111827")
    style.configure("Header.TLabel", font=("Segoe UI", 20, "bold"), foreground="#111827", background=BG_COLOR)
    style.configure("Subheader.TLabel", font=("Segoe UI", 11), foreground="#4B5563", background=BG_COLOR)

    style.configure("TButton", font=("Segoe UI", 10), padding=6)
    style.configure("Accent.TButton", background=PRIMARY_COLOR, foreground="white")
    style.map("Accent.TButton",
              background=[("active", "#1658C4")],
              foreground=[("disabled", "#E5E7EB")])
    style.configure("Secondary.TButton", background="white", foreground="#111827", borderwidth=1)
    style.map("Secondary.TButton",
              background=[("active", "#E5E7EB")])

    style.configure("Danger.TButton", background=DANGER_COLOR, foreground="white")
    style.map("Danger.TButton",
              background=[("active", "#B73232")])

    style.configure("Treeview",
                    background="white",
                    foreground="#111827",
                    rowheight=24,
                    fieldbackground="white")
    style.configure("Treeview.Heading",
                    font=("Segoe UI", 10, "bold"),
                    background="#E5E7EB",
                    foreground="#111827")

def maximize_window(win: tk.Misc) -> None:
    """Make the window effectively full screen on most platforms."""
    try:
        win.state("zoomed")
    except tk.TclError:
    
        win.update_idletasks()
        width = win.winfo_screenwidth()
        height = win.winfo_screenheight()
        win.geometry(f"{width}x{height}+0+0")

def build_header(parent: tk.Misc, title: str, subtitle: str | None = None) -> tk.Frame:
    container = ttk.Frame(parent)
    title_label = ttk.Label(container, text=title, style="Header.TLabel")
    title_label.pack(anchor="w")
    if subtitle:
        sub_label = ttk.Label(container, text=subtitle, style="Subheader.TLabel")
        sub_label.pack(anchor="w", pady=(2, 0))
    return container
