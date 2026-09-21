"""
Convierte el titulo original a algo legible en alfabeto latino cuando
hace falta (japones, ruso, griego, etc). Si ya esta en latino (frances,
italiano, portugues...) lo deja tal cual -- esos se leen bien con
tildes y todo.
"""

import unicodedata

import pykakasi
from unidecode import unidecode

_kks = pykakasi.kakasi()


def _is_latin_or_neutral(ch):
    if not ch.isalpha():
        return True  # numeros, espacios, puntuacion -> no molestan
    try:
        name = unicodedata.name(ch)
    except ValueError:
        return True
    return name.startswith("LATIN")


def needs_romanization(text):
    if not text:
        return False
    return any(not _is_latin_or_neutral(c) for c in text)


def romanize(text, language_code=None):
    if not needs_romanization(text):
        return text

    if language_code == "ja":
        try:
            parts = _kks.convert(text)
            result = " ".join(p["hepburn"] for p in parts).strip()
            return result.title() if result else text
        except Exception:
            pass  # si pykakasi falla por lo que sea, cae al fallback generico

    try:
        return unidecode(text)
    except Exception:
        return text
