"""
Borra todo (library.db, library.html, stats.html) para arrancar de cero.
Pide confirmacion explicita antes de tocar nada -- no hay drama de
correrlo por error y arrepentirse.

Uso:
    python reset_db.py
"""

import os

import config

FILES = [config.DB_PATH, config.HTML_OUTPUT_PATH, config.STATS_OUTPUT_PATH]


def main():
    existing = [f for f in FILES if os.path.exists(f)]

    if not existing:
        print("No hay nada que borrar -- ya esta todo limpio.")
        return

    print("Esto borra PARA SIEMPRE:")
    for f in existing:
        print(f"  - {f}")

    confirm = input('\nEscribi "borrar todo" para confirmar (cualquier otra cosa cancela): ').strip()
    if confirm != "borrar todo":
        print("Cancelado, no se toco nada.")
        return

    for f in existing:
        os.remove(f)

    print("\nListo, todo borrado. Corré bulk_import.py cuando quieras para arrancar de cero.")


if __name__ == "__main__":
    main()
