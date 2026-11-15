import { describe, expect, it } from 'vitest';
import type { Calificacion, Candidato, Propuesta } from './contrato.gen';
import {
	agruparEmpates,
	aURL,
	calcularAfinidad,
	desdeURL,
	pesos,
	TOPE_COBERTURA,
	UMBRAL_EMPATE
} from './afinidad';
import { concrecion, masConcretas, proporcion, termometroGlobal, termometroTema } from './termometro';

const cal = (valor: boolean): Calificacion => ({
	valor,
	consenso: 'unanime',
	votos: [{ proveedor: 'mock', modelo: 'm', valor, justificacion: null }],
	nota_revision: null
});

let n = 0;
function prop(tema: string, o: { meta?: boolean; plazo?: boolean; fin?: boolean; comp?: boolean; enfoques?: string[] } = {}): Propuesta {
	return {
		id: `p${++n}`,
		tema,
		resumen: 'r',
		cita: 'cita de prueba larga',
		pagina: 1,
		cita_verificada: true,
		contexto: [],
		enfoques: o.enfoques ?? [],
		rubrica: {
			meta: cal(o.meta ?? false),
			plazo: cal(o.plazo ?? false),
			financiamiento: cal(o.fin ?? false),
			competencia_municipal: cal(o.comp ?? true)
		}
	};
}

function cand(id: string, propuestas: Propuesta[], disponible = true): Candidato {
	return {
		id,
		nombre: id,
		lista: '1',
		organizacion: 'o',
		foto: null,
		foto_fuente: null,
		trayectoria: [],
		es_mock: true,
		plan_trabajo: disponible
			? { disponible, paginas: 10, sha256: null, nota: null, fuente: { url: 'u', titulo: 't', consultado: '2026-11-14', archivo: null } }
			: { disponible, nota: 'no', paginas: null, sha256: null, fuente: null },
		propuestas
	};
}

const TODO = { meta: true, plazo: true, fin: true };

describe('termómetro', () => {
	it('concreción = (meta+plazo+fin)/3 y competencia no suma', () => {
		expect(concrecion(prop('s', TODO))).toBe(1);
		expect(concrecion(prop('s', { meta: true }))).toBeCloseTo(1 / 3);
		expect(concrecion(prop('s', { ...TODO, comp: false }))).toBe(1);
	});

	it('termómetro por tema y desglose', () => {
		const c = cand('a', [prop('s', TODO), prop('s'), prop('m', { meta: true, comp: false })]);
		const t = termometroTema(c, 's');
		expect(t.valor).toBe(0.5);
		expect(t).toMatchObject({ propuestas: 2, conMeta: 1, conPlazo: 1, conFinanciamiento: 1, fueraDeCompetencia: 0 });
		expect(termometroTema(c, 'm').fueraDeCompetencia).toBe(1);
		expect(termometroTema(c, 'x').valor).toBeNull();
	});

	it('global promedia temas, no propuestas', () => {
		// tema s: 1 propuesta perfecta; tema m: 9 propuestas vacías
		const c = cand('a', [prop('s', TODO), ...Array.from({ length: 9 }, () => prop('m'))]);
		expect(termometroGlobal(c).valor).toBe(0.5);
	});

	it('proporción de cada 10: no premia el volumen', () => {
		expect(proporcion(36, 110).texto).toBe('3 de cada 10');
		expect(proporcion(15, 44).texto).toBe('3 de cada 10');
		expect(proporcion(36, 110).deCada10).toBeCloseTo(3.27, 2);
		expect(proporcion(1, 119)).toMatchObject({ texto: '1 de 119', singular: true });
		expect(proporcion(2, 4).texto).toBe('2 de 4');
		expect(proporcion(0, 50).texto).toBe('ninguna');
		expect(proporcion(1, 10)).toMatchObject({ texto: '1 de cada 10', singular: true });
	});

	it('conAlgunDato y más concretas', () => {
		const ps = [prop('s'), prop('s', { meta: true }), prop('s', TODO), prop('s', { plazo: true })];
		expect(termometroTema(cand('a', ps), 's').conAlgunDato).toBe(3);
		expect(masConcretas(ps).map((p) => p.id)).toEqual([ps[2].id, ps[1].id, ps[3].id]);
	});
});

