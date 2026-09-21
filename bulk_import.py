"""
Carga masiva desde tu export de ratings de IMDB.

Como conseguir el CSV:
    IMDB -> tu perfil -> "Your Ratings" -> boton de exportar (icono de
    3 puntitos arriba a la derecha de la lista) -> te manda un mail con
    el CSV, o lo descarga directo segun el navegador.

El CSV de IMDB ya trae: Const (imdb_id), Your Rating, Title, Title Type,
Year, Directors, Date Rated. Con el imdb_id buscamos en TMDB el poster
y el titulo original -- no hay que tipear nada a mano.

Uso:
    python bulk_import.py ratings.csv

Es re-ejecutable: si corta a mitad de camino (se te corta el internet,
lo que sea), lo volves a correr y sigue -- los titulos ya cargados no
se duplican (se actualizan), así que no hay drama en repetir.
"""

import csv
import os
import sys
import time

import requests

import config
import db
from export_html import build as export_html
from build_stats import build as export_stats

SLEEP_BETWEEN_CALLS = 0.05  # TMDB permite ~50 req/seg, dejamos margen

TITLE_TYPE_MAP = {
    "movie": "movie",
    "tv movie": "movie",
    "video": "movie",
    "short": "movie",
    "tv short": "movie",
    "tv series": "tv",
    "tv mini series": "tv",
    "tv miniseries": "tv",
    "tv special": "tv",
    # formato viejo de IMDB (por si alguien tiene un export de antes del cambio)
    "tvmovie": "movie",
    "tvseries": "tv",
    "tvminiseries": "tv",
    "tvshort": "movie",
}

KNOWN_SERIES_CREATORS = {
    "Dragon Ball": "Akira Toriyama",
    "Dragon Ball Z": "Akira Toriyama",
}


def normalize_title_type(raw):
    return TITLE_TYPE_MAP.get(raw.strip().lower())


def api_get(path, params=None, retries=4):
    params = dict(params or {})
    params["api_key"] = config.TMDB_API_KEY

    last_error = None
    for attempt in range(retries):
        try:
            resp = requests.get(f"{config.TMDB_BASE_URL}{path}", params=params, timeout=15)
            if resp.status_code == 429:
                time.sleep(2)
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            last_error = e
            time.sleep(1.2 * (attempt + 1))  # espera un poco mas cada intento

    raise last_error


def find_by_imdb_id(imdb_id):
    """Devuelve (media_type, tmdb_id) o (None, None) si no hay match."""
    data = api_get(f"/find/{imdb_id}", {"external_source": "imdb_id"})
    if data.get("movie_results"):
        return "movie", data["movie_results"][0]["id"]
    if data.get("tv_results"):
        return "tv", data["tv_results"][0]["id"]
    return None, None


def search_by_title(media_type, title, year=None):
    """Respaldo cuando /find no matchea por imdb_id (pasa con series viejas,
    animes con varias ediciones, o paginas 'paraguas' de IMDB). Busca por
    nombre y, si hay año, lo suma para afinar la puntería."""
    if not title:
        return None
    params = {"query": title}
    if year and year.isdigit():
        year_key = "year" if media_type == "movie" else "first_air_date_year"
        params[year_key] = year
    data = api_get(f"/search/{media_type}", params)
    results = data.get("results") or []
    return results[0]["id"] if results else None


def get_details(media_type, tmdb_id):
    """Detalle completo -- trae poster, titulo original Y production_countries
    (esto ultimo no viene en /find, hace falta este pedido aparte)."""
    append = "credits" if media_type == "tv" else None
    params = {"append_to_response": append} if append else None
    return api_get(f"/{media_type}/{tmdb_id}", params)


def parse_countries(detail):
    countries = detail.get("production_countries") or []
    codes = [c["iso_3166_1"] for c in countries if c.get("iso_3166_1")]
    return ",".join(codes) if codes else None


