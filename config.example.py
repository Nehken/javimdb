"""
Configuration template. Copy this file to config.py and fill in your values.
Never commit config.py — it contains your API key.

How to get a TMDB API key (free):
  1. Create an account at https://www.themoviedb.org/
  2. Go to Settings -> API -> Create -> Developer
  3. Copy the "API Key (v3 auth)"

Recommended: set it as an environment variable so it never touches a file:
  Windows:  $env:TMDB_API_KEY = "your_key_here"
  Linux/Mac: export TMDB_API_KEY=your_key_here
"""

import os

TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "")

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

DB_PATH = os.path.join(os.path.dirname(__file__), "library.db")
HTML_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "library.html")
STATS_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "stats.html")
