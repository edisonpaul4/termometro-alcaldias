/**
 * Identidad visual por tema: 12 tonos repartidos por el círculo cromático (~30° c/u),
 * todos con contraste AA para texto blanco y como ícono sobre fondo claro. Son categorías, no valoraciones.
 * Si una ciudad agrega un tema nuevo, cae al color neutro.
 */
const COLORES: Record<string, string> = {
	riesgos: '#e11d48', // rosa-rojo
	empleo: '#ea580c', // naranja
	movilidad: '#b45309', // ámbar
	rural: '#4d7c0f', // lima
	ambiente: '#15803d', // verde
	inclusion: '#0f766e', // turquesa
	'agua-servicios': '#0369a1', // celeste
	vivienda: '#1d4ed8', // azul
	seguridad: '#4338ca', // índigo
	transparencia: '#6d28d9', // violeta
	cultura: '#a21caf', // fucsia
	'espacio-publico': '#be185d' // rosa
};

export const colorTema = (id: string) => COLORES[id] ?? '#4b4f58';

/** Fondo translúcido del color (para "pastillas" y fichas de tema). */
export const tinte = (hex: string, alfa = 0.1) => {
	const n = parseInt(hex.slice(1), 16);
	return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${alfa})`;
};