def parse_director_or_creator(detail, media_type, csv_directors):
    if media_type == "tv":
        creators = [person["name"] for person in detail.get("created_by", []) if person.get("name")]
        if creators:
            return ", ".join(dict.fromkeys(creators))
        credit_jobs = (
            "Creator",
            "Author",
            "Comic Book",
            "Original Story",
            "Series Composition",
            "Series Director",
            "Director",
        )
        crew = detail.get("credits", {}).get("crew", [])
        for job in credit_jobs:
            names = [person["name"] for person in crew if person.get("job") == job and person.get("name")]
            if names:
                return ", ".join(dict.fromkeys(names))
        return csv_directors or None
    return csv_directors or None


def creator_for_series(title, detail, csv_directors):
    if title in KNOWN_SERIES_CREATORS:
        return KNOWN_SERIES_CREATORS[title]
    return parse_director_or_creator(detail, "tv", csv_directors)


def backfill_missing_creators():
    rows = [
        row for row in db.get_all_titles()
        if row["media_type"] == "tv"
        and not (row.get("director") or "").strip()
        and (row["tmdb_id"] > 0 or row["title_en"] in KNOWN_SERIES_CREATORS)
    ]
    updated = 0
    failed = 0
    with db.get_conn() as conn:
        for row in rows:
            try:
                if row["title_en"] in KNOWN_SERIES_CREATORS:
                    creators = KNOWN_SERIES_CREATORS[row["title_en"]]
                else:
                    detail = api_get(f"/tv/{row['tmdb_id']}", {"append_to_response": "credits"})
                    creators = creator_for_series(row["title_en"], detail, None)
                if creators:
                    conn.execute("UPDATE titles SET director = ? WHERE id = ?", (creators, row["id"]))
                    updated += 1
                else:
                    failed += 1
            except requests.exceptions.RequestException:
                failed += 1
            time.sleep(SLEEP_BETWEEN_CALLS)
    return updated, failed


def parse_imdb_public_rating(row):
    raw = row.get("IMDb Rating", "").strip()
    try:
        return float(raw)
    except ValueError:
        return None


def fallback_tmdb_id(imdb_id):
    """ID temporal para titulos que TMDB no matchea. Antes usaba hash()
    de Python, que cambia en cada corrida del script y generaba un
    duplicado nuevo cada vez que reimportabas -- por eso salian cosas
    repetidas. Esto usa los numeros del propio imdb_id (siempre los
    mismos), asi el mismo titulo siempre cae en el mismo id ficticio."""
    digits = "".join(ch for ch in imdb_id if ch.isdigit())
    return -int(digits) if digits else -(abs(hash(imdb_id)) % (10**9))