describe('afinidad', () => {
	it('pesos por prioridad', () => {
		expect(pesos(5)).toEqual([5, 4, 3, 2, 1]);
		expect(pesos(1)).toEqual([1]);
	});

	it('quien propone el enfoque elegido y con concreción gana', () => {
		const a = cand('a', [prop('s', { ...TODO, enfoques: ['tec'] })]);
		const b = cand('b', [prop('s', { enfoques: ['tec'] })]); // mismo enfoque, vago
		const c = cand('c', [prop('s', { ...TODO, enfoques: ['control'] })]); // concreto pero otro enfoque
		const r = calcularAfinidad([c, b, a], { temas: ['s'], enfoques: { s: ['tec'] } });
		expect(r.map((x) => x.candidato.id)).toEqual(['a', 'b', 'c']);
		expect(r[0].afinidad).toBeCloseTo(100);
		expect(r[1].afinidad).toBeCloseTo(50); // propone lo que quiero, sin detalle: vale la mitad
		expect(r[2].afinidad).toBeCloseTo(0); // concreto, pero no propone lo que elegí
	});

	it('la concreción se mide solo sobre el enfoque elegido', () => {
		// Concreto en "control", vago en "tec": si elijo "tec", cuenta su vaguedad
		const a = cand('a', [prop('s', { ...TODO, enfoques: ['control'] }), prop('s', { enfoques: ['tec'] })]);
		const r = calcularAfinidad([a], { temas: ['s'], enfoques: { s: ['tec'] } });
		expect(r[0].afinidad).toBeCloseTo(50);
		expect(r[0].detalle[0].concrecion).toBe(0);
	});

	it('sin propuestas en el tema = 0', () => {
		const r = calcularAfinidad([cand('a', [prop('m', TODO)])], { temas: ['s'], enfoques: {} });
		expect(r[0].afinidad).toBe(0);
		expect(r[0].detalle[0].modo).toBe('sin-propuestas');
	});

	it('modo cobertura con tope: más cantidad no suma más allá del tope', () => {
		const muchas = cand('a', Array.from({ length: 10 }, () => prop('s')));
		const tope = cand('b', Array.from({ length: TOPE_COBERTURA }, () => prop('s')));
		const r = calcularAfinidad([muchas, tope], { temas: ['s'], enfoques: {} });
		expect(r[0].afinidad).toBeCloseTo(r[1].afinidad);
		expect(r[0].detalle[0].cobertura).toBe(1);
	});

	it('propuestas fuera de competencia no cuentan', () => {
		const a = cand('a', [prop('s', { ...TODO, comp: false, enfoques: ['tec'] })]);
		const r = calcularAfinidad([a], { temas: ['s'], enfoques: { s: ['tec'] } });
		expect(r[0].afinidad).toBe(0);
		expect(r[0].detalle[0].propuestasExcluidas).toBe(1);
	});

	it('el tema prioritario pesa más', () => {
		const a = cand('a', [prop('s', TODO)]);
		const b = cand('b', [prop('m', TODO)]);
		const r = calcularAfinidad([b, a], { temas: ['s', 'm'], enfoques: {} });
		expect(r[0].candidato.id).toBe('a');
		expect(r[0].afinidad).toBeCloseTo((2 / 3) * 100);
	});

	it('candidato sin plan aparece marcado y con 0', () => {
		const r = calcularAfinidad([cand('g', [], false)], { temas: ['s'], enfoques: {} });
		expect(r[0]).toMatchObject({ afinidad: 0, sinPlan: true });
	});
});

describe('empate técnico', () => {
	const g = (xs: number[]) => agruparEmpates(xs.map((afinidad) => ({ afinidad, grupo: 0 }))).map((r) => r.grupo);

	it('agrupa diferencias menores al umbral', () => {
		expect(UMBRAL_EMPATE).toBe(5);
		expect(g([80, 77, 60, 58, 30])).toEqual([0, 0, 1, 1, 2]);
	});

	it('no encadena: compara contra la cabeza del grupo', () => {
		expect(g([80, 77, 74, 71])).toEqual([0, 0, 1, 1]);
	});
});

describe('estado en URL', () => {
	const temas = new Set(['s', 'm']);
	const enf = new Map([['tec', 's'], ['bus', 'm']]);

	it('ida y vuelta', () => {
		const sel = { temas: ['m', 's'], enfoques: { s: ['tec'] } };
		expect(desdeURL(aURL(sel), temas, enf)).toEqual(sel);
	});

	it('ignora temas/enfoques inválidos o cruzados', () => {
		const s = desdeURL('t=s.hack.m&e_s=tec_bus_x&e_m=bus&e_hack=tec', temas, enf);
		expect(s).toEqual({ temas: ['s', 'm'], enfoques: { s: ['tec'], m: ['bus'] } });
	});

	it('formato legible', () => {
		expect(aURL({ temas: ['s', 'm'], enfoques: { s: ['tec', 'x'] } })).toBe('t=s.m&e_s=tec_x');
	});

	it('máximo 5 temas y sin duplicados', () => {
		const muchos = new Set(['a', 'b', 'c', 'd', 'e', 'f']);
		expect(desdeURL('t=a.a.b.c.d.e.f', muchos, enf).temas).toEqual(['a', 'b', 'c', 'd', 'e']);
	});
});
