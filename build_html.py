"""
Lee library.db y genera un library.html autocontenido (los datos van
embebidos como JSON adentro del HTML, asi que lo podes abrir haciendo
doble click, sin levantar ningun servidor).
"""

import json

import config
import db
from transliterate import romanize
from templates import FONTS_LINK, BASE_CSS

TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JaviMDb</title>
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png">
<link rel="icon" type="image/x-icon" href="favicon.ico">
__FONTS_LINK__
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/nouislider@15.7.1/dist/nouislider.min.css">
<style>
__BASE_CSS__
  header {
    padding: 48px 40px 28px;
    border-bottom: 1px solid var(--line);
    position: relative;
  }
  header h1 {
    font-family: 'Bitter', serif;
    font-weight: 800;
    font-size: 2.3rem;
    margin: 0 0 6px;
    letter-spacing: -0.01em;
  }
  header h1 .brand-mark {
    color: var(--gold);
  }
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
  header .sub {
    color: var(--ink-muted);
    font-size: 0.88rem;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.02em;
  }
  .stats-link {
    position: absolute;
    top: 44px;
    right: 40px;
    color: var(--ink-muted);
    text-decoration: none;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    border: 1px solid var(--line);
    padding: 8px 14px;
    border-radius: 6px;
  }
  .stats-link:hover { border-color: var(--gold); color: var(--ink); }
  .country-filter {
    display: none;
    margin-left: 8px;
    color: var(--ink-muted);
  }
  .count-tag {
    font-family: 'JetBrains Mono', monospace;
    color: var(--gold);
  }
  .controls {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    padding: 20px 40px;
    border-bottom: 1px solid var(--line);
    background: var(--bg-raised);
    position: sticky;
    top: 0;
    z-index: 10;
  }
  .controls input, .controls select {
    background: var(--bg);
    border: 1px solid var(--line);
    color: var(--ink);
    padding: 10px 14px;
    border-radius: 6px;
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
  }
  .search-wrap {
    position: relative;
    flex: 1 1 240px;
  }
  .search-wrap input {
    width: 100%;
    padding-right: 34px;
  }
  .search-clear {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: var(--ink-muted);
    font-size: 0.85rem;
    cursor: pointer;
    padding: 4px 6px;
    display: none;
    border-radius: 4px;
  }
  .search-clear:hover { color: var(--ink); background: var(--bg-raised); }
  .search-clear.visible { display: block; }
  .controls input { flex: 1 1 240px; }
  .controls input:focus, .controls select:focus {
    outline: none;
    border-color: var(--gold);
  }
  #filter-year {
    flex: none;
    width: 88px;
    text-align: center;
    -moz-appearance: textfield;
  }
  #filter-year::-webkit-inner-spin-button,
  #filter-year::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
  .edit-toggle {
    background: var(--bg);
    border: 1px solid var(--line);
    color: var(--ink);
    padding: 10px 16px;
    border-radius: 6px;
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    cursor: pointer;
    white-space: nowrap;
  }
  .edit-toggle.active {
    background: var(--gold);
    color: #1a1810;
    border-color: var(--gold);
    font-weight: 600;
  }
  .filter-btn-toggle {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--bg);
    border: 1px solid var(--line);
    color: var(--ink);
    padding: 10px 16px;
    border-radius: 6px;
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    cursor: pointer;
    white-space: nowrap;
  }
  .filter-btn-toggle:hover { border-color: var(--gold); }
  .filter-btn-toggle.active {
    border-color: var(--gold);
    color: var(--gold);
  }
  .filter-badge {
    display: inline-block;
    background: var(--gold);
    color: #1a1810;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: 0.7rem;
    line-height: 1;
    padding: 3px 6px;
    border-radius: 999px;
    min-width: 8px;
    text-align: center;
  }
  .advanced-panel {
    display: none;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    align-items: end;
    gap: 16px;
    padding: 18px 40px 22px;
    background: var(--bg-raised);
    border-bottom: 1px solid var(--line);
  }
  .advanced-panel.open { display: grid; }
  .advanced-panel input,
  .advanced-panel select {
    background: var(--bg);
    border: 1px solid var(--line);
    color: var(--ink);
    padding: 10px 14px;
    border-radius: 6px;
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    width: 100%;
  }
  .advanced-panel input:focus,
  .advanced-panel select:focus {
    outline: none;
    border-color: var(--gold);
  }
  .advanced-field {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .advanced-field label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--ink-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }
  .advanced-year-row {
    display: flex;
    gap: 10px;
  }
  .clear-advanced-btn {
    background: var(--bg);
    border: 1px solid var(--rust);
    color: var(--rust);
    padding: 10px 16px;
    border-radius: 6px;
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    cursor: pointer;
    white-space: nowrap;
  }
  .clear-advanced-btn:hover {
    background: var(--rust);
    color: var(--ink);
  }
  .export-wrap {
    position: relative;
  }
  .export-menu {
    display: none;
    position: absolute;
    top: calc(100% + 6px);
    right: 0;
    background: var(--bg-raised);
    border: 1px solid var(--line);
    border-radius: 6px;
    padding: 6px;
    min-width: 190px;
    z-index: 20;
    box-shadow: 0 8px 18px rgba(0,0,0,0.35);
  }
  .export-menu.open { display: block; }
  .export-menu-item {
    display: block;
    width: 100%;
    text-align: left;
    background: none;
    border: none;
    color: var(--ink);
    padding: 9px 10px;
    border-radius: 4px;
    cursor: pointer;
    font-family: 'Inter', sans-serif;
    font-size: 0.88rem;
  }
  .export-menu-item:hover { background: var(--bg); }
  #back-to-top {
    display: none;
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: var(--gold);
    color: var(--bg);
    border: none;
    font-size: 1.2rem;
    line-height: 1;
    cursor: pointer;
    box-shadow: 0 2px 10px rgba(0,0,0,0.4);
    z-index: 20;
    opacity: 0;
    transition: opacity 0.2s ease;
  }
  #back-to-top.visible {
    opacity: 1;
  }
  .filter-chip {
    display: none;
    align-items: center;
    gap: 6px;
    background: var(--bg);
    border: 1px solid var(--gold);
    border-radius: 6px;
    padding: 8px 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: var(--gold);
    white-space: nowrap;
  }
  .filter-chip button {
    background: none;
    border: none;
    color: var(--ink-muted);
    cursor: pointer;
    padding: 0 2px;
    font-size: 0.8rem;
    line-height: 1;
  }
  .filter-chip button:hover { color: var(--ink); }
  .rating-slider-wrap {
    display: flex;
    gap: 12px;
    align-items: center;
    flex: 1 1 280px;
    background: var(--bg);
    border: 1px solid var(--line);
    border-radius: 6px;
    padding: 10px 14px;
  }
  .rating-slider-wrap:focus-within {
    border-color: var(--gold);
  }
  #rating-slider {
    flex: 1;
  }
  #rating-slider.noUi-target {
    background: #34313b !important;
    border-radius: 1px !important;
    border: none !important;
    box-shadow: none !important;
    height: 2px !important;
  }
  #rating-slider .noUi-connect {
    background: #34313b !important;
    border-radius: 1px !important;
  }
  #rating-slider .noUi-handle {
    width: 18px !important;
    height: 18px !important;
    right: -9px !important;
    top: -8px !important;
    border-radius: 50% !important;
    border: none !important;
    background: #c9a34e !important;
    box-shadow: 0 0 8px rgba(201, 163, 78, 0.5) !important;
    cursor: grab !important;
  }
  #rating-slider .noUi-handle::before,
  #rating-slider .noUi-handle::after {
    display: none !important;
  }
  #rating-slider .noUi-handle:hover,
  #rating-slider .noUi-handle:active,
  #rating-slider .noUi-handle.noUi-active {
    box-shadow: 0 0 12px rgba(201, 163, 78, 0.8) !important;
  }
  .noui-target[disabled] .noui-handle {
    cursor: not-allowed;
  }
  .rating-slider-value {
    font-family: 'JetBrains Mono', monospace;
    color: var(--ink);
    font-size: 0.85rem;
    white-space: nowrap;
    width: 72px;
    text-align: center;
    font-weight: 600;
    letter-spacing: 0.5px;
  }
  @media (max-width: 900px) {
    .rating-slider-wrap {
      min-width: 240px;
    }
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
    gap: 26px;
    padding: 32px 40px 60px;
  }
  .card {
    position: relative;
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 8px;
    overflow: hidden;
    text-decoration: none;
    color: inherit;
    display: block;
    transition: border-color 180ms ease, box-shadow 180ms ease;
  }
  .card:hover {
    border-color: var(--gold);
    box-shadow: 0 8px 18px rgba(0,0,0,0.18);
  }
  .card.tier-elite {
    border: 2px solid var(--gold);
    box-shadow: 0 0 0 1px rgba(201,163,78,0.25), 0 4px 20px rgba(201,163,78,0.3);
  }
  .card.tier-low {
    border: 2px solid rgba(122,28,26,0.6);
  }
  .tier-star {
    position: absolute;
    bottom: 8px;
    left: 8px;
    color: var(--gold);
    font-size: 1.05rem;
    text-shadow: 0 1px 4px rgba(0,0,0,0.7);
  }
  .poster-wrap {
    position: relative;
    aspect-ratio: 2 / 3;
    background: var(--bg-raised);
  }
  .poster-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }
  .no-poster {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--ink-muted);
    font-family: 'Fraunces', serif;
    font-size: 0.85rem;
    padding: 12px;
    text-align: center;
  }
  .stamp {
    position: absolute;
    top: 10px;
    right: 10px;
    color: #1a1810;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    font-size: 0.82rem;
    padding: 4px 7px;
    border-radius: 4px;
    transform: rotate(3deg);
    box-shadow: 0 2px 6px rgba(0,0,0,0.4);
  }
  .stamp-input {
    position: absolute;
    top: 10px;
    right: 10px;
    width: 54px;
    color: #1a1810;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    font-size: 0.85rem;
    padding: 4px 4px;
    border-radius: 4px;
    border: 2px solid var(--ink);
    text-align: center;
    -moz-appearance: textfield;
  }
  .stamp-input::-webkit-inner-spin-button,
  .stamp-input::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
  .stamp-input:focus {
    outline: none;
    border-color: var(--ink);
  }
  .type-flag {
    position: absolute;
    top: 10px;
    left: 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 3px 6px;
    border-radius: 4px;
    background: rgba(22,21,26,0.85);
  }
  .type-flag.movie { color: var(--rust); }
  .type-flag.tv { color: var(--teal); }
  .meta {
    padding: 12px 14px 16px;
  }
  .meta .title-en {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 0.98rem;
    line-height: 1.25;
    margin: 0 0 2px;
  }
  .meta .title-original {
    font-size: 0.8rem;
    color: var(--ink-muted);
    font-style: italic;
    margin: 0 0 8px;
  }
  .meta .director, .meta .year {
    font-size: 0.76rem;
    color: var(--ink-muted);
    font-family: 'JetBrains Mono', monospace;
  }
  .empty {
    padding: 80px 40px;
    text-align: center;
    color: var(--ink-muted);
    font-family: 'Fraunces', serif;
    font-size: 1.1rem;
  }

  @media (max-width: 650px), (max-height: 500px) {
    header {
      padding: 24px 16px 16px;
    }
    header h1 {
      font-size: 1.8rem;
    }
    .stats-link {
      display: block;
      position: static;
      top: auto;
      right: auto;
      margin-top: 12px;
      width: 100%;
      text-align: center;
    }
    .controls {
      position: static;
      flex-direction: column;
      gap: 8px;
      padding: 12px 16px;
    }
    .search-wrap {
      width: 100%;
      flex: 0 1 auto;
    }
    .controls input,
    .controls select,
    .filter-btn-toggle,
    .edit-toggle {
      width: 100%;
    }
    #filter-year {
      flex: 0 1 auto;
      width: 100%;
      text-align: left;
    }
    .export-wrap {
      width: 100%;
    }
    .export-wrap .filter-btn-toggle {
      justify-content: center;
    }
    .export-menu {
      left: 0;
      right: 0;
    }
    .controls input,
    .controls select,
    .advanced-panel input,
    .advanced-panel select {
      font-size: 16px;
    }
    .advanced-panel {
      grid-template-columns: 1fr;
      padding: 14px 16px 18px;
    }
    .grid {
      grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
      gap: 16px;
      padding: 16px 12px 40px;
    }
    .card { border-radius: 6px; }
    .meta { padding: 10px; }
    .meta .title-en { font-size: 0.85rem; }
    .meta .director,
    .meta .year { font-size: 0.7rem; }
    #back-to-top { display: flex; align-items: center; justify-content: center; }
  }
