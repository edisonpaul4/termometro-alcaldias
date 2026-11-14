import { ciudadesActivas, sitio } from '#lib/server/datos.js';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = () => ({
	temas: sitio.temas,
	ciudades: ciudadesActivas().map((c) => {
		const d = sitio.datos[c.id];
		return {
			...c,
			es_mock: d.ciudad.es_mock,
			eleccion: d.ciudad.eleccion,
			candidatos: d.candidatos.length,
			paginas: d.candidatos.reduce((s, x) => s + (x.plan_trabajo.paginas ?? 0), 0)
		};
	})
});
