"""Esquemas de salida de cada paso del pipeline (lo que se pide a la IA como JSON estructurado).

Sin restricciones de largo/patrón/rango en los esquemas que van a la API: no todos los proveedores
las soportan en salidas estructuradas. Esas reglas se aplican después, en el pipeline
(recorte de resúmenes, saneamiento de ids e íconos, verificación de citas).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .citas import ResultadoCita


class PropuestaExtraida(BaseModel):
    tema: str = Field(description="id de uno de los temas permitidos")
    resumen: str = Field(description="Resumen neutral en una oración (máx. 200 caracteres), sin adjetivos valorativos")
    cita: str = Field(description="Fragmento COPIADO LITERALMENTE del plan, sin cambiar ni una palabra")
    pagina: int = Field(description="Página del PDF donde está la cita (1 = primera)")


class Extraccion(BaseModel):
    propuestas: list[PropuestaExtraida]


class Transcripcion(BaseModel):
    paginas: list[str] = Field(description="Texto de cada página, en orden, transcrito literalmente")


class VotoCriterio(BaseModel):
    valor: bool
    justificacion: str = Field(description="Una oración")


class VotoRubrica(BaseModel):
    meta: VotoCriterio
    plazo: VotoCriterio
    financiamiento: VotoCriterio
    competencia_municipal: VotoCriterio


class EnfoquePropuesto(BaseModel):
    id: str = Field(description="slug en minúsculas con guiones")
    nombre: str = Field(description="Máx. 4 palabras")
    descripcion: str = Field(description="Máx. 120 caracteres")
    icono: str


class Asignacion(BaseModel):
    propuesta_id: str
    enfoques: list[str]


class Agrupacion(BaseModel):
    enfoques: list[EnfoquePropuesto] = Field(description="Entre 2 y 4 enfoques")
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
