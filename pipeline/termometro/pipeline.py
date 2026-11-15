"""Orquestador del pipeline multi-IA (PLAN.md §8). Incremental: cada llamada a la IA se cachea
por el hash de su entrada + versión del prompt + modelo; volver a correr solo procesa lo nuevo.

    [0] texto por página (pdftotext)          [0b] transcripción si es escaneado (Gemini)
    [1] extracción (Claude)                   [2] verificación de citas (sin IA)
    [3] auditoría de cobertura (Gemini)       [4] jurado a ciegas (Claude, GPT, Gemini)
    [5] consenso + kappa                      [6] enfoques (GPT propone, Claude valida)
    [7] auditoría de neutralidad (GPT)        [8] exportación + cola de revisión humana
"""

from __future__ import annotations

import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .cache import Cache, huella
from .resumenes import datos_sin_respaldo
from .citas import normalizar, verificar
from .config import DIR_SALIDA, config
from .consenso import consolidar, kappa_fleiss, resolver_humano
from .datos import DIR_DATOS, RAIZ_REPO, cargar
from .esquemas import (
    Agrupacion,
    AuditoriaNeutralidad,
    Extraccion,
    FragmentoContexto,
    PropuestaExtraida,
    PropuestaVerificada,
    ResultadoDocumento,
    Transcripcion,
    VotoRubrica,
    VotosLote,
)
from .llm import Equipo, PresupuestoAgotado, ProveedorIA, Solicitud, cargar_prompt, equipo, llamar
from .modelos import Calificacion, Candidato, ContextoCita, Criterio, Enfoque, Enfoques, Propuesta, Rubrica, Tema, VotoJurado
from .texto import texto_pdf

CRITERIOS = [c.value for c in Criterio]


# ─── Utilidades ─────────────────────────────────────────────────────────────


def id_propuesta(candidato: str, cita: str) -> str:
    """Estable entre corridas: mismo candidato + misma cita = mismo id."""
    return f"{candidato}-{huella(normalizar(cita))[:8]}"


def iconos_permitidos() -> set[str]:
    """Única fuente de verdad: el registro de íconos de la web."""
    ts = (RAIZ_REPO / "web/src/lib/iconos.ts").read_text(encoding="utf-8")
    bloque = ts.split("export const contenido", 1)[1].split("};", 1)[0]
    return set(re.findall(r"'([a-z0-9-]+)':", bloque))


def anonimizar(texto: str, terminos: list[str]) -> str:
    for t in sorted(terminos, key=len, reverse=True):
        texto = re.sub(re.escape(t), "[candidatura]", texto, flags=re.IGNORECASE)
    return texto


def terminos_identificables(c: Candidato) -> list[str]:
    genericas = {"movimiento", "partido", "alianza", "ciudadana", "democracia", "nacional", "oportunidades"}
    palabras = [w for w in re.findall(r"[\wÁÉÍÓÚáéíóúÑñ]+", c.nombre) if len(w) >= 4]
    org = [w for w in re.findall(r"[\wÁÉÍÓÚáéíóúÑñ]+", c.organizacion) if len(w) >= 5 and w.lower() not in genericas]
    return [c.nombre, c.organizacion, *palabras, *org]


def paginas_marcadas(paginas: list[str]) -> str:
    return "\n\n".join(f"=== Página {i} ===\n{p.strip()}" for i, p in enumerate(paginas, start=1))


# ─── Reporte ────────────────────────────────────────────────────────────────


