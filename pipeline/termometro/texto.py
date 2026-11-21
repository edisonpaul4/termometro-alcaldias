"""[0] Texto por página de un PDF (pdftotext). Cacheado por el sha256 del archivo."""

from __future__ import annotations

import subprocess
from pathlib import Path

from pydantic import BaseModel

from .cache import Cache, sha256_archivo

VERSION = "v1"
# Menos de esto (caracteres no blancos por página, en promedio) = probablemente escaneado
UMBRAL_ESCANEADO = 60


class TextoPDF(BaseModel):
    sha256: str
    paginas: list[str]
    escaneado: bool

    @property
    def n_paginas(self) -> int:
        return len(self.paginas)


def _extraer(ruta: Path, sha: str) -> TextoPDF:
    salida = subprocess.run(
        ["pdftotext", "-enc", "UTF-8", str(ruta), "-"], capture_output=True, text=True, encoding="utf-8", check=True
    ).stdout
    paginas = salida.split("\f")
    if paginas and not paginas[-1].strip():
        paginas = paginas[:-1]  # pdftotext termina con un \f
    chars = sum(len("".join(p.split())) for p in paginas)
    return TextoPDF(sha256=sha, paginas=paginas, escaneado=chars < UMBRAL_ESCANEADO * max(len(paginas), 1))


def texto_pdf(ruta: Path, cache: Cache) -> TextoPDF:
    sha = sha256_archivo(ruta)
    return cache.obtener("texto", VERSION, "pdftotext", sha, TextoPDF, lambda: _extraer(ruta, sha))