</style>
<script src="https://cdn.jsdelivr.net/npm/nouislider@15.7.1/dist/nouislider.min.js"></script>
</head>
<body>

<header>
  <h1><a id="brand-link" href="library.html">Jav<span class="brand-mark">iMDb</span></a></h1>
  <div class="sub" id="count-tag">cargando...</div>
  <a class="stats-link" id="stats-link" href="stats.html">Stats →</a>
</header>

<div class="controls">
  <div class="search-wrap">
    <input type="text" id="search" placeholder="Buscar por titulo, director o creador...">
    <button id="search-clear" class="search-clear" title="Limpiar busqueda">✕</button>
  </div>
  <select id="filter-type">
    <option value="all">Todas</option>
    <option value="movie">Peliculas</option>
    <option value="tv">Series</option>
  </select>
  <input type="number" id="filter-year" placeholder="Año" min="1900" max="2099">
  <select id="sort-by">
    <option value="watched_desc" selected>Vista mas reciente</option>
    <option value="added_desc">Recien agregadas</option>
    <option value="rating_desc">Nota (mayor a menor)</option>
    <option value="rating_asc">Nota (menor a mayor)</option>
    <option value="year_desc">Año (mas nueva primero)</option>
    <option value="year_asc">Año (mas vieja primero)</option>
    <option value="title_asc">Alfabetico (A-Z)</option>
  </select>
  <button id="toggle-advanced" class="filter-btn-toggle">⚙️ Filtros <span id="active-filter-count" class="filter-badge" style="display:none;">0</span></button>
  <div class="export-wrap">
    <button id="toggle-export" class="filter-btn-toggle">⬇ Exportar</button>
    <div id="export-menu" class="export-menu">
      <button id="export-html" class="export-menu-item">Descargar HTML</button>
    </div>
  </div>
  <div id="decade-chip" class="filter-chip">
    <span id="decade-chip-label"></span>
    <button id="decade-chip-clear" title="Quitar filtro de década">✕</button>
  </div>
  <button id="edit-toggle" class="edit-toggle">✎ Editar</button>