@dataclass
class Reporte:
    ciudad: str
    modo: str
    documentos: dict[str, dict] = field(default_factory=dict)
    descartadas: list[PropuestaVerificada] = field(default_factory=list)
    pendientes: dict[str, dict] = field(default_factory=dict)  # propuesta_id → qué falta decidir
    neutralidad: list[dict] = field(default_factory=list)
    kappa: dict[str, float | None] = field(default_factory=dict)
    acuerdo: dict[str, float | None] = field(default_factory=dict)  # % de propuestas con los 3 jurados de acuerdo
    errores: list[str] = field(default_factory=list)
    contexto_descartado: int = 0
    exportadas: int = 0
    cache: str = ""

    def markdown(self) -> str:
        l = [f"# Reporte de calidad · {self.ciudad} · modo {self.modo}", ""]
        l += ["## Documentos", "", "| Candidato | Págs | Escaneado | Verificadas | Descartadas |", "|---|---|---|---|---|"]
        for c, d in sorted(self.documentos.items()):
            l.append(f"| {c} | {d['paginas']} | {'sí' if d['escaneado'] else 'no'} | {d['verificadas']} | {d['descartadas']} |")
        total_v = sum(d["verificadas"] for d in self.documentos.values())
        total_d = sum(d["descartadas"] for d in self.documentos.values())
        pct = 100 * total_v / max(1, total_v + total_d)
        l += ["", f"**Citas verificadas: {total_v} de {total_v + total_d} ({pct:.1f}%)**", ""]
        l += ["## Acuerdo entre jurados (kappa de Fleiss)", ""]
        for crit, k in self.kappa.items():
            nivel = "—" if k is None else "casi perfecto" if k >= 0.8 else "sustancial" if k >= 0.6 else "moderado" if k >= 0.4 else "⚠️ bajo: revisar la rúbrica"
            ac = self.acuerdo.get(crit)
            l.append(f"- {crit}: kappa {'—' if k is None else k} ({nivel}) · unanimidad en {'—' if ac is None else f'{ac:.0%}'} de las propuestas")
        l.append("")
        l.append("> Con criterios muy raros (p. ej. casi ninguna propuesta tiene plazo) el kappa cae aunque los jurados casi siempre coincidan: mirar también el % de unanimidad.")
        l += ["", f"Fragmentos de contexto descartados por no estar literalmente en el plan: {self.contexto_descartado}"]
        l += ["", f"## Cola de revisión humana: {len(self.pendientes)}", ""]
        for pid, motivo in list(self.pendientes.items())[:50]:
            l.append(f"- `{pid}`: {motivo['motivo']}")
        l += ["", f"## Auditoría de neutralidad: {len(self.neutralidad)} observaciones", ""]
        for o in self.neutralidad[:50]:
            l.append(f"- `{o['propuesta_id']}`: {o['problema']} → {o['sugerencia']}")
        l += ["", f"## Citas descartadas (no encontradas en el plan): {len(self.descartadas)}", ""]
        for p in self.descartadas[:50]:
            l.append(f"- {p.candidato} p.{p.pagina}: “{p.cita[:140]}” ({p.verificacion.metodo}, similitud {p.verificacion.similitud})")
        if self.errores:
            l += ["", "## Errores", "", *[f"- {e}" for e in self.errores]]
        l += ["", f"Propuestas exportadas: **{self.exportadas}**", "", "## Caché", "", "```", self.cache, "```"]
        return "\n".join(l) + "\n"


# ─── Pasos por documento [0]–[3] ────────────────────────────────────────────


