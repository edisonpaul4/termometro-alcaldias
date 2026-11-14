"""IA simulada: respuestas plausibles, determinísticas y sin costo, para probar el pipeline.

Usa heurísticas simples sobre el texto real (verbos de acción, cifras, años, montos), así que
también sirve para ensayar el pipeline con PDFs reales. NADA de lo que produce se publica:
la exportación marca todo con es_mock=true y el build de producción lo bloquea.
"""

from __future__ import annotations

import hashlib
import re

from pydantic import BaseModel

from .esquemas import (
    Agrupacion,
    Asignacion,
    AuditoriaNeutralidad,
    EnfoquePropuesto,
    Extraccion,
    Observacion,
    PropuestaExtraida,
    Transcripcion,
    VotoCriterio,
    VotoRubrica,
    VotosLote,
    EvaluacionPropuesta,
)
from .llm import Solicitud
from .modelos import Proveedor

VERBOS = r"(implementar|construir|crear|ampliar|instalar|impulsar|fortalecer|promover|mejorar|garantizar|dotar|rehabilitar|recuperar|incrementar|desarrollar|establecer|ejecutar|reducir|regularizar|entregar|contratar|habilitar|repotenciar|modernizar|implementaremos|construiremos|crearemos|ampliaremos|instalaremos)"

PALABRAS_TEMA = {
    "seguridad": r"segur|delincu|polic|vigilanc|cámara|alarma|crimen|violencia",
    "movilidad": r"movilidad|tránsito|transporte|bus|metro|trole|vial|vía|ciclo|semáfor|peat",
    "agua-servicios": r"agua|alcantarill|potable|saneamiento|servicios básicos",
    "ambiente": r"basura|residuo|recicl|ambient|verde|arbol|contamina|relleno",
    "empleo": r"empleo|emprend|econom|producti|negocio|inversi|trabajo",
    "espacio-publico": r"espacio público|comercio|mercado|plaza|vendedor|autónom",
    "riesgos": r"riesgo|quebrada|deslave|incendio|emergencia|bomber|lluvia",
    "rural": r"rural|parroquia|campesin|agrícol|agricult",
    "transparencia": r"transparen|corrupci|rendición|participaci|contrataci|datos abiertos",
    "inclusion": r"inclusi|discapacid|adulto mayor|niñ|mujer|salud|vulnerable",
    "cultura": r"cultur|turis|patrimon|deporte|centro histórico|arte",
    "vivienda": r"vivienda|barrio|legaliz|escritur|territori|suelo|urban",
}

ICONOS_POR_TEMA = {
    "seguridad": ["security-camera", "lightbulb", "police-car"],
    "movilidad": ["bus", "road-horizon", "bicycle"],
    "agua-servicios": ["pipe", "drop", "tree-evergreen"],
    "ambiente": ["recycle", "truck", "tree"],
    "empleo": ["rocket-launch", "buildings", "handshake"],
    "espacio-publico": ["squares-four", "basket", "storefront"],
    "riesgos": ["cloud-rain", "fire-truck", "mountains"],
    "rural": ["path", "grains", "plant"],
    "transparencia": ["chart-bar", "users-three", "eye"],
    "inclusion": ["baby", "first-aid-kit", "hand-heart"],
    "cultura": ["church", "confetti", "mask-happy"],
    "vivienda": ["house", "scroll", "house-line"],
}

CITA_INVENTADA = "Construiremos un teleférico submarino de 90 kilómetros entre el Panecillo y la Luna en 2027."


