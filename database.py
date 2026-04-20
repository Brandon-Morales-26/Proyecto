import sqlite3
from datetime import datetime, timedelta

def conectar():
    return sqlite3.connect("inventario_pc.db")

def iniciar_db():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS componentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                fecha_compra TEXT NOT NULL,
                meses_garantia INTEGER NOT NULL
            )
        ''')

def guardar_componente(nombre, meses):
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO componentes (nombre, fecha_compra, meses_garantia) VALUES (?, ?, ?)",
                       (nombre, fecha_hoy, meses))

def obtener_componentes():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM componentes")
        return cursor.fetchall()

def eliminar_componente(id_item):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM componentes WHERE id = ?", (id_item,))
        conn.commit()
from datetime import datetime


DB_PATH = "inventario_pc.db"


def conectar():
    return sqlite3.connect(DB_PATH)


def iniciar_db():
    """Crea la tabla si no existe y aplica migraciones pendientes."""
    with conectar() as conn:
        cursor = conn.cursor()

        # Tabla base (compatible con instalaciones nuevas)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS componentes (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre          TEXT    NOT NULL,
                fecha_compra    TEXT    NOT NULL,
                meses_garantia  INTEGER NOT NULL,
                descripcion     TEXT    DEFAULT ''
            )
        ''')

        # ── Migración automática ─────────────────────────────────────────
        # Si la DB ya existía sin la columna 'descripcion', la añadimos
        # sin perder ningún dato previo.
        columnas = [fila[1] for fila in cursor.execute("PRAGMA table_info(componentes)")]
        if "descripcion" not in columnas:
            cursor.execute("ALTER TABLE componentes ADD COLUMN descripcion TEXT DEFAULT ''")

        conn.commit()


# ── CRUD ─────────────────────────────────────────────────────────────────────

def guardar_componente(nombre: str, fecha_compra: str, meses: int, descripcion: str = "") -> int:
    """
    Inserta un componente y devuelve el id generado.

    Parámetros
    ----------
    nombre       : nombre del componente (ej. 'Teclado Mecánico')
    fecha_compra : fecha en formato 'YYYY-MM-DD'
    meses        : meses de garantía
    descripcion  : texto libre con especificaciones (opcional)
    """
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO componentes (nombre, fecha_compra, meses_garantia, descripcion) "
            "VALUES (?, ?, ?, ?)",
            (nombre, fecha_compra, meses, descripcion.strip())
        )
        conn.commit()
        return cursor.lastrowid


def obtener_componentes() -> list[tuple]:
    """
    Devuelve todas las filas como lista de tuplas:
    (id, nombre, fecha_compra, meses_garantia, descripcion)
    """
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nombre, fecha_compra, meses_garantia, descripcion "
            "FROM componentes ORDER BY fecha_compra DESC"
        )
        return cursor.fetchall()


def obtener_componente(id_item: int) -> tuple | None:
    """Devuelve una fila por id, o None si no existe."""
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nombre, fecha_compra, meses_garantia, descripcion "
            "FROM componentes WHERE id = ?",
            (id_item,)
        )
        return cursor.fetchone()


def actualizar_componente(id_item: int, nombre: str, fecha_compra: str,
                          meses: int, descripcion: str = "") -> None:
    """Actualiza todos los campos de un componente existente."""
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE componentes "
            "SET nombre=?, fecha_compra=?, meses_garantia=?, descripcion=? "
            "WHERE id=?",
            (nombre, fecha_compra, meses, descripcion.strip(), id_item)
        )
        conn.commit()


def eliminar_componente(id_item: int) -> None:
    """Elimina un componente por su id."""
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM componentes WHERE id = ?", (id_item,))
        conn.commit()


def buscar_componentes(termino: str) -> list[tuple]:
    """Búsqueda por nombre o descripción (LIKE, insensible a mayúsculas)."""
    patron = f"%{termino}%"
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nombre, fecha_compra, meses_garantia, descripcion "
            "FROM componentes "
            "WHERE nombre LIKE ? OR descripcion LIKE ? "
            "ORDER BY fecha_compra DESC",
            (patron, patron)
        )
        return cursor.fetchall()
