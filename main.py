"""
main.py
-------
Comparador de precios Steam vs Epic Games.
Layout:
  row 0 → Hero  (título + búsqueda)
  row 1 → Área de resultados  (expandible)
  row 2 → Barra inferior fija  (status + botón calculadora)
"""

import tkinter as tk
import threading
import customtkinter as ctk

from database import search_both
from components import (
    GameCard, SectionHeader,
    COLORS, FONT_DISPLAY, FONT_H1, FONT_H2,
    FONT_BODY, FONT_SMALL, FONT_TITLE,
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Game Price Comparator  •  Steam vs Epic")
        self.geometry("1140x780")
        self.minsize(900, 620)
        self.configure(fg_color=COLORS["bg_main"])

        # ── Layout principal: 3 filas ──
        # row 0 = hero        (tamaño fijo)
        # row 1 = resultados  (expande)
        # row 2 = footer bar  (tamaño fijo)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self._build_hero()
        self._build_results_area()
        self._build_footer_bar()

    # ──────────────────────────────────────────
    #  ROW 0 — Hero con título y búsqueda
    # ──────────────────────────────────────────
    def _build_hero(self):
        hero = ctk.CTkFrame(
            self, fg_color=COLORS["bg_surface"],
            corner_radius=0,
        )
        hero.grid(row=0, column=0, sticky="ew")
        hero.grid_columnconfigure(0, weight=1)

        # ── Fila 0: título + badges ──
        title_row = ctk.CTkFrame(hero, fg_color="transparent")
        title_row.grid(row=0, column=0, sticky="w", padx=32, pady=(20, 0))

        ctk.CTkLabel(
            title_row,
            text="🎮  Game Price Comparator",
            font=FONT_DISPLAY,
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        for label, fg, txt in [
            ("STEAM",      COLORS["accent_steam_dim"],  COLORS["accent_steam"]),
            ("EPIC GAMES", COLORS["accent_epic_dim"],   COLORS["accent_epic"]),
        ]:
            ctk.CTkLabel(
                title_row,
                text=f"  {label}  ",
                font=("Segoe UI", 9, "bold"),
                fg_color=fg, text_color=txt,
                corner_radius=6,
            ).pack(side="left", padx=(10, 0))

        # ── Fila 1: subtítulo ──
        ctk.CTkLabel(
            hero,
            text="Compara precios en tiempo real · Haz clic en cualquier resultado para abrir la tienda",
            font=FONT_SMALL,
            text_color=COLORS["text_secondary"],
        ).grid(row=1, column=0, sticky="w", padx=34, pady=(3, 0))

        # ── Fila 2: búsqueda ──
        search_row = ctk.CTkFrame(hero, fg_color="transparent")
        search_row.grid(row=2, column=0, sticky="w", padx=32, pady=(12, 18))

        self.search_var = tk.StringVar()

        self.search_entry = ctk.CTkEntry(
            search_row,
            textvariable=self.search_var,
            placeholder_text="🔍  Buscar juego... ej: Cyberpunk, Elden Ring, GTA V",
            width=480, height=42,
            font=FONT_BODY,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border_bright"],
            border_width=1,
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_muted"],
            corner_radius=10,
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<Return>", lambda e: self._do_search())

        self.search_btn = ctk.CTkButton(
            search_row,
            text="Buscar",
            width=110, height=42,
            font=("Segoe UI", 12, "bold"),
            fg_color=COLORS["accent_steam"],
            hover_color=COLORS["accent_steam_dim"],
            corner_radius=10,
            command=self._do_search,
        )
        self.search_btn.pack(side="left", padx=(10, 0))

        # Separador inferior del hero
        ctk.CTkFrame(hero, height=1, fg_color=COLORS["border"]).grid(
            row=3, column=0, sticky="ew",
        )

    # ──────────────────────────────────────────
    #  ROW 1 — Área de resultados (expande)
    # ──────────────────────────────────────────
    def _build_results_area(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=1, column=0, sticky="nsew", padx=24, pady=(14, 0))
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(1, weight=1)

        # Cabeceras de plataforma
        self.steam_header = SectionHeader(
            container, "Steam", COLORS["accent_steam"])
        self.steam_header.grid(
            row=0, column=0, sticky="ew", pady=(0, 8))

        self.epic_header = SectionHeader(
            container, "Epic Games", COLORS["accent_epic"])
        self.epic_header.grid(
            row=0, column=1, sticky="ew", padx=(14, 0), pady=(0, 8))

        # Scroll frames
        scroll_cfg = dict(
            fg_color=COLORS["bg_main"],
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["border_bright"],
            corner_radius=0,
        )

        self.steam_scroll = ctk.CTkScrollableFrame(container, **scroll_cfg)
        self.steam_scroll.grid(row=1, column=0, sticky="nsew")

        self.epic_scroll = ctk.CTkScrollableFrame(container, **scroll_cfg)
        self.epic_scroll.grid(row=1, column=1, sticky="nsew", padx=(14, 0))

        self._show_placeholder(self.steam_scroll, "steam")
        self._show_placeholder(self.epic_scroll, "epic")

    # ──────────────────────────────────────────
    #  ROW 2 — Barra inferior fija
    #          (status izquierda · botón calculadora derecha)
    # ──────────────────────────────────────────
    def _build_footer_bar(self):
        footer = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_surface"],
            corner_radius=0,
            height=56,
        )
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_propagate(False)
        footer.grid_columnconfigure(0, weight=1)

        # Línea de acento naranja en la parte superior del footer
        ctk.CTkFrame(
            footer, height=2,
            fg_color=COLORS["accent_bottleneck"],
            corner_radius=0,
        ).place(relx=0, rely=0, relwidth=1)

        # Status (izquierda)
        self.status_var = tk.StringVar(
            value="Listo · Escribe un juego y presiona Buscar o Enter")
        ctk.CTkLabel(
            footer,
            textvariable=self.status_var,
            font=FONT_SMALL,
            text_color=COLORS["text_muted"],
        ).place(x=20, rely=0.55, anchor="w")

        # Botón calculadora (derecha)
        cta = ctk.CTkButton(
            footer,
            text="  ⚡  Calculadora de Cuello de Botella  →",
            width=300, height=36,
            font=("Segoe UI", 11, "bold"),
            fg_color=COLORS["accent_bottleneck"],
            hover_color="#bf4a18",
            text_color="#fff",
            corner_radius=8,
            command=self._open_bottleneck,
        )
        cta.place(relx=1.0, rely=0.55, anchor="e", x=-20)

    # ──────────────────────────────────────────
    #  Lógica de búsqueda
    # ──────────────────────────────────────────
    def _do_search(self):
        query = self.search_var.get().strip()
        if not query:
            self._set_status("⚠  Ingresa un término de búsqueda.")
            return

        self.search_btn.configure(state="disabled", text="⏳ Buscando…")
        self._set_status(f"Buscando «{query}» en Steam y Epic…")
        self._clear_results()
        self._show_loading()

        def worker():
            results = search_both(query, max_results=10)
            self.after(0, lambda: self._render_results(results, query))

        threading.Thread(target=worker, daemon=True).start()

    def _render_results(self, results: dict, query: str):
        self._clear_results()
        steam_games = results.get("steam", [])
        epic_games  = results.get("epic", [])
        epic_error  = results.get("epic_error")

        self.steam_header.update_count(len(steam_games))
        self.epic_header.update_count(len(epic_games))

        if steam_games:
            for g in steam_games:
                GameCard(self.steam_scroll, g, COLORS["accent_steam"]).pack(
                    fill="x", pady=(0, 8), padx=2)
        else:
            self._no_results(self.steam_scroll, "steam")

        if epic_games:
            for g in epic_games:
                GameCard(self.epic_scroll, g, COLORS["accent_epic"]).pack(
                    fill="x", pady=(0, 8), padx=2)
        else:
            self._epic_error_panel(self.epic_scroll, epic_error, query)

        total = len(steam_games) + len(epic_games)
        self._set_status(
            f"✓  {total} resultados para «{query}»"
            + ("  |  ⚠ Epic sin respuesta" if epic_error and not epic_games else "")
        )
        self.search_btn.configure(state="normal", text="Buscar")

    # ──────────────────────────────────────────
    #  Helpers UI
    # ──────────────────────────────────────────
    def _clear_results(self):
        for w in self.steam_scroll.winfo_children():  w.destroy()
        for w in self.epic_scroll.winfo_children():   w.destroy()

    def _show_placeholder(self, frame, platform: str):
        emoji = "🎮" if platform == "steam" else "🕹️"
        name  = "Steam" if platform == "steam" else "Epic Games"
        ctk.CTkLabel(
            frame,
            text=f"{emoji}\n\nBusca un juego para ver\nresultados de {name}",
            font=FONT_BODY,
            text_color=COLORS["text_muted"],
            justify="center",
        ).pack(expand=True, pady=60)

    def _show_loading(self):
        for frame in (self.steam_scroll, self.epic_scroll):
            ctk.CTkLabel(
                frame, text="⏳  Cargando resultados…",
                font=FONT_BODY, text_color=COLORS["text_secondary"],
            ).pack(pady=60)

    def _no_results(self, frame, platform: str):
        ctk.CTkLabel(
            frame, text="😕  Sin resultados",
            font=FONT_BODY, text_color=COLORS["text_muted"],
        ).pack(pady=60)

    def _epic_error_panel(self, frame, error_msg: str | None, query: str):
        wrap = ctk.CTkFrame(
            frame, fg_color=COLORS["bg_surface"],
            corner_radius=14, border_width=1,
            border_color=COLORS["border_bright"],
        )
        wrap.pack(fill="x", pady=20, padx=4)

        ctk.CTkLabel(wrap, text="⚠️  Epic Games no respondió",
                     font=FONT_TITLE, text_color=COLORS["accent_gold"],
                     ).pack(pady=(18, 4))

        ctk.CTkLabel(wrap, text=error_msg or "Error desconocido.",
                     font=FONT_SMALL, text_color=COLORS["text_secondary"],
                     wraplength=260, justify="center",
                     ).pack(padx=16, pady=(0, 6))

        ctk.CTkLabel(wrap,
                     text="• API de Epic bloqueó la solicitud\n• Sin conexión a internet",
                     font=FONT_SMALL, text_color=COLORS["text_muted"],
                     justify="left",
                     ).pack(padx=20, pady=(0, 10))

        ctk.CTkButton(
            wrap, text="🔄  Reintentar Epic",
            width=160, height=34,
            font=("Segoe UI", 11, "bold"),
            fg_color=COLORS["accent_epic"],
            hover_color=COLORS["accent_epic_dim"],
            corner_radius=8,
            command=lambda: self._retry_epic(query),
        ).pack(pady=(0, 18))

    def _retry_epic(self, query: str):
        from database import search_epic
        self._set_status(f"Reintentando Epic para «{query}»…")
        for w in self.epic_scroll.winfo_children(): w.destroy()
        ctk.CTkLabel(self.epic_scroll, text="⏳ Reintentando…",
                     font=FONT_BODY, text_color=COLORS["text_secondary"]).pack(pady=40)

        def worker():
            epic, err = [], None
            try:
                epic = search_epic(query, 10)
                if not epic:
                    err = "Sin resultados en Epic para esta búsqueda."
            except Exception as e:
                err = str(e)
            self.after(0, lambda: self._render_epic_only(epic, err, query))

        threading.Thread(target=worker, daemon=True).start()

    def _render_epic_only(self, epic_games, error, query):
        for w in self.epic_scroll.winfo_children(): w.destroy()
        self.epic_header.update_count(len(epic_games))
        if epic_games:
            for g in epic_games:
                GameCard(self.epic_scroll, g, COLORS["accent_epic"]).pack(
                    fill="x", pady=(0, 8), padx=2)
            self._set_status(f"✓ Epic: {len(epic_games)} resultados para «{query}»")
        else:
            self._epic_error_panel(self.epic_scroll, error, query)
            self._set_status("⚠ Epic sigue sin responder.")

    def _set_status(self, msg: str):
        self.status_var.set(msg)

    def _open_bottleneck(self):
        from bottleneck import BottleneckWindow
        win = BottleneckWindow(self)
        win.grab_set()


if __name__ == "__main__":
    app = App()
    app.mainloop()