</div>
<div id="advanced-panel" class="advanced-panel">
  <div class="rating-slider-wrap">
    <div id="rating-slider"></div>
    <div class="rating-slider-value" id="rating-display">1 - 10</div>
  </div>
  <div class="advanced-year-row">
    <div class="advanced-field">
      <label for="year-min">Desde</label>
      <input type="number" id="year-min" placeholder="1900" min="1900" max="2099">
    </div>
    <div class="advanced-field">
      <label for="year-max">Hasta</label>
      <input type="number" id="year-max" placeholder="2099" min="1900" max="2099">
    </div>
    <div class="advanced-field">
      <label for="filter-lang">Idioma</label>
      <select id="filter-lang">
        <option value="">Todos</option>
      </select>
    </div>
  </div>
  <button id="clear-advanced" class="clear-advanced-btn">Limpiar avanzados</button>
</div>

<div class="grid" id="grid"></div>
<div class="empty" id="empty" style="display:none;">Nada por acá con esos filtros.</div>
<button id="back-to-top" aria-label="Volver arriba">↑</button>

<script>
const DATA = __DATA_JSON__;
const IMG_BASE = "__IMG_BASE__";
const EDITABLE = __EDITABLE__;

const grid = document.getElementById('grid');
const emptyMsg = document.getElementById('empty');
const searchInput = document.getElementById('search');
const searchClear = document.getElementById('search-clear');
const typeFilter = document.getElementById('filter-type');
const sortBy = document.getElementById('sort-by');
const countTag = document.getElementById('count-tag');
const editBtn = document.getElementById('edit-toggle');
const statsLink = document.getElementById('stats-link');
const ratingDisplay = document.getElementById('rating-display');
const ratingSliderEl = document.getElementById('rating-slider');
const yearInput = document.getElementById('filter-year');
const toggleAdvancedBtn = document.getElementById('toggle-advanced');
const advancedPanel = document.getElementById('advanced-panel');
const clearAdvancedBtn = document.getElementById('clear-advanced');
const activeFilterCountEl = document.getElementById('active-filter-count');
const yearMinInput = document.getElementById('year-min');
const yearMaxInput = document.getElementById('year-max');
const toggleExportBtn = document.getElementById('toggle-export');
const exportMenu = document.getElementById('export-menu');
const exportHtmlBtn = document.getElementById('export-html');
const backToTop = document.getElementById('back-to-top');
const params = new URLSearchParams(window.location.search);
let countryFilter = params.get('country');
let decadeFilter = params.get('decade') ? parseInt(params.get('decade')) : null;
let yearFilter = null;

