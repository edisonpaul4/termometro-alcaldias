"""[2] Verificación DETERMINÍSTICA de citas (sin IA).

Una propuesta solo se publica si su cita aparece literalmente en el plan de trabajo.
Tolerancias (porque los PDF ensucian el texto): mayúsculas, espacios, saltos de línea,
guiones de corte de palabra, comillas tipográficas y, para OCR, una similitud ≥ 95%.
Si la cita está en otra página, se corrige el número de página y se deja constancia.
"""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher
from typing import Literal

from pydantic import BaseModel

UMBRAL_FUZZY = 0.95
MIN_CARACTERES = 20

_REEMPLAZOS = str.maketrans({"“": '"', "”": '"', "„": '"', "«": '"', "»": '"', "‘": "'", "’": "'", "–": "-", "—": "-", "­": ""})


def normalizar(texto: str) -> str:
    t = unicodedata.normalize("NFKC", texto).translate(_REEMPLAZOS)
    t = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", t)  # palabra cortada con guion al final de línea
    t = re.sub(r"\s+", " ", t)
    return t.strip().lower()


class ResultadoCita(BaseModel):
    verificada: bool
    pagina: int | None  # página donde realmente está (1-indexada)
    metodo: Literal["exacta", "aproximada", "no_encontrada", "muy_corta"]
    similitud: float
    pagina_corregida: bool = False


def _mejor_ventana(cita: str, pagina: str) -> float:
    """Mayor similitud de la cita contra un tramo de la página de su mismo largo.

    Se ancla en los bloques idénticos más largos entre cita y página (un error de OCR
    corta la cita en pocos bloques largos) y se prueban pequeños desplazamientos.
    """
    n = len(cita)
    if n == 0 or not pagina:
        return 0.0
    sm = SequenceMatcher(None, pagina, cita, autojunk=False)
    bloques = sorted(sm.get_matching_blocks(), key=lambda b: -b.size)[:3]
    mejor = 0.0
    for a, b, tam in bloques:
        if tam < 8:
            continue
        inicio = a - b  # dónde empezaría la cita en la página si este bloque está alineado
        for d in range(-4, 5):
            i = max(0, inicio + d)
            ventana = pagina[i : i + n]
            v = SequenceMatcher(None, cita, ventana, autojunk=False)
            if v.real_quick_ratio() < UMBRAL_FUZZY or v.quick_ratio() < UMBRAL_FUZZY:
                continue
            mejor = max(mejor, v.ratio())
    return mejor


def verificar(cita: str, paginas: list[str], pagina_declarada: int, minimo: int = MIN_CARACTERES) -> ResultadoCita:
    c = normalizar(cita)
    if len(c) < minimo:
        return ResultadoCita(verificada=False, pagina=None, metodo="muy_corta", similitud=0.0)

    norm = [normalizar(p) for p in paginas]
    total = len(norm)
    d = pagina_declarada - 1
    # Orden de búsqueda: la página declarada, sus vecinas y luego el resto
    orden = [i for i in (d, d - 1, d + 1) if 0 <= i < total]
    orden += [i for i in range(total) if i not in orden]

    for i in orden:
        if c in norm[i]:
            return ResultadoCita(verificada=True, pagina=i + 1, metodo="exacta", similitud=1.0, pagina_corregida=i != d)

    mejor_sim, mejor_pag = 0.0, None
    for i in orden:
        sim = _mejor_ventana(c, norm[i])
        if sim > mejor_sim:
            mejor_sim, mejor_pag = sim, i
        if sim >= 0.99:
            break
    if mejor_sim >= UMBRAL_FUZZY and mejor_pag is not None:
        return ResultadoCita(
            verificada=True, pagina=mejor_pag + 1, metodo="aproximada", similitud=round(mejor_sim, 4), pagina_corregida=mejor_pag != d
        )
    return ResultadoCita(verificada=False, pagina=None, metodo="no_encontrada", similitud=round(mejor_sim, 4))
