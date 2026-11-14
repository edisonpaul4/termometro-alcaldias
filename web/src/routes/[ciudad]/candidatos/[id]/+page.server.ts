import { error } from '@sveltejs/kit';
import { ciudadesActivas, datosCiudad, sitio } from '#lib/server/datos.js';
import type { EntryGenerator, PageServerLoad } from './$types';

export const entries: EntryGenerator = () =>
	ciudadesActivas().flatMap((c) => sitio.datos[c.id].candidatos.map((x) => ({ ciudad: c.id, id: x.id })));

/** Datos completos (citas, votos, justificaciones) solo del candidato de esta página. */
export const load: PageServerLoad = ({ params }) => {
	const candidato = datosCiudad(params.ciudad).candidatos.find((c) => c.id === params.id);
	if (!candidato) error(404, 'Candidato no encontrado');
	return { candidato };
};