def procesar_documento(c: Candidato, temas: list[Tema], eq: Equipo, cache: Cache, rep: Reporte) -> ResultadoDocumento | None:
    if not c.plan_trabajo.disponible or not c.plan_trabajo.fuente or not c.plan_trabajo.fuente.archivo:
        return None
    pdf = RAIZ_REPO / c.plan_trabajo.fuente.archivo
    texto = texto_pdf(pdf, cache)
    paginas = texto.paginas

    if texto.escaneado:  # [0b] transcripción independiente del extractor
        p = cargar_prompt("transcripcion")
        sol = Solicitud("transcripcion", p.texto, "Transcribe el documento adjunto.", Transcripcion, pdf=pdf, extra={"paginas": paginas})
        tr = cache.obtener("transcripcion", p.version, eq.transcriptor.modelo, texto.sha256, Transcripcion, lambda: llamar(eq.transcriptor, sol, Transcripcion))
        paginas = tr.paginas or paginas

    ids_temas = [t.id for t in temas]
    lista_temas = "\n".join(f"  - `{t.id}`: {t.nombre} ({t.descripcion})" for t in temas)

    # [1] extracción
    p = cargar_prompt("extraccion")
    usuario = p.render(TEMAS=lista_temas, PAGINAS=paginas_marcadas(paginas))
    sol = Solicitud("extraccion", "", usuario, Extraccion, extra={"paginas": paginas})
    ext = cache.obtener("extraccion", p.version, eq.extractor.modelo, huella([texto.sha256, ids_temas]), Extraccion, lambda: llamar(eq.extractor, sol, Extraccion))

    verificadas: dict[str, PropuestaVerificada] = {}
    descartadas: list[PropuestaVerificada] = []

    def incorporar(props: list[PropuestaExtraida], origen: str) -> None:
        for pe in props:
            r = verificar(pe.cita, paginas, pe.pagina)
            # El contexto también se verifica literalmente; lo que no está en el PDF se descarta
            contexto: list[FragmentoContexto] = []
            for f in pe.contexto[:4]:
                rc = verificar(f.texto, paginas, f.pagina, minimo=8)
                t = f.texto.strip()
                if rc.verificada and normalizar(t) not in normalizar(pe.cita) and t not in [x.texto for x in contexto]:
                    contexto.append(FragmentoContexto(texto=t, pagina=rc.pagina or f.pagina))
                elif not rc.verificada:
                    rep.contexto_descartado += 1
            pv = PropuestaVerificada(
                id=id_propuesta(c.id, pe.cita), candidato=c.id, tema=pe.tema if pe.tema in ids_temas else "",
                resumen=pe.resumen.strip(), cita=pe.cita.strip(), pagina=r.pagina or pe.pagina, contexto=contexto, verificacion=r, origen=origen,
            )
            if r.verificada and pv.tema and pv.id not in verificadas:
                verificadas[pv.id] = pv
            elif not r.verificada or not pv.tema:
                descartadas.append(pv)

    incorporar(ext.propuestas, "extraccion")  # [2]

    # [3] cobertura (una vuelta)
    p = cargar_prompt("cobertura")
    extraidas = "\n".join(f"- [{v.tema}] {v.resumen}" for v in verificadas.values())
    usuario = p.render(TEMAS_IDS=", ".join(ids_temas), EXTRAIDAS=extraidas, PAGINAS=paginas_marcadas(paginas))
    sol = Solicitud("cobertura", "", usuario, Extraccion, extra={"paginas": paginas})
    cob = cache.obtener("cobertura", p.version, eq.cobertura.modelo, huella([texto.sha256, sorted(verificadas)]), Extraccion, lambda: llamar(eq.cobertura, sol, Extraccion))
    incorporar(cob.propuestas, "cobertura")

    rep.documentos[c.id] = {"paginas": len(paginas), "escaneado": texto.escaneado, "verificadas": len(verificadas), "descartadas": len(descartadas)}
    rep.descartadas += descartadas
    return ResultadoDocumento(candidato=c.id, sha256=texto.sha256, escaneado=texto.escaneado, verificadas=list(verificadas.values()), descartadas=descartadas)


# ─── [4] Jurado ─────────────────────────────────────────────────────────────


TAM_LOTE = 10


