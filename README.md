# JaviMDb

Personal catalog of movies and TV shows. You set the rating (1–10, half-points allowed); each card links directly to IMDb.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Get a TMDB API key (free)

1. Create an account at <https://www.themoviedb.org/>
2. Go to Settings → API → Create → Developer → fill in the short form (personal use)
3. Copy the **API Key (v3 auth)**

### 3. Configure

Copy `config.example.py` to `config.py` and set your key. The recommended way is via environment variable so the key never lives in a file:

```powershell
# PowerShell
$env:TMDB_API_KEY = "your_key_here"
python add_title.py "blade runner"
```

```bash
# Bash / Linux / Mac
export TMDB_API_KEY=your_key_here
python add_title.py "blade runner"
```

`config.py` is in `.gitignore` — never commit it.

## Usage

### Bulk import from IMDB

If you have hundreds of titles rated on IMDB, export your ratings (Profile → Your Ratings → Export) and run:

```bash
python bulk_import.py ratings.csv
```

Safe to re-run: it skips titles already in the DB.

### Add a title

```bash
python add_title.py "seven samurai"
```

Shows numbered results, fetches director/creator automatically, then asks for your rating and watch date. Regenerates `library.html` and `stats.html` after saving.

### Browse the catalog

Open `library.html` in a browser (double-click). No server or internet required — all data is embedded in the file. Includes search, movie/series filter, and sort by rating, year, title, or watch date.

### Edit ratings (local server)

```bash
python app.py
```

Opens a Flask server at `http://127.0.0.1:5000`. Click the rating badge on any card to update it in-place. Saves to `library.db` and regenerates `library.html` immediately.

## What's not in the repo

- `library.db` — your SQLite database (back it up separately)
- `library.html` / `stats.html` — generated files, rebuilt automatically
- `ratings.csv` — your IMDB export (keep a local copy, not tracked)
- `config.py` — contains your API key

## Notes

- TV shows get a single overall rating, no per-season breakdown.
- Adding a title that's already in the DB (same `tmdb_id` + type) updates the rating and date instead of duplicating.
- `library.db` is standard SQLite — open it with [DB Browser for SQLite](https://sqlitebrowser.org/) if you need to edit rows directly.