const langSelect = document.getElementById('filter-lang');
const langDisplay = new Intl.DisplayNames(['es'], { type: 'language' });
// TMDB usa 'cn' como código no-estándar para chino; normalizar antes de deduplicar
const LANG_CODE_FIX = { 'cn': 'zh' };
[...new Set(DATA.map(d => d.original_language).filter(Boolean).map(c => LANG_CODE_FIX[c] || c))]
  .sort((a, b) => (langDisplay.of(a) || a).localeCompare(langDisplay.of(b) || b, 'es'))
  .forEach(code => {
    const opt = document.createElement('option');
    opt.value = code;
    opt.textContent = langDisplay.of(code) || code;
    langSelect.appendChild(opt);
  });
let yearMin = null;
let yearMax = null;
let minRating = 1;
let maxRating = 10;
let editMode = false;

// Inicializar noui-slider cuando esté disponible
function initSlider() {
  if (typeof noUiSlider === 'undefined') {
    setTimeout(initSlider, 50);
    return;
  }

  noUiSlider.create(ratingSliderEl, {
    start: [1, 10],
    connect: true,
    step: 0.5,
    range: { min: 1, max: 10 },
    tooltips: false
  });

  // Force styles with setProperty to ensure !important is applied
  const target = ratingSliderEl;
  target.style.setProperty('background', '#34313b', 'important');

  const connect = target.querySelector('.noUi-connect');
  if (connect) {
    connect.style.setProperty('background', '#34313b', 'important');
    connect.style.setProperty('background-color', '#34313b', 'important');
  }

  const handles = target.querySelectorAll('.noUi-handle');
  handles.forEach(h => {
    h.style.setProperty('background', '#c9a34e', 'important');
    h.style.setProperty('background-color', '#c9a34e', 'important');
    h.style.setProperty('box-shadow', '0 0 8px rgba(201, 163, 78, 0.5)', 'important');
  });

  // 'update' solo actualiza el texto mientras se arrastra (sin re-render costoso)
  ratingSliderEl.noUiSlider.on('update', (values) => {
    const lo = parseFloat(values[0]);
    const hi = parseFloat(values[1]);
    ratingDisplay.textContent = lo === 1 && hi === 10 ? '1 - 10' : `${lo} - ${hi}`;
  });

  // 'change' aplica el filtro al soltar el handle
  ratingSliderEl.noUiSlider.on('change', (values) => {
    minRating = parseFloat(values[0]);
    maxRating = parseFloat(values[1]);
    updateActiveFilterBadge();
    render();
  });
}

