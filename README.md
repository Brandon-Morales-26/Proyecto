# 🎮 Game Price Comparator — Steam vs Epic Games

Compara precios de videojuegos en **tiempo real** entre Steam y Epic Games Store.

---

## 📁 Estructura del proyecto

```
steam_epic_comparator/
├── main.py          ← Punto de entrada, UI principal (CustomTkinter)
├── database.py      ← Capa de datos: APIs de Steam y Epic
├── components.py    ← Widgets reutilizables (GameCard, SectionHeader)
├── requirements.txt ← Dependencias Python
└── README.md        ← Este archivo
```

---

## ⚙️ Instalación paso a paso

### 1. Verifica que tengas Python ≥ 3.10

```bash
python --version
```

Si no lo tienes, descárgalo de https://www.python.org/downloads/

---

### 2. (Opcional) Crea un entorno virtual

```bash
# Crear entorno
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (macOS / Linux)
source venv/bin/activate
```

---

### 3. Instala las dependencias

```bash
pip install -r requirements.txt
```

Esto instala:

| Librería | Para qué se usa |
|---|---|
| `customtkinter` | Ya la tienes ✅ — UI moderna |
| `requests` | Llamadas HTTP a las APIs |
| `Pillow` | Carga y redimensiona imágenes de portadas |
| `python-dotenv` | (Opcional) variables de entorno |

> Si ya tienes `customtkinter`, puedes instalar solo el resto:
> ```bash
> pip install requests Pillow python-dotenv
> ```

---

### 4. Ejecuta la app

```bash
python main.py
```

---

## 🚀 Uso

1. Escribe el nombre de un juego en la barra de búsqueda.
2. Presiona **Buscar** o pulsa **Enter**.
3. Los resultados aparecen en dos columnas: Steam (azul) | Epic (verde).
4. Haz clic en **"Ver en tienda →"** para abrir la página del juego en tu navegador.

---

## 🌐 APIs utilizadas

- **Steam Store Search API** — pública, sin autenticación.
- **Epic Games GraphQL Catalog API** — pública, sin autenticación.

Los precios se muestran en **USD** tal como los entregan las APIs.

---

## 🔧 Posibles problemas

| Problema | Solución |
|---|---|
| `ModuleNotFoundError: PIL` | `pip install Pillow` |
| `ModuleNotFoundError: requests` | `pip install requests` |
| No aparecen resultados de Epic | La API pública de Epic puede tener cambios; revisa tu conexión |
| Imágenes no cargan | Conexión lenta; las imágenes se cargan en segundo plano |

---

## 🛠️ Próximas mejoras sugeridas

- [ ] Filtro por rango de precio
- [ ] Ordenar por mayor descuento
- [ ] Historial de búsquedas recientes
- [ ] Exportar comparativa a CSV
- [ ] Soporte para GOG, Humble Bundle
