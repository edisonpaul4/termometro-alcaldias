"""La ciudad demo debe ser válida, determinística y 100% ficticia."""

import shutil

import pytest

from termometro import demo
from termometro.datos import DIR_DATOS, ErrorDatos, cargar

# Apellidos/organizaciones reales que JAMÁS deben aparecer en datos mock.
NOMBRES_REALES = [
    "almeida", "muñoz", "munoz", "jijón", "jijon", "díaz", "diaz", "romero", "burbano", "yunda",
    "desamblanc", "larrea", "merino", "pabel", "sociedad patriótica", "social cristiano", "creo",
    "avanza", "imparables", "adn", "centro democrático", "alianza ciudadana", "revolución ciudadana",
]


@pytest.fixture
def datos_demo(tmp_path):
    d = tmp_path / "datos"
    shutil.copytree(DIR_DATOS, d)
    shutil.rmtree(d / "ciudades" / "demo", ignore_errors=True)
    demo.generar(d, cargar(DIR_DATOS).temas)
    return d


def test_demo_valida(datos_demo):
    sitio = cargar(datos_demo)
    dc = sitio.datos["demo"]
    assert dc.ciudad.es_mock
    assert all(c.es_mock for c in dc.candidatos)
    assert len(dc.candidatos) == len(demo.PERFILES)


def test_demo_es_deterministica(datos_demo, tmp_path):
    otra = tmp_path / "otra"
    shutil.copytree(datos_demo, otra)
    demo.generar(otra, cargar(otra).temas)
    for a in (datos_demo / "ciudades/demo").rglob("*.yaml"):
        b = otra / a.relative_to(datos_demo)
        assert a.read_text() == b.read_text(), a.name


def test_demo_no_contiene_nombres_reales(datos_demo):
    import re

    for f in (datos_demo / "ciudades/demo").rglob("*.yaml"):
        texto = f.read_text(encoding="utf-8").lower()
        for nombre in NOMBRES_REALES:
            assert not re.search(rf"\b{re.escape(nombre)}\b", texto), f"'{nombre}' aparece en {f.name}"


def test_demo_bloqueada_en_produccion(datos_demo):
    with pytest.raises(ErrorDatos, match="'demo' contiene datos mock"):
        cargar(datos_demo, produccion=True)


def test_demo_cubre_los_casos_de_ui(datos_demo):
    dc = cargar(datos_demo).datos["demo"]
    votos = [
        calif
        for c in dc.candidatos
        for p in c.propuestas
        for calif in (p.rubrica.meta, p.rubrica.plazo, p.rubrica.financiamiento, p.rubrica.competencia_municipal)
    ]
    consensos = {v.consenso for v in votos}
    assert consensos == {"unanime", "mayoria", "humano"}
    assert any(voto.valor is None for v in votos for voto in v.votos), "falta un jurado caído"
    assert any(not c.plan_trabajo.disponible for c in dc.candidatos), "falta un candidato sin plan"
    assert any(not p.rubrica.competencia_municipal.valor for c in dc.candidatos for p in c.propuestas)
