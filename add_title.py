"""
Uso:
    python add_title.py "nombre de la pelicula o serie"

Flujo:
    1. Busca en TMDB (peliculas y series juntas)
    2. Elegis cual es de una lista numerada
    3. Trae director/creador + imdb_id automaticamente
    4. Te pide tu nota (1 a 10, pasos de 0.5) y fecha vista
    5. Guarda en library.db y regenera library.html
"""

import sys
import datetime
import requests

import config
import db
from export_html import build as export_html
from build_stats import build as export_stats


def api_get(path, params=None):
    params = dict(params or {})
    params["api_key"] = config.TMDB_API_KEY
    params.setdefault("language", "en-US")
    resp = requests.get(f"{config.TMDB_BASE_URL}{path}", params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def search(query):
    data = api_get("/search/multi", {"query": query, "include_adult": "false"})
    results = [r for r in data.get("results", []) if r.get("media_type") in ("movie", "tv")]
    return results


def pick_result(results):
    print("\nResultados:")
    for i, r in enumerate(results[:20]):
        media_type = "Peli" if r["media_type"] == "movie" else "Serie"
        title = r.get("title") or r.get("name")
        original = r.get("original_title") or r.get("original_name")
        date = r.get("release_date") or r.get("first_air_date") or ""
        year = date[:4] if date else "?"
        extra = f" (orig: {original})" if original and original != title else ""
        print(f"  [{i}] {media_type} | {title}{extra} | {year}")

    if not results:
        print("  Sin resultados.")
        return None

    choice = input("\nElegi un numero (o Enter para cancelar): ").strip()
    if choice == "":
        return None
    return results[int(choice)]


def get_director_or_creator(media_type, tmdb_id):
    if media_type == "movie":
        data = api_get(f"/movie/{tmdb_id}", {"append_to_response": "credits,external_ids"})
        crew = data.get("credits", {}).get("crew", [])
        directors = [c["name"] for c in crew if c.get("job") == "Director"]
        director = ", ".join(directors) if directors else None
    else:
        data = api_get(f"/tv/{tmdb_id}", {"append_to_response": "credits,external_ids"})
        # Las series no tienen "director" por episodio en este endpoint -> usamos creadores
        creators = [c["name"] for c in data.get("created_by", [])]
        director = ", ".join(creators) if creators else None

    return data, director


def prompt_rating():
    while True:
        raw = input("Tu nota (1 a 10, medios puntos permitidos, ej 8.5): ").strip().replace(",", ".")
        try:
            value = float(raw)
        except ValueError:
            print("  No es un numero valido.")
            continue
        if value < 1 or value > 10:
            print("  Tiene que estar entre 1 y 10.")
            continue
        if (value * 2) % 1 != 0:
            print("  Solo se permiten pasos de 0.5 (ej: 7, 7.5, 8).")
            continue
        return value


def prompt_date():
    raw = input("Fecha en que la viste (YYYY-MM-DD, Enter = hoy, 's' = sin fecha): ").strip()
    if raw.lower() == "s":
        return None
    if raw == "":
        return datetime.date.today().isoformat()
    return raw


def main():
    if config.TMDB_API_KEY in ("", "PEGA_TU_API_KEY_ACA"):
        print("Falta configurar TMDB_API_KEY en config.py (o la variable de entorno TMDB_API_KEY).")
        sys.exit(1)

    if len(sys.argv) < 2:
        print('Uso: python add_title.py "nombre de la pelicula o serie"')
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    db.init_db()

    results = search(query)
    picked = pick_result(results)
    if picked is None:
        print("Cancelado.")
        return

    media_type = picked["media_type"]
    detail, director = get_director_or_creator(media_type, picked["id"])

    title_en = detail.get("title") or detail.get("name")
    title_original = detail.get("original_title") or detail.get("original_name")
    date = detail.get("release_date") or detail.get("first_air_date") or ""
    year = int(date[:4]) if date[:4].isdigit() else None
    imdb_id = detail.get("external_ids", {}).get("imdb_id")
    countries = detail.get("production_countries") or []
    country_codes = ",".join(c["iso_3166_1"] for c in countries if c.get("iso_3166_1")) or None

    print(f"\n{title_en} ({year}) -- dirigida/creada por: {director or 'desconocido'}")
    if not imdb_id:
        print("  (Ojo: TMDB no tiene el imdb_id para este titulo, el link a IMDB va a quedar vacio)")

    rating = prompt_rating()
    date_watched = prompt_date()

    entry = {
        "tmdb_id": picked["id"],
        "media_type": media_type,
        "title_en": title_en,
        "title_original": title_original or title_en,
        "original_language": detail.get("original_language"),
        "year": year,
        "director": director,
        "poster_path": detail.get("poster_path"),
        "imdb_id": imdb_id,
        "rating": rating,
        "date_watched": date_watched,
        "production_countries": country_codes,
        "imdb_public_rating": None,
    }
    db.insert_title(entry)
    print("Guardado.")

    export_html()
    print(f"library.html actualizado -> {config.HTML_OUTPUT_PATH}")
    export_stats()


if __name__ == "__main__":
    main()
