"""Generador de la ciudad ficticia `demo` para desarrollar la web sin datos reales.

REGLA: aquí NUNCA aparecen nombres de candidatos u organizaciones reales.
Todo va marcado con es_mock=true y el build de producción lo rechaza.

Los perfiles están pensados para ejercitar la UI:
  A  muy concreta (termómetro alto), cubre todos los temas
  B  vaga (termómetro bajo), muchas propuestas
  C  varias promesas fuera de la competencia municipal
  D  concreto pero cubre pocos temas
  E/F casi idénticos → prueba el "empate técnico"
  G  plan de trabajo no disponible, sin propuestas
Además: votos 3/3, 2/3, un jurado caído y casos resueltos por humano.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

from .modelos import (
    Calificacion,
    Candidato,
    Ciudad,
    Consenso,
    Enfoque,
    Enfoques,
    Fuente,
    PlanTrabajo,
    Propuesta,
    Proveedor,
    Rubrica,
    Tema,
    Trayectoria,
    VotoJurado,
)

SEMILLA = 2026
HOY = date(2026, 11, 14)
PAGINAS_PLAN = 40
FUENTE_DEMO = "https://example.org/demo"

# (id, tema, nombre, icono, descripción, verbo, objeto, unidad)
ENFOQUES: list[tuple[str, str, str, str, str, str, str, str]] = [
    ("seg-tecnologia", "seguridad", "Tecnología y monitoreo", "📹", "Cámaras, alarmas comunitarias y centros de monitoreo.", "Instalar", "cámaras de videovigilancia conectadas al ECU 911", "cámaras"),
    ("seg-espacios", "seguridad", "Recuperar espacios", "💡", "Iluminación, parques y espacios públicos seguros.", "Instalar", "luminarias LED en barrios", "luminarias"),
    ("seg-control", "seguridad", "Más agentes de control", "👮", "Más agentes metropolitanos y patrullaje.", "Contratar", "agentes metropolitanos de control", "agentes"),
    ("mov-transporte", "movilidad", "Transporte público", "🚌", "Más buses, mejores frecuencias e integración con el Metro.", "Incorporar", "buses eléctricos al sistema municipal", "buses"),
    ("mov-vias", "movilidad", "Vías y tránsito", "🛣️", "Mantenimiento vial, semaforización y obras viales.", "Repavimentar", "kilómetros de vías principales", "km"),
    ("mov-activa", "movilidad", "Bici y peatones", "🚲", "Ciclovías, veredas y movilidad activa.", "Construir", "kilómetros de ciclovías conectadas", "km"),
    ("agua-cobertura", "agua-servicios", "Ampliar cobertura", "🚰", "Llevar agua y alcantarillado a barrios sin servicio.", "Conectar", "hogares a la red de agua potable", "hogares"),
    ("agua-fuentes", "agua-servicios", "Nuevas fuentes de agua", "🏞️", "Proteger páramos y asegurar agua a futuro.", "Proteger", "hectáreas de páramo en zonas de captación", "hectáreas"),
    ("amb-reciclaje", "ambiente", "Reciclaje", "♻️", "Separación en la fuente y gestores de reciclaje.", "Construir", "centros de acopio de reciclaje", "centros"),
    ("amb-recoleccion", "ambiente", "Recolección eficiente", "🚛", "Más frecuencias y contenedores.", "Instalar", "contenedores soterrados", "contenedores"),
    ("emp-emprendimiento", "empleo", "Emprendimiento", "🚀", "Créditos, capacitación y ferias para emprendedores.", "Entregar", "créditos semilla a emprendedores", "créditos"),
    ("emp-inversion", "empleo", "Atraer inversión", "🏗️", "Simplificar trámites y atraer empresas.", "Reducir a", "días el trámite de licencia de funcionamiento", "días"),
    ("esp-ordenar", "espacio-publico", "Ordenar el comercio", "🗂️", "Regular y reubicar el comercio autónomo.", "Reubicar", "comerciantes autónomos en plataformas comerciales", "comerciantes"),
    ("esp-mercados", "espacio-publico", "Mercados renovados", "🏪", "Rehabilitar mercados municipales.", "Rehabilitar", "mercados municipales", "mercados"),
    ("rie-prevencion", "riesgos", "Prevención", "🌧️", "Limpieza de quebradas, alertas tempranas y obras de mitigación.", "Intervenir", "quebradas con obras de mitigación", "quebradas"),
    ("rie-respuesta", "riesgos", "Respuesta a emergencias", "🚒", "Bomberos y equipamiento de emergencia.", "Equipar", "estaciones de bomberos", "estaciones"),
    ("rur-vialidad", "rural", "Vías rurales", "🛤️", "Caminos y conectividad en parroquias rurales.", "Asfaltar", "kilómetros de vías en parroquias rurales", "km"),
    ("rur-produccion", "rural", "Producción rural", "🌽", "Apoyo a agricultores y circuitos cortos.", "Crear", "ferias de productores rurales", "ferias"),
    ("tra-datos", "transparencia", "Datos abiertos", "📊", "Publicar contratos y gastos en línea.", "Publicar", "% de los contratos municipales en datos abiertos", "%"),
    ("tra-participacion", "transparencia", "Participación ciudadana", "🗳️", "Presupuestos participativos y rendición de cuentas.", "Asignar", "% del presupuesto de inversión a presupuestos participativos", "%"),
    ("inc-cuidado", "inclusion", "Centros de cuidado", "🧸", "Guarderías y centros para adultos mayores.", "Abrir", "centros de cuidado infantil", "centros"),
    ("inc-salud", "inclusion", "Salud municipal", "🏥", "Unidades de salud y atención en barrios.", "Construir", "unidades de salud municipales", "unidades"),
    ("cul-centro", "cultura", "Centro Histórico", "⛪", "Revitalizar el Centro Histórico.", "Rehabilitar", "inmuebles patrimoniales del Centro Histórico", "inmuebles"),
    ("cul-eventos", "cultura", "Cultura y deporte en barrios", "🎭", "Eventos culturales y canchas en barrios.", "Organizar", "festivales culturales barriales al año", "festivales"),
    ("viv-social", "vivienda", "Vivienda social", "🏠", "Vivienda asequible en zonas con servicios.", "Construir", "viviendas de interés social", "viviendas"),
    ("viv-legalizar", "vivienda", "Legalizar barrios", "📜", "Regularizar barrios y entregar escrituras.", "Entregar", "escrituras en barrios regularizados", "escrituras"),
]

# Promesas fuera de competencia municipal (para el perfil C y algún caso suelto)
FUERA_DE_COMPETENCIA = [
    ("seguridad", "seg-control", "Duplicar el número de policías nacionales en la ciudad"),
    ("empleo", "emp-inversion", "Reducir el IVA para los comercios de la ciudad"),
    ("inclusion", "inc-salud", "Contratar médicos para los hospitales del Ministerio de Salud"),
    ("seguridad", "seg-control", "Reformar el Código Penal para endurecer las penas por robo"),
]

PLAZOS = ["en los primeros 100 días", "hasta diciembre de 2027", "en el primer año de gestión", "hasta 2029"]
FINANCIAMIENTO = [
    "con un crédito del BID", "reasignando el 5% del gasto corriente", "mediante una alianza público-privada",
    "con un fondo de USD 12 millones del presupuesto de inversión",
]
VAGOS = ["Impulsar", "Fortalecer", "Promover", "Mejorar"]

JURADO = [(Proveedor.mock, "mock-extractor"), (Proveedor.mock, "mock-jurado-b"), (Proveedor.mock, "mock-jurado-c")]


@dataclass
class Perfil:
    slug: str
    nombre: str
    lista: str
    organizacion: str
    p_meta: float
    p_plazo: float
    p_financiamiento: float
    temas: list[str] | None  # None = todos
    propuestas_por_tema: tuple[int, int]
    fuera_competencia: int = 0
    plan_disponible: bool = True


PERFILES = [
    Perfil("candidata-a", "Candidata A (demo)", "D1", "Movimiento Ficticio Uno", 0.9, 0.8, 0.7, None, (2, 3)),
    Perfil("candidato-b", "Candidato B (demo)", "D2", "Partido Ficticio Dos", 0.15, 0.1, 0.05, None, (3, 4)),
    Perfil("candidata-c", "Candidata C (demo)", "D3", "Alianza Ficticia Tres", 0.5, 0.4, 0.3, None, (1, 2), fuera_competencia=4),
    Perfil("candidato-d", "Candidato D (demo)", "D4", "Movimiento Ficticio Cuatro", 0.85, 0.85, 0.6,
           ["movilidad", "agua-servicios", "ambiente", "rural", "transparencia"], (2, 3)),
    Perfil("candidata-e", "Candidata E (demo)", "D5", "Partido Ficticio Cinco", 0.6, 0.5, 0.4, None, (2, 2)),
    Perfil("candidato-f", "Candidato F (demo)", "D6", "Partido Ficticio Seis", 0.6, 0.5, 0.4, None, (2, 2)),
    Perfil("candidata-g", "Candidata G (demo)", "D7", "Movimiento Ficticio Siete", 0, 0, 0, [], (0, 0), plan_disponible=False),
]


def _fuente(titulo: str) -> Fuente:
    return Fuente(url=FUENTE_DEMO, titulo=f"[DEMO] {titulo}", consultado=HOY)


class _Jurado:
    """Genera votos coherentes con el valor verdadero, con algo de desacuerdo controlado."""

    def __init__(self, rng: random.Random):
        self.rng = rng

    def calificar(self, verdad: bool) -> Calificacion:
        r = self.rng.random()
        if r < 0.75:  # unánime
            valores = [verdad] * 3
            return self._calif(verdad, Consenso.unanime, valores)
        if r < 0.90:  # 2 de 3, un disidente
            valores = [verdad, verdad, not verdad]
            self.rng.shuffle(valores)
            return self._calif(verdad, Consenso.mayoria, valores)
        if r < 0.96:  # un jurado caído, los otros dos coinciden
            valores = [verdad, verdad, None]
            self.rng.shuffle(valores)
            return self._calif(verdad, Consenso.mayoria, valores)
        # empate (1 a favor, 1 en contra, 1 caído) → resuelto por humano
        valores = [True, False, None]
        self.rng.shuffle(valores)
        return self._calif(verdad, Consenso.humano, valores, nota="[DEMO] Revisado: el texto no especifica el dato.")

    def _calif(self, valor, consenso, valores, nota=None) -> Calificacion:
        votos = [
            VotoJurado(
                proveedor=prov, modelo=mod, valor=v,
                justificacion=None if v is None else f"[DEMO] Justificación simulada ({'sí' if v else 'no'}).",
            )
            for (prov, mod), v in zip(JURADO, valores)
        ]
        return Calificacion(valor=valor, consenso=consenso, votos=votos, nota_revision=nota)


def _texto(rng, verbo, objeto, unidad, meta, plazo, fin) -> tuple[str, str]:
    """Devuelve (resumen, cita) coherentes con los criterios que cumple."""
    if meta:
        n = rng.choice([3, 5, 10, 20, 50, 100, 300, 500, 1000, 5000]) if unidad != "%" else rng.choice([20, 50, 100])
        base = f"{verbo} {n}{'' if unidad == '%' else ' '}{objeto}"
    else:
        base = f"{rng.choice(VAGOS)} {objeto.split(' ', 1)[-1] if unidad == '%' else objeto}"
    partes = [base]
    if plazo:
        partes.append(rng.choice(PLAZOS))
    if fin:
        partes.append(rng.choice(FINANCIAMIENTO))
    resumen = ", ".join(partes)
    cita = f"[DEMO] Nos comprometemos a {resumen[0].lower()}{resumen[1:]}, como parte de nuestro plan para la ciudad."
    return resumen[:220], cita


def _propuestas(perfil: Perfil, temas: list[Tema], rng: random.Random) -> list[Propuesta]:
    if not perfil.plan_disponible:
        return []
    jurado = _Jurado(rng)
    ids_temas = perfil.temas if perfil.temas is not None else [t.id for t in temas]
    salida: list[Propuesta] = []

    def agregar(tema, enfoque_ids, resumen, cita, meta, plazo, fin, competencia):
        n = len(salida) + 1
        salida.append(Propuesta(
            id=f"{perfil.slug}-{n:02d}",
            tema=tema,
            resumen=resumen,
            cita=cita,
            pagina=rng.randint(3, PAGINAS_PLAN),
            cita_verificada=True,
            enfoques=enfoque_ids,
            rubrica=Rubrica(
                meta=jurado.calificar(meta),
                plazo=jurado.calificar(plazo),
                financiamiento=jurado.calificar(fin),
                competencia_municipal=jurado.calificar(competencia),
            ),
        ))

    for tema in ids_temas:
        enf_tema = [e for e in ENFOQUES if e[1] == tema]
        for _ in range(rng.randint(*perfil.propuestas_por_tema)):
            eid, _, _, _, _, verbo, objeto, unidad = rng.choice(enf_tema)
            meta = rng.random() < perfil.p_meta
            plazo = rng.random() < perfil.p_plazo
            fin = rng.random() < perfil.p_financiamiento
            resumen, cita = _texto(rng, verbo, objeto, unidad, meta, plazo, fin)
            agregar(tema, [eid], resumen, cita, meta, plazo, fin, True)

    for tema, eid, texto in FUERA_DE_COMPETENCIA[: perfil.fuera_competencia]:
        agregar(tema, [eid], texto, f"[DEMO] {texto}, porque la ciudad lo necesita.", False, False, False, False)
    return salida


def generar(dir_datos: Path, temas: list[Tema]) -> list[Path]:
    rng = random.Random(SEMILLA)
    dir_ciudad = dir_datos / "ciudades" / "demo"
    dir_cand = dir_ciudad / "candidatos"
    dir_cand.mkdir(parents=True, exist_ok=True)
    for viejo in dir_cand.glob("*.yaml"):
        viejo.unlink()

    escritos: list[Path] = []

    def escribir(ruta: Path, modelo, comentario: str):
        datos = modelo.model_dump(mode="json", exclude_defaults=True)
        texto = f"# {comentario}\n# GENERADO por `termometro demo` — no editar a mano.\n"
        texto += yaml.safe_dump(datos, allow_unicode=True, sort_keys=False, width=120)
        ruta.write_text(texto, encoding="utf-8")
        escritos.append(ruta)

    ciudad = Ciudad(
        id="demo", nombre="Ciudad Demo", eleccion=date(2026, 11, 29), debate=date(2026, 11, 22),
        fin_campana=date(2026, 11, 26), candidatos_verificados=True, es_mock=True,
    )
    escribir(dir_ciudad / "ciudad.yaml", ciudad, "Ciudad FICTICIA para desarrollo")

    enfoques = Enfoques(enfoques=[
        Enfoque(id=i, tema=t, nombre=n, icono=ic, descripcion=d) for i, t, n, ic, d, *_ in ENFOQUES
    ])
    escribir(dir_ciudad / "enfoques.yaml", enfoques, "Enfoques FICTICIOS")

    for perfil in PERFILES:
        plan = (
            PlanTrabajo(disponible=True, fuente=_fuente(f"Plan de trabajo {perfil.nombre}"), paginas=PAGINAS_PLAN)
            if perfil.plan_disponible
            else PlanTrabajo(disponible=False, nota="[DEMO] El plan de trabajo no está publicado en la fuente oficial.")
        )
        cand = Candidato(
            id=perfil.slug,
            nombre=perfil.nombre,
            lista=perfil.lista,
            organizacion=perfil.organizacion,
            trayectoria=[Trayectoria(cargo="[DEMO] Cargo ficticio", periodo="2019–2023", fuente=_fuente("Trayectoria"))],
            plan_trabajo=plan,
            propuestas=_propuestas(perfil, temas, rng),
            es_mock=True,
        )
        escribir(dir_cand / f"{perfil.slug}.yaml", cand, f"Candidato FICTICIO ({perfil.nombre})")
    return escritos
