/** Contacto público para reclamos y correcciones. */
export const CORREO = 'edisonpaul4444@gmail.com';

/** Enlace mailto con asunto y cuerpo prellenados (nada sale del navegador hasta que la persona envía). */
export function mailto(asunto: string, cuerpo = ''): string {
	return `mailto:${CORREO}?subject=${encodeURIComponent(asunto)}&body=${encodeURIComponent(cuerpo)}`;
}