initSlider();

if (EDITABLE) {
  statsLink.href = '/stats';
  document.getElementById('brand-link').href = '/';
}

if (!EDITABLE) {
  editBtn.style.display = 'none';
} else {
  editBtn.addEventListener('click', () => {
    editMode = !editMode;
    editBtn.textContent = editMode ? '✓ Listo' : '✎ Editar';
    editBtn.classList.toggle('active', editMode);
    render();
  });
}

if (countryFilter) {
  const valid = DATA.flatMap(item => (item.production_countries || '').split(','))
    .map(code => code.trim()).includes(countryFilter);
  if (!valid) {
    window.history.replaceState({}, '', window.location.pathname);
    countryFilter = null;
  }
}

if (decadeFilter) {
  const chip = document.getElementById('decade-chip');
  const label = decadeFilter >= 2000 ? `${decadeFilter}s` : `${String(decadeFilter).slice(2)}s`;
  document.getElementById('decade-chip-label').textContent = `Década: ${label}`;
  chip.style.display = 'flex';
  document.getElementById('decade-chip-clear').addEventListener('click', () => {
    decadeFilter = null;
    chip.style.display = 'none';
    window.history.replaceState({}, '', window.location.pathname);
    render();
  });
}

function imdbUrl(imdbId) {
  return imdbId ? `https://www.imdb.com/title/${imdbId}/` : null;
}

