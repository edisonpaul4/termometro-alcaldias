"""End-to-end con IA simulada: PDF ficticio → pipeline → datos/ válidos → incremental → revisión humana."""

import shutil

import pytest
import yaml

from termometro.cache import Cache
from termometro.datos import DIR_DATOS, cargar
from termometro.llm import equipo
from termometro.mock_llm import CITA_INVENTADA
from termometro.pipeline import ejecutar, id_propuesta

from .pdf_ficticio import pdf_simple

PAGINAS = [
    ["Plan de trabajo 2027-2031", "Candidatura Ficticia Uno - Movimiento de Prueba"],
    [
        "EJE SEGURIDAD.",
        "Instalaremos 300 camaras de videovigilancia en los barrios del sur hasta 2028 con un credito del BID.",
        "Implementaremos alarmas comunitarias en cada barrio y fortaleceremos la vigilancia nocturna.",
    ],
    [
        "EJE MOVILIDAD.",
        "Ampliaremos la flota de buses electricos con 60 unidades nuevas en los primeros 100 dias.",
        "Construiremos 25 kilometros de ciclovias conectadas al transporte publico de la ciudad.",
        "Mejoraremos la semaforizacion de las vias principales para reducir el trafico.",
    ],
]


@pytest.fixture
def entorno(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_MODE", "mock")
    from termometro import config as cfg

    cfg.config.cache_clear()
    datos = tmp_path / "datos"
    datos.mkdir()
    for f in ("temas.yaml",):
        shutil.copy(DIR_DATOS / f, datos / f)
    (datos / "ciudades.yaml").write_text(yaml.safe_dump([{"id": "ficticia", "nombre": "Ficticia", "nombre_oficial": "Ficticia", "activa": True}]))
    dc = datos / "ciudades" / "ficticia"
    (dc / "candidatos").mkdir(parents=True)
    (dc / "ciudad.yaml").write_text(yaml.safe_dump({"id": "ficticia", "nombre": "Ficticia", "eleccion": "2026-11-29", "fin_campana": "2026-11-26", "candidatos_verificados": True, "es_mock": True}))
    (dc / "enfoques.yaml").write_text("enfoques: []\n")
    pdf = tmp_path / "plan.pdf"
    pdf.write_bytes(pdf_simple(PAGINAS))
    (dc / "candidatos" / "candidata-x.yaml").write_text(yaml.safe_dump({
        "id": "candidata-x", "nombre": "Candidata X", "lista": "99", "organizacion": "Movimiento de Prueba", "es_mock": True,
        "plan_trabajo": {"disponible": True, "paginas": 3, "fuente": {"url": "https://example.org", "titulo": "Plan", "consultado": "2026-11-14", "archivo": str(pdf)}},
    }))
    yield datos, tmp_path
    cfg.config.cache_clear()


def correr(datos, tmp_path, cache):
    return ejecutar("ficticia", dir_datos=datos, cache=cache, eq=equipo(), dir_salida=tmp_path / "salida")


def test_pipeline_completo(entorno):
    datos, tmp = entorno
    cache = Cache(tmp / "cache")
    rep = correr(datos, tmp, cache)

    # La cita inventada se descarta; las reales se verifican
    assert [p.cita for p in rep.descartadas] == [CITA_INVENTADA]
    assert rep.documentos["candidata-x"]["verificadas"] >= 4

    # La salida es un datos/ válido según el contrato
    sitio = cargar(datos)
    props = sitio.datos["ficticia"].candidatos[0].propuestas
    assert props and all(p.cita_verificada for p in props)
    assert sitio.datos["ficticia"].enfoques, "debió generar enfoques"
    assert (tmp / "salida" / "ficticia" / "reporte.md").exists()

    # Incremental: segunda corrida sin cambios = cero llamadas nuevas a la IA
    cache2 = Cache(tmp / "cache")
    correr(datos, tmp, cache2)
    assert cache2.stats.calculos == 0, cache2.stats.resumen()


def test_ids_estables_y_revision_humana(entorno):
    datos, tmp = entorno
    rep = correr(datos, tmp, Cache(tmp / "cache"))
    cita = "Construiremos 25 kilometros de ciclovias conectadas al transporte publico de la ciudad."
    pid = id_propuesta("candidata-x", cita)
    ids = {p.id for p in cargar(datos).datos["ficticia"].candidatos[0].propuestas} | set(rep.pendientes)
    assert pid in ids, "el id debe derivarse de la cita, estable entre corridas"

    # Un humano descarta una propuesta y resuelve un criterio
    (datos / "ciudades/ficticia/revision.yaml").write_text(yaml.safe_dump({"propuestas": {
        pid: {"descartar": True, "motivo": "prueba"},
    }}))
    correr(datos, tmp, Cache(tmp / "cache"))
    ids2 = {p.id for p in cargar(datos).datos["ficticia"].candidatos[0].propuestas}
    assert pid not in ids2


def test_produccion_rechaza_salida_mock(entorno):
    from termometro.datos import ErrorDatos

    datos, tmp = entorno
    correr(datos, tmp, Cache(tmp / "cache"))
    with pytest.raises(ErrorDatos, match="mock"):
        cargar(datos, produccion=True)
