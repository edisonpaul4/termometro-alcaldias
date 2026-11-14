/**
 * Algoritmo de afinidad del flujo "Lo que me importa". Especificado en PLAN.md §6.
 * Todo corre en el navegador del usuario; nada se envía a ningún servidor.
 */
import { fueraDeCompetencia, propuestasDelTema, termometroTema, type CandidatoMin } from './termometro';

export const PESO_ENFOQUE = 0.6;
export const PESO_COBERTURA = 0.5;
/** Tope de propuestas que cuentan para "cobertura": más cantidad no es mejor. */
export const TOPE_COBERTURA = 3;
/** Diferencia (en puntos de 0–100) bajo la cual se declara empate técnico. */
export const UMBRAL_EMPATE = 5;

export interface Seleccion {
	/** Temas en orden de prioridad (el primero es el más importante). */
	temas: string[];
	/** Enfoques elegidos por tema. Vacío o ausente = "no estoy seguro". */
	enfoques: Record<string, string[]>;
}

export interface DetalleTema {
	tema: string;
	peso: number;
	/** 0–1 */
	puntaje: number;
	modo: 'enfoques' | 'cobertura' | 'sin-propuestas';
	/** Proporción de enfoques elegidos que el candidato propone (modo enfoques) */
	coincidenciaEnfoques: number | null;
	enfoquesCoincidentes: string[];
	cobertura: number | null;
	concrecion: number;
	/** Propuestas que cuentan (dentro de la competencia municipal) */
	propuestasValidas: number;
	/** Propuestas excluidas por estar fuera de la competencia municipal */
	propuestasExcluidas: number;
}

export interface Resultado<C extends CandidatoMin = CandidatoMin> {
	candidato: C;
	/** 0–100 */
	afinidad: number;
	detalle: DetalleTema[];
	sinPlan: boolean;
	/** Índice del grupo de empate técnico (0 = el primero) */
	grupo: number;
}

/** w_i = n - i + 1 */
export function pesos(n: number): number[] {
	return Array.from({ length: n }, (_, i) => n - i);
}

function validas(c: CandidatoMin, tema: string) {
	const todas = propuestasDelTema(c, tema);
	const ok = todas.filter((p) => !fueraDeCompetencia(p));
	return { ok, excluidas: todas.length - ok.length };
}

export function puntajeTema(
	c: CandidatoMin,
	tema: string,
	enfoquesElegidos: string[],
	maxPropuestasTema: number
): Omit<DetalleTema, 'peso'> {
	const { ok, excluidas } = validas(c, tema);
	const conc = ok.length ? (termometroTema({ ...c, propuestas: ok }, tema).valor ?? 0) : 0;
	const base = { tema, concrecion: conc, propuestasValidas: ok.length, propuestasExcluidas: excluidas };

	if (!ok.length) {
		return { ...base, puntaje: 0, modo: 'sin-propuestas', coincidenciaEnfoques: null, enfoquesCoincidentes: [], cobertura: null };
	}
	if (enfoquesElegidos.length) {
		const propios = new Set(ok.flatMap((p) => p.enfoques ?? []));
		const coinciden = enfoquesElegidos.filter((e) => propios.has(e));
		const coincidencia = coinciden.length / enfoquesElegidos.length;
		return {
			...base,
			puntaje: PESO_ENFOQUE * coincidencia + (1 - PESO_ENFOQUE) * conc,
			modo: 'enfoques',
			coincidenciaEnfoques: coincidencia,
			enfoquesCoincidentes: coinciden,
			cobertura: null
		};
	}
	const denom = Math.min(Math.max(maxPropuestasTema, 1), TOPE_COBERTURA);
	const cobertura = Math.min(ok.length, TOPE_COBERTURA) / denom;
	return {
		...base,
		puntaje: PESO_COBERTURA * cobertura + (1 - PESO_COBERTURA) * conc,
		modo: 'cobertura',
		coincidenciaEnfoques: null,
		enfoquesCoincidentes: [],
		cobertura
	};
}

export function calcularAfinidad<C extends CandidatoMin>(candidatos: C[], sel: Seleccion): Resultado<C>[] {
	const w = pesos(sel.temas.length);
	const sumaW = w.reduce((a, b) => a + b, 0) || 1;
	const maxPorTema = Object.fromEntries(
		sel.temas.map((t) => [t, Math.max(0, ...candidatos.map((c) => validas(c, t).ok.length))])
	);

	const resultados = candidatos.map((c) => {
		const detalle = sel.temas.map((t, i) => ({
			...puntajeTema(c, t, sel.enfoques[t] ?? [], maxPorTema[t]),
			peso: w[i]
		}));
		const afinidad = (detalle.reduce((s, d) => s + d.peso * d.puntaje, 0) / sumaW) * 100;
		return { candidato: c, afinidad, detalle, sinPlan: !c.plan_trabajo.disponible, grupo: 0 };
	});

	resultados.sort((a, b) => b.afinidad - a.afinidad);
	return agruparEmpates(resultados);
}

/**
 * Empate técnico: un candidato queda en el mismo grupo que el anterior si la
 * diferencia con el PRIMERO del grupo es menor al umbral (evita cadenas infinitas
 * de 4 + 4 + 4 puntos).
 */
export function agruparEmpates<T extends { afinidad: number; grupo: number }>(ordenados: T[]): T[] {
	let grupo = 0;
	let cabeza = ordenados[0]?.afinidad ?? 0;
	return ordenados.map((r, i) => {
		if (i > 0 && cabeza - r.afinidad >= UMBRAL_EMPATE) {
			grupo++;
			cabeza = r.afinidad;
		}
		return { ...r, grupo };
	});
}

/* ── Estado en la URL (compartible, sin datos personales) ─────────────────── */

/** ?t=seguridad.movilidad&e_seguridad=seg-tecnologia_seg-espacios
 *  Solo caracteres que URLSearchParams no codifica (slugs + "." + "_"), para links legibles. */
export function aURL(sel: Seleccion): string {
	const p = new URLSearchParams();
	if (sel.temas.length) p.set('t', sel.temas.join('.'));
	for (const t of sel.temas) if (sel.enfoques[t]?.length) p.set(`e_${t}`, sel.enfoques[t].join('_'));
	return p.toString();
}

export function desdeURL(qs: string | URLSearchParams, temasValidos: Set<string>, enfoquesValidos: Map<string, string>): Seleccion {
	const p = typeof qs === 'string' ? new URLSearchParams(qs) : qs;
	const temas = [...new Set((p.get('t') ?? '').split('.').filter((t) => temasValidos.has(t)))].slice(0, 5);
	const enfoques: Record<string, string[]> = {};
	for (const t of temas) {
		const lista = p.get(`e_${t}`);
		if (lista) enfoques[t] = [...new Set(lista.split('_').filter((e) => enfoquesValidos.get(e) === t))];
	}
	return { temas, enfoques };
}
