import type { Calificacion, Candidato } from './contrato.gen';
import type { CandidatoMin } from './termometro';

export const fotoUrl = (ciudad: string, c: CandidatoMin) =>
	c.foto ? `/fotos/${ciudad}/${c.id}${c.foto.slice(c.foto.lastIndexOf('.'))}` : null;

export const iniciales = (nombre: string) =>
	nombre
		.replace(/\(.*?\)/g, '')
		.trim()
		.split(/\s+/)
		.slice(0, 2)
		.map((p) => p[0])
		.join('')
		.toUpperCase();

export const pct = (v: number | null) => (v === null ? '—' : `${Math.round(v * 100)}%`);

/** Fisher–Yates con crypto: orden de candidatos aleatorio en cada visita (neutralidad). */
export function barajar<T>(xs: readonly T[]): T[] {
	const a = [...xs];
	const r = new Uint32Array(a.length);
	crypto.getRandomValues(r);
	for (let i = a.length - 1; i > 0; i--) {
		const j = r[i] % (i + 1);
		[a[i], a[j]] = [a[j], a[i]];
	}
	return a;
}

/** Muestra votos coincidentes o el origen explícito de una revisión editorial. */
export function textoConsenso(c: Calificacion): string {
	if (c.consenso === 'humano') return 'Resuelto en revisión humana';
	if (c.consenso === 'revision_ia') return 'Resuelto en revisión editorial de IA';
	const validos = c.votos.filter((v) => v.valor !== null);
	const coinciden = validos.filter((v) => v.valor === c.valor).length;
	return `${coinciden} de ${c.votos.length} IA coinciden`;
}

/** Enlace al PDF oficial abierto en la página de la cita. */
export const enlacePagina = (c: Candidato, pagina: number) =>
	c.plan_trabajo.fuente ? `${c.plan_trabajo.fuente.url}#page=${pagina}` : null;

export function diasHasta(fecha: string, hoy = new Date()): number {
	const objetivo = new Date(`${fecha}T07:00:00-05:00`);
	return Math.max(0, Math.ceil((objetivo.getTime() - hoy.getTime()) / 86_400_000));
}
