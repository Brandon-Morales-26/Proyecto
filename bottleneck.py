"""
bottleneck.py
-------------
Ventana de calculadora de cuello de botella.
Analiza CPU, GPU y RAM para detectar el componente limitante.

No requiere librerías adicionales — usa solo customtkinter.
"""

import tkinter as tk
import customtkinter as ctk
import threading
import time

from components import COLORS, FONT_DISPLAY, FONT_H1, FONT_H2, FONT_TITLE, FONT_BODY, FONT_SMALL, FONT_BADGE

# ──────────────────────────────────────────────
#  BASE DE DATOS DE COMPONENTES (scores normalizados 0-100)
#  Score = rendimiento relativo para gaming (1080p)
# ──────────────────────────────────────────────

CPUS: dict[str, dict] = {
    # Intel
    "Intel Core i3-10100":        {"score": 38, "cores": 4,  "threads": 8,  "tdp": 65},
    "Intel Core i3-12100":        {"score": 52, "cores": 4,  "threads": 8,  "tdp": 60},
    "Intel Core i5-10400":        {"score": 52, "cores": 6,  "threads": 12, "tdp": 65},
    "Intel Core i5-10600K":       {"score": 58, "cores": 6,  "threads": 12, "tdp": 125},
    "Intel Core i5-11600K":       {"score": 62, "cores": 6,  "threads": 12, "tdp": 125},
    "Intel Core i5-12400":        {"score": 67, "cores": 6,  "threads": 12, "tdp": 65},
    "Intel Core i5-12600K":       {"score": 72, "cores": 10, "threads": 16, "tdp": 125},
    "Intel Core i5-13600K":       {"score": 80, "cores": 14, "threads": 20, "tdp": 125},
    "Intel Core i5-14600K":       {"score": 83, "cores": 14, "threads": 20, "tdp": 125},
    "Intel Core i7-10700K":       {"score": 65, "cores": 8,  "threads": 16, "tdp": 125},
    "Intel Core i7-11700K":       {"score": 68, "cores": 8,  "threads": 16, "tdp": 125},
    "Intel Core i7-12700K":       {"score": 78, "cores": 12, "threads": 20, "tdp": 125},
    "Intel Core i7-13700K":       {"score": 86, "cores": 16, "threads": 24, "tdp": 125},
    "Intel Core i7-14700K":       {"score": 89, "cores": 20, "threads": 28, "tdp": 125},
    "Intel Core i9-12900K":       {"score": 85, "cores": 16, "threads": 24, "tdp": 125},
    "Intel Core i9-13900K":       {"score": 93, "cores": 24, "threads": 32, "tdp": 125},
    "Intel Core i9-14900K":       {"score": 95, "cores": 24, "threads": 32, "tdp": 125},
    "Intel Core Ultra 5 245K":    {"score": 84, "cores": 14, "threads": 14, "tdp": 125},
    "Intel Core Ultra 7 265K":    {"score": 91, "cores": 20, "threads": 20, "tdp": 125},
    "Intel Core Ultra 9 285K":    {"score": 97, "cores": 24, "threads": 24, "tdp": 125},
    # AMD
    "AMD Ryzen 3 3300X":          {"score": 46, "cores": 4,  "threads": 8,  "tdp": 65},
    "AMD Ryzen 5 3600":           {"score": 56, "cores": 6,  "threads": 12, "tdp": 65},
    "AMD Ryzen 5 5600":           {"score": 69, "cores": 6,  "threads": 12, "tdp": 65},
    "AMD Ryzen 5 5600X":          {"score": 71, "cores": 6,  "threads": 12, "tdp": 65},
    "AMD Ryzen 5 7600":           {"score": 78, "cores": 6,  "threads": 12, "tdp": 65},
    "AMD Ryzen 5 7600X":          {"score": 80, "cores": 6,  "threads": 12, "tdp": 105},
    "AMD Ryzen 7 3700X":          {"score": 58, "cores": 8,  "threads": 16, "tdp": 65},
    "AMD Ryzen 7 5700X":          {"score": 72, "cores": 8,  "threads": 16, "tdp": 65},
    "AMD Ryzen 7 5800X":          {"score": 75, "cores": 8,  "threads": 16, "tdp": 105},
    "AMD Ryzen 7 7700X":          {"score": 84, "cores": 8,  "threads": 16, "tdp": 105},
    "AMD Ryzen 7 7800X3D":        {"score": 98, "cores": 8,  "threads": 16, "tdp": 120},
    "AMD Ryzen 9 5900X":          {"score": 80, "cores": 12, "threads": 24, "tdp": 105},
    "AMD Ryzen 9 5950X":          {"score": 83, "cores": 16, "threads": 32, "tdp": 105},
    "AMD Ryzen 9 7900X":          {"score": 88, "cores": 12, "threads": 24, "tdp": 170},
    "AMD Ryzen 9 7950X":          {"score": 92, "cores": 16, "threads": 32, "tdp": 170},
    "AMD Ryzen 9 7950X3D":        {"score": 99, "cores": 16, "threads": 32, "tdp": 120},
    "AMD Ryzen 9 9900X":          {"score": 94, "cores": 12, "threads": 24, "tdp": 120},
    "AMD Ryzen 9 9950X":          {"score": 100,"cores": 16, "threads": 32, "tdp": 170},
}

