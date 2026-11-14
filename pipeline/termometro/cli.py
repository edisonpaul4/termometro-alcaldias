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

    if args.fotos:
        import shutil

        from .datos import RAIZ_REPO

        dir_fotos = Path(args.fotos)
        shutil.rmtree(dir_fotos, ignore_errors=True)
        n = 0
        for cid, dc in sitio.datos.items():
            for c in dc.candidatos:
                if c.foto:
                    origen = RAIZ_REPO / c.foto
                    destino = dir_fotos / cid / f"{c.id}{origen.suffix}"
                    destino.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(origen, destino)
                    n += 1
        print(f"✓ {n} fotos copiadas a {dir_fotos}")
    return 0


def cmd_demo(args) -> int:
    """Regenera la ciudad ficticia `demo` (datos mock para desarrollar la web)."""
    import yaml
    from pydantic import TypeAdapter

    from . import demo
    from .modelos import Tema

    dir_datos = Path(args.datos)
    temas = TypeAdapter(list[Tema]).validate_python(yaml.safe_load((dir_datos / "temas.yaml").read_text("utf-8")))
    escritos = demo.generar(dir_datos, temas)
    print(f"✓ {len(escritos)} archivos de la ciudad demo generados")
    return 0


def cmd_pipeline(args) -> int:
    from .config import DIR_SALIDA, config
    from .pipeline import ejecutar

    cfg = config()
    print(f"▶ pipeline · ciudad={args.ciudad} · {cfg!r}")
    rep = ejecutar(args.ciudad, solo=args.solo or None, destino=Path(args.destino) if args.destino else None)
    v = sum(d["verificadas"] for d in rep.documentos.values())
    d = sum(d["descartadas"] for d in rep.documentos.values())
    print(f"✓ {len(rep.documentos)} documentos · {v} citas verificadas · {d} descartadas · {rep.exportadas} propuestas exportadas")
    print("  kappa: " + " · ".join(f"{k}={'—' if x is None else x}" for k, x in rep.kappa.items()))
    print(f"  cola de revisión humana: {len(rep.pendientes)} · observaciones de neutralidad: {len(rep.neutralidad)} · errores: {len(rep.errores)}")
    from .llm import GASTO

    print(f"  gasto: USD {GASTO.usd:.3f} · {GASTO.llamadas} llamadas · {GASTO.tokens_in:,} tokens entrada · {GASTO.tokens_out:,} salida")
    print("  caché:\n" + rep.cache)
    print(f"  reporte: {DIR_SALIDA / args.ciudad / 'reporte.md'}")
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
    e.add_argument("--fotos", help="Directorio donde copiar las fotos (fotos/<ciudad>/<id>.<ext>)")
    e.set_defaults(func=cmd_exportar)

    d = sub.add_parser("demo", help="Regenera la ciudad ficticia 'demo' (datos mock)")
    d.add_argument("--datos", default=str(DIR_DATOS))
    d.set_defaults(func=cmd_demo)

    pl = sub.add_parser("pipeline", help="Corre el pipeline multi-IA (incremental) para una ciudad")
    pl.add_argument("--ciudad", required=True)
    pl.add_argument("--solo", nargs="*", help="Procesar solo estos candidatos (ids)")
    pl.add_argument("--destino", help="Directorio datos/ de salida (por defecto: datos/ en modo real, pipeline/.salida/datos en mock)")
    pl.set_defaults(func=cmd_pipeline)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
