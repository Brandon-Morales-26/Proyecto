"""
database.py
-----------
Capa de datos: consulta las APIs de Steam e Epic Games
y devuelve resultados normalizados para la UI.
"""

import requests
import urllib.parse
from typing import Optional


# ──────────────────────────────────────────────
#  STEAM
# ──────────────────────────────────────────────

STEAM_SEARCH_URL = "https://store.steampowered.com/api/storesearch/"
STEAM_DETAILS_URL = "https://store.steampowered.com/api/appdetails"
STEAM_STORE_BASE = "https://store.steampowered.com/app/"


def search_steam(query: str, max_results: int = 10) -> list[dict]:
    """Busca juegos en Steam y retorna lista normalizada."""
    params = {
        "term": query,
        "l": "spanish",
        "cc": "AR",
        "infinite": 1,
    }
    try:
        resp = requests.get(STEAM_SEARCH_URL, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])[:max_results]
    except Exception:
        return []

    results = []
    for item in items:
        app_id = item.get("id")
        price_info = item.get("price", {})
        final_cents = price_info.get("final", 0)       # en centavos USD*100
        initial_cents = price_info.get("initial", 0)
        discount_pct = price_info.get("discount_percent", 0)

        results.append({
            "id": str(app_id),
            "title": item.get("name", "Sin título"),
            "price": final_cents / 100 if final_cents else 0.0,
            "original_price": initial_cents / 100 if initial_cents else 0.0,
            "discount": discount_pct,
            "currency": "USD",
            "is_free": final_cents == 0,
            "url": f"{STEAM_STORE_BASE}{app_id}",
            "image": item.get("tiny_image", ""),
            "platform": "steam",
        })
    return results


# ──────────────────────────────────────────────
#  EPIC GAMES  (API pública via store-site-prod)
# ──────────────────────────────────────────────

EPIC_GQL_URL = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions"

# Endpoint real que usa el frontend de Epic Games Store
EPIC_STORE_URL = (
    "https://store-site-backend-static.ak.epicgames.com"
    "/graphql?operationName=searchStoreQuery"
)

EPIC_GQL_QUERY = """
query searchStoreQuery(
  $allowCountries: String
  $category: String
  $count: Int
  $keywords: String
  $locale: String
  $sortBy: String
  $sortDir: String
  $start: Int
) {
  Catalog {
    searchStore(
      allowCountries: $allowCountries
      category: $category
      count: $count
      keywords: $keywords
      locale: $locale
      sortBy: $sortBy
      sortDir: $sortDir
      start: $start
    ) {
      elements {
        title
        id
        namespace
        keyImages { type url }
        productSlug
        urlSlug
        price(country: $allowCountries) {
          totalPrice {
            discountPrice
            originalPrice
            discount
            currencyCode
            currencyInfo { decimals }
          }
        }
      }
      paging { total count }
    }
  }
}
"""

EPIC_HEADERS = {
    "Content-Type": "application/json;charset=UTF-8",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://store.epicgames.com",
    "Referer": "https://store.epicgames.com/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}


def search_epic(query: str, max_results: int = 10) -> list[dict]:
    """Busca juegos en Epic Games Store y retorna lista normalizada."""
    payload = {
        "query": EPIC_GQL_QUERY,
        "variables": {
            "keywords": query,
            "locale": "en-US",
            "allowCountries": "US",
            "count": max_results,
            "sortBy": "relevancy",
            "sortDir": "DESC",
            "category": "games/edition/base|bundles/games|editors",
            "start": 0,
        },
    }

    try:
        resp = requests.post(
            "https://graphql.epicgames.com/graphql",
            json=payload,
            headers=EPIC_HEADERS,
            timeout=12,
        )
        resp.raise_for_status()
        data = resp.json()
        elements = (
            data.get("data", {})
            .get("Catalog", {})
            .get("searchStore", {})
            .get("elements", [])
        )
    except Exception:
        # Fallback: intentar con el endpoint alternativo
        elements = _search_epic_fallback(query, max_results)

    results = []
    for el in elements:
        price_data = el.get("price", {}).get("totalPrice", {})
        decimals = price_data.get("currencyInfo", {}).get("decimals", 2)
        divisor = 10 ** decimals if decimals else 100

        original = price_data.get("originalPrice", 0) / divisor
        final    = price_data.get("discountPrice",  0) / divisor
        discount_pct = (
            round((1 - final / original) * 100) if original > 0 and final < original else 0
        )

        # Imagen: preferir Thumbnail, luego DieselGameBox, luego la primera
        images = el.get("keyImages", [])
        thumb = ""
        for preferred in ("Thumbnail", "DieselGameBoxTall", "DieselGameBox", "OfferImageTall"):
            for img in images:
                if img.get("type") == preferred:
                    thumb = img.get("url", "")
                    break
            if thumb:
                break
        if not thumb and images:
            thumb = images[0].get("url", "")

        slug = el.get("productSlug") or el.get("urlSlug") or ""
        # Limpiar slugs con sufijos tipo "/home"
        slug = slug.split("/")[0] if slug else ""
        store_url = (
            f"https://store.epicgames.com/en-US/p/{slug}"
            if slug else "https://store.epicgames.com"
        )

        results.append({
            "id":             el.get("id", ""),
            "title":          el.get("title", "Sin título"),
            "price":          final,
            "original_price": original,
            "discount":       discount_pct,
            "currency":       price_data.get("currencyCode", "USD"),
            "is_free":        final == 0 and original == 0,
            "url":            store_url,
            "image":          thumb,
            "platform":       "epic",
        })
    return results


def _search_epic_fallback(query: str, max_results: int) -> list:
    """
    Segundo intento usando el endpoint estático de Epic con
    parámetros en query string (sin autenticación).
    """
    import urllib.parse
    variables = {
        "keywords": query,
        "locale": "en-US",
        "allowCountries": "US",
        "count": max_results,
        "sortBy": "relevancy",
        "sortDir": "DESC",
        "category": "games/edition/base|bundles/games|editors",
        "start": 0,
    }
    params = {
        "operationName": "searchStoreQuery",
        "variables": __import__("json").dumps(variables),
        "query": EPIC_GQL_QUERY,
    }
    try:
        resp = requests.get(
            "https://store-site-backend-static-ipv4.ak.epicgames.com/graphql",
            params=params,
            headers=EPIC_HEADERS,
            timeout=12,
        )
        resp.raise_for_status()
        data = resp.json()
        return (
            data.get("data", {})
            .get("Catalog", {})
            .get("searchStore", {})
            .get("elements", [])
        )
    except Exception:
        return []


# ──────────────────────────────────────────────
#  FUNCIÓN COMBINADA
# ──────────────────────────────────────────────

def search_both(query: str, max_results: int = 8) -> dict:
    """
    Retorna un dict con resultados de Steam y Epic.
    Incluye 'epic_error' con el mensaje si algo falla.
    """
    steam = search_steam(query, max_results)

    epic = []
    epic_error = None
    try:
        epic = search_epic(query, max_results)
        if not epic:
            epic_error = "Sin resultados en Epic para esta búsqueda."
    except Exception as e:
        epic_error = str(e)

    return {"steam": steam, "epic": epic, "epic_error": epic_error}
