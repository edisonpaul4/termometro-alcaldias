"""CLI del pipeline: `termometro <comando>`."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .datos import DIR_DATOS, ErrorDatos, cargar
from .modelos import DatosSitio


def cmd_validar(args) -> int:
    try:
        sitio = cargar(Path(args.datos), produccion=args.produccion)
    except ErrorDatos as e:
        print(f"✗ {e}", file=sys.stderr)
        return 1
    for cid, dc in sitio.datos.items():
        n_prop = sum(len(c.propuestas) for c in dc.candidatos)
        mock = " [MOCK]" if dc.ciudad.es_mock else ""
        print(f"✓ {cid}{mock}: {len(dc.candidatos)} candidatos, {n_prop} propuestas, {len(dc.enfoques)} enfoques")
    print(f"✓ {len(sitio.temas)} temas · modo {'producción' if args.produccion else 'desarrollo'}")
    return 0


def cmd_schema(args) -> int:
    schema = _sin_titulos_de_campo(DatosSitio.model_json_schema(mode="serialization"))
    salida = Path(args.out)
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✓ schema escrito en {salida}")
    return 0


def _sin_titulos_de_campo(nodo):
    """Quita los `title` de las propiedades (no de los modelos) para que json2ts no
    genere un alias por campo (Id1, Nombre2...). Los modelos conservan su título."""
    if isinstance(nodo, dict):
        if "properties" in nodo:
            nodo["properties"] = {
                k: {kk: _sin_titulos_de_campo(vv) for kk, vv in v.items() if kk != "title"}
                for k, v in nodo["properties"].items()
            }
        return {k: (_sin_titulos_de_campo(v) if k != "properties" else v) for k, v in nodo.items()}
    if isinstance(nodo, list):
        return [_sin_titulos_de_campo(x) for x in nodo]
    return nodo


def cmd_exportar(args) -> int:
    """Exporta todo `datos/` validado como un único JSON para la web."""
    try:
        sitio = cargar(Path(args.datos), produccion=args.produccion)
    except ErrorDatos as e:
        print(f"✗ {e}", file=sys.stderr)
        return 1
    salida = Path(args.out)
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(sitio.model_dump_json(indent=1), encoding="utf-8")
    print(f"✓ datos exportados en {salida}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="termometro", description="Pipeline del Termómetro de Alcaldías")
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validar", help="Valida datos/ contra el contrato")
    v.add_argument("--datos", default=str(DIR_DATOS))
    v.add_argument("--produccion", action="store_true", help="Aplica reglas de publicación (sin mocks, lista verificada)")
    v.set_defaults(func=cmd_validar)

    s = sub.add_parser("schema", help="Exporta el JSON Schema del contrato")
    s.add_argument("--out", required=True)
    s.set_defaults(func=cmd_schema)

    e = sub.add_parser("exportar", help="Exporta datos/ validado como JSON para la web")
    e.add_argument("--datos", default=str(DIR_DATOS))
    e.add_argument("--out", required=True)
    e.add_argument("--produccion", action="store_true")
    e.set_defaults(func=cmd_exportar)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