def juzgar(todas: list[PropuestaVerificada], jurado: list[ProveedorIA], terminos: dict[str, list[str]], cache: Cache,
           rep: Reporte, paralelo: int) -> dict[str, dict[str, list[VotoJurado]]]:
    """[4] Jurado a ciegas en LOTES (opción A): cada llamada evalúa hasta 10 propuestas, numeradas 1..10,
    mezcladas entre candidaturas y anonimizadas. El resultado se cachea POR PROPUESTA, así que el
    pipeline sigue siendo incremental: solo se juzga lo que no tiene voto en caché."""
    p = cargar_prompt("jurado_lote")
    anon = {}
    for pv in todas:
        # Los jurados NO ven el resumen (lo escribió otra IA): solo la cita y su contexto, anonimizados
        c = anonimizar(pv.cita, terminos[pv.candidato])
        ctx = [anonimizar(f.texto, terminos[pv.candidato]) for f in pv.contexto]
        anon[pv.id] = (pv.tema, ctx, c, huella([pv.tema, c, ctx]))

    votos: dict[str, dict[str, VotoRubrica | None]] = {pv.id: {} for pv in todas}
    tareas = []
    for j in jurado:
        faltan = []
        for pv in todas:
            v = cache.leer("jurado", p.version, j.modelo, anon[pv.id][3], VotoRubrica)
            if v is not None:
                votos[pv.id][j.modelo] = v
            else:
                faltan.append(pv.id)
        faltan.sort(key=lambda pid: anon[pid][3])  # orden pseudoaleatorio estable: mezcla candidaturas
        tareas += [(j, faltan[k : k + TAM_LOTE]) for k in range(0, len(faltan), TAM_LOTE)]

    def ejecutar_lote(tarea):
        j, ids = tarea
        def bloque(n: int, pid: str) -> str:
            tema, ctx, cita, _ = anon[pid]
            contexto = "\n".join(f'- "{x}"' for x in ctx) if ctx else "(el plan no aporta más contexto para esta propuesta)"
            return f'### Propuesta {n}\nTema: {tema}\nCita textual del plan: "{cita}"\nContexto en el mismo plan:\n{contexto}'

        bloques = [bloque(n, pid) for n, pid in enumerate(ids, start=1)]
        sol = Solicitud("jurado_lote", "", p.render(PROPUESTAS="\n\n".join(bloques)), VotosLote,
                        extra={"citas": [" ".join([anon[pid][2], *anon[pid][1]]) for pid in ids]})
        try:
            lote = llamar(j, sol, VotosLote)
        except RuntimeError as e:
            if isinstance(e, PresupuestoAgotado):
                raise
            rep.errores.append(f"jurado {j.modelo}: lote de {len(ids)} falló: {str(e)[:200]}")
            return
        por_num = {ev.numero: ev for ev in lote.evaluaciones}
        omitidas = [pid for n, pid in enumerate(ids, start=1) if n not in por_num]
        if omitidas and len(ids) > 1:  # reintento solo con las omitidas (lote más chico)
            ejecutar_lote((j, omitidas))
        for n, pid in enumerate(ids, start=1):
            ev = por_num.get(n)
            if ev is None:
                if len(ids) == 1:  # ni siquiera sola: voto nulo, se reintenta en la próxima corrida
                    rep.errores.append(f"jurado {j.modelo}: omitió {pid}")
                continue
            vr = VotoRubrica(**{k: getattr(ev, k) for k in CRITERIOS})
            cache.guardar("jurado", p.version, j.modelo, anon[pid][3], vr)
            votos[pid][j.modelo] = vr

    with ThreadPoolExecutor(max_workers=paralelo) as ex:
        list(ex.map(ejecutar_lote, tareas))

    salida: dict[str, dict[str, list[VotoJurado]]] = {}
    for pv in todas:
        por_criterio: dict[str, list[VotoJurado]] = {k: [] for k in CRITERIOS}
        for j in jurado:
            vr = votos[pv.id].get(j.modelo)
            for k in CRITERIOS:
                vc = getattr(vr, k) if vr else None
                por_criterio[k].append(VotoJurado(proveedor=j.proveedor, modelo=j.modelo,
                                                  valor=vc.valor if vc else None, justificacion=vc.justificacion if vc else None))
        salida[pv.id] = por_criterio
    return salida


# ─── [6] Enfoques ───────────────────────────────────────────────────────────


