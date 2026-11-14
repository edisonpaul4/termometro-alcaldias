import { error } from '@sveltejs/kit';
import { ciudadesActivas, datosCiudad, sitio } from '#lib/server/datos.js';
import type { EntryGenerator, PageServerLoad } from './$types';

export const entries: EntryGenerator = () =>
	ciudadesActivas().flatMap((c) => sitio.temas.map((t) => ({ ciudad: c.id, tema: t.id })));

/** Datos completos solo de las propuestas de ESTE tema. */
export const load: PageServerLoad = ({ params }) => {
	const tema = sitio.temas.find((t) => t.id === params.tema);
	if (!tema) error(404, 'Tema no encontrado');
	const completos = datosCiudad(params.ciudad).candidatos.map((c) => ({
		...c,
		propuestas: (c.propuestas ?? []).filter((p) => p.tema === tema.id)
	}));
	return { tema, completos };
};
