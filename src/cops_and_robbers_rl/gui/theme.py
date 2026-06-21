"""Central visual theme for the native Tkinter dashboard."""

from tkinter import Tk, ttk

COLORS = {
    "page": "#0b1220",
    "header": "#111c33",
    "card": "#17233b",
    "accent_card": "#1d3157",
    "board": "#dce6f1",
    "cell_a": "#edf3f8",
    "cell_b": "#e2ebf3",
    "grid": "#b6c5d5",
    "coordinate": "#8da0b5",
    "cop": "#2563eb",
    "thief": "#ef4444",
    "barrier": "#475569",
    "shadow": "#94a3b8",
    "text": "#f8fafc",
    "muted": "#a9b8cc",
    "accent": "#38bdf8",
}


def configure_theme(root: Tk) -> None:
    """Apply one coherent theme without changing application behavior."""
    root.configure(background=COLORS["page"])
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Page.TFrame", background=COLORS["page"])
    style.configure("Header.TFrame", background=COLORS["header"])
    style.configure("Controls.TFrame", background=COLORS["header"])
    style.configure("Card.TFrame", background=COLORS["card"])
    style.configure("AccentCard.TFrame", background=COLORS["accent_card"])
    style.configure(
        "Title.TLabel",
        background=COLORS["header"],
        foreground=COLORS["text"],
        font=("Segoe UI", 22, "bold"),
    )
    style.configure(
        "Subtitle.TLabel",
        background=COLORS["header"],
        foreground=COLORS["muted"],
        font=("Segoe UI", 10),
    )
    style.configure(
        "Badge.TLabel",
        background=COLORS["accent_card"],
        foreground=COLORS["accent"],
        padding=(12, 7),
        font=("Segoe UI", 8, "bold"),
    )
    style.configure(
        "MetricTitle.TLabel",
        background=COLORS["card"],
        foreground=COLORS["accent"],
        font=("Segoe UI", 8, "bold"),
    )
    style.configure(
        "MetricValue.TLabel",
        background=COLORS["card"],
        foreground=COLORS["text"],
        font=("Segoe UI", 13, "bold"),
    )
    style.configure(
        "AccentMetricTitle.TLabel",
        background=COLORS["accent_card"],
        foreground=COLORS["accent"],
        font=("Segoe UI", 8, "bold"),
    )
    style.configure(
        "AccentMetricValue.TLabel",
        background=COLORS["accent_card"],
        foreground=COLORS["text"],
        font=("Segoe UI", 13, "bold"),
    )
    style.configure(
        "Body.TLabel",
        background=COLORS["card"],
        foreground=COLORS["muted"],
        font=("Segoe UI", 10),
    )
    style.configure(
        "Footer.TLabel",
        background=COLORS["header"],
        foreground=COLORS["muted"],
        font=("Segoe UI", 9),
    )
    style.configure(
        "Secondary.TButton",
        background="#263652",
        foreground=COLORS["text"],
        borderwidth=0,
        padding=(12, 10),
        font=("Segoe UI", 9, "bold"),
    )
    style.map("Secondary.TButton", background=[("active", "#344766")])
    style.configure(
        "Accent.TButton",
        background="#0284c7",
        foreground="white",
        borderwidth=0,
        padding=(12, 10),
        font=("Segoe UI", 9, "bold"),
    )
    style.map("Accent.TButton", background=[("active", "#0369a1")])
    style.configure(
        "Game.Horizontal.TProgressbar",
        troughcolor=COLORS["card"],
        background=COLORS["accent"],
        bordercolor=COLORS["page"],
        lightcolor=COLORS["accent"],
        darkcolor=COLORS["accent"],
        thickness=8,
    )