GPUS: dict[str, dict] = {
    # NVIDIA
    "NVIDIA GTX 1650":            {"score": 28, "vram": 4,  "tier": "Entry"},
    "NVIDIA GTX 1660":            {"score": 36, "vram": 6,  "tier": "Mid"},
    "NVIDIA GTX 1660 Super":      {"score": 40, "vram": 6,  "tier": "Mid"},
    "NVIDIA GTX 1660 Ti":         {"score": 42, "vram": 6,  "tier": "Mid"},
    "NVIDIA RTX 2060":            {"score": 47, "vram": 6,  "tier": "Mid"},
    "NVIDIA RTX 2060 Super":      {"score": 52, "vram": 8,  "tier": "Mid"},
    "NVIDIA RTX 2070":            {"score": 55, "vram": 8,  "tier": "Mid"},
    "NVIDIA RTX 2070 Super":      {"score": 60, "vram": 8,  "tier": "Mid"},
    "NVIDIA RTX 2080":            {"score": 65, "vram": 8,  "tier": "High"},
    "NVIDIA RTX 2080 Super":      {"score": 68, "vram": 8,  "tier": "High"},
    "NVIDIA RTX 2080 Ti":         {"score": 75, "vram": 11, "tier": "High"},
    "NVIDIA RTX 3060":            {"score": 57, "vram": 12, "tier": "Mid"},
    "NVIDIA RTX 3060 Ti":         {"score": 68, "vram": 8,  "tier": "Mid"},
    "NVIDIA RTX 3070":            {"score": 75, "vram": 8,  "tier": "High"},
    "NVIDIA RTX 3070 Ti":         {"score": 79, "vram": 8,  "tier": "High"},
    "NVIDIA RTX 3080":            {"score": 87, "vram": 10, "tier": "Ultra"},
    "NVIDIA RTX 3080 Ti":         {"score": 92, "vram": 12, "tier": "Ultra"},
    "NVIDIA RTX 3090":            {"score": 94, "vram": 24, "tier": "Ultra"},
    "NVIDIA RTX 3090 Ti":         {"score": 96, "vram": 24, "tier": "Ultra"},
    "NVIDIA RTX 4060":            {"score": 62, "vram": 8,  "tier": "Mid"},
    "NVIDIA RTX 4060 Ti":         {"score": 72, "vram": 8,  "tier": "Mid"},
    "NVIDIA RTX 4060 Ti 16GB":    {"score": 74, "vram": 16, "tier": "Mid"},
    "NVIDIA RTX 4070":            {"score": 82, "vram": 12, "tier": "High"},
    "NVIDIA RTX 4070 Super":      {"score": 88, "vram": 12, "tier": "High"},
    "NVIDIA RTX 4070 Ti":         {"score": 91, "vram": 12, "tier": "High"},
    "NVIDIA RTX 4070 Ti Super":   {"score": 94, "vram": 16, "tier": "Ultra"},
    "NVIDIA RTX 4080":            {"score": 96, "vram": 16, "tier": "Ultra"},
    "NVIDIA RTX 4080 Super":      {"score": 97, "vram": 16, "tier": "Ultra"},
    "NVIDIA RTX 4090":            {"score": 100,"vram": 24, "tier": "Ultra"},
    "NVIDIA RTX 5070":            {"score": 90, "vram": 12, "tier": "High"},
    "NVIDIA RTX 5070 Ti":         {"score": 95, "vram": 16, "tier": "Ultra"},
    "NVIDIA RTX 5080":            {"score": 98, "vram": 16, "tier": "Ultra"},
    "NVIDIA RTX 5090":            {"score": 100,"vram": 32, "tier": "Ultra"},
    # AMD
    "AMD RX 6600":                {"score": 50, "vram": 8,  "tier": "Mid"},
    "AMD RX 6600 XT":             {"score": 55, "vram": 8,  "tier": "Mid"},
    "AMD RX 6700 XT":             {"score": 65, "vram": 12, "tier": "Mid"},
    "AMD RX 6800":                {"score": 75, "vram": 16, "tier": "High"},
    "AMD RX 6800 XT":             {"score": 83, "vram": 16, "tier": "High"},
    "AMD RX 6900 XT":             {"score": 88, "vram": 16, "tier": "Ultra"},
    "AMD RX 7600":                {"score": 55, "vram": 8,  "tier": "Mid"},
    "AMD RX 7700 XT":             {"score": 67, "vram": 12, "tier": "Mid"},
    "AMD RX 7800 XT":             {"score": 76, "vram": 16, "tier": "High"},
    "AMD RX 7900 GRE":            {"score": 83, "vram": 16, "tier": "High"},
    "AMD RX 7900 XT":             {"score": 90, "vram": 20, "tier": "Ultra"},
    "AMD RX 7900 XTX":            {"score": 94, "vram": 24, "tier": "Ultra"},
    "AMD RX 9070":                {"score": 82, "vram": 16, "tier": "High"},
    "AMD RX 9070 XT":             {"score": 90, "vram": 16, "tier": "Ultra"},
}

