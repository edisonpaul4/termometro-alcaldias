/**
 * Termómetro de concreción. Implementa la sección "Cálculo" de pipeline/rubrica.md.
 * La IA solo califica criterios Sí/No; todos los números se calculan aquí.
 */
import type { Consenso } from './contrato.gen';

/* Tipos estructurales mínimos: sirven tanto para los datos completos como para la
 * versión "ligera" que se envía a las páginas de listado (sin citas ni votos). */
export interface CalifMin {
	valor: boolean;
	consenso: Consenso;
}
export interface PropuestaMin {
	id: string;
	tema: string;
	resumen: string;
	pagina: number;
	enfoques?: string[];
	rubrica: { meta: CalifMin; plazo: CalifMin; financiamiento: CalifMin; competencia_municipal: CalifMin };
}
export interface CandidatoMin {
	id: string;
	nombre: string;
	lista: string;
	organizacion: string;
	foto?: string | null;
	plan_trabajo: { disponible: boolean; paginas?: number | null };
	propuestas?: PropuestaMin[];
}

/** (meta + plazo + financiamiento) / 3. La competencia municipal NO suma: es una alerta. */
export function concrecion(p: PropuestaMin): number {
	const r = p.rubrica;
	return (+r.meta.valor + +r.plazo.valor + +r.financiamiento.valor) / 3;
}

export function fueraDeCompetencia(p: PropuestaMin): boolean {
	return !p.rubrica.competencia_municipal.valor;
}

export interface Lectura {
	/** 0–1, o null si no hay propuestas */
	valor: number | null;
	propuestas: number;
	conMeta: number;
	conPlazo: number;
	conFinanciamiento: number;
	/** propuestas con al menos un dato: meta, plazo o financiamiento */
	conAlgunDato: number;
	fueraDeCompetencia: number;
}

function leer(ps: PropuestaMin[]): Lectura {
	const n = ps.length;
	return {
		valor: n ? ps.reduce((s, p) => s + concrecion(p), 0) / n : null,
		propuestas: n,
		conMeta: ps.filter((p) => p.rubrica.meta.valor).length,
		conPlazo: ps.filter((p) => p.rubrica.plazo.valor).length,
		conFinanciamiento: ps.filter((p) => p.rubrica.financiamiento.valor).length,
		conAlgunDato: ps.filter((p) => concrecion(p) > 0).length,
		fueraDeCompetencia: ps.filter(fueraDeCompetencia).length
	};
}

export function propuestasDelTema<P extends PropuestaMin>(c: { propuestas?: P[] }, tema: string): P[] {
	return (c.propuestas ?? []).filter((p) => p.tema === tema);
}

/** Termómetro de un candidato en un tema. */
export function termometroTema(c: { propuestas?: PropuestaMin[] }, tema: string): Lectura {
	return leer(propuestasDelTema(c, tema));
}

/** Termómetro global = promedio de los termómetros por tema (no por propuesta),
 *  para que un tema con 15 propuestas vagas no pese más que los demás. */
export function termometroGlobal(c: { propuestas?: PropuestaMin[] }): Lectura {
	const ps = c.propuestas ?? [];
	const temas = [...new Set(ps.map((p) => p.tema))];
	const base = leer(ps);
	if (!temas.length) return base;
	const valor = temas.reduce((s, t) => s + (termometroTema(c, t).valor ?? 0), 0) / temas.length;
	return { ...base, valor };
}

/* ── Proporción "de cada 10" ────────────────────────────────────────────────
 * Lo que se muestra al votante. Siempre en proporción y sobre una escala fija de 10,
 * igual para todos: un plan más largo no se ve "más concreto" por tener más propuestas. */

export interface Proporcion {
	/** 0–10, con decimales (para llenar casillas parciales) */
	deCada10: number;
	/** texto de la cantidad: "3 de cada 10", "1 de 119", "2 de 4", "ninguna" */
	texto: string;
	/** true si el texto usa "de cada 10" (concuerda en número con el verbo) */
	singular: boolean;
}

/** Con menos de 10 propuestas o menos de 0,5 de cada 10, se muestra el conteo exacto. */
export function proporcion(n: number, total: number): Proporcion {
	if (!total || !n) return { deCada10: 0, texto: 'ninguna', singular: true };
	const x = (10 * n) / total;
	if (total < 10 || x < 0.5) return { deCada10: x, texto: `${n} de ${total}`, singular: n === 1 };
	const r = Math.round(x);
	return { deCada10: x, texto: `${r} de cada 10`, singular: r === 1 };
}

/** Proporción de propuestas sin ningún dato en un conjunto de candidatos (contexto de ciudad). */
export function soloIntenciones(cs: { propuestas?: PropuestaMin[] }[]): { total: number; sinDatos: number } {
	const ps = cs.flatMap((c) => c.propuestas ?? []);
	return { total: ps.length, sinDatos: ps.filter((p) => concrecion(p) === 0).length };
}

/** Las propuestas más concretas, en el orden del plan ante empates. */
export function masConcretas<P extends PropuestaMin>(ps: P[], n = 3): P[] {
	return ps
		.map((p, i) => ({ p, i, c: concrecion(p) }))
		.filter((x) => x.c > 0)
		.sort((a, b) => b.c - a.c || a.i - b.i)
		.slice(0, n)
		.map((x) => x.p);
}