def agrupar_enfoques(tema: Tema, props: list[PropuestaVerificada], eq: Equipo, cache: Cache, rep: Reporte) -> Agrupacion | None:
    if len(props) < 2:
        return None
    iconos = iconos_permitidos()
    lista = "\n".join(f"- `{x.id}`: {x.resumen}" for x in sorted(props, key=lambda x: x.id))
    entrada = huella([tema.id, [(x.id, x.resumen) for x in sorted(props, key=lambda x: x.id)]])
    ids = [x.id for x in props]

    p1 = cargar_prompt("enfoques")
    u1 = p1.render(TEMA=f"{tema.nombre} ({tema.descripcion})", PREFIJO=tema.id, ICONOS=", ".join(sorted(iconos)), PROPUESTAS=lista)
    s1 = Solicitud("enfoques", "", u1, Agrupacion, extra={"tema": tema.id, "propuestas": ids})
    ag = cache.obtener("enfoques", p1.version, eq.enfoques_propone.modelo, entrada, Agrupacion, lambda: llamar(eq.enfoques_propone, s1, Agrupacion))

    p2 = cargar_prompt("enfoques_validacion")
    u2 = p2.render(TEMA=tema.nombre, ICONOS=", ".join(sorted(iconos)), AGRUPACION=ag.model_dump_json(indent=1), PROPUESTAS=lista)
    s2 = Solicitud("enfoques_validacion", "", u2, Agrupacion, extra={"agrupacion": ag.model_dump()})
    ag = cache.obtener("enfoques_val", p2.version, eq.enfoques_valida.modelo, huella([entrada, ag.model_dump()]), Agrupacion, lambda: llamar(eq.enfoques_valida, s2, Agrupacion))

    # Saneamiento determinístico: prefijo de id, íconos válidos, asignaciones conocidas
    validos = {}
    for e in ag.enfoques[:4]:
        slug = re.sub(r"[^a-z0-9]+", "-", e.id.lower()).strip("-") or "enfoque"
        eid = slug if slug.startswith(f"{tema.id}-") else f"{tema.id}-{slug}"
        icono = e.icono if e.icono in iconos else tema.icono
        if icono != e.icono:
            rep.errores.append(f"enfoque {eid}: ícono '{e.icono}' no permitido → '{icono}'")
        validos[e.id] = e.model_copy(update={"id": eid, "icono": icono, "nombre": e.nombre.strip()[:40], "descripcion": e.descripcion.strip()[:160]})
    if len(validos) < 2:
        rep.errores.append(f"tema {tema.id}: menos de 2 enfoques válidos, se omite")
        return None
    asign = [a.model_copy(update={"enfoques": [validos[x].id for x in a.enfoques if x in validos]}) for a in ag.asignaciones if a.propuesta_id in ids]
    return Agrupacion(enfoques=list(validos.values()), asignaciones=asign)


# ─── Orquestación ───────────────────────────────────────────────────────────