RAM_OPTIONS: dict[str, dict] = {
    "8 GB DDR4 2400 MHz":  {"score": 40, "gb": 8,  "type": "DDR4"},
    "8 GB DDR4 3200 MHz":  {"score": 52, "gb": 8,  "type": "DDR4"},
    "16 GB DDR4 3200 MHz": {"score": 72, "gb": 16, "type": "DDR4"},
    "16 GB DDR4 3600 MHz": {"score": 78, "gb": 16, "type": "DDR4"},
    "32 GB DDR4 3200 MHz": {"score": 82, "gb": 32, "type": "DDR4"},
    "32 GB DDR4 3600 MHz": {"score": 85, "gb": 32, "type": "DDR4"},
    "16 GB DDR5 4800 MHz": {"score": 80, "gb": 16, "type": "DDR5"},
    "16 GB DDR5 6000 MHz": {"score": 88, "gb": 16, "type": "DDR5"},
    "32 GB DDR5 6000 MHz": {"score": 94, "gb": 32, "type": "DDR5"},
    "32 GB DDR5 6400 MHz": {"score": 96, "gb": 32, "type": "DDR5"},
    "64 GB DDR5 6000 MHz": {"score": 98, "gb": 64, "type": "DDR5"},
}


# ──────────────────────────────────────────────
#  LÓGICA DE ANÁLISIS
# ──────────────────────────────────────────────

