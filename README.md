# Mi Catálogo

Catálogo personal de películas y series. Vos ponés la nota (1 a 10, medios
puntos permitidos), cada tarjeta te lleva a IMDB con un click.

## 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 2. Conseguir una API key de TMDB (gratis)

1. Creá una cuenta en <https://www.themoviedb.org/>
2. Andá a Settings → API → "Create" → elegís "Developer" → completás el
   formulario corto (es para uso personal, poné eso).
3. Te dan una "API Key (v3 auth)". Copiala.
4. Abrí `config.py` y pegala donde dice `PEGA_TU_API_KEY_ACA`
   (o exportala como variable de entorno `TMDB_API_KEY` si preferís no
   dejarla en el archivo).

## 3. Carga masiva (tu export de IMDB)

Si ya tenés cientos o miles de títulos rateados en IMDB, no los cargues
a mano uno por uno. Exportá tu lista desde IMDB (perfil → "Your
Ratings" → botón de exportar) y corré:

```bash
python bulk_import.py ratings.csv
```

Lee el CSV de IMDB (que ya trae imdb_id, tu nota, director, tipo), busca
cada título en TMDB por su imdb_id para sacar poster y título original,
y carga todo solo. Es re-ejecutable sin miedo: si se corta a mitad de
camino, lo corrés de nuevo y sigue donde había quedado (no duplica).

Ojo: como IMDB solo permite notas enteras, lo que importe va a entrar
con nota entera. Los medios puntos los vas sumando de acá en adelante,
a mano, con `add_title.py` o editando directo en `library.db`.

## 4. Agregar un título nuevo (uno por uno, de acá en adelante)

```bash
python add_title.py "seven samurai"
```

Te va a mostrar una lista numerada de resultados (películas y series
mezcladas). Elegís el número correcto, te muestra el director/creador que
sacó automáticamente, y te pide:

- Tu nota (acepta medios puntos: 7, 7.5, 8...)
- Fecha en que la viste (Enter = hoy, `s` = sin fecha)

Guarda en `library.db` y regenera `library.html` automáticamente.

## 5. Ver tu catálogo

Abrí `library.html` con doble click (o arrastralo a un navegador). No
necesita servidor ni internet para verse — los datos ya quedan embebidos
adentro del archivo. Cada tarjeta:

- Muestra título en inglés, título original (si difiere), director, año
- Tiene tu nota como sello en la esquina
- Al hacer click te lleva directo a la página de IMDB de ese título

Tiene buscador, filtro por película/serie, y varios criterios de orden
(nota, año, alfabético, fecha en que la viste).

## Notas

- Las series se guardan con **una sola nota global**, sin desglose por
  temporada — como lo pediste.
- Si agregás un título que ya existe (mismo `tmdb_id` + tipo), se
  actualiza la nota y la fecha en vez de duplicarse.
- Si TMDB no tiene el `imdb_id` de algo (pasa con títulos muy nuevos o
  muy nicho), la tarjeta se genera igual pero el click no va a ningún
  lado — es la excepción rara, no la regla.
- `library.db` es SQLite estándar — lo podés abrir con DB Browser for
  SQLite si en algún momento querés editar/borrar filas a mano en vez de
  por línea de comando.
