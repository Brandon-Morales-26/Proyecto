"""
components.py
-------------
Widgets reutilizables con diseño refinado.
"""

import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import urllib.request
import io
import threading

# ──────────────────────────────────────────────
#  PALETA & DESIGN TOKENS
# ──────────────────────────────────────────────
COLORS = {
    "bg_main":           "#080b12",
    "bg_card":           "#0e1220",
    "bg_card_hover":     "#141825",
    "bg_surface":        "#111523",
    "bg_input":          "#0c0f1a",
    "accent_steam":      "#1b9ad8",
    "accent_steam_dim":  "#0f5a82",
    "accent_epic":       "#2ecc71",
    "accent_epic_dim":   "#1a7a45",
    "accent_gold":       "#f5a623",
    "accent_red":        "#ef5350",
    "accent_bottleneck": "#ff6b35",
    "text_primary":      "#e8edf8",
    "text_secondary":    "#6b7a9e",
    "text_muted":        "#3a4260",
    "free_color":        "#00e676",
    "discount_color":    "#e85d00",
    "border":            "#1e2438",
    "border_bright":     "#2e3a58",
}

FONT_DISPLAY = ("Segoe UI Semibold", 26)
FONT_H1      = ("Segoe UI Semibold", 20)
FONT_H2      = ("Segoe UI", 14, "bold")
FONT_TITLE   = ("Segoe UI", 12, "bold")
FONT_BODY    = ("Segoe UI", 11)
FONT_SMALL   = ("Segoe UI", 10)
FONT_BADGE   = ("Segoe UI", 8, "bold")
FONT_MONO    = ("Consolas", 11)
FONT_PRICE   = ("Segoe UI Semibold", 15)

# ──────────────────────────────────────────────
#  Image cache
# ──────────────────────────────────────────────
_img_cache: dict[str, ImageTk.PhotoImage] = {}


def _fetch_image_async(url: str, label: ctk.CTkLabel, size=(88, 50)):
    if url in _img_cache:
        label.configure(image=_img_cache[url])
        return

    def _load():
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=6) as r:
                data = r.read()
            img = Image.open(io.BytesIO(data)).convert("RGBA")
            img = img.resize(size, Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            _img_cache[url] = photo
            label.configure(image=photo)
        except Exception:
            pass

    threading.Thread(target=_load, daemon=True).start()


# ──────────────────────────────────────────────
#  GameCard
# ──────────────────────────────────────────────

class GameCard(ctk.CTkFrame):
    def __init__(self, master, game: dict, platform_color: str, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        self.game = game
        self.platform_color = platform_color
        self._build()
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)

    def _build(self):
        self.grid_columnconfigure(2, weight=1)

        # Barra lateral de plataforma
        bar = ctk.CTkFrame(self, width=3, fg_color=self.platform_color, corner_radius=2)
        bar.grid(row=0, column=0, rowspan=3, sticky="ns", padx=(8, 0), pady=8)

        # Imagen
        self.img_label = ctk.CTkLabel(self, text="", width=88, height=50)
        self.img_label.grid(row=0, column=1, rowspan=3, padx=(10, 12), pady=10, sticky="ns")
        if self.game.get("image"):
            _fetch_image_async(self.game["image"], self.img_label)

        # Título
        ctk.CTkLabel(
            self, text=self.game.get("title", "?"),
            font=FONT_TITLE,
            text_color=COLORS["text_primary"],
            anchor="w", wraplength=220, justify="left",
        ).grid(row=0, column=2, sticky="w", padx=(0, 10), pady=(10, 2))

        # Precio
        pf = ctk.CTkFrame(self, fg_color="transparent")
        pf.grid(row=1, column=2, sticky="w", pady=2)
        self._build_price(pf)

        # Link
        url = self.game.get("url", "")
        if url:
            lnk = ctk.CTkLabel(
                self, text="Abrir tienda  →",
                font=FONT_SMALL,
                text_color=self.platform_color,
                cursor="hand2",
            )
            lnk.grid(row=2, column=2, sticky="w", pady=(0, 10))
            lnk.bind("<Button-1>", lambda e: __import__("webbrowser").open(url))

    def _build_price(self, frame):
        if self.game.get("is_free"):
            ctk.CTkLabel(
                frame, text="GRATIS",
                font=("Segoe UI Semibold", 14),
                text_color=COLORS["free_color"],
            ).pack(side="left")
            return

        price    = self.game.get("price", 0)
        original = self.game.get("original_price", 0)
        discount = self.game.get("discount", 0)

        if discount > 0 and original > price:
            ctk.CTkLabel(
                frame, text=f"${original:.2f}",
                font=("Segoe UI", 10),
                text_color=COLORS["text_muted"],
            ).pack(side="left", padx=(0, 5))

        ctk.CTkLabel(
            frame, text=f"${price:.2f}",
            font=FONT_PRICE,
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        ctk.CTkLabel(
            frame, text=" USD",
            font=FONT_SMALL,
            text_color=COLORS["text_secondary"],
        ).pack(side="left")

        if discount > 0:
            ctk.CTkLabel(
                frame, text=f"  -{discount}%  ",
                font=FONT_BADGE,
                fg_color=COLORS["discount_color"],
                text_color="#fff",
                corner_radius=4,
            ).pack(side="left", padx=(8, 0))

    def _on_hover(self, e):
        self.configure(fg_color=COLORS["bg_card_hover"], border_color=COLORS["border_bright"])

    def _on_leave(self, e):
        self.configure(fg_color=COLORS["bg_card"], border_color=COLORS["border"])


# ──────────────────────────────────────────────
#  SectionHeader
# ──────────────────────────────────────────────

class SectionHeader(ctk.CTkFrame):
    def __init__(self, master, title: str, color: str, count: int = 0, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.count_var = tk.StringVar(value=f"{count} resultados")

        pill = ctk.CTkFrame(self, fg_color=COLORS["bg_surface"], corner_radius=20)
        pill.pack(fill="x")

        ctk.CTkFrame(pill, width=8, height=8, fg_color=color, corner_radius=4
                     ).pack(side="left", padx=(14, 8), pady=12)

        ctk.CTkLabel(pill, text=title, font=FONT_H2,
                     text_color=COLORS["text_primary"]).pack(side="left")

        ctk.CTkLabel(pill, textvariable=self.count_var,
                     font=FONT_SMALL,
                     text_color=COLORS["text_secondary"]).pack(side="left", padx=(8, 14))

    def update_count(self, n: int):
        self.count_var.set(f"{n} resultados")