def analyze_bottleneck(cpu_name: str, gpu_name: str, ram_name: str) -> dict:
    """
    Calcula el cuello de botella comparando los scores normalizados.
    Retorna porcentajes de uso y el componente limitante.
    """
    cpu = CPUS.get(cpu_name, {})
    gpu = GPUS.get(gpu_name, {})
    ram = RAM_OPTIONS.get(ram_name, {})

    cs = cpu.get("score", 50)
    gs = gpu.get("score", 50)
    rs = ram.get("score", 50)

    # Diferencias relativas
    cpu_gpu_diff = abs(cs - gs)
    ram_factor   = max(0, (70 - rs) / 70)  # RAM penaliza si score < 70

    # Cuello de botella CPU→GPU: CPU no puede alimentar la GPU
    cpu_bottleneck_pct = round(max(0, (gs - cs) / max(gs, 1) * 100 * 0.85), 1)
    # Cuello de botella GPU→CPU: GPU no puede aprovechar el CPU
    gpu_bottleneck_pct = round(max(0, (cs - gs) / max(cs, 1) * 100 * 0.75), 1)
    # RAM siempre tiene un impacto menor
    ram_bottleneck_pct = round(ram_factor * 45, 1)

    # Cuál es el componente limitante
    scores = {
        "CPU": cs,
        "GPU": gs,
        "RAM": rs,
    }
    min_comp = min(scores, key=scores.get)
    max_comp = max(scores, key=scores.get)

    # Nivel general del sistema
    system_score = round((cs * 0.35 + gs * 0.50 + rs * 0.15))

    # Recomendación
    bottleneck_pct = max(cpu_bottleneck_pct, gpu_bottleneck_pct, ram_bottleneck_pct)

    if bottleneck_pct < 10:
        level = "Equilibrado"
        level_color = COLORS["free_color"]
        recommendation = "Tu sistema está bien balanceado. ¡Buen trabajo!"
    elif bottleneck_pct < 25:
        level = "Leve"
        level_color = COLORS["accent_gold"]
        if min_comp == "CPU":
            recommendation = f"Tu CPU limita levemente a tu GPU. Considera actualizar el procesador."
        elif min_comp == "GPU":
            recommendation = f"Tu CPU es algo más potente que tu GPU. Una GPU más rápida lo balancearía."
        else:
            recommendation = f"Tu RAM puede estar frenando el sistema. Prueba con más GB o mayor frecuencia."
    elif bottleneck_pct < 45:
        level = "Moderado"
        level_color = COLORS["accent_bottleneck"]
        recommendation = f"Cuello de botella notable en {min_comp}. Actualizar ese componente daría un gran salto de rendimiento."
    else:
        level = "Severo"
        level_color = COLORS["accent_red"]
        recommendation = f"¡Cuello de botella severo en {min_comp}! El resto del sistema desperdicia su potencial. Actualiza {min_comp} primero."

    return {
        "cpu_score":          cs,
        "gpu_score":          gs,
        "ram_score":          rs,
        "cpu_bottleneck_pct": cpu_bottleneck_pct,
        "gpu_bottleneck_pct": gpu_bottleneck_pct,
        "ram_bottleneck_pct": ram_bottleneck_pct,
        "bottleneck_pct":     bottleneck_pct,
        "bottleneck_level":   level,
        "bottleneck_color":   level_color,
        "weakest":            min_comp,
        "strongest":          max_comp,
        "system_score":       system_score,
        "recommendation":     recommendation,
        "cpu_info":           cpu,
        "gpu_info":           gpu,
        "ram_info":           ram,
    }


# ──────────────────────────────────────────────
#  VENTANA PRINCIPAL
# ──────────────────────────────────────────────

class BottleneckWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Calculadora de Cuello de Botella  •  Game Price Comparator")
        self.geometry("860x680")
        self.minsize(780, 600)
        self.configure(fg_color=COLORS["bg_main"])
        self.resizable(True, True)
        self._result_widgets = []
        self._build_ui()

    # ────────────────────────────────────────────

    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._build_header()
        self._build_body()

    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color=COLORS["bg_surface"], corner_radius=0, height=80)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)

        # Línea de acento
        ctk.CTkFrame(hdr, height=3, fg_color=COLORS["accent_bottleneck"], corner_radius=0
                     ).place(relx=0, rely=0, relwidth=1)

        inner = ctk.CTkFrame(hdr, fg_color="transparent")
        inner.place(relx=0.03, rely=0.55, anchor="w")

        ctk.CTkLabel(inner, text="⚡", font=("Segoe UI", 28),
                     text_color=COLORS["accent_bottleneck"]).pack(side="left", padx=(0, 10))

        title_col = ctk.CTkFrame(inner, fg_color="transparent")
        title_col.pack(side="left")

        ctk.CTkLabel(title_col, text="Calculadora de Cuello de Botella",
                     font=FONT_H1, text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(title_col,
                     text="Selecciona tus componentes para detectar el eslabón más débil de tu PC",
                     font=FONT_SMALL, text_color=COLORS["text_secondary"]).pack(anchor="w")

    def _build_body(self):
        body = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg_main"],
            scrollbar_button_color=COLORS["border"],
        )
        body.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        body.grid_columnconfigure(0, weight=1)

        # ── Selectores de componentes ──
        sel_frame = ctk.CTkFrame(body, fg_color=COLORS["bg_surface"], corner_radius=16,
                                 border_width=1, border_color=COLORS["border"])
        sel_frame.pack(fill="x", padx=24, pady=(20, 0))
        sel_frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(sel_frame, text="Selecciona tus componentes",
                     font=FONT_H2, text_color=COLORS["text_primary"]
                     ).grid(row=0, column=0, columnspan=3, sticky="w", padx=20, pady=(16, 4))

        ctk.CTkLabel(sel_frame,
                     text="Elige el componente más cercano al tuyo. Si no está exacto, selecciona el más similar.",
                     font=FONT_SMALL, text_color=COLORS["text_muted"]
                     ).grid(row=1, column=0, columnspan=3, sticky="w", padx=20, pady=(0, 12))

        # CPU
        self._make_selector(sel_frame, col=0,
                            label="🖥️  Procesador (CPU)",
                            options=sorted(CPUS.keys()),
                            color=COLORS["accent_steam"],
                            attr="_cpu_var")

        # GPU
        self._make_selector(sel_frame, col=1,
                            label="🎮  Tarjeta de Video (GPU)",
                            options=sorted(GPUS.keys()),
                            color=COLORS["accent_epic"],
                            attr="_gpu_var")

        # RAM
        self._make_selector(sel_frame, col=2,
                            label="💾  Memoria RAM",
                            options=list(RAM_OPTIONS.keys()),
                            color=COLORS["accent_gold"],
                            attr="_ram_var")

        # Botón analizar
        btn_row = ctk.CTkFrame(sel_frame, fg_color="transparent")
        btn_row.grid(row=3, column=0, columnspan=3, pady=(10, 20))

        self.analyze_btn = ctk.CTkButton(
            btn_row,
            text="  ⚡  Analizar mi PC  ",
            width=220, height=46,
            font=("Segoe UI", 13, "bold"),
            fg_color=COLORS["accent_bottleneck"],
            hover_color="#cc4a1a",
            corner_radius=12,
            command=self._do_analyze,
        )
        self.analyze_btn.pack()

        # ── Área de resultados (se llena al analizar) ──
        self.results_frame = ctk.CTkFrame(body, fg_color="transparent")
        self.results_frame.pack(fill="x", padx=24, pady=(16, 24))
        self.results_frame.grid_columnconfigure(0, weight=1)

    def _make_selector(self, parent, col: int, label: str,
                       options: list, color: str, attr: str):
        col_frame = ctk.CTkFrame(parent, fg_color="transparent")
        col_frame.grid(row=2, column=col, padx=14, pady=(0, 8), sticky="ew")

        ctk.CTkLabel(col_frame, text=label, font=FONT_SMALL,
                     text_color=color).pack(anchor="w", pady=(0, 4))

        var = tk.StringVar(value=options[0])
        setattr(self, attr, var)

        combo = ctk.CTkOptionMenu(
            col_frame,
            variable=var,
            values=options,
            width=240, height=36,
            font=("Segoe UI", 10),
            fg_color=COLORS["bg_input"],
            button_color=color,
            button_hover_color=COLORS["bg_card_hover"],
            text_color=COLORS["text_primary"],
            dropdown_fg_color=COLORS["bg_surface"],
            dropdown_text_color=COLORS["text_primary"],
            dropdown_hover_color=COLORS["bg_card"],
            corner_radius=8,
            dynamic_resizing=False,
        )
        combo.pack(fill="x")

    # ────────────────────────────────────────────
    #  Análisis
    # ────────────────────────────────────────────

    def _do_analyze(self):
        cpu = self._cpu_var.get()
        gpu = self._gpu_var.get()
        ram = self._ram_var.get()

        self.analyze_btn.configure(state="disabled", text="Analizando…")
        for w in self.results_frame.winfo_children():
            w.destroy()

        # Barra de progreso animada
        prog_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS["bg_surface"],
                                  corner_radius=12)
        prog_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(prog_frame, text="Analizando componentes…",
                     font=FONT_BODY, text_color=COLORS["text_secondary"]).pack(pady=(14, 6))
        prog = ctk.CTkProgressBar(prog_frame, width=400, height=8,
                                  fg_color=COLORS["border"],
                                  progress_color=COLORS["accent_bottleneck"])
        prog.pack(pady=(0, 14))
        prog.set(0)
        prog.start()

        def worker():
            time.sleep(1.2)  # Simula análisis para UX
            result = analyze_bottleneck(cpu, gpu, ram)
            self.after(0, lambda: self._render_result(result, prog_frame))

        threading.Thread(target=worker, daemon=True).start()

    def _render_result(self, r: dict, prog_frame):
        prog_frame.destroy()
        self.analyze_btn.configure(state="normal", text="  ⚡  Analizar mi PC  ")
        rf = self.results_frame

        # ── Card principal: resultado global ──
        main_card = ctk.CTkFrame(rf, fg_color=COLORS["bg_surface"],
                                 corner_radius=16, border_width=1,
                                 border_color=r["bottleneck_color"])
        main_card.pack(fill="x", pady=(0, 14))

        top_row = ctk.CTkFrame(main_card, fg_color="transparent")
        top_row.pack(fill="x", padx=20, pady=(18, 8))

        # Score del sistema
        score_box = ctk.CTkFrame(top_row, fg_color=COLORS["bg_card"],
                                 corner_radius=12, width=90, height=90)
        score_box.pack(side="left", padx=(0, 20))
        score_box.pack_propagate(False)
        ctk.CTkLabel(score_box, text=str(r["system_score"]),
                     font=("Segoe UI Semibold", 32),
                     text_color=r["bottleneck_color"]).place(relx=0.5, rely=0.4, anchor="center")
        ctk.CTkLabel(score_box, text="/ 100",
                     font=FONT_SMALL, text_color=COLORS["text_muted"]).place(relx=0.5, rely=0.78, anchor="center")

        # Texto resultado
        text_col = ctk.CTkFrame(top_row, fg_color="transparent")
        text_col.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            text_col,
            text=f"Cuello de Botella:  {r['bottleneck_level']}",
            font=("Segoe UI Semibold", 18),
            text_color=r["bottleneck_color"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            text_col,
            text=f"Componente limitante:  {r['weakest']}",
            font=FONT_TITLE,
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w", pady=(4, 0))

        ctk.CTkLabel(
            text_col,
            text=r["recommendation"],
            font=FONT_SMALL,
            text_color=COLORS["text_primary"],
            wraplength=440,
            justify="left",
        ).pack(anchor="w", pady=(8, 0))

        # ── Barras de componentes ──
        bars_card = ctk.CTkFrame(rf, fg_color=COLORS["bg_surface"],
                                 corner_radius=14, border_width=1,
                                 border_color=COLORS["border"])
        bars_card.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(bars_card, text="Rendimiento por componente",
                     font=FONT_H2, text_color=COLORS["text_primary"]
                     ).pack(anchor="w", padx=20, pady=(16, 10))

        components = [
            ("🖥️  CPU", r["cpu_score"], COLORS["accent_steam"],
             f"{CPUS.get(self._cpu_var.get(), {}).get('cores', '?')} núcleos  ·  {CPUS.get(self._cpu_var.get(), {}).get('tdp', '?')}W TDP"),
            ("🎮  GPU", r["gpu_score"], COLORS["accent_epic"],
             f"{GPUS.get(self._gpu_var.get(), {}).get('vram', '?')} GB VRAM  ·  {GPUS.get(self._gpu_var.get(), {}).get('tier', '?')}"),
            ("💾  RAM", r["ram_score"], COLORS["accent_gold"],
             f"{RAM_OPTIONS.get(self._ram_var.get(), {}).get('gb', '?')} GB  ·  {RAM_OPTIONS.get(self._ram_var.get(), {}).get('type', '?')}"),
        ]

        for label, score, color, detail in components:
            self._bar_row(bars_card, label, score, color, detail)

        ctk.CTkFrame(bars_card, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=20)

        # ── Cuello de botella detallado ──
        bn_card = ctk.CTkFrame(rf, fg_color=COLORS["bg_surface"],
                               corner_radius=14, border_width=1,
                               border_color=COLORS["border"])
        bn_card.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(bn_card, text="Análisis de cuello de botella",
                     font=FONT_H2, text_color=COLORS["text_primary"]
                     ).pack(anchor="w", padx=20, pady=(16, 10))

        bn_items = [
            ("CPU limitando GPU", r["cpu_bottleneck_pct"], COLORS["accent_steam"],
             "El CPU no puede procesar suficientes frames para la GPU"),
            ("GPU limitando CPU", r["gpu_bottleneck_pct"], COLORS["accent_epic"],
             "La GPU es el cuello de botella para el CPU"),
            ("Impacto de RAM",   r["ram_bottleneck_pct"], COLORS["accent_gold"],
             "La RAM frena el sistema por capacidad o velocidad"),
        ]

        for label, pct, color, desc in bn_items:
            self._bottleneck_bar(bn_card, label, pct, color, desc)

        ctk.CTkFrame(bn_card, height=24, fg_color="transparent").pack()

    def _bar_row(self, parent, label: str, score: int, color: str, detail: str):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 12))

        top = ctk.CTkFrame(row, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(top, text=label, font=FONT_TITLE,
                     text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkLabel(top, text=detail, font=FONT_SMALL,
                     text_color=COLORS["text_muted"]).pack(side="left", padx=(10, 0))
        ctk.CTkLabel(top, text=f"{score}/100", font=("Segoe UI", 11, "bold"),
                     text_color=color).pack(side="right")

        bar_bg = ctk.CTkFrame(row, height=8, fg_color=COLORS["border"], corner_radius=4)
        bar_bg.pack(fill="x", pady=(4, 0))

        bar_fill = ctk.CTkFrame(bar_bg, height=8,
                                fg_color=color, corner_radius=4)
        # Animación de barra
        self._animate_bar(bar_fill, bar_bg, score / 100)

    def _bottleneck_bar(self, parent, label: str, pct: float, color: str, desc: str):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 10))

        top = ctk.CTkFrame(row, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(top, text=label, font=FONT_SMALL,
                     text_color=COLORS["text_secondary"]).pack(side="left")
        pct_color = COLORS["free_color"] if pct < 10 else (
            COLORS["accent_gold"] if pct < 25 else (
                COLORS["accent_bottleneck"] if pct < 45 else COLORS["accent_red"]
            )
        )
        ctk.CTkLabel(top, text=f"{pct:.0f}%", font=("Segoe UI", 10, "bold"),
                     text_color=pct_color).pack(side="right")

        bar_bg = ctk.CTkFrame(row, height=6, fg_color=COLORS["border"], corner_radius=3)
        bar_bg.pack(fill="x", pady=(3, 0))

        bar_fill = ctk.CTkFrame(bar_bg, height=6, fg_color=pct_color, corner_radius=3)
        self._animate_bar(bar_fill, bar_bg, pct / 100)

        ctk.CTkLabel(row, text=desc, font=("Segoe UI", 9),
                     text_color=COLORS["text_muted"]).pack(anchor="w")

    def _animate_bar(self, bar_fill, bar_bg, target: float, step: float = 0.0):
        """Anima la barra desde 0 hasta target progresivamente."""
        if step >= target:
            bar_fill.place(relx=0, rely=0, relwidth=target, relheight=1)
            return
        bar_fill.place(relx=0, rely=0, relwidth=step, relheight=1)
        next_step = min(step + 0.02, target)
        self.after(16, lambda: self._animate_bar(bar_fill, bar_bg, target, next_step))
