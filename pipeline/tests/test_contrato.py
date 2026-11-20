"""Tests del contrato de datos: modelos + carga con referencias cruzadas."""

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from termometro.datos import ErrorDatos, cargar
from termometro.modelos import Calificacion, Consenso


def voto(valor, proveedor="mock"):
    return {"proveedor": proveedor, "modelo": "mock-1", "valor": valor, "justificacion": "x"}


def calif(valor=True, consenso="unanime", votos=(True, True, True), **kw):
    return {"valor": valor, "consenso": consenso, "votos": [voto(v) for v in votos], **kw}


def rubrica():
    return {c: calif() for c in ("meta", "plazo", "financiamiento", "competencia_municipal")}


def propuesta(**kw):
    base = {
        "id": "p1",
        "tema": "seguridad",
        "resumen": "Instalar 100 cámaras",
        "cita": "instalaremos 100 cámaras de videovigilancia",
        "pagina": 2,
        "cita_verificada": True,
        "enfoques": ["tecnologia"],
        "rubrica": rubrica(),
    }
    return base | kw


def candidato(**kw):
    base = {
        "id": "candidata-a",
        "nombre": "Candidata A",
        "lista": "1",
        "organizacion": "Movimiento Demo",
        "plan_trabajo": {
            "disponible": True,
            "paginas": 10,
            "fuente": {"url": "https://example.org/plan.pdf", "titulo": "Plan", "consultado": "2026-11-14"},
        },
        "propuestas": [propuesta()],
        "es_mock": True,
    }
    return base | kw


def escribir_datos(raiz: Path, *, cand=None, ciudad_extra=None, enfoques=None) -> Path:
    d = raiz / "datos"
    (d / "ciudades/demo/candidatos").mkdir(parents=True)
    w = lambda p, o: (d / p).write_text(yaml.safe_dump(o, allow_unicode=True), encoding="utf-8")  # noqa: E731
    w("temas.yaml", [{"id": "seguridad", "nombre": "Seguridad", "nombre_corto": "Seguridad", "icono": "shield-check", "descripcion": "x"}])
    w("ciudades.yaml", [{"id": "demo", "nombre": "Demo", "nombre_oficial": "Ciudad Demo", "activa": True}])
    w(
        "ciudades/demo/ciudad.yaml",
        {"id": "demo", "nombre": "Demo", "eleccion": "2026-11-29", "fin_campana": "2026-11-26",
         "candidatos_verificados": True, "es_mock": True} | (ciudad_extra or {}),
    )
    w("ciudades/demo/enfoques.yaml", {"enfoques": enfoques if enfoques is not None else [
        {"id": "tecnologia", "tema": "seguridad", "nombre": "Tecnología", "descripcion": "x", "icono": "security-camera"}]})
    c = cand or candidato()
    w(f"ciudades/demo/candidatos/{c['id']}.yaml", c)
    return d


# ─── Calificación / consenso ────────────────────────────────────────────────

class TestConsenso:
    def test_unanime_valido(self):
        assert Calificacion.model_validate(calif()).consenso == Consenso.unanime

    def test_mayoria_valida(self):
        Calificacion.model_validate(calif(consenso="mayoria", votos=(True, True, False)))

    def test_valor_contra_la_mayoria_falla(self):
        with pytest.raises(ValidationError, match="mayoría"):
            Calificacion.model_validate(calif(valor=False, consenso="mayoria", votos=(True, True, False)))

    def test_unanime_con_desacuerdo_falla(self):
        with pytest.raises(ValidationError, match="unanime"):
            Calificacion.model_validate(calif(votos=(True, True, False)))

    def test_mayoria_cuando_es_unanime_falla(self):
        with pytest.raises(ValidationError, match="unanime"):
            Calificacion.model_validate(calif(consenso="mayoria"))

    def test_jurado_caido_con_dos_coincidentes_es_mayoria(self):
        Calificacion.model_validate(calif(consenso="mayoria", votos=(True, True, None)))
        with pytest.raises(ValidationError):
            Calificacion.model_validate(calif(consenso="unanime", votos=(True, True, None)))

    def test_empate_requiere_humano(self):
        with pytest.raises(ValidationError, match="empate"):
            Calificacion.model_validate(calif(consenso="mayoria", votos=(True, False, None)))
        Calificacion.model_validate(calif(consenso="humano", votos=(True, False, None), nota_revision="revisado"))

    def test_humano_requiere_nota(self):
        with pytest.raises(ValidationError, match="nota_revision"):
            Calificacion.model_validate(calif(consenso="humano"))

    def test_revision_ia_resuelve_empate_con_nota(self):
        c = Calificacion.model_validate(calif(valor=False, consenso="revision_ia", votos=(True, False), nota_revision="La cita no fija una fecha."))
        assert c.consenso == Consenso.revision_ia
        assert [v.valor for v in c.votos] == [True, False]

    def test_revision_ia_requiere_nota_y_empate(self):
        with pytest.raises(ValidationError, match="nota_revision"):
            Calificacion.model_validate(calif(consenso="revision_ia", votos=(True, False)))
        with pytest.raises(ValidationError, match="empate"):
            Calificacion.model_validate(calif(consenso="revision_ia", votos=(True, True), nota_revision="Revisado"))