// Un color pensado para cada nota entera (no una curva continua) -- asi el
// salto de 6 a 7 es una decision de diseño, no una fraccion diluida de un
// gradiente de punta a punta. El 5 tiene que leerse como "mediocre" de una,
// y cada escalon de ahi para arriba se nota antes de llegar al dorado del 10.
function ratingColor(rating) {
  const stops = [
    [122, 28, 26],   // 1
    [140, 34, 27],   // 2
    [162, 45, 28],   // 3
    [181, 60, 29],   // 4
    [197, 79, 31],   // 5  -- mediocre, sin dudas
    [204, 101, 34],  // 6
    [206, 126, 40],  // 7
    [203, 149, 50],  // 8
    [201, 163, 66],  // 9
    [201, 163, 78],  // 10 -- dorado de marca
  ];
  const t = Math.max(1, Math.min(10, rating)) - 1; // 0..9
  const lo = Math.floor(t);
  const hi = Math.min(9, Math.ceil(t));
  const frac = t - lo;
  const rgb = stops[lo].map((v, i) => Math.round(v + (stops[hi][i] - v) * frac));
  return `rgb(${rgb.join(',')})`;
}

function formatRating(rating) {
  return Number.isInteger(rating) ? String(rating) : rating.toFixed(1);
}

function tierClass(rating) {
  if (rating >= 9) return 'tier-elite';
  if (rating <= 4) return 'tier-low';
  return '';
}

function updateActiveFilterBadge() {
  let count = 0;
  if (yearMin !== null) count++;
  if (yearMax !== null) count++;
  if (minRating !== 1 || maxRating !== 10) count++;
  if (langSelect.value) count++;
  activeFilterCountEl.textContent = count;
  activeFilterCountEl.style.display = count > 0 ? 'inline-block' : 'none';
}