def _azar(*partes: str) -> float:
    """Número en [0,1) determinístico a partir de un texto."""
    return int(hashlib.sha256("|".join(partes).encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


def _tema(texto: str) -> str | None:
    t = texto.lower()
    mejores = sorted(((len(re.findall(p, t)), tema) for tema, p in PALABRAS_TEMA.items()), reverse=True)
    return mejores[0][1] if mejores[0][0] else None


def _oraciones(pagina: str) -> list[str]:
    plano = " ".join(pagina.split())
    return [s.strip() for s in re.split(r"(?<=[.;:])\s+|\s•\s|\s-\s", plano) if 50 <= len(s.strip()) <= 300]


class MockIA:
    def __init__(self, proveedor: Proveedor, modelo: str):
        self.proveedor = proveedor
        self.modelo = modelo

    def generar(self, sol: Solicitud) -> BaseModel:
        return getattr(self, f"_{sol.paso}")(sol)

    # [1] extracción: oraciones con verbo de acción y tema reconocible
    def _extraccion(self, sol: Solicitud) -> Extraccion:
        paginas: list[str] = sol.extra["paginas"]
        props: list[PropuestaExtraida] = []
        vistos: set[str] = set()
        for n, pag in enumerate(paginas, start=1):
            for s in _oraciones(pag):
                if not re.search(VERBOS, s, re.I) or s in vistos:
                    continue
                tema = _tema(s)
                if not tema:
                    continue
                vistos.add(s)
                props.append(PropuestaExtraida(tema=tema, resumen=s[:200], cita=s, pagina=n, contexto=[]))
                if len(props) >= 40:
                    break
        # Una cita inventada a propósito: el verificador DEBE descartarla
        props.append(PropuestaExtraida(tema="movilidad", resumen="Teleférico submarino (mock, inventada)", cita=CITA_INVENTADA, pagina=1, contexto=[]))
        return Extraccion(propuestas=props)

    def _transcripcion(self, sol: Solicitud) -> Transcripcion:
        return Transcripcion(paginas=sol.extra.get("paginas", []))

    # [3] cobertura: el mock no encuentra faltantes
    def _cobertura(self, sol: Solicitud) -> Extraccion:
        return Extraccion(propuestas=[])

    # [4] jurado: heurísticas + algo de desacuerdo y fallas controladas entre jurados
    def _jurado(self, sol: Solicitud) -> VotoRubrica:
        cita: str = sol.extra["cita"].lower()
        verdad = {
            "meta": bool(re.search(r"\d", cita)),
            "plazo": bool(re.search(r"\b20[2-3]\d\b|\bdías\b|\bmeses\b|primer año|primeros", cita)),
            "financiamiento": bool(re.search(r"\$|usd|dólares|crédito|financ|presupuesto|\bbid\b|\bcaf\b|alianza público", cita)),
            "competencia_municipal": not re.search(r"policía nacional|código penal|\biva\b|fuerzas armadas|ministerio de", cita),
        }
        votos = {}
        for crit, v in verdad.items():
            r = _azar(self.modelo, crit, cita)
            if r < 0.03:
                raise RuntimeError("mock: respuesta inválida simulada")
            votos[crit] = VotoCriterio(valor=(not v) if r < 0.12 else v, justificacion=f"[MOCK] {'Sí' if v else 'No'} según heurística.")
        return VotoRubrica(**votos)

    def _jurado_lote(self, sol: Solicitud) -> VotosLote:
        evals = []
        for n, cita in enumerate(sol.extra["citas"], start=1):
            try:
                vr = self._jurado(Solicitud("jurado", "", "", VotoRubrica, extra={"cita": cita}))
            except RuntimeError:
                continue  # el mock "olvida" esta propuesta: se reintenta en la próxima corrida
            evals.append(EvaluacionPropuesta(numero=n, **vr.model_dump()))
        return VotosLote(evaluaciones=evals)

    # [6] enfoques: catálogo fijo por tema, asignación por palabras
    def _enfoques(self, sol: Solicitud) -> Agrupacion:
        tema: str = sol.extra["tema"]
        iconos = ICONOS_POR_TEMA.get(tema, ["sparkle", "target", "lightbulb"])
        enfoques = [
            EnfoquePropuesto(id=f"{tema}-enfoque-{i + 1}", nombre=f"Enfoque {i + 1} (mock)", descripcion="[MOCK] Agrupación simulada.", icono=ic)
            for i, ic in enumerate(iconos[:3])
        ]
        asign = [
            Asignacion(propuesta_id=pid, enfoques=[enfoques[int(_azar(pid) * len(enfoques))].id])
            for pid in sol.extra["propuestas"]
        ]
        return Agrupacion(enfoques=enfoques, asignaciones=asign)

    def _enfoques_validacion(self, sol: Solicitud) -> Agrupacion:
        return Agrupacion.model_validate(sol.extra["agrupacion"])

    # [7] neutralidad: marca adjetivos valorativos
    def _neutralidad(self, sol: Solicitud) -> AuditoriaNeutralidad:
        obs = [
            Observacion(propuesta_id=pid, problema="[MOCK] Adjetivo valorativo", sugerencia="Quitar el adjetivo.")
            for pid, resumen in sol.extra["resumenes"].items()
            if re.search(r"\b(histórico|ambicios|excelente|mejor|peor|nefast|corrupt)", resumen, re.I)
        ]
        return AuditoriaNeutralidad(observaciones=obs)
