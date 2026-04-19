import sqlite3
from datetime import datetime

def conectar_db():
    # Esto crea el archivo 'gaming_app.db' en tu carpeta si no existe
    conexion = sqlite3.connect("gaming_app.db")
    return conexion

def crear_tablas():
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    # Creamos la tabla de inventario
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS componentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL, 
            fecha_compra DATE NOT NULL,
            meses_garantia INTEGER NOT NULL
        )
    ''')
    conexion.commit()
    conexion.close()

def agregar_componente(nombre, tipo, fecha_compra, meses_garantia):
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO componentes (nombre, tipo, fecha_compra, meses_garantia)
        VALUES (?, ?, ?, ?)
    ''', (nombre, tipo, fecha_compra, meses_garantia))
    conexion.commit()
    conexion.close()
    print(f"Componente {nombre} guardado con éxito.")

# Ejecutamos la creación de tablas la primera vez
if __name__ == "__main__":
    crear_tablas()