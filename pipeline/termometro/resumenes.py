"""Verificación DETERMINÍSTICA de resúmenes (sin IA).

El resumen lo escribe la IA, pero el votante lo lee como si fuera del candidato. Por eso
ningún dato del resumen (cifra, año, monto, plazo) puede faltar en la cita o su contexto:
si el resumen dice "en los primeros 100 días" y la cita no, el sitio le atribuye al plan
algo que no se puede verificar.
"""

from __future__ import annotations

import re

from .citas import normalizar

_PALABRAS = {
    "un": 1, "uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7, "ocho": 8,
    "nueve": 9, "diez": 10, "once": 11, "doce": 12, "quince": 15, "veinte": 20, "treinta": 30, "cuarenta": 40,
    "cincuenta": 50, "sesenta": 60, "noventa": 90, "cien": 100, "ciento": 100, "doscientos": 200, "trescientos": 300,
    "quinientos": 500, "mil": 1000, "primer": 1, "primero": 1, "primera": 1, "primeros": 1, "segundo": 2, "segunda": 2,
    "tercer": 3, "tercero": 3, "tercera": 3, "cuarto": 4, "cuarta": 4,
}
_NUM = re.compile(r"\d+(?:[.,]\d+)*")


def _numeros(texto: str) -> set[str]:
    """Cifras de un texto, normalizadas ("1.000" → "1000", "0,3" → "0.3"), más las escritas en palabras."""
    t = normalizar(texto)
    nums: set[str] = set()
    for m in _NUM.findall(t):
        if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", m):  # separador de miles
            m = m.replace(".", "")
        nums.add(m.replace(",", "."))
        nums.update(re.split(r"[.,]", m))  # también cada parte: "0,3" respalda "0.3" y "3"
    for w in re.findall(r"[a-záéíóúñ]+", t):
        if w in _PALABRAS:
            nums.add(str(_PALABRAS[w]))
    return nums


def datos_sin_respaldo(resumen: str, cita: str, contexto: list[str]) -> list[str]:
    """Cifras del resumen que no aparecen ni en la cita ni en el contexto."""
    fuente = _numeros(" ".join([cita, *contexto]))
    faltan = []
    for m in _NUM.findall(normalizar(resumen)):
        crudo = m.replace(".", "") if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", m) else m
        crudo = crudo.replace(",", ".")
        if crudo not in fuente:
            faltan.append(m)
    # Plazos relativos escritos con palabras ("el primer año") que la fuente no menciona
    for frase in re.findall(r"(?:primer[oa]?s?|segund[oa]s?)\s+(?:año|años|mes|meses|días|semestre|trimestre)", normalizar(resumen)):
        if frase.split()[-1] not in normalizar(" ".join([cita, *contexto])):
            faltan.append(frase)
    return faltan
