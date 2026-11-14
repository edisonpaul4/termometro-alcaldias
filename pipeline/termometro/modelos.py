"""Contrato de datos entre el pipeline y la web.

Estos modelos son la ÚNICA fuente de verdad del formato de `datos/`.
De aquí se exporta el JSON Schema y, desde ahí, los tipos TypeScript de la web.
Cambiar algo aquí = cambiar el contrato: correr `make schema` y `make validar`.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Slug = Annotated[str, Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$", description="Identificador en minúsculas con guiones")]
Icono = Annotated[
    str,
    Field(
        pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$",
        description="Nombre de un ícono Phosphor (https://phosphoricons.com), p. ej. 'shield-check'. "
        "Debe estar en el registro de la web (web/src/lib/iconos.ts).",
    ),
]


class Base(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, json_schema_serialization_defaults_required=True)


# ─── Catálogos comunes ──────────────────────────────────────────────────────


class Tema(Base):
    """Eje temático común a todas las ciudades (seguridad, movilidad...)."""

    id: Slug
    nombre: str
    nombre_corto: str = Field(max_length=14, description="Para tarjetas pequeñas en móvil")
    icono: Icono
    descripcion: str


class CiudadRegistro(Base):
    """Entrada de `datos/ciudades.yaml`."""

    id: Slug
    nombre: str
    nombre_oficial: str
    dignidad: str = "Alcaldía"
    activa: bool


# ─── Por ciudad ─────────────────────────────────────────────────────────────


class Ciudad(Base):
    """`datos/ciudades/<id>/ciudad.yaml`."""

    id: Slug
    nombre: str
    eleccion: date
    debate: date | None = None
    fin_campana: date
    candidatos_verificados: bool = Field(description="Lista confirmada contra la fuente oficial del CNE")
    es_mock: bool = False


class Enfoque(Base):
    """Forma de abordar un tema, agrupada a partir de propuestas reales (paso 2 del flujo)."""

    id: Slug
    tema: Slug
    nombre: str = Field(max_length=40)
    descripcion: str
    icono: Icono


class Enfoques(Base):
    """`datos/ciudades/<id>/enfoques.yaml`."""

    enfoques: list[Enfoque]

    @model_validator(mode="after")
    def _ids_unicos(self) -> Enfoques:
        _sin_duplicados([e.id for e in self.enfoques], "enfoque")
        return self


# ─── Fuentes ────────────────────────────────────────────────────────────────


class Fuente(Base):
    """Referencia pública a una fuente. `archivo` apunta a la copia en `fuentes/`."""

    url: str
    titulo: str
    consultado: date
    archivo: str | None = Field(default=None, description="Ruta relativa a la raíz del repo")


class Trayectoria(Base):
    cargo: str
    periodo: str
    fuente: Fuente


class PlanTrabajo(Base):
    disponible: bool
    fuente: Fuente | None = None
    paginas: int | None = Field(default=None, ge=1)
    sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    nota: str | None = None

    @model_validator(mode="after")
    def _coherente(self) -> PlanTrabajo:
        if self.disponible and (self.fuente is None or self.paginas is None):
            raise ValueError("un plan disponible requiere fuente y páginas")
        if not self.disponible and not self.nota:
            raise ValueError("un plan no disponible requiere una nota explicando por qué")
        return self


# ─── Calificación por jurado de IA ──────────────────────────────────────────


class Criterio(StrEnum):
    meta = "meta"
    plazo = "plazo"
    financiamiento = "financiamiento"
    competencia_municipal = "competencia_municipal"


class Proveedor(StrEnum):
    anthropic = "anthropic"
    openai = "openai"
    google = "google"
    mock = "mock"


class VotoJurado(Base):
    proveedor: Proveedor
    modelo: str
    valor: bool | None = Field(description="null = el modelo falló o devolvió una respuesta inválida")
    justificacion: str | None = None


class Consenso(StrEnum):
    unanime = "unanime"  # todos los jurados válidos coinciden (y al menos 3)
    mayoria = "mayoria"  # mayoría simple, o unanimidad con menos de 3 jurados válidos
    humano = "humano"  # resuelto en revisión humana


class Calificacion(Base):
    valor: bool
    consenso: Consenso
    votos: list[VotoJurado] = Field(min_length=1)
    nota_revision: str | None = Field(default=None, description="Obligatoria si consenso = humano")

    @model_validator(mode="after")
    def _coherente(self) -> Calificacion:
        if self.consenso == Consenso.humano:
            if not self.nota_revision:
                raise ValueError("una calificación resuelta por humano requiere nota_revision")
            return self
        validos = [v.valor for v in self.votos if v.valor is not None]
        if not validos:
            raise ValueError("sin votos válidos el consenso debe ser 'humano'")
        a_favor = sum(validos)
        mayoria = a_favor > len(validos) / 2
        if a_favor * 2 == len(validos):
            raise ValueError("empate entre jurados: debe resolverse por humano")
        if self.valor != mayoria:
            raise ValueError("valor no coincide con la mayoría de los jurados")
        unanime = len(set(validos)) == 1 and len(validos) >= 3
        if self.consenso == Consenso.unanime and not unanime:
            raise ValueError("consenso 'unanime' requiere ≥3 votos válidos coincidentes")
        if self.consenso == Consenso.mayoria and unanime:
            raise ValueError("los votos son unánimes: el consenso debe ser 'unanime'")
        return self


class Rubrica(Base):
    meta: Calificacion
    plazo: Calificacion
    financiamiento: Calificacion
    competencia_municipal: Calificacion


# ─── Candidato y propuestas ─────────────────────────────────────────────────


class Propuesta(Base):
    id: Slug
    tema: Slug
    resumen: str = Field(max_length=220, description="Resumen neutral, sin adjetivos valorativos")
    cita: str = Field(min_length=10, description="Texto LITERAL del plan de trabajo")
    pagina: int = Field(ge=1)
    cita_verificada: bool = Field(description="La cita se encontró en el texto de esa página")
    enfoques: list[Slug] = []
    rubrica: Rubrica


class Candidato(Base):
    """`datos/ciudades/<ciudad>/candidatos/<id>.yaml`."""

    id: Slug
    nombre: str
    lista: str
    organizacion: str
    foto: str | None = None
    foto_fuente: Fuente | None = None
    trayectoria: list[Trayectoria] = []
    plan_trabajo: PlanTrabajo
    propuestas: list[Propuesta] = []
    es_mock: bool = False

    @model_validator(mode="after")
    def _coherente(self) -> Candidato:
        _sin_duplicados([p.id for p in self.propuestas], "propuesta")
        if self.foto and not self.foto_fuente:
            raise ValueError("toda foto requiere foto_fuente")
        if self.propuestas and not self.plan_trabajo.disponible:
            raise ValueError("hay propuestas pero el plan de trabajo figura como no disponible")
        if self.plan_trabajo.paginas:
            fuera = [p.id for p in self.propuestas if p.pagina > self.plan_trabajo.paginas]
            if fuera:
                raise ValueError(f"propuestas con página fuera del plan: {fuera}")
        return self


# ─── Bundle exportado (lo que consume la web) ───────────────────────────────


class DatosCiudad(Base):
    ciudad: Ciudad
    enfoques: list[Enfoque]
    candidatos: list[Candidato]


class DatosSitio(Base):
    """Todo lo que la web necesita. Se exporta como JSON Schema → tipos TS."""

    version_schema: Literal[1] = 1
    temas: list[Tema]
    ciudades: list[CiudadRegistro]
    datos: dict[str, DatosCiudad]


def _sin_duplicados(ids: list[str], que: str) -> None:
    from collections import Counter

    dup = {i for i, n in Counter(ids).items() if n > 1}
    if dup:
        raise ValueError(f"ids de {que} duplicados: {sorted(dup)}")