# ─── Carga de datos/ ────────────────────────────────────────────────────────

class TestCarga:
    def test_datos_validos(self, tmp_path):
        sitio = cargar(escribir_datos(tmp_path))
        assert sitio.datos["demo"].candidatos[0].propuestas[0].id == "p1"

    def test_tema_inexistente(self, tmp_path):
        d = escribir_datos(tmp_path, cand=candidato(propuestas=[propuesta(tema="futbol", enfoques=[])]))
        with pytest.raises(ErrorDatos, match="tema inexistente 'futbol'"):
            cargar(d)

    def test_enfoque_de_otro_tema(self, tmp_path):
        enf = [{"id": "tecnologia", "tema": "seguridad", "nombre": "T", "descripcion": "x", "icono": "security-camera"},
               {"id": "metro", "tema": "seguridad", "nombre": "M", "descripcion": "x", "icono": "bus"}]
        d = escribir_datos(tmp_path, enfoques=enf, cand=candidato(propuestas=[propuesta(enfoques=["inventado"])]))
        with pytest.raises(ErrorDatos, match="enfoque inexistente 'inventado'"):
            cargar(d)

    def test_cita_no_verificada_no_se_publica(self, tmp_path):
        d = escribir_datos(tmp_path, cand=candidato(propuestas=[propuesta(cita_verificada=False)]))
        with pytest.raises(ErrorDatos, match="cita no verificada"):
            cargar(d)

    def test_pagina_fuera_del_plan(self, tmp_path):
        d = escribir_datos(tmp_path, cand=candidato(propuestas=[propuesta(pagina=99)]))
        with pytest.raises(ErrorDatos, match="página fuera del plan"):
            cargar(d)

    def test_id_distinto_al_archivo(self, tmp_path):
        d = escribir_datos(tmp_path)
        (d / "ciudades/demo/candidatos/candidata-a.yaml").rename(d / "ciudades/demo/candidatos/otro.yaml")
        with pytest.raises(ErrorDatos, match="no coincide con el nombre del archivo"):
            cargar(d)

    def test_campo_desconocido_rechazado(self, tmp_path):
        d = escribir_datos(tmp_path, cand=candidato(apodo="X"))
        with pytest.raises(ErrorDatos, match="apodo"):
            cargar(d)

    def test_acumula_varios_errores(self, tmp_path):
        d = escribir_datos(tmp_path, cand=candidato(propuestas=[propuesta(tema="futbol", cita_verificada=False)]))
        with pytest.raises(ErrorDatos) as e:
            cargar(d)
        assert len(e.value.errores) >= 2


class TestProduccion:
    def test_mock_bloquea_produccion(self, tmp_path):
        d = escribir_datos(tmp_path)
        cargar(d)  # en desarrollo pasa
        with pytest.raises(ErrorDatos, match="contiene datos mock"):
            cargar(d, produccion=True)

    def test_lista_no_verificada_bloquea_produccion(self, tmp_path):
        d = escribir_datos(tmp_path, ciudad_extra={"es_mock": False, "candidatos_verificados": False},
                           cand=candidato(es_mock=False))
        with pytest.raises(ErrorDatos, match="no tiene la lista de candidatos verificada"):
            cargar(d, produccion=True)

    def test_datos_reales_verificados_pasan(self, tmp_path):
        d = escribir_datos(tmp_path, ciudad_extra={"es_mock": False}, cand=candidato(es_mock=False))
        cargar(d, produccion=True)


def test_datos_del_repo_validan_en_desarrollo():
    """El contenido real de datos/ siempre debe validar (en modo desarrollo)."""
    cargar()
