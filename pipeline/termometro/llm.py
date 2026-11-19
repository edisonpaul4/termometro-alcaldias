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
import threading
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
        rubrica = (DIR_PROMPTS.parent / "rubrica.md").read_text(encoding="utf-8")
        # Los jurados reciben SOLO el bloque marcado (sin metadatos del proyecto ni reglas de cálculo)
        rubrica = rubrica.split("<!-- jurado:inicio -->", 1)[1].split("<!-- jurado:fin -->", 1)[0].strip()
        texto = texto.replace("{{RUBRICA}}", rubrica)
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
        GASTO.verificar()
        t0 = time.monotonic()
        try:
            r = prov.generar(sol)
            salida = tipo.model_validate(r.model_dump() if isinstance(r, BaseModel) else r)
            registrar(sol, prov, time.monotonic() - t0, getattr(prov, "ultimo_uso", None))
            return salida
        except (NotImplementedError, PresupuestoAgotado):
            raise
        except Exception as e:  # noqa: BLE001 — se registra y se reintenta
            ultimo = e
            registrar(sol, prov, time.monotonic() - t0, getattr(prov, "ultimo_uso", None), error=f"{type(e).__name__}: {str(e)[:300]}")
            if i < intentos - 1 and config().modo == "real":
                time.sleep(2**i)
    raise RuntimeError(f"{prov.proveedor.value}/{prov.modelo} falló en {sol.paso}: {ultimo}") from ultimo


# ─── Costos y presupuesto ───────────────────────────────────────────────────

# USD por millón de tokens (entrada, salida). Fuente: páginas oficiales de precios, 14 nov 2026.
# Gemini 4 Carbon duplica su precio el 1 dic 2026. Los tokens de razonamiento se cobran como salida.
PRECIOS = {
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "gpt-6.1-sol": (2.00, 10.00),
    "gemini-4-carbon": (2.00, 10.00),
}


class PresupuestoAgotado(RuntimeError):
    pass


class Contador:
    """Gasto acumulado de la corrida (thread-safe). Corta todo al superar MAX_USD."""

    def __init__(self):
        self._lock = threading.Lock()
        self.usd = 0.0
        self.tokens_in = 0
        self.tokens_out = 0
        self.llamadas = 0

    def sumar(self, modelo: str, tin: int, tout: int) -> float:
        pin, pout = PRECIOS.get(modelo, (0.0, 0.0))
        costo = (tin * pin + tout * pout) / 1_000_000
        with self._lock:
            self.usd += costo
            self.tokens_in += tin
            self.tokens_out += tout
            self.llamadas += 1
        return costo

    def verificar(self) -> None:
        tope = config().max_usd
        if self.usd >= tope:
            raise PresupuestoAgotado(f"Presupuesto agotado: USD {self.usd:.2f} ≥ MAX_USD {tope:.2f}")


GASTO = Contador()


# ─── Proveedores reales ─────────────────────────────────────────────────────


class _ConUso:
    """Uso de la última llamada, por hilo (las llamadas del jurado corren en paralelo)."""

    _tl: threading.local

    @property
    def ultimo_uso(self) -> dict:
        return getattr(self._tl, "uso", {})


def _uso(modelo: str, tin: int, tout: int) -> dict:
    return {"tokens_entrada": tin, "tokens_salida": tout, "usd": round(GASTO.sumar(modelo, tin, tout), 5)}


class AnthropicIA(_ConUso):
    """Claude vía SDK oficial: streaming + salida estructurada (Pydantic) + fallback ante rechazos."""

    proveedor = Proveedor.anthropic

    def __init__(self, modelo: str):
        import anthropic

        self.modelo = modelo
        self.cliente = anthropic.Anthropic(api_key=config().clave("ANTHROPIC_API_KEY"), max_retries=2, timeout=900.0)
        self._tl = threading.local()

    def generar(self, sol: Solicitud) -> BaseModel:
        import base64

        contenido: list[dict] = []
        if sol.pdf:
            datos = base64.standard_b64encode(sol.pdf.read_bytes()).decode("ascii")
            contenido.append({"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": datos}})
        contenido.append({"type": "text", "text": sol.usuario})
        extra = {"system": sol.sistema} if sol.sistema else {}
        with self.cliente.beta.messages.stream(
            model=self.modelo,
            max_tokens=64000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",  # si un clasificador rechaza, el servidor reintenta con el modelo de respaldo
            output_config={"effort": "high" if sol.paso in ("extraccion", "enfoques_validacion") else "medium"},
            output_format=sol.esquema,
            # El razonamiento se transmite resumido: sin esto no llega ningún byte mientras el modelo
            # piensa y, en documentos largos, la conexión se corta por tiempo de espera.
            thinking={"type": "adaptive", "display": "summarized"},
            messages=[{"role": "user", "content": contenido}],
            **extra,
        ) as stream:
            msg = stream.get_final_message()
        self._tl.uso = _uso(self.modelo, msg.usage.input_tokens + (msg.usage.cache_read_input_tokens or 0) + (msg.usage.cache_creation_input_tokens or 0), msg.usage.output_tokens)
        if msg.stop_reason == "refusal":
            raise RuntimeError(f"rechazo del modelo: {getattr(msg.stop_details, 'category', None)}")
        if msg.stop_reason == "max_tokens":
            raise RuntimeError("respuesta truncada (max_tokens)")
        if msg.parsed_output is None:
            raise RuntimeError("sin salida estructurada")
        return msg.parsed_output


