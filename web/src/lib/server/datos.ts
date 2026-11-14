/** Acceso a los datos exportados por el pipeline (`make datos`). Solo en build/servidor. */
import { error } from '@sveltejs/kit';
import type { Candidato, DatosCiudad, DatosSitio } from '../contrato.gen';
import type { CandidatoMin } from '../termometro';
import raw from './datos.gen.json';

export const sitio = raw as unknown as DatosSitio;

export const ciudadesActivas = () => sitio.ciudades.filter((c) => c.activa);

export function datosCiudad(id: string): DatosCiudad & { registro: DatosSitio['ciudades'][number] } {
	const registro = ciudadesActivas().find((c) => c.id === id);
	const datos = sitio.datos[id];
	if (!registro || !datos) error(404, 'Ciudad no encontrada');
	return { ...datos, registro };
}

/** Versión liviana para listados y el flujo: sin citas, votos ni justificaciones. */
export function aligerar(c: Candidato): CandidatoMin {
	return {
		id: c.id,
		nombre: c.nombre,
		lista: c.lista,
		organizacion: c.organizacion,
		foto: c.foto,
		plan_trabajo: { disponible: c.plan_trabajo.disponible },
		propuestas: (c.propuestas ?? []).map((p) => ({
			id: p.id,
			tema: p.tema,
			resumen: p.resumen,
			pagina: p.pagina,
			enfoques: p.enfoques,
			rubrica: {
				meta: { valor: p.rubrica.meta.valor, consenso: p.rubrica.meta.consenso },
				plazo: { valor: p.rubrica.plazo.valor, consenso: p.rubrica.plazo.consenso },
				financiamiento: { valor: p.rubrica.financiamiento.valor, consenso: p.rubrica.financiamiento.consenso },
				competencia_municipal: { valor: p.rubrica.competencia_municipal.valor, consenso: p.rubrica.competencia_municipal.consenso }
			}
		}))
	};
}
