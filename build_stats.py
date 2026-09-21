"""
Genera el dashboard de estadisticas (stats.html): numeros generales,
ranking de directores y desglose por pais de produccion.

Uso:
    python build_stats.py

Se puede correr suelto (regenera stats.html a partir de lo que haya en
library.db) o se sirve en vivo desde app.py en /stats.

Decisiones de conteo, para que quede documentado:
  - Una coproduccion (ej Argentina/España) le suma un titulo a CADA pais
    involucrado, no solo al primero que lista TMDB.
  - El ranking de directores solo cuenta a alguien con 3 o mas titulos
    cargados -- con 1 o 2 el promedio no dice mucho todavia.
  - Si un titulo tiene varios directores/creadores (separados por coma
    en el campo), cada uno se cuenta por separado.
"""

import statistics
from collections import defaultdict

import config
import db
from countries import country_name

MIN_TITLES_FOR_DIRECTOR_RANKING = 3

TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JaviMDb — Stats</title>
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png">
<link rel="icon" type="image/x-icon" href="favicon.ico">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bitter:wght@700;800&family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #16151a;
    --bg-raised: #201e25;
    --card: #221f27;
    --line: #34313b;
    --ink: #ece7da;
    --ink-muted: #938d80;
    --gold: #c9a34e;
    --rust: #b1503f;
    --teal: #4f8079;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font-family: 'Inter', sans-serif;
    -webkit-font-smoothing: antialiased;
  }
  header {
    padding: 40px 40px 24px;
    border-bottom: 1px solid var(--line);
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
  }
  header h1 {
    font-family: 'Bitter', serif;
    font-weight: 800;
    font-size: 2rem;
    margin: 0;
  }
  header h1 .brand-mark { color: var(--gold); }
  header h1 a {
    position: relative;
    display: inline-block;
    color: inherit;
    text-decoration: none;
  }
  header h1 a::after {
    content: '';
    position: absolute;
    left: 0;
    bottom: -4px;
    width: 0;
    height: 2px;
    background: var(--gold);
    transition: width 180ms ease;
  }
  header h1 a:hover::after { width: 100%; }
  header h1 a:hover .brand-mark {
    color: var(--ink);
    text-shadow: 0 0 12px rgba(201,163,78,0.35);
  }
  @media (prefers-reduced-motion: reduce) {
    header h1 a, header h1 a::after { transition: none; }
  }
  header a.back-link {
    color: var(--ink-muted);
    text-decoration: none;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    border: 1px solid var(--line);
    padding: 8px 14px;
    border-radius: 6px;
  }
  header a.back-link:hover { border-color: var(--gold); color: var(--ink); }

  main { padding: 32px 40px 60px; max-width: 1100px; }

  .kpi-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
    margin-bottom: 44px;
  }
  .kpi {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 18px 20px;
  }
  .kpi .value {
    font-family: 'Bitter', serif;
    font-weight: 800;
    font-size: 2rem;
    color: var(--gold);
    line-height: 1;
  }
  .kpi .label {
    font-size: 0.78rem;
    color: var(--ink-muted);
    margin-top: 6px;
    font-family: 'JetBrains Mono', monospace;
  }

  section { margin-bottom: 48px; }
  section h2 {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 1.3rem;
    margin: 0 0 4px;
  }
  section .section-note {
    color: var(--ink-muted);
    font-size: 0.82rem;
    margin: 0 0 18px;
  }

  table { width: 100%; border-collapse: collapse; }
  th {
    text-align: left;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--ink-muted);
    padding: 8px 12px;
    border-bottom: 1px solid var(--line);
  }
  td {
    padding: 10px 12px;
    border-bottom: 1px solid var(--line);
    font-size: 0.92rem;
  }
  td.num, th.num { text-align: right; font-family: 'JetBrains Mono', monospace; }
  tr:hover td { background: var(--bg-raised); }
  .rating-cell { color: var(--gold); font-family: 'JetBrains Mono', monospace; font-weight: 600; }

  .bar-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 7px 0;
    color: inherit;
    text-decoration: none;
  }
  .bar-row:hover { background: var(--bg-raised); }
  .bar-row .name { width: 170px; flex-shrink: 0; font-size: 0.88rem; }
  .bar-row .bar-track {
    flex: 1;
    background: var(--bg-raised);
    border-radius: 4px;
    height: 20px;
    overflow: hidden;
  }
  .bar-row .bar-fill {
    height: 100%;
    background: var(--gold);
    border-radius: 4px;
  }
  .bar-row .count {
    width: 120px;
    white-space: nowrap;
    text-align: right;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: var(--ink-muted);
    flex-shrink: 0;
  }
  @media (max-width: 650px) {
    main { padding-left: 16px; padding-right: 16px; }
    .bar-row { gap: 8px; }
    .bar-row .name { width: 92px; font-size: 0.78rem; }
    .bar-row .count { width: 104px; font-size: 0.7rem; }
  }

  .decade-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 4px;
  }
  .decade-tile {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 16px 18px;
    text-decoration: none;
    color: inherit;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    min-width: 88px;
    transition: border-color 150ms ease, background 150ms ease;
  }
  .decade-tile:hover {
    border-color: var(--gold);
    background: var(--bg-raised);
  }
  .decade-tile .decade-label {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 1.35rem;
    color: var(--ink);
  }
  .decade-tile .decade-count {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    color: var(--ink-muted);
    text-align: center;
  }
