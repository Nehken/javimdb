"""
Traduce codigos ISO 3166-1 (los que devuelve TMDB en production_countries)
a nombres en castellano, usando la tabla de territorios de Babel -- cubre
practicamente todos los paises reales, no una lista armada a mano.
"""

from babel import Locale

_locale = Locale("es")

LEGACY_COUNTRIES = {
    "XI": "Islas del Canal (código legado)",
    "AN": "Antillas Neerlandesas (disuelto)",
    "SU": "Unión Soviética (histórico)",
}


def country_name(code):
    return LEGACY_COUNTRIES.get(code, _locale.territories.get(code, code))