// Exporta EXACTAMENTE lo que se ve en pantalla: reutiliza el CSS de la página
// y el HTML actual del grid (mismos filtros, mismo orden, mismas notas).
function exportCurrentView() {
  const fontLinks = Array.from(document.head.querySelectorAll('link[href*="fonts.googleapis.com"]'))
    .map(l => l.outerHTML).join('\\n');
  const css = document.querySelector('style').textContent;
  const today = new Date().toISOString().slice(0, 10);
  const html = `<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JaviMDb - export ${today}</title>
${fontLinks}
<style>${css}</style>
</head>
<body>
<header>
  <h1><a>Jav<span class="brand-mark">iMDb</span></a></h1>
  <div class="sub">${countTag.textContent} · exportado el ${today}</div>
</header>
<div class="grid">${grid.innerHTML}</div>
</body>
</html>`;
  const blob = new Blob([html], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `javimdb-export-${today}.html`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function render() {
  const q = searchInput.value.trim().toLowerCase();
  const type = typeFilter.value;

  let items = DATA.filter(item => {
    if (countryFilter && !(item.production_countries || '').split(',').map(code => code.trim()).includes(countryFilter)) return false;
    if (decadeFilter && (!item.year || item.year < decadeFilter || item.year >= decadeFilter + 10)) return false;
    if (yearFilter && item.year !== yearFilter) return false;
    if (yearMin !== null && (!item.year || item.year < yearMin)) return false;
    if (yearMax !== null && (!item.year || item.year > yearMax)) return false;
    if (type !== 'all' && item.media_type !== type) return false;
    if (langSelect.value && (LANG_CODE_FIX[item.original_language] || item.original_language) !== langSelect.value) return false;
    if (item.rating < minRating || item.rating > maxRating) return false;
    if (!q) return true;
    const haystack = `${item.title_en} ${item.title_original_display || item.title_original} ${item.director || ''}`.toLowerCase();
    return haystack.includes(q);
  });

  const movieCount = items.filter(d => d.media_type === 'movie').length;
  const tvCount = items.filter(d => d.media_type === 'tv').length;
  countTag.textContent = `${movieCount} pelis · ${tvCount} series`;

  switch (sortBy.value) {
    case 'rating_desc': items.sort((a,b) => b.rating - a.rating); break;
    case 'rating_asc': items.sort((a,b) => a.rating - b.rating); break;
    case 'year_desc': items.sort((a,b) => (b.year||0) - (a.year||0)); break;
    case 'year_asc': items.sort((a,b) => (a.year||0) - (b.year||0)); break;
    case 'title_asc': items.sort((a,b) => a.title_en.localeCompare(b.title_en)); break;
    case 'watched_desc': items.sort((a,b) => (b.date_watched||'').localeCompare(a.date_watched||'')); break;
    default: items.sort((a,b) => (b.added_at||'').localeCompare(a.added_at||''));
  }

  grid.innerHTML = '';
  emptyMsg.style.display = items.length ? 'none' : 'block';

  items.forEach((item, index) => {
    const url = imdbUrl(item.imdb_id) || '#';
    const inEditMode = editMode && EDITABLE;
    const el = document.createElement(inEditMode ? 'div' : 'a');
    el.className = `card ${tierClass(item.rating)}`;
    el.style.animationDelay = `${Math.min(index, 20) * 18}ms`;
    if (!inEditMode) {
      el.href = url;
      el.target = '_blank';
      el.rel = 'noopener';
    }

    const posterHtml = item.poster_path
      ? `<img src="${IMG_BASE}${item.poster_path}" alt="${item.title_en}" loading="lazy">`
      : `<div class="no-poster">${item.title_en}</div>`;

    const displayOriginal = item.title_original_display || item.title_original;
    const showOriginal = displayOriginal && displayOriginal !== item.title_en;

    const stampHtml = inEditMode
      ? `<input type="text" inputmode="decimal" class="stamp-input"
           value="${item.rating}" data-id="${item.id}"
           style="background:${ratingColor(item.rating)}">`
      : `<span class="stamp" style="background:${ratingColor(item.rating)}">${formatRating(item.rating)}</span>`;

    el.innerHTML = `
      <div class="poster-wrap">
        ${posterHtml}
        <span class="type-flag ${item.media_type}">${item.media_type === 'movie' ? 'peli' : 'serie'}</span>
        ${stampHtml}
        ${item.rating >= 9 ? '<span class="tier-star">★</span>' : ''}
      </div>
      <div class="meta">
        <p class="title-en">${item.title_en}</p>
        ${showOriginal ? `<p class="title-original">${displayOriginal}</p>` : ''}
        <p class="director">${item.director || (item.media_type === 'tv' ? 'Creador desconocido' : 'Director desconocido')}</p>
        <p class="year">${item.year || ''}</p>
      </div>
    `;
    grid.appendChild(el);
  });
}

async function saveRating(input) {
  const id = Number(input.dataset.id);
  const val = parseFloat(input.value);

  if (isNaN(val) || val < 1 || val > 10 || (val * 2) % 1 !== 0) {
    alert('La nota tiene que ser entre 1 y 10, en pasos de 0.5.');
    render();
    return;
  }

  try {
    const res = await fetch('/api/rating', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, rating: val }),
    });
    if (!res.ok) throw new Error('server error');
    const item = DATA.find(d => d.id === id);
    if (item) item.rating = val;
  } catch (err) {
    alert('No se pudo guardar. ¿Esta corriendo "python app.py"?');
  }
  render();
}