class OpenAIIA(_ConUso):
    proveedor = Proveedor.openai

    def __init__(self, modelo: str):
        import openai

        self.modelo = modelo
        self.cliente = openai.OpenAI(api_key=config().clave("OPENAI_API_KEY"), max_retries=4)
        self._tl = threading.local()

    def generar(self, sol: Solicitud) -> BaseModel:
        if sol.pdf:
            raise NotImplementedError("OpenAI no recibe PDFs en este pipeline (rol sin documentos)")
        r = self.cliente.responses.parse(
            model=self.modelo,
            instructions=sol.sistema or None,
            input=[{"role": "user", "content": sol.usuario}],
            text_format=sol.esquema,
        )
        u = r.usage
        self._tl.uso = _uso(self.modelo, u.input_tokens if u else 0, u.output_tokens if u else 0)
        if r.output_parsed is None:
            raise RuntimeError("sin salida estructurada")
        return r.output_parsed


class GoogleIA(_ConUso):
    proveedor = Proveedor.google

    def __init__(self, modelo: str):
        from google import genai

        self.modelo = modelo
        self.cliente = genai.Client(api_key=config().clave("GEMINI_API_KEY"))
        self._tl = threading.local()

    def generar(self, sol: Solicitud) -> BaseModel:
        from google.genai import types

        partes: list = []
        if sol.pdf:
            partes.append(types.Part.from_bytes(data=sol.pdf.read_bytes(), mime_type="application/pdf"))
        partes.append(sol.usuario)
        r = self.cliente.models.generate_content(
            model=self.modelo,
            contents=partes,
            config=types.GenerateContentConfig(
                system_instruction=sol.sistema or None,
                response_mime_type="application/json",
                response_schema=sol.esquema,
                max_output_tokens=65536,
            ),
        )
        um = r.usage_metadata
        tin = (um.prompt_token_count or 0) if um else 0
        tout = ((um.candidates_token_count or 0) + (um.thoughts_token_count or 0)) if um else 0
        self._tl.uso = _uso(self.modelo, tin, tout)
        if isinstance(r.parsed, BaseModel):
            return r.parsed
        if r.text:
            return sol.esquema.model_validate_json(r.text)
        raise RuntimeError(f"sin salida estructurada (finish_reason={r.candidates[0].finish_reason if r.candidates else None})")


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
    # Si el transcriptor se niega (p. ej. Gemini corta con RECITATION en documentos oficiales largos)
    transcriptor_respaldo: ProveedorIA | None = None


def equipo() -> Equipo:
    cfg = config()
    if cfg.modo == "mock":
        from .mock_llm import MockIA

        a, o, g = (MockIA(Proveedor.mock, f"mock-{n}") for n in ("anthropic", "openai", "google"))
        aj = a
    else:
        a, o, g = AnthropicIA(cfg.modelo_anthropic), OpenAIIA(cfg.modelo_openai), GoogleIA(cfg.modelo_gemini)
        # Jurado de Claude con un modelo más económico (opción C); el extractor sigue en Opus
        aj = a if cfg.modelo_jurado_anthropic == cfg.modelo_anthropic else AnthropicIA(cfg.modelo_jurado_anthropic)
    return Equipo(
        extractor=a, transcriptor=g, cobertura=g, jurado=[aj, o, g], enfoques_propone=o, enfoques_valida=a, neutralidad=o,
        transcriptor_respaldo=aj,
    )
