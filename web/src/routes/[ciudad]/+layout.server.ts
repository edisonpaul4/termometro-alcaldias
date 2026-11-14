import { aligerar, datosCiudad, sitio } from '#lib/server/datos.js';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = ({ params }) => {
	const d = datosCiudad(params.ciudad);
	return {
		ciudad: d.ciudad,
		registro: d.registro,
		candidatos: d.candidatos.map(aligerar),
		enfoques: d.enfoques,
		temas: sitio.temas
	};
};
