"""
Completa el campo `genres` de los titulos ya cargados (corrida unica).

Uso:
    python backfill_genres.py              # trae los generos desde TMDB
    python backfill_genres.py ratings.csv  # ademas, rellena con la columna
                                           # "Genres" del CSV de IMDB los
                                           # titulos que TMDB no matcheo

Es re-ejecutable: solo toca titulos con genres vacio (NULL), asi que si
se corta a la mitad lo volves a correr y sigue.
"""

import csv
import sys
import time

import requests

import config
import db
from bulk_import import api_get, parse_genres, parse_csv_genres, SLEEP_BETWEEN_CALLS
from build_html import build as export_html


def main():
    if config.TMDB_API_KEY in ("", "PEGA_TU_API_KEY_ACA"):
        print("Falta configurar TMDB_API_KEY en config.py.")
        sys.exit(1)

    db.init_db()  # corre la migracion (agrega la columna genres si falta)

    csv_genres = {}
    if len(sys.argv) > 1:
        with open(sys.argv[1], newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                const = (row.get("Const") or "").strip()
                genres = parse_csv_genres(row)
                if const and genres:
                    csv_genres[const] = genres

    pending = [r for r in db.get_all_titles() if r.get("genres") is None]
    print(f"{len(pending)} titulos sin generos. Arrancando...")

    done, from_csv, failed, unmatched = 0, 0, 0, []

    with db.get_conn() as conn:
        for i, row in enumerate(pending, start=1):
            genres = None
            if row["tmdb_id"] > 0:
                try:
                    detail = api_get(f"/{row['media_type']}/{row['tmdb_id']}", {"language": "en-US"})
                    genres = parse_genres(detail) or ""  # "" = TMDB no tiene generos; evita reintentar
                    done += 1
                except requests.exceptions.RequestException as e:
                    print(f"  ERROR de red en {row['title_en']}: {e}")
                    failed += 1
                time.sleep(SLEEP_BETWEEN_CALLS)
            else:
                genres = csv_genres.get(row.get("imdb_id") or "")
                if genres:
                    from_csv += 1
                else:
                    unmatched.append(row["title_en"])

            if genres is not None:
                conn.execute("UPDATE titles SET genres = ? WHERE id = ?", (genres, row["id"]))
            if i % 50 == 0:
                print(f"  [{i}/{len(pending)}] ...")

    export_html()

    rows = db.get_all_titles()
    docs = [r for r in rows if "Documentary" in (r.get("genres") or "").split(",")]
    anime = [r for r in rows
             if "Animation" in (r.get("genres") or "").split(",") and r.get("original_language") == "ja"]
    other_animation = [r for r in rows
                       if "Animation" in (r.get("genres") or "").split(",") and r.get("original_language") != "ja"]

    print(f"\nListo. {done} desde TMDB, {from_csv} desde el CSV, {failed} con error de red.")
    print(f"Documentales: {len(docs)} | Anime (Animacion + japones): {len(anime)}")
    if other_animation:
        print("\nAnimacion que NO cuenta como anime (idioma original distinto de japones), por si alguna deberia:")
        for r in other_animation:
            print(f"  - {r['title_en']} ({r.get('year')}) [{r.get('original_language')}]")
    if unmatched:
        print(f"\n{len(unmatched)} titulos sin generos (no estan en TMDB y no hay CSV para completarlos):")
        for t in unmatched:
            print(f"  - {t}")


if __name__ == "__main__":
    main()
