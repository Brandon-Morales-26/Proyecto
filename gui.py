import customtkinter as ctk
from datetime import datetime, timedelta
import tkinter as tk
import math
import database as db


# ── Paleta azul-verde oscuro ──────────────────────────────────────────────────
FONDO_APP    = "#080f1a"
FONDO_PANEL  = "#0d1a2e"
FONDO_ITEM   = "#0f2236"

AZUL_VIVO    = "#00b4d8"
AZUL_MEDIO   = "#0077a8"
AZUL_HOVER   = "#005f87"
AZUL_OSCURO  = "#023e5c"
VERDE_VIVO   = "#00d68f"
AMBAR_AVISO  = "#f4a261"
ROJO_CRITICO = "#e63946"
ROJO_HOVER   = "#b52b36"

GRIS_TEXTO   = "#5a7a99"
BLANCO_SUAVE = "#c8dff0"
BORDE_SUTIL  = "#112840"


# ── Canvas decorativo de fondo ────────────────────────────────────────────────

class FondoDecorado(tk.Canvas):
    """
    Canvas animado con:
    - Cuadrícula de puntos tenues
    - Orbes grandes semi-transparentes pulsantes (efecto nebulosa)
    - Líneas diagonales decorativas en esquinas
    - Línea central horizontal punteada
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, highlightthickness=0, bg=FONDO_APP, **kwargs)
        self._tick = 0
        self._orbs = [
            {"cx": 0.12, "cy": 0.18, "r": 210, "color": "#003a5c", "phase": 0.0, "speed": 0.008},
            {"cx": 0.88, "cy": 0.12, "r": 175, "color": "#004d40", "phase": 1.0, "speed": 0.006},
            {"cx": 0.72, "cy": 0.78, "r": 250, "color": "#002b4a", "phase": 2.2, "speed": 0.005},
            {"cx": 0.08, "cy": 0.82, "r": 145, "color": "#003d33", "phase": 3.5, "speed": 0.007},
            {"cx": 0.50, "cy": 0.48, "r": 190, "color": "#001e38", "phase": 1.8, "speed": 0.004},
        ]
        self.bind("<Configure>", lambda e: self._dibujar())
        self._animar()

    def _dibujar(self):
        self.delete("all")
        W = self.winfo_width()
        H = self.winfo_height()
        if W < 2 or H < 2:
            return

        # Cuadrícula de puntos
        paso = 38
        for x in range(0, W, paso):
            for y in range(0, H, paso):
                self.create_oval(x - 1, y - 1, x + 1, y + 1,
                                 fill="#0d2a45", outline="")

        # Líneas diagonales esquina superior izquierda
        for i in range(12):
            off = i * 28
            self.create_line(0, off, off, 0, fill="#0d2a45", width=1)

        # Líneas diagonales esquina inferior derecha
        for i in range(12):
            off = i * 28
            self.create_line(W, H - off, W - off, H, fill="#0d2a45", width=1)

        # Orbes animados
        t = self._tick
        for orb in self._orbs:
            pulse = math.sin(t * orb["speed"] + orb["phase"]) * 16
            cx = int(orb["cx"] * W)
            cy = int(orb["cy"] * H)
            r  = int(orb["r"] + pulse)
            for k, c in enumerate(["#0a1e35", "#091929", "#071420"]):
                rk = r - k * 20
                if rk > 0:
                    self.create_oval(cx - rk, cy - rk, cx + rk, cy + rk,
                                     fill=c, outline="")
            self.create_oval(cx - r - 28, cy - r - 28, cx + r + 28, cy + r + 28,
                             fill="", outline=orb["color"], width=1)

        # Línea central horizontal punteada
        self.create_line(40, H // 2, W - 40, H // 2,
                         fill="#0d2a45", width=1, dash=(4, 18))

    def _animar(self):
        self._tick += 1
        self._dibujar()
        self.after(62, self._animar)


# ── Tooltip ───────────────────────────────────────────────────────────────────

class TooltipLabel(ctk.CTkLabel):
    def __init__(self, master, tooltip_text="", **kwargs):
        super().__init__(master, **kwargs)
        self._tooltip_text = tooltip_text
        self._tw = None
        self.bind("<Enter>", self._show)
        self.bind("<Leave>", self._hide)

    def _show(self, _=None):
        if not self._tooltip_text:
            return
        x = self.winfo_rootx() + 20
        y = self.winfo_rooty() + 20
        self._tw = ctk.CTkToplevel(self)
        self._tw.wm_overrideredirect(True)
        self._tw.geometry(f"+{x}+{y}")
        ctk.CTkLabel(
            self._tw, text=self._tooltip_text,
            fg_color=FONDO_PANEL, corner_radius=6,
            text_color=BLANCO_SUAVE, padx=10, pady=5
        ).pack()

    def _hide(self, _=None):
        if self._tw:
            self._tw.destroy()
            self._tw = None


# ── Diálogo de confirmación ───────────────────────────────────────────────────

class DialogoConfirmar(ctk.CTkToplevel):
    def __init__(self, parent, nombre, callback_confirmar):
        super().__init__(parent)
        self.title("Confirmar eliminación")
        self.geometry("380x170")
        self.resizable(False, False)
        self.configure(fg_color=FONDO_PANEL)
        self.grab_set()

        ctk.CTkLabel(
            self,
            text=f"¿Eliminar «{nombre}»?",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=BLANCO_SUAVE
        ).pack(pady=(22, 6))
        ctk.CTkLabel(
            self, text="Esta acción no se puede deshacer.",
            text_color=GRIS_TEXTO, font=ctk.CTkFont(size=12)
        ).pack()

        frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        frame_btns.pack(pady=20)

        ctk.CTkButton(
            frame_btns, text="Cancelar", width=130,
            fg_color="transparent", border_width=1,
            border_color=BORDE_SUTIL, text_color=BLANCO_SUAVE,
            hover_color=FONDO_ITEM, command=self.destroy
        ).grid(row=0, column=0, padx=8)

        ctk.CTkButton(
            frame_btns, text="Eliminar", width=130,
            fg_color=ROJO_CRITICO, hover_color=ROJO_HOVER,
            command=lambda: [callback_confirmar(), self.destroy()]
        ).grid(row=0, column=1, padx=8)


# ── Tarjeta de componente ─────────────────────────────────────────────────────

class TarjetaComponente(ctk.CTkFrame):
    def __init__(self, master, id_db, nombre, fecha_compra_str,
                 meses_garantia, descripcion, callback_borrar, **kwargs):
        super().__init__(master, corner_radius=12, fg_color=FONDO_ITEM,
                         border_width=1, border_color=BORDE_SUTIL, **kwargs)

        fecha_dt    = datetime.strptime(fecha_compra_str, "%Y-%m-%d")
        vencimiento = fecha_dt + timedelta(days=meses_garantia * 30)
        dias_rest   = (vencimiento - datetime.now()).days

        if dias_rest < 0:
            color_badge = ROJO_CRITICO; icono = "✕"; badge_txt = "VENCIDA"
        elif dias_rest < 15:
            color_badge = ROJO_CRITICO; icono = "⚠"; badge_txt = f"{dias_rest}d"
        elif dias_rest < 60:
            color_badge = AMBAR_AVISO;  icono = "~"; badge_txt = f"{dias_rest}d"
        else:
            color_badge = VERDE_VIVO;   icono = "✓"; badge_txt = f"{dias_rest}d"

        # Barra lateral de color según estado
        barra = tk.Frame(self, width=4, bg=color_badge)
        barra.pack(side="left", fill="y")

        interior = ctk.CTkFrame(self, fg_color="transparent")
        interior.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        interior.columnconfigure(1, weight=1)

        # Icono
        ctk.CTkLabel(
            interior, text=icono,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=color_badge, width=32
        ).grid(row=0, column=0, rowspan=3, padx=(4, 10))

        # Nombre
        ctk.CTkLabel(
            interior, text=nombre,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=BLANCO_SUAVE, anchor="w"
        ).grid(row=0, column=1, sticky="ew", pady=(2, 0))

        # Descripción
        if descripcion and descripcion.strip():
            ctk.CTkLabel(
                interior, text=descripcion.strip(),
                font=ctk.CTkFont(size=11),
                text_color=GRIS_TEXTO, anchor="w", wraplength=370
            ).grid(row=1, column=1, sticky="ew", pady=(0, 2))

        # Fechas
        texto_fechas = (
            f"Compra: {fecha_dt.strftime('%d/%m/%Y')}  ·  "
            f"Vence: {vencimiento.strftime('%d/%m/%Y')}"
        )
        ctk.CTkLabel(
            interior, text=texto_fechas,
            font=ctk.CTkFont(size=10),
            text_color=GRIS_TEXTO, anchor="w"
        ).grid(row=2, column=1, sticky="ew", pady=(0, 2))

        # Badge días
        tooltip_msg = ("Garantía vencida" if dias_rest < 0
                       else f"{dias_rest} días de garantía restantes")
        TooltipLabel(
            interior, tooltip_text=tooltip_msg,
            text=badge_txt,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="white", fg_color=color_badge,
            corner_radius=6, padx=8, pady=2,
            width=66, anchor="center"
        ).grid(row=0, column=2, rowspan=3, padx=10)

        # Botón eliminar
        ctk.CTkButton(
            interior, text="✕", width=32, height=32,
            fg_color="transparent", border_width=1,
            border_color=ROJO_CRITICO, text_color=ROJO_CRITICO,
            hover_color="#2a0a0e", corner_radius=8,
            font=ctk.CTkFont(size=13),
            command=lambda: DialogoConfirmar(
                self.winfo_toplevel(), nombre,
                lambda: callback_borrar(id_db)
            )
        ).grid(row=0, column=3, rowspan=3, padx=(4, 12))


# ── Formulario ────────────────────────────────────────────────────────────────

class PanelFormulario(ctk.CTkFrame):
    def __init__(self, master, callback_agregar, **kwargs):
        super().__init__(master, corner_radius=14, fg_color=FONDO_PANEL,
                         border_width=1, border_color=BORDE_SUTIL, **kwargs)
        self._callback = callback_agregar

        # Título
        titulo_f = ctk.CTkFrame(self, fg_color="transparent")
        titulo_f.grid(row=0, column=0, columnspan=4, sticky="w",
                      padx=16, pady=(14, 6))
        ctk.CTkLabel(titulo_f, text="⊕", font=ctk.CTkFont(size=14),
                     text_color=AZUL_VIVO).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(titulo_f, text="Añadir componente",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=BLANCO_SUAVE).pack(side="left")

        # Etiquetas
        for col, lbl in enumerate(["Componente", "Fecha compra (DD/MM/AAAA)", "Garantía (meses)"]):
            ctk.CTkLabel(self, text=lbl, font=ctk.CTkFont(size=10),
                         text_color=GRIS_TEXTO
                         ).grid(row=1, column=col,
                                padx=(16 if col == 0 else 6, 4),
                                pady=(0, 3), sticky="w")

        # Entradas fila 2
        self.entry_nombre = ctk.CTkEntry(
            self, placeholder_text="ej: RTX 4080 Super", width=210,
            fg_color=FONDO_ITEM, border_color=AZUL_OSCURO, text_color=BLANCO_SUAVE)
        self.entry_nombre.grid(row=2, column=0, padx=(16, 6), pady=(0, 8))

        self.entry_fecha = ctk.CTkEntry(
            self, placeholder_text="dd/mm/aaaa", width=150,
            fg_color=FONDO_ITEM, border_color=AZUL_OSCURO, text_color=BLANCO_SUAVE)
        self.entry_fecha.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.entry_fecha.grid(row=2, column=1, padx=6, pady=(0, 8))

        self.entry_garantia = ctk.CTkEntry(
            self, placeholder_text="ej: 24", width=90,
            fg_color=FONDO_ITEM, border_color=AZUL_OSCURO, text_color=BLANCO_SUAVE)
        self.entry_garantia.grid(row=2, column=2, padx=6, pady=(0, 8))

        ctk.CTkButton(
            self, text="+ Guardar", width=120,
            fg_color=AZUL_MEDIO, hover_color=AZUL_HOVER,
            text_color="white", font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=10, command=self._enviar
        ).grid(row=2, column=3, padx=(6, 16), pady=(0, 8))

        # Descripción
        ctk.CTkLabel(self, text="Descripción / Especificaciones (opcional)",
                     font=ctk.CTkFont(size=10), text_color=GRIS_TEXTO
                     ).grid(row=3, column=0, columnspan=4,
                            sticky="w", padx=16, pady=(0, 3))

        self.entry_desc = ctk.CTkTextbox(
            self, height=52, corner_radius=10,
            fg_color=FONDO_ITEM, border_color=AZUL_OSCURO,
            border_width=1, text_color=BLANCO_SUAVE)
        self.entry_desc.grid(row=4, column=0, columnspan=4,
                             padx=16, pady=(0, 10), sticky="ew")

        self._ph = "ej: 16 GB DDR5 6000 MHz · CL30 · 2×8 GB · XMP 3.0"
        self._set_placeholder()
        self.entry_desc.bind("<FocusIn>",  self._clear_ph)
        self.entry_desc.bind("<FocusOut>", self._restore_ph)

        # Error
        self.label_error = ctk.CTkLabel(
            self, text="", text_color=ROJO_CRITICO, font=ctk.CTkFont(size=11))
        self.label_error.grid(row=5, column=0, columnspan=4, padx=16, pady=(0, 8))

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def _set_placeholder(self):
        self.entry_desc.delete("1.0", "end")
        self.entry_desc.insert("1.0", self._ph)
        self.entry_desc.configure(text_color=GRIS_TEXTO)

    def _clear_ph(self, _=None):
        if self.entry_desc.get("1.0", "end").strip() == self._ph:
            self.entry_desc.delete("1.0", "end")
            self.entry_desc.configure(text_color=BLANCO_SUAVE)

    def _restore_ph(self, _=None):
        if not self.entry_desc.get("1.0", "end").strip():
            self._set_placeholder()

    def _get_desc(self):
        t = self.entry_desc.get("1.0", "end").strip()
        return "" if t == self._ph else t

    def _enviar(self):
        nombre    = self.entry_nombre.get().strip()
        fecha_raw = self.entry_fecha.get().strip()
        meses_raw = self.entry_garantia.get().strip()
        desc      = self._get_desc()

        if not nombre:
            self.label_error.configure(text="El nombre no puede estar vacío.")
            return
        try:
            fecha_dt = datetime.strptime(fecha_raw, "%d/%m/%Y")
        except ValueError:
            self.label_error.configure(text="Fecha inválida. Usa DD/MM/AAAA.")
            return
        try:
            meses = int(meses_raw)
            if meses <= 0:
                raise ValueError
        except ValueError:
            self.label_error.configure(text="Los meses deben ser un número entero positivo.")
            return

        self.label_error.configure(text="")
        self._callback(nombre, fecha_dt.strftime("%Y-%m-%d"), meses, desc)

        self.entry_nombre.delete(0, "end")
        self.entry_garantia.delete(0, "end")
        self.entry_fecha.delete(0, "end")
        self.entry_fecha.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self._set_placeholder()


# ── Panel de estadísticas ─────────────────────────────────────────────────────

class PanelEstadisticas(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=14, fg_color=FONDO_PANEL,
                         border_width=1, border_color=BORDE_SUTIL, **kwargs)
        self._labels = {}
        specs = [
            ("total",   "TOTAL",     AZUL_VIVO),
            ("ok",      "OK",        VERDE_VIVO),
            ("aviso",   "AVISO",     AMBAR_AVISO),
            ("critico", "CRÍTICO",   ROJO_CRITICO),
            ("vencido", "VENCIDOS",  ROJO_CRITICO),
        ]
        for i, (clave, titulo, color) in enumerate(specs):
            self.columnconfigure(i, weight=1)
            if i > 0:
                tk.Frame(self, width=1, bg=BORDE_SUTIL).grid(
                    row=0, column=i, rowspan=3, sticky="ns")

            ctk.CTkLabel(self, text=titulo, font=ctk.CTkFont(size=9, weight="bold"),
                         text_color=GRIS_TEXTO
                         ).grid(row=0, column=i, padx=16, pady=(12, 0))

            lbl = ctk.CTkLabel(self, text="0",
                               font=ctk.CTkFont(size=26, weight="bold"),
                               text_color=GRIS_TEXTO)
            lbl.grid(row=1, column=i, padx=16, pady=(2, 0))

            barra = tk.Frame(self, height=3, bg=BORDE_SUTIL)
            barra.grid(row=2, column=i, sticky="ew", padx=20, pady=(4, 12))

            self._labels[clave] = (lbl, barra, color)

    def actualizar(self, componentes):
        total = len(componentes)
        ok = aviso = critico = vencido = 0
        for _, _, fecha_compra, meses, _ in componentes:
            fecha_dt    = datetime.strptime(fecha_compra, "%Y-%m-%d")
            vencimiento = fecha_dt + timedelta(days=meses * 30)
            dias        = (vencimiento - datetime.now()).days
            if dias < 0:    vencido += 1
            elif dias < 15: critico += 1
            elif dias < 60: aviso   += 1
            else:           ok      += 1

        datos = {"total": total, "ok": ok, "aviso": aviso,
                 "critico": critico, "vencido": vencido}
        for clave, (lbl, barra, color) in self._labels.items():
            val = datos[clave]
            activo = val > 0
            lbl.configure(text=str(val),
                          text_color=color if activo else GRIS_TEXTO)
            barra.configure(bg=color if activo else BORDE_SUTIL)


# ── App principal ─────────────────────────────────────────────────────────────

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PC Master Manager")
        self.geometry("860x800")
        self.minsize(720, 580)
        self.configure(fg_color=FONDO_APP)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Fondo decorativo animado
        self._fondo = FondoDecorado(self)
        self._fondo.place(x=0, y=0, relwidth=1, relheight=1)

        # Frame principal encima del canvas
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.place(x=0, y=0, relwidth=1, relheight=1)

        # ── Encabezado ────────────────────────────────────────────────────────
        hdr = ctk.CTkFrame(main, fg_color="transparent")
        hdr.pack(fill="x", padx=26, pady=(22, 0))

        ctk.CTkLabel(hdr, text="◈", font=ctk.CTkFont(size=28),
                     text_color=AZUL_VIVO).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(hdr, text="PC Master Manager",
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=BLANCO_SUAVE).pack(side="left")
        ctk.CTkLabel(hdr, text="·  Inventario de garantías",
                     font=ctk.CTkFont(size=13),
                     text_color=GRIS_TEXTO).pack(side="left", padx=8)
        ctk.CTkLabel(hdr, text=datetime.now().strftime("%d %b %Y"),
                     font=ctk.CTkFont(size=11),
                     text_color=GRIS_TEXTO).pack(side="right")

        # Separador decorativo con acento de color
        sep_frame = ctk.CTkFrame(main, fg_color="transparent")
        sep_frame.pack(fill="x", padx=26, pady=(10, 0))
        tk.Frame(sep_frame, height=1, bg=BORDE_SUTIL).pack(fill="x")
        tk.Frame(sep_frame, height=1, bg=AZUL_VIVO).pack(fill="x", padx=0, pady=(1, 0))

        # ── Estadísticas ──────────────────────────────────────────────────────
        self.panel_stats = PanelEstadisticas(main)
        self.panel_stats.pack(fill="x", padx=26, pady=(14, 0))

        # ── Formulario ────────────────────────────────────────────────────────
        self.panel_form = PanelFormulario(main, callback_agregar=self.agregar)
        self.panel_form.pack(fill="x", padx=26, pady=(12, 0))

        # ── Búsqueda + filtro ──────────────────────────────────────────────────
        buscar_f = ctk.CTkFrame(main, fg_color="transparent")
        buscar_f.pack(fill="x", padx=26, pady=(12, 0))

        ctk.CTkLabel(buscar_f, text="⌕", font=ctk.CTkFont(size=16),
                     text_color=AZUL_VIVO).pack(side="left", padx=(0, 6))

        self.entry_buscar = ctk.CTkEntry(
            buscar_f,
            placeholder_text="Buscar por nombre o especificación...",
            width=320, fg_color=FONDO_PANEL,
            border_color=AZUL_OSCURO, text_color=BLANCO_SUAVE)
        self.entry_buscar.pack(side="left")
        self.entry_buscar.bind("<KeyRelease>", lambda e: self.cargar_datos())

        self.combo_filtro = ctk.CTkComboBox(
            buscar_f,
            values=["Todos", "OK", "Aviso", "Crítico", "Vencido"],
            width=140, fg_color=FONDO_PANEL,
            border_color=AZUL_OSCURO, button_color=AZUL_MEDIO,
            button_hover_color=AZUL_HOVER,
            dropdown_fg_color=FONDO_PANEL, text_color=BLANCO_SUAVE,
            command=lambda v: self.cargar_datos())
        self.combo_filtro.set("Todos")
        self.combo_filtro.pack(side="left", padx=10)

        self.lbl_contador = ctk.CTkLabel(
            buscar_f, text="", font=ctk.CTkFont(size=11), text_color=GRIS_TEXTO)
        self.lbl_contador.pack(side="right")

        # ── Lista ──────────────────────────────────────────────────────────────
        self.scrollable = ctk.CTkScrollableFrame(
            main, fg_color="transparent",
            label_text="  Hardware registrado",
            label_font=ctk.CTkFont(size=12, weight="bold"),
            label_fg_color=FONDO_PANEL,
            label_text_color=AZUL_VIVO,
            scrollbar_button_color=AZUL_OSCURO,
            scrollbar_button_hover_color=AZUL_MEDIO,
        )
        self.scrollable.pack(fill="both", expand=True, padx=26, pady=(10, 22))

        self.cargar_datos()

    # ── Lógica ────────────────────────────────────────────────────────────────

    def agregar(self, nombre, fecha_db, meses, descripcion=""):
        db.guardar_componente(nombre, fecha_db, meses, descripcion)
        self.cargar_datos()

    def borrar(self, id_item):
        db.eliminar_componente(id_item)
        self.cargar_datos()

    def cargar_datos(self, *_):
        for w in self.scrollable.winfo_children():
            w.destroy()

        busqueda = self.entry_buscar.get().strip().lower()
        filtro   = self.combo_filtro.get()
        filas    = db.obtener_componentes()

        self.panel_stats.actualizar(filas)

        mostradas = 0
        for fila in filas:
            id_db, nombre, fecha_compra, meses, descripcion = fila

            if busqueda and (busqueda not in nombre.lower()
                             and busqueda not in descripcion.lower()):
                continue

            fecha_dt    = datetime.strptime(fecha_compra, "%Y-%m-%d")
            vencimiento = fecha_dt + timedelta(days=meses * 30)
            dias_rest   = (vencimiento - datetime.now()).days

            if filtro == "OK"      and not (dias_rest >= 60):     continue
            if filtro == "Aviso"   and not (0 <= dias_rest < 60): continue
            if filtro == "Crítico" and not (0 <= dias_rest < 15): continue
            if filtro == "Vencido" and not (dias_rest < 0):       continue

            TarjetaComponente(
                self.scrollable,
                id_db=id_db, nombre=nombre,
                fecha_compra_str=fecha_compra,
                meses_garantia=meses, descripcion=descripcion,
                callback_borrar=self.borrar
            ).pack(fill="x", pady=5, padx=4)
            mostradas += 1

        self.lbl_contador.configure(
            text=f"{mostradas} de {len(filas)} componentes")

        if mostradas == 0:
            ctk.CTkFrame(self.scrollable,
                         fg_color="transparent", height=30).pack()
            ctk.CTkLabel(
                self.scrollable, text="◈  Sin resultados",
                text_color=GRIS_TEXTO,
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(pady=(30, 4))
            ctk.CTkLabel(
                self.scrollable,
                text="Añade un componente o cambia el filtro.",
                text_color=GRIS_TEXTO, font=ctk.CTkFont(size=12)
            ).pack()