def ejecutar(ciudad: str, *, dir_datos: Path = DIR_DATOS, destino: Path | None = None, solo: list[str] | None = None,
             cache: Cache | None = None, eq: Equipo | None = None, dir_salida: Path = DIR_SALIDA, globales: bool = True) -> Reporte:
    cfg = config()
    cache = cache or Cache()
    eq = eq or equipo()
    sitio = cargar(dir_datos)
    dc = sitio.datos[ciudad]
    rep = Reporte(ciudad=ciudad, modo=cfg.modo)
    # En modo mock NUNCA se escribe sobre datos/ de una ciudad real
    if destino is None:
        destino = dir_datos if (cfg.modo == "real" or dc.ciudad.es_mock) else dir_salida / "datos"
    revision = _leer_revision(dir_datos / "ciudades" / ciudad / "revision.yaml")

    candidatos = [c for c in dc.candidatos if not solo or c.id in solo]
    with ThreadPoolExecutor(max_workers=4 if cfg.modo == "real" else 1) as ex:
        resultados = list(ex.map(lambda c: procesar_documento(c, sitio.temas, eq, cache, rep), candidatos))
    docs: dict[str, ResultadoDocumento] = {r.candidato: r for r in resultados if r}

    todas = [pv for r in docs.values() for pv in r.verificadas if not revision.get(pv.id, {}).get("descartar")]
    for pv in todas:  # ediciones humanas de resumen/tema
        ed = revision.get(pv.id, {})
        if ed.get("resumen"):
            pv.resumen = ed["resumen"]
        if ed.get("tema"):
            pv.tema = ed["tema"]
        if faltan := datos_sin_respaldo(pv.resumen, pv.cita, [f.texto for f in pv.contexto]):
            rep.errores.append(f"{pv.id}: el resumen trae datos sin respaldo en la cita ni el contexto ({', '.join(faltan)}): corregir en revision.yaml")

    # [4] + [5]
    terminos = {c.id: terminos_identificables(c) for c in dc.candidatos}
    votos = juzgar(todas, eq.jurado, terminos, cache, rep, paralelo=8 if cfg.modo == "real" else 1)
    rubricas: dict[str, Rubrica] = {}
    for pv in todas:
        cal: dict[str, Calificacion] = {}
        faltan = []
        for k in CRITERIOS:
            decision = revision.get(pv.id, {}).get("criterios", {}).get(k)
            if decision:
                cal[k] = resolver_humano(votos[pv.id][k], bool(decision["valor"]), decision.get("nota") or "Revisado")
            elif (cons := consolidar(votos[pv.id][k])) is not None:
                cal[k] = cons
            else:
                faltan.append(k)
        if faltan:
            rep.pendientes[pv.id] = {"motivo": f"jurado sin mayoría en: {', '.join(faltan)}", "criterios": faltan, "propuesta": pv}
        else:
            rubricas[pv.id] = Rubrica(**cal)
    rep.kappa = {k: kappa_fleiss([[v.valor for v in votos[pid][k]] for pid in votos]) for k in CRITERIOS}
    rep.acuerdo = {k: _acuerdo_unanime([[v.valor for v in votos[pid][k]] for pid in votos]) for k in CRITERIOS}

    # [6]
    por_tema: dict[str, list[PropuestaVerificada]] = defaultdict(list)
    for pv in todas:
        por_tema[pv.tema].append(pv)
    enfoques: list[Enfoque] = []
    asignacion: dict[str, list[str]] = {}
    for t in sitio.temas if globales else []:
        ag = agrupar_enfoques(t, por_tema.get(t.id, []), eq, cache, rep)
        if ag:
            enfoques += [Enfoque(id=e.id, tema=t.id, nombre=e.nombre, descripcion=e.descripcion, icono=e.icono) for e in ag.enfoques]
            asignacion |= {a.propuesta_id: a.enfoques for a in ag.asignaciones}

    # [7]
    if globales:
        _auditar_neutralidad(todas, dc.candidatos, eq, cache, rep)

    # [8]
    _exportar(ciudad, dc.candidatos, todas, rubricas, asignacion, enfoques, dir_datos, destino, cfg.modo == "mock", rep)
    rep.cache = cache.stats.resumen()
    _escribir_salidas(ciudad, rep, dir_salida)
    return rep


def _acuerdo_unanime(items: list[list[bool | None]]) -> float | None:
    completos = [it for it in items if it and all(v is not None for v in it)]
    return sum(len(set(it)) == 1 for it in completos) / len(completos) if completos else None


def _auditar_neutralidad(todas: list[PropuestaVerificada], candidatos: list[Candidato], eq: Equipo, cache: Cache, rep: Reporte) -> None:
    if not todas:
        return
    letra = {c.id: chr(65 + i) for i, c in enumerate(sorted(candidatos, key=lambda x: huella(x.id)))}
    resumenes = {pv.id: pv.resumen for pv in todas}
    texto = "\n".join(f"- Candidatura {letra[pv.candidato]} · `{pv.id}`: {pv.resumen}" for pv in sorted(todas, key=lambda x: x.id))
    p = cargar_prompt("neutralidad")
    sol = Solicitud("neutralidad", "", p.render(RESUMENES=texto), AuditoriaNeutralidad, extra={"resumenes": resumenes})
    au = cache.obtener("neutralidad", p.version, eq.neutralidad.modelo, huella(sorted(resumenes.items())), AuditoriaNeutralidad, lambda: llamar(eq.neutralidad, sol, AuditoriaNeutralidad))
    rep.neutralidad = [o.model_dump() for o in au.observaciones if o.propuesta_id in resumenes]