def main():
    if config.TMDB_API_KEY in ("", "PEGA_TU_API_KEY_ACA"):
        print("Falta configurar TMDB_API_KEY en config.py.")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Uso: python bulk_import.py ratings.csv")
        sys.exit(1)

    csv_path = sys.argv[1]
    db.init_db()

    ok, skipped, failed = 0, 0, 0
    fallback_matches = []  # para el CSV de revision -- titulos que no matchearon por imdb_id directo

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total = len(rows)
    print(f"{total} filas en el CSV. Arrancando...")

    for i, row in enumerate(rows, start=1):
        imdb_id = row.get("Const", "").strip()
        title_type_raw = row.get("Title Type", "").strip()
        media_type = normalize_title_type(title_type_raw)

        if not imdb_id or not media_type:
            print(f"  [{i}/{total}] saltado (sin imdb_id o tipo no soportado): {row.get('Title')}")
            skipped += 1
            continue

        try:
            found_type, tmdb_id = find_by_imdb_id(imdb_id)
        except requests.RequestException as e:
            print(f"  [{i}/{total}] ERROR de red en {imdb_id}: {e}")
            failed += 1
            continue

        if tmdb_id is None:
            # /find no encontro nada por imdb_id -> segundo intento por nombre+año
            try:
                fallback_id = search_by_title(media_type, row.get("Title", "").strip(), row.get("Year", "").strip())
            except requests.RequestException:
                fallback_id = None
            if fallback_id:
                found_type, tmdb_id = media_type, fallback_id
                used_fallback = True
            else:
                used_fallback = False
        else:
            used_fallback = False

        imdb_public_rating = parse_imdb_public_rating(row)

        if tmdb_id is None:
            # No esta en TMDB -> igual lo guardamos con lo que trae el CSV de IMDB,
            # sin poster, titulo original ni pais (raro, pasa con titulos de nicho)
            title_en = row.get("Title")
            entry = {
                "tmdb_id": fallback_tmdb_id(imdb_id),
                "media_type": media_type,
                "title_en": title_en,
                "title_original": title_en,
                "original_language": None,
                "year": int(row["Year"]) if row.get("Year", "").isdigit() else None,
                "director": row.get("Directors"),
                "poster_path": None,
                "imdb_id": imdb_id,
                "rating": float(row.get("Your Rating") or 0),
                "date_watched": row.get("Date Rated") or None,
                "production_countries": None,
                "imdb_public_rating": imdb_public_rating,
            }
        else:
            try:
                detail = get_details(found_type, tmdb_id)
            except requests.RequestException as e:
                print(f"  [{i}/{total}] ERROR de red trayendo detalle de {imdb_id}: {e}")
                failed += 1
                continue

            title_en = detail.get("title") or detail.get("name")
            title_original = detail.get("original_title") or detail.get("original_name")
            date = detail.get("release_date") or detail.get("first_air_date") or ""
            entry = {
                "tmdb_id": tmdb_id,
                "media_type": found_type,
                "title_en": title_en,
                "title_original": title_original or title_en,
                "original_language": detail.get("original_language"),
                "year": int(date[:4]) if date[:4].isdigit() else (
                    int(row["Year"]) if row.get("Year", "").isdigit() else None
                ),
                "director": creator_for_series(title_en, detail, row.get("Directors")) if found_type == "tv" else row.get("Directors") or None,
                "poster_path": detail.get("poster_path"),
                "imdb_id": imdb_id,
                "rating": float(row.get("Your Rating") or 0),
                "date_watched": row.get("Date Rated") or None,
                "production_countries": parse_countries(detail),
                "imdb_public_rating": imdb_public_rating,
            }

            if used_fallback:
                fallback_matches.append({
                    "Titulo en tu CSV": row.get("Title"),
                    "Año en tu CSV": row.get("Year"),
                    "imdb_id": imdb_id,
                    "Matcheo con (TMDB)": title_en,
                    "Titulo original (TMDB)": title_original,
                    "Año (TMDB)": entry["year"],
                    "URL IMDB": row.get("URL"),
                })

        db.insert_title(entry)
        ok += 1
        if i % 50 == 0:
            print(f"  [{i}/{total}] ... ({ok} ok, {skipped} saltados, {failed} con error)")

        time.sleep(SLEEP_BETWEEN_CALLS)

    export_html()
    export_stats()
    print(f"\nListo. {ok} cargados, {skipped} saltados, {failed} con error de red.")
    print(f"library.html actualizado -> {config.HTML_OUTPUT_PATH}")

    if fallback_matches:
        review_path = os.path.join(os.path.dirname(__file__), "matches_de_respaldo_revisar.csv")
        with open(review_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(fallback_matches[0].keys()))
            w.writeheader()
            w.writerows(fallback_matches)
        print(
            f"\n{len(fallback_matches)} titulos entraron por busqueda de respaldo (no matchearon por "
            f"imdb_id directo) -- revisalos en matches_de_respaldo_revisar.csv por si alguno "
            f"pesco la pelicula/serie equivocada."
        )


if __name__ == "__main__":
    main()
