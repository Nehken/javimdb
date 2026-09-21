"""
Servidor local para editar notas sin friccion de linea de comandos.

Uso:
    python app.py

Abrís http://127.0.0.1:5000 en el navegador. Apretás "Editar" arriba a
la derecha, click en el sello de nota de la tarjeta que quieras
corregir, escribís la nota nueva, Enter (o click afuera). Se guarda al
toque en library.db. Cada guardado tambien regenera library.html, asi
que el archivo estatico queda al dia aunque no lo vuelvas a exportar
a mano. Cerrá la terminal cuando termines de editar.
"""

from flask import Flask, jsonify, request

import db
from export_html import render_page, build as export_html
from build_stats import render_stats_page, build as export_stats

app = Flask(__name__)


@app.route("/")
def index():
    db.init_db()
    return render_page(editable=True)


@app.route("/stats")
def stats():
    db.init_db()
    return render_stats_page(back_href="/", catalog_href="/")


@app.route("/api/rating", methods=["POST"])
def update_rating():
    data = request.get_json(force=True, silent=True) or {}
    row_id = data.get("id")
    rating = data.get("rating")

    try:
        rating = float(rating)
    except (TypeError, ValueError):
        return jsonify({"error": "nota invalida"}), 400

    if rating < 1 or rating > 10 or (rating * 2) % 1 != 0:
        return jsonify({"error": "la nota tiene que ser entre 1 y 10, en pasos de 0.5"}), 400

    with db.get_conn() as conn:
        cur = conn.execute("SELECT id FROM titles WHERE id = ?", (row_id,))
        if cur.fetchone() is None:
            return jsonify({"error": "no existe ese titulo"}), 404
        conn.execute("UPDATE titles SET rating = ? WHERE id = ?", (rating, row_id))

    export_html()  # mantiene library.html sincronizado de paso
    export_stats()  # y el dashboard tambien
    return jsonify({"ok": True, "id": row_id, "rating": rating})


if __name__ == "__main__":
    db.init_db()
    print("Abri http://127.0.0.1:5000 en el navegador para editar notas.")
    print("O desde otro dispositivo: http://192.168.1.4:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
