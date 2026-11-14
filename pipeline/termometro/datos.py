"""Carga y validación de `datos/` (schema + referencias cruzadas + reglas de producción)."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import TypeAdapter, ValidationError

from .modelos import (
    Candidato,
    Ciudad,
    CiudadRegistro,
    DatosCiudad,
    DatosSitio,
    Enfoques,
    Tema,
)

RAIZ_REPO = Path(__file__).resolve().parents[2]
DIR_DATOS = RAIZ_REPO / "datos"


class ErrorDatos(Exception):
    def __init__(self, errores: list[str]):
        self.errores = errores
        super().__init__(f"{len(errores)} error(es) en datos:\n" + "\n".join(f"  • {e}" for e in errores))


def _leer(ruta: Path):
    with ruta.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def _rel(ruta: Path) -> str:
    try:
        return str(ruta.relative_to(RAIZ_REPO))
    except ValueError:
        return str(ruta)


def cargar(dir_datos: Path = DIR_DATOS, *, produccion: bool = False) -> DatosSitio:
    """Carga todo `datos/`. Acumula todos los errores y los lanza juntos en ErrorDatos.

    produccion=True agrega las reglas de publicación:
      - una ciudad activa no puede tener datos mock
      - una ciudad activa debe tener la lista de candidatos verificada
    """
    errores: list[str] = []

    def validar(modelo, ruta: Path):
        try:
            return TypeAdapter(modelo).validate_python(_leer(ruta))
        except FileNotFoundError:
            errores.append(f"{_rel(ruta)}: no existe")
        except ValidationError as e:
            for err in e.errors():
                loc = ".".join(str(x) for x in err["loc"])
                errores.append(f"{_rel(ruta)} [{loc}]: {err['msg']}")
        except yaml.YAMLError as e:
            errores.append(f"{_rel(ruta)}: YAML inválido ({e})")
        return None

    temas = validar(list[Tema], dir_datos / "temas.yaml") or []
    registro = validar(list[CiudadRegistro], dir_datos / "ciudades.yaml") or []
    ids_temas = {t.id for t in temas}

    datos: dict[str, DatosCiudad] = {}
    for reg in registro:
        dir_ciudad = dir_datos / "ciudades" / reg.id
        ciudad = validar(Ciudad, dir_ciudad / "ciudad.yaml")
        enf = validar(Enfoques, dir_ciudad / "enfoques.yaml")
        enfoques = enf.enfoques if enf else []
        candidatos: list[Candidato] = []
        for ruta in sorted((dir_ciudad / "candidatos").glob("*.yaml")):
            c = validar(Candidato, ruta)
            if c is None:
                continue
            if c.id != ruta.stem:
                errores.append(f"{_rel(ruta)}: el id '{c.id}' no coincide con el nombre del archivo")
            candidatos.append(c)

        if ciudad is None:
            continue
        if ciudad.id != reg.id:
            errores.append(f"ciudad '{reg.id}': ciudad.yaml tiene id '{ciudad.id}'")

        # Referencias cruzadas
        enfoque_tema = {e.id: e.tema for e in enfoques}
        for e in enfoques:
            if e.tema not in ids_temas:
                errores.append(f"{reg.id}/enfoques: '{e.id}' usa tema inexistente '{e.tema}'")
        for c in candidatos:
            for p in c.propuestas:
                donde = f"{reg.id}/{c.id}/{p.id}"
                if p.tema not in ids_temas:
                    errores.append(f"{donde}: tema inexistente '{p.tema}'")
                for eid in p.enfoques:
                    if eid not in enfoque_tema:
                        errores.append(f"{donde}: enfoque inexistente '{eid}'")
                    elif enfoque_tema[eid] != p.tema:
                        errores.append(f"{donde}: enfoque '{eid}' es del tema '{enfoque_tema[eid]}', no de '{p.tema}'")
                if not p.cita_verificada:
                    errores.append(f"{donde}: cita no verificada (no se puede publicar)")

        if produccion and reg.activa:
            if ciudad.es_mock or any(c.es_mock for c in candidatos):
                errores.append(f"PRODUCCIÓN: la ciudad activa '{reg.id}' contiene datos mock")
            if not ciudad.candidatos_verificados:
                errores.append(f"PRODUCCIÓN: la ciudad activa '{reg.id}' no tiene la lista de candidatos verificada")
            if not candidatos:
                errores.append(f"PRODUCCIÓN: la ciudad activa '{reg.id}' no tiene candidatos")

        datos[reg.id] = DatosCiudad(ciudad=ciudad, enfoques=enfoques, candidatos=candidatos)

    if produccion and not any(r.activa for r in registro):
        errores.append("PRODUCCIÓN: no hay ninguna ciudad activa")

    if errores:
        raise ErrorDatos(errores)
    return DatosSitio(temas=temas, ciudades=registro, datos=datos)
