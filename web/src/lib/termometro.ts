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
	plan_trabajo: { disponible: boolean };
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

/** Texto corto y neutral para el valor del termómetro. */
export function etiqueta(valor: number | null): string {
	if (valor === null) return 'Sin propuestas';
	if (valor >= 0.67) return 'Muy concreto';
	if (valor >= 0.34) return 'Algo concreto';
	if (valor > 0) return 'Poco concreto';
	return 'Nada concreto';
}
