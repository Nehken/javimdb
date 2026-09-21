"""
Configuracion del proyecto.
Conseguir una API key gratis en: https://www.themoviedb.org/settings/api
(Creas una cuenta -> Settings -> API -> "Create" -> pedis "Developer" -> te la dan al toque, es gratis)
"""

import os

# Pegá tu API key acá adentro de las comillas, o seteala como variable de entorno TMDB_API_KEY
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "c5d1fb2d17b6a678d72fcd1ca4b23a3f")

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

DB_PATH = os.path.join(os.path.dirname(__file__), "library.db")
HTML_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "library.html")
STATS_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "stats.html")
