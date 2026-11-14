"""Esquemas de salida de cada paso del pipeline (lo que se pide a la IA como JSON estructurado)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .citas import ResultadoCita


class PropuestaExtraida(BaseModel):
    tema: str = Field(description="id de uno de los temas permitidos")
    resumen: str = Field(max_length=220, description="Resumen neutral en una oración, sin adjetivos valorativos")
    cita: str = Field(description="Fragmento COPIADO LITERALMENTE del plan, sin cambiar ni una palabra")
    pagina: int = Field(ge=1, description="Página del PDF donde está la cita")


class Extraccion(BaseModel):
    propuestas: list[PropuestaExtraida]


class Transcripcion(BaseModel):
    paginas: list[str] = Field(description="Texto de cada página, en orden, transcrito literalmente")


class VotoCriterio(BaseModel):
    valor: bool
    justificacion: str = Field(max_length=300)


class VotoRubrica(BaseModel):
    meta: VotoCriterio
    plazo: VotoCriterio
    financiamiento: VotoCriterio
    competencia_municipal: VotoCriterio


class EnfoquePropuesto(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")
    nombre: str = Field(max_length=40)
    descripcion: str = Field(max_length=120)
    icono: str


class Asignacion(BaseModel):
    propuesta_id: str
    enfoques: list[str]


class Agrupacion(BaseModel):
    enfoques: list[EnfoquePropuesto] = Field(min_length=2, max_length=4)
    asignaciones: list[Asignacion]


class Observacion(BaseModel):
    propuesta_id: str
    problema: str
    sugerencia: str


class AuditoriaNeutralidad(BaseModel):
    observaciones: list[Observacion]


# ─── Intermedios del pipeline (se cachean, no se piden a la IA) ─────────────


class PropuestaVerificada(BaseModel):
    id: str
    candidato: str
    tema: str
    resumen: str
    cita: str
    pagina: int
    verificacion: ResultadoCita
    origen: Literal["extraccion", "cobertura"]


class ResultadoDocumento(BaseModel):
    """Salida de los pasos [1]-[3] para UN documento (unidad incremental)."""

    candidato: str
    sha256: str
    escaneado: bool
    verificadas: list[PropuestaVerificada]
    descartadas: list[PropuestaVerificada]