grid.addEventListener('change', (e) => {
  if (e.target.classList.contains('stamp-input')) saveRating(e.target);
});
grid.addEventListener('keydown', (e) => {
  if (e.target.classList.contains('stamp-input') && e.key === 'Enter') e.target.blur();
});

function updateClearButton() {
  searchClear.classList.toggle('visible', searchInput.value.length > 0);
}

searchInput.addEventListener('input', () => { updateClearButton(); render(); });
searchInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') searchInput.blur();
});
searchClear.addEventListener('click', () => {
  searchInput.value = '';
  updateClearButton();
  searchInput.focus();
  render();
});
updateClearButton();
typeFilter.addEventListener('change', render);
langSelect.addEventListener('change', () => { updateActiveFilterBadge(); render(); });
sortBy.addEventListener('change', render);
yearInput.addEventListener('input', () => {
  const v = parseInt(yearInput.value);
  yearFilter = yearInput.value.length === 4 && !isNaN(v) ? v : null;
  render();
});
yearInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') yearInput.blur();
});

// --- Panel de filtros avanzados ---
toggleAdvancedBtn.addEventListener('click', () => {
  const isOpen = advancedPanel.classList.toggle('open');
  toggleAdvancedBtn.classList.toggle('active', isOpen);
});

yearMinInput.addEventListener('input', () => {
  const v = parseInt(yearMinInput.value);
  yearMin = yearMinInput.value.length === 4 && !isNaN(v) ? v : null;
  updateActiveFilterBadge();
  render();
});
yearMinInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') yearMinInput.blur();
});

yearMaxInput.addEventListener('input', () => {
  const v = parseInt(yearMaxInput.value);
  yearMax = yearMaxInput.value.length === 4 && !isNaN(v) ? v : null;
  updateActiveFilterBadge();
  render();
});
yearMaxInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') yearMaxInput.blur();
});

clearAdvancedBtn.addEventListener('click', () => {
  yearMinInput.value = '';
  yearMaxInput.value = '';
  yearMin = null;
  yearMax = null;
  langSelect.value = '';
  if (ratingSliderEl.noUiSlider) {
    ratingSliderEl.noUiSlider.set([1, 10]);
  }
  minRating = 1;
  maxRating = 10;
  updateActiveFilterBadge();
  render();
});

// --- Exportar ---
toggleExportBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  exportMenu.classList.toggle('open');
});
document.addEventListener('click', (e) => {
  if (!exportMenu.contains(e.target)) exportMenu.classList.remove('open');
});
exportHtmlBtn.addEventListener('click', () => {
  exportMenu.classList.remove('open');
  exportCurrentView();
});

// --- Volver arriba ---
window.addEventListener('scroll', () => {
  backToTop.classList.toggle('visible', window.scrollY > 400);
});
backToTop.addEventListener('click', () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

updateActiveFilterBadge();
render();
</script>
</body>
</html>
"""
TEMPLATE = TEMPLATE.replace("__BASE_CSS__", BASE_CSS).replace("__FONTS_LINK__", FONTS_LINK)


def render_page(editable=False):
    rows = db.get_all_titles()
    for r in rows:
        # el titulo original crudo queda en title_original (por si lo queres
        # exportar/consultar despues); lo que se muestra en la tarjeta es
        # la version romanizada, legible en alfabeto latino
        r["title_original_display"] = romanize(r.get("title_original"), r.get("original_language"))
    # Escape </ to prevent </script> inside a JSON string from closing the script tag early.
    html = TEMPLATE.replace("__DATA_JSON__", json.dumps(rows, ensure_ascii=False).replace("</", "<\\/"))
    html = html.replace("__IMG_BASE__", config.TMDB_IMAGE_BASE)
    html = html.replace("__EDITABLE__", "true" if editable else "false")
    return html


def build():
    """Genera library.html estatico -- para mirar, sin editar, sin servidor."""
    html = render_page(editable=False)
    with open(config.HTML_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    build()