</style>
</head>
<body>

<header>
  <h1><a href="__BACK_HREF__">Jav<span class="brand-mark">iMDb</span></a> — Stats</h1>
  <a class="back-link" href="__BACK_HREF__">← catálogo</a>
</header>

<main>
  <div class="kpi-row">
    <div class="kpi"><div class="value">__TOTAL__</div><div class="label">producciones</div></div>
    <div class="kpi"><div class="value">__MOVIES__</div><div class="label">peliculas</div></div>
    <div class="kpi"><div class="value">__SERIES__</div><div class="label">series</div></div>
    <div class="kpi"><div class="value">__AVG__</div><div class="label">nota promedio</div></div>
    <div class="kpi"><div class="value">__ELITE__</div><div class="label">con 9 o mas</div></div>
    <div class="kpi"><div class="value">__COUNTRIES__</div><div class="label">paises distintos</div></div>
  </div>

  <section>
    <h2>Por década</h2>
    <p class="section-note">Hacé click en una década para ver sus títulos en el catálogo.</p>
    <div class="decade-grid">__DECADE_SQUARES__</div>
  </section>

  <section>
    <h2>Directores y creadores mejor puntuados</h2>
    <p class="section-note">Incluye directores de películas y creadores de series, con __MIN_DIR__ o mas titulos cargados.</p>
    <table>
      <thead><tr><th>Director / creador</th><th class="num">Titulos</th><th class="num">Promedio</th></tr></thead>
      <tbody>__DIRECTOR_ROWS_BY_RATING__</tbody>
    </table>
  </section>

  <section>
    <h2>Directores y creadores que mas viste</h2>
    <table>
      <thead><tr><th>Director / creador</th><th class="num">Titulos</th><th class="num">Promedio</th></tr></thead>
      <tbody>__DIRECTOR_ROWS_BY_COUNT__</tbody>
    </table>
  </section>

  <section>
    <h2>Por país de producción</h2>
    <p class="section-note">Una coproducción suma una producción a cada país involucrado. Hacé click en un país para ver sus títulos.</p>
    __COUNTRY_BARS__
  </section>
</main>

