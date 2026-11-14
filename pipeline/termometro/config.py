"""Configuración desde `.env` (raíz del repo) + variables de entorno (estas ganan).

Nunca imprime ni registra valores de claves de API.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from .datos import RAIZ_REPO

DIR_PIPELINE = RAIZ_REPO / "pipeline"
DIR_CACHE = DIR_PIPELINE / ".cache"
DIR_LOGS = DIR_PIPELINE / "logs"
DIR_SALIDA = DIR_PIPELINE / ".salida"
DIR_PROMPTS = DIR_PIPELINE / "prompts"


def _leer_env(ruta: Path) -> dict[str, str]:
    if not ruta.exists():
        return {}
    valores: dict[str, str] = {}
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        valores[clave.strip()] = valor.split(" #", 1)[0].strip().strip('"').strip("'")
    return valores


@dataclass(frozen=True)
class Config:
    modo: str  # "mock" | "real"
    modelo_anthropic: str
    modelo_openai: str
    modelo_gemini: str
    max_usd: float
    _claves: dict[str, str]

    def clave(self, nombre: str) -> str:
        valor = self._claves.get(nombre, "")
        if not valor:
            raise RuntimeError(f"Falta {nombre} en .env (necesaria con LLM_MODE=real)")
        return valor

    def tiene_clave(self, nombre: str) -> bool:
        return bool(self._claves.get(nombre))

    def __repr__(self) -> str:  # jamás exponer claves
        return f"Config(modo={self.modo!r}, anthropic={self.modelo_anthropic!r}, openai={self.modelo_openai!r}, gemini={self.modelo_gemini!r}, max_usd={self.max_usd})"


@cache
def config() -> Config:
    v = _leer_env(RAIZ_REPO / ".env") | {k: val for k, val in os.environ.items() if val}
    modo = v.get("LLM_MODE", "mock").lower()
    if modo not in ("mock", "real"):
        raise RuntimeError(f"LLM_MODE inválido: {modo!r} (usar mock o real)")
    return Config(
        modo=modo,
        modelo_anthropic=v.get("MODELO_ANTHROPIC", "claude-opus-5-5"),
        modelo_openai=v.get("MODELO_OPENAI", "gpt-6.1-sol"),
        modelo_gemini=v.get("MODELO_GEMINI", "gemini-4-carbon"),
        max_usd=float(v.get("MAX_USD", "15")),
        _claves={k: v[k] for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY") if k in v},
    )
