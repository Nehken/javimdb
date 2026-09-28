"""
Capa de acceso a datos. Una sola tabla: `titles`.
Peliculas y series conviven en la misma tabla (media_type distingue),
sin desglose por temporada/episodio -- una nota global por serie.
"""

import sqlite3
from contextlib import contextmanager

from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS titles (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    tmdb_id         INTEGER NOT NULL,
    media_type      TEXT NOT NULL CHECK (media_type IN ('movie', 'tv')),
    title_en        TEXT NOT NULL,          -- titulo en ingles (o el internacional que devuelve TMDB)
    title_original  TEXT NOT NULL,          -- titulo original (frances, japones, castellano, etc)
    original_language TEXT,
    year            INTEGER,
    director        TEXT,                   -- director (peli) o creador/es (serie)
    poster_path     TEXT,                   -- path relativo de TMDB, se arma la URL completa al exportar
    imdb_id         TEXT,                   -- ej: tt0078748 -> arma el link a imdb.com/title/tt0078748
    rating          REAL NOT NULL,          -- tu nota, 1.0 a 10.0 en pasos de 0.5
    date_watched    TEXT,                   -- YYYY-MM-DD, opcional
    production_countries TEXT,              -- codigos ISO separados por coma, ej "AR,ES" (coproducciones)
    imdb_public_rating REAL,                -- nota publica de IMDB (del CSV), para comparar con la tuya
    added_at        TEXT DEFAULT (datetime('now')),
    UNIQUE(tmdb_id, media_type)
);
"""


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _migrate(conn):
    """Agrega columnas nuevas a bases ya existentes sin tocar lo cargado."""
    existing = {row["name"] for row in conn.execute("PRAGMA table_info(titles)")}
    if "production_countries" not in existing:
        conn.execute("ALTER TABLE titles ADD COLUMN production_countries TEXT")
    if "imdb_public_rating" not in existing:
        conn.execute("ALTER TABLE titles ADD COLUMN imdb_public_rating REAL")


def init_db():
    with get_conn() as conn:
        conn.execute(SCHEMA)
        _migrate(conn)


def insert_title(entry: dict):
    """entry necesita: tmdb_id, media_type, title_en, title_original,
    original_language, year, director, poster_path, imdb_id, rating, date_watched.
    production_countries e imdb_public_rating son opcionales."""
    entry = {"production_countries": None, "imdb_public_rating": None, **entry}
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO titles
                (tmdb_id, media_type, title_en, title_original, original_language,
                 year, director, poster_path, imdb_id, rating, date_watched,
                 production_countries, imdb_public_rating)
            VALUES
                (:tmdb_id, :media_type, :title_en, :title_original, :original_language,
                 :year, :director, :poster_path, :imdb_id, :rating, :date_watched,
                 :production_countries, :imdb_public_rating)
            ON CONFLICT(tmdb_id, media_type) DO UPDATE SET
                rating=excluded.rating,
                date_watched=excluded.date_watched,
                production_countries=COALESCE(excluded.production_countries, titles.production_countries),
                imdb_public_rating=COALESCE(excluded.imdb_public_rating, titles.imdb_public_rating)
            """,
            entry,
        )


def get_all_titles():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM titles ORDER BY added_at DESC").fetchall()
        return [dict(r) for r in rows]


def delete_title(row_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM titles WHERE id = ?", (row_id,))