def _leer_revision(ruta: Path) -> dict[str, dict]:
    if not ruta.exists():
        return {}
    return (yaml.safe_load(ruta.read_text(encoding="utf-8")) or {}).get("propuestas", {}) or {}


def _exportar(ciudad, candidatos, todas, rubricas, asignacion, enfoques, dir_datos, destino, es_mock, rep) -> None:
    dir_c = destino / "ciudades" / ciudad
    (dir_c / "candidatos").mkdir(parents=True, exist_ok=True)
    por_cand: dict[str, list[Propuesta]] = defaultdict(list)
    ids_enfoques = {e.id for e in enfoques}
    for pv in sorted(todas, key=lambda x: (x.pagina, x.id)):
        if pv.id not in rubricas:
            continue  # pendiente de revisión: no se publica
        por_cand[pv.candidato].append(Propuesta(
            id=pv.id, tema=pv.tema, resumen=pv.resumen[:220], cita=pv.cita, pagina=pv.pagina, cita_verificada=True,
            contexto=[ContextoCita(texto=f.texto, pagina=f.pagina) for f in pv.contexto],
            enfoques=[e for e in asignacion.get(pv.id, []) if e in ids_enfoques], rubrica=rubricas[pv.id],
        ))
    for c in candidatos:
        actualizado = c.model_copy(update={"propuestas": por_cand.get(c.id, []), "es_mock": c.es_mock or es_mock})
        Candidato.model_validate(actualizado.model_dump())  # valida el contrato antes de escribir
        _escribir_yaml(dir_c / "candidatos" / f"{c.id}.yaml", actualizado, "Generado por el pipeline. Ediciones: usar revision.yaml")
        rep.exportadas += len(por_cand.get(c.id, []))
    _escribir_yaml(dir_c / "enfoques.yaml", Enfoques(enfoques=enfoques), "Generado por el pipeline (paso 6)")
    if destino != dir_datos:  # copia mínima para que la salida sea un datos/ válido por sí mismo
        (destino / "temas.yaml").write_text((dir_datos / "temas.yaml").read_text(encoding="utf-8"), encoding="utf-8")
        registro = [r for r in (yaml.safe_load((dir_datos / "ciudades.yaml").read_text(encoding="utf-8")) or []) if r["id"] == ciudad]
        (destino / "ciudades.yaml").write_text(yaml.safe_dump(registro, allow_unicode=True, sort_keys=False), encoding="utf-8")
        ciudad_src = (dir_datos / "ciudades" / ciudad / "ciudad.yaml").read_text(encoding="utf-8")
        if es_mock and "es_mock: true" not in ciudad_src:
            ciudad_src += "es_mock: true\n"
        (dir_c / "ciudad.yaml").write_text(ciudad_src, encoding="utf-8")


def _escribir_yaml(ruta: Path, modelo, comentario: str) -> None:
    datos = modelo.model_dump(mode="json", exclude_defaults=True)
    ruta.write_text(f"# {comentario}\n" + yaml.safe_dump(datos, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")


def _escribir_salidas(ciudad: str, rep: Reporte, dir_salida: Path = DIR_SALIDA) -> None:
    dir_s = dir_salida / ciudad
    dir_s.mkdir(parents=True, exist_ok=True)
    (dir_s / "reporte.md").write_text(rep.markdown(), encoding="utf-8")
    # Plantilla para la revisión humana: copiar las decisiones a datos/ciudades/<c>/revision.yaml
    plantilla = {"propuestas": {
        pid: {
            "_contexto": {"candidato": d["propuesta"].candidato, "resumen": d["propuesta"].resumen, "cita": d["propuesta"].cita, "pagina": d["propuesta"].pagina},
            "criterios": {k: {"valor": None, "nota": ""} for k in d["criterios"]},
        } for pid, d in rep.pendientes.items()
    }}
    (dir_s / "pendientes.yaml").write_text(
        "# Decisiones pendientes. Completar valor (true/false) y nota, y copiar a datos/ciudades/<ciudad>/revision.yaml\n"
        + yaml.safe_dump(plantilla, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