</body>
</html>
"""


def _split_names(raw):
    if not raw:
        return []
    return [n.strip() for n in raw.split(",") if n.strip()]


def _fmt(n):
    return f"{n:.1f}" if n != int(n) else str(int(n))


def build_stats_data():
    rows = db.get_all_titles()

    total = len(rows)
    movies = sum(1 for r in rows if r["media_type"] == "movie")
    series = sum(1 for r in rows if r["media_type"] == "tv")
    avg = statistics.mean(r["rating"] for r in rows) if rows else 0
    elite = sum(1 for r in rows if r["rating"] >= 9)

    director_ratings = defaultdict(list)
    for r in rows:
        for name in _split_names(r.get("director")):
            director_ratings[name].append(r["rating"])

    director_stats = [
        {"name": name, "count": len(ratings), "avg": statistics.mean(ratings)}
        for name, ratings in director_ratings.items()
        if len(ratings) >= MIN_TITLES_FOR_DIRECTOR_RANKING
    ]
    top_by_rating = sorted(director_stats, key=lambda d: (-d["avg"], -d["count"]))[:15]
    top_by_count = sorted(director_stats, key=lambda d: (-d["count"], -d["avg"]))[:15]

    country_ratings = defaultdict(list)
    for r in rows:
        codes = (r.get("production_countries") or "").split(",")
        for code in codes:
            code = code.strip()
            if code:
                country_ratings[code].append(r["rating"])

    country_stats = sorted(
        (
            {"code": code, "name": country_name(code), "count": len(ratings), "avg": statistics.mean(ratings)}
            for code, ratings in country_ratings.items()
        ),
        key=lambda c: -c["count"],
    )

    decade_counts = defaultdict(int)
    for r in rows:
        if r.get("year"):
            decade_counts[(r["year"] // 10) * 10] += 1

    return {
        "total": total,
        "movies": movies,
        "series": series,
        "avg": avg,
        "elite": elite,
        "n_countries": len(country_stats),
        "top_by_rating": top_by_rating,
        "top_by_count": top_by_count,
        "countries": country_stats,
        "decades": dict(decade_counts),
    }


def _decade_label(decade):
    return f"{decade}s" if decade >= 2000 else f"{str(decade)[2:]}s"


def _decade_squares_html(decades, catalog_href):
    if not decades:
        return '<p style="color:var(--ink-muted)">Sin datos de año todavía.</p>'
    parts = []
    for decade, count in sorted(decades.items()):
        label = _decade_label(decade)
        parts.append(
            f'<a class="decade-tile" href="{catalog_href}?decade={decade}">'
            f'<div class="decade-label">{label}</div>'
            f'<div class="decade-count">{count} título{"s" if count != 1 else ""}</div>'
            f'</a>'
        )
    return "".join(parts)


def _director_rows_html(director_list):
    if not director_list:
        return '<tr><td colspan="3" style="color:var(--ink-muted)">Todavia no hay suficiente data.</td></tr>'
    return "".join(
        f'<tr><td>{d["name"]}</td><td class="num">{d["count"]}</td>'
        f'<td class="num rating-cell">{_fmt(d["avg"])}</td></tr>'
        for d in director_list
    )


def _country_bars_html(countries, catalog_href):
    if not countries:
        return '<p style="color:var(--ink-muted)">Todavia no hay paises cargados -- corré bulk_import.py o add_title.py de nuevo para completarlos.</p>'
    max_count = max(c["count"] for c in countries)
    rows = []
    for c in countries:
        pct = round((c["count"] / max_count) * 100)
        rows.append(
            f'<a class="bar-row" href="{catalog_href}?country={c["code"]}">'
            f'<div class="name">{c["name"]}</div>'
            f'<div class="bar-track"><div class="bar-fill" style="width:{pct}%"></div></div>'
            f'<div class="count"><span>{c["count"]}</span> producciones · nota <span>{_fmt(c["avg"])}</span></div>'
            f'</a>'
        )
    return "".join(rows)


def render_stats_page(back_href="library.html", catalog_href="library.html"):
    data = build_stats_data()
    html = TEMPLATE
    html = html.replace("__BACK_HREF__", back_href)
    html = html.replace("__TOTAL__", str(data["total"]))
    html = html.replace("__MOVIES__", str(data["movies"]))
    html = html.replace("__SERIES__", str(data["series"]))
    html = html.replace("__AVG__", _fmt(data["avg"]))
    html = html.replace("__ELITE__", str(data["elite"]))
    html = html.replace("__COUNTRIES__", str(data["n_countries"]))
    html = html.replace("__MIN_DIR__", str(MIN_TITLES_FOR_DIRECTOR_RANKING))
    html = html.replace("__DIRECTOR_ROWS_BY_RATING__", _director_rows_html(data["top_by_rating"]))
    html = html.replace("__DIRECTOR_ROWS_BY_COUNT__", _director_rows_html(data["top_by_count"]))
    html = html.replace("__COUNTRY_BARS__", _country_bars_html(data["countries"], catalog_href))
    html = html.replace("__DECADE_SQUARES__", _decade_squares_html(data["decades"], catalog_href))
    return html


def build():
    db.init_db()
    html = render_stats_page(back_href="library.html", catalog_href="library.html")
    with open(config.STATS_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    build()
