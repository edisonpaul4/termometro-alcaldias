"""Capa de proveedores de IA. Todos devuelven salidas estructuradas validadas con Pydantic.

- LLM_MODE=mock → MockProveedor (sin red, sin costo, determinístico)
- LLM_MODE=real → Anthropic / OpenAI / Google (se implementan en F6)

Roles (ver PLAN.md §8):
    extractor        → anthropic
    transcriptor     → google   (OCR de planes escaneados; independiente del extractor)
    cobertura        → google
    jurado           → anthropic, openai, google (a ciegas)
    enfoques         → openai propone, anthropic valida
    neutralidad      → openai
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol, TypeVar

from pydantic import BaseModel

from .config import DIR_LOGS, DIR_PROMPTS, config
from .modelos import Proveedor

M = TypeVar("M", bound=BaseModel)


@dataclass
class Solicitud:
    paso: str
    sistema: str
    usuario: str
    esquema: type[BaseModel]
    pdf: Path | None = None  # documento adjunto (p. ej. plan escaneado)
    # Datos estructurados de la entrada. Los proveedores reales los ignoran (ya están en el
    # texto del prompt); el mock los usa para generar respuestas coherentes.
    extra: dict[str, Any] = field(default_factory=dict)


class ProveedorIA(Protocol):
    proveedor: Proveedor
    modelo: str

    def generar(self, sol: Solicitud) -> BaseModel: ...


# ─── Prompts versionados ────────────────────────────────────────────────────


@dataclass(frozen=True)
class Prompt:
    nombre: str
    texto: str
    version: str  # hash corto del contenido: editar el prompt invalida solo su caché

    def render(self, **valores: str) -> str:
        t = self.texto
        for k, v in valores.items():
            t = t.replace("{{" + k + "}}", v)
        return t


def cargar_prompt(nombre: str) -> Prompt:
    from .cache import sha256_texto

    texto = (DIR_PROMPTS / f"{nombre}.md").read_text(encoding="utf-8")
    if "{{RUBRICA}}" in texto:
        texto = texto.replace("{{RUBRICA}}", (DIR_PROMPTS.parent / "rubrica.md").read_text(encoding="utf-8"))
    return Prompt(nombre=nombre, texto=texto, version=sha256_texto(texto)[:12])


# ─── Bitácora ───────────────────────────────────────────────────────────────


def registrar(sol: Solicitud, prov: ProveedorIA, segundos: float, uso: dict | None = None, error: str | None = None) -> None:
    DIR_LOGS.mkdir(parents=True, exist_ok=True)
    fila = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "paso": sol.paso,
        "proveedor": prov.proveedor.value,
        "modelo": prov.modelo,
        "segundos": round(segundos, 2),
        "uso": uso or {},
        "error": error,
    }
    with (DIR_LOGS / "llamadas.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(fila, ensure_ascii=False) + "\n")


def llamar(prov: ProveedorIA, sol: Solicitud, tipo: type[M], intentos: int = 3) -> M:
    """Llama al proveedor con reintentos (backoff exponencial) y valida la salida."""
    ultimo: Exception | None = None
    for i in range(intentos):
        t0 = time.monotonic()
        try:
            r = prov.generar(sol)
            salida = tipo.model_validate(r.model_dump() if isinstance(r, BaseModel) else r)
            registrar(sol, prov, time.monotonic() - t0)
            return salida
        except NotImplementedError:
            raise
        except Exception as e:  # noqa: BLE001 — se registra y se reintenta
            ultimo = e
            registrar(sol, prov, time.monotonic() - t0, error=f"{type(e).__name__}: {e}")
            if i < intentos - 1 and config().modo == "real":
                time.sleep(2**i)
    raise RuntimeError(f"{prov.proveedor.value}/{prov.modelo} falló en {sol.paso}: {ultimo}") from ultimo


# ─── Proveedores reales (F6) ────────────────────────────────────────────────


class _Real:
    proveedor: Proveedor

    def __init__(self, modelo: str):
        self.modelo = modelo

    def generar(self, sol: Solicitud) -> BaseModel:
        raise NotImplementedError(f"Proveedor {self.proveedor.value} real: se implementa en F6")


class AnthropicIA(_Real):
    proveedor = Proveedor.anthropic


class OpenAIIA(_Real):
    proveedor = Proveedor.openai


class GoogleIA(_Real):
    proveedor = Proveedor.google


# ─── Fábrica ────────────────────────────────────────────────────────────────


@dataclass
class Equipo:
    extractor: ProveedorIA
    transcriptor: ProveedorIA
    cobertura: ProveedorIA
    jurado: list[ProveedorIA]
    enfoques_propone: ProveedorIA
    enfoques_valida: ProveedorIA
    neutralidad: ProveedorIA


def equipo() -> Equipo:
    cfg = config()
    if cfg.modo == "mock":
        from .mock_llm import MockIA

        a, o, g = (MockIA(Proveedor.mock, f"mock-{n}") for n in ("anthropic", "openai", "google"))
    else:
        a, o, g = AnthropicIA(cfg.modelo_anthropic), OpenAIIA(cfg.modelo_openai), GoogleIA(cfg.modelo_gemini)
    return Equipo(
        extractor=a, transcriptor=g, cobertura=g, jurado=[a, o, g], enfoques_propone=o, enfoques_valida=a, neutralidad=o
    )